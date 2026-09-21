from collections import defaultdict
from dataclasses import asdict
import logging
import os
import time

from bs4 import BeautifulSoup
from cohere.errors import TooManyRequestsError
from dotenv import load_dotenv
from langchain_cohere import CohereRerank
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import requests

from db.models import NOC
from noc.repository import NOCRepository
from noc.types import EmbeddingInfo, IdealNOC

load_dotenv()

logger = logging.getLogger(__name__)

K_RRF = 60
NOC_FETCH_MAX_ATTEMPTS = 3
NOC_FETCH_BACKOFF_SECONDS = 2

# The Cohere trial key allows 10 calls/minute; a single /evaluate run alone
# makes 10 rerank calls, so it's easy to land on the wrong side of that
# window (e.g. right after a profile confirmation also used the key). A
# short wait is unlikely to help — the whole window needs to roll over —
# so back off long enough to plausibly cross into the next one.
COHERE_RERANK_MAX_ATTEMPTS = 2
COHERE_RERANK_BACKOFF_SECONDS = 20


class NOCService:
    def __init__(self, noc_repository: NOCRepository):
        self.noc_repository = noc_repository
        self.rerank_engine = CohereRerank(
            cohere_api_key=os.getenv("COHERE_API_KEY"), model="rerank-english-v3.0"
        )

    def _get_noc_code_list(self, filepath: str) -> list[str]:
        try:
            df = pd.read_csv(filepath, dtype={"Code - NOC 2021 V1.0": str})
        except FileNotFoundError as e:
            raise FileNotFoundError(f"NOC code list file not found: {filepath}") from e
        try:
            return df.loc[
                df["Hierarchical structure"] == "Unit Group", "Code - NOC 2021 V1.0"
            ].to_numpy()
        except KeyError as e:
            raise ValueError(
                f"NOC code list file '{filepath}' is missing expected column {e}"
            ) from e

    def _get_list_after_heading(self, soup: BeautifulSoup, heading: str) -> list[str]:
        h4 = soup.find("h4", string=lambda s: s and heading.lower() in s.lower())
        if not h4:
            return []

        panel = h4.find_parent("section")
        if not panel:
            return []

        return [li.get_text(" ", strip=True) for li in panel.find_all("li")]

    def _create_embedding(self, info: EmbeddingInfo):
        combined_info = ""
        for key, value in asdict(info).items():
            combined_info += f"{key}: {value}\n"
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
        embedding = embedding_model.embed_query(combined_info)
        return combined_info, embedding

    def _parse_noc(self, html: str) -> NOC:
        soup = BeautifulSoup(html, "html.parser")

        # title
        title_h2 = soup.find("h2")
        if not title_h2:
            raise ValueError("Could not find NOC title (unexpected page structure)")
        full_title = title_h2.get_text(" ", strip=True)
        if "–" not in full_title:
            raise ValueError(f"Could not parse NOC code/title from '{full_title}'")
        noc_code, title = full_title.split("–", 1)
        noc_code = noc_code.strip()
        title = title.strip()

        # description
        description_p = title_h2.find_next("p")
        description = description_p.get_text(" ", strip=True) if description_p else ""

        # example titles
        example_div = soup.find("div", id="ExampleTitles")
        example_titles = []
        inclusions = []
        if example_div:
            first_ul = example_div.find("ul")
            if first_ul:
                example_titles = [
                    li.get_text(" ", strip=True) for li in first_ul.find_all("li")
                ]

            inclusion_h5 = example_div.find("h5", string="Inclusions")
            if inclusion_h5:
                ul = inclusion_h5.find_next("ul")
                if ul:
                    inclusions = [
                        li.get_text(" ", strip=True) for li in ul.find_all("li")
                    ]

        # main section
        main_duties = self._get_list_after_heading(soup, "Main duties")

        employment_requirements = self._get_list_after_heading(
            soup,
            "Employment requirements",
        )

        additional_information = self._get_list_after_heading(
            soup,
            "Additional information",
        )

        exclusions = self._get_list_after_heading(
            soup,
            "Exclusions",
        )

        # breakdown summary
        summary = {}
        breakdown = soup.find("h3", string="Breakdown summary")
        if breakdown:
            section = breakdown.find_parent("section")
            if section:
                for dt in section.find_all("dt"):
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        summary[dt.get_text(" ", strip=True)] = dd.get_text(
                            " ",
                            strip=True,
                        )

        def _summary_field(key: str) -> str:
            if key not in summary:
                raise ValueError(
                    f"NOC {noc_code}: breakdown summary is missing '{key}'"
                )
            return summary[key]

        def _summary_code_and_detail(key: str) -> tuple[str, str]:
            value = _summary_field(key)
            if "–" not in value:
                raise ValueError(
                    f"NOC {noc_code}: could not parse code/detail from '{key}': '{value}'"
                )
            code, detail = value.split("–", 1)
            return code.strip(), detail.strip()

        teer_value = _summary_field("TEER")
        try:
            teer = int(teer_value.split("–")[0].strip())
        except ValueError as e:
            raise ValueError(
                f"NOC {noc_code}: could not parse TEER from '{teer_value}'"
            ) from e

        # Broad category
        broad_category_code, broad_category_detail = _summary_code_and_detail(
            "Broad occupational category"
        )

        # Major group
        major_group_code, major_group_detail = _summary_code_and_detail("Major group")

        # Sub major group
        sub_major_group_code, sub_major_group_detail = _summary_code_and_detail(
            "Sub-major group"
        )

        # Minor group
        minor_group_code, minor_group_detail = _summary_code_and_detail("Minor group")

        info = EmbeddingInfo(
            noc_code=noc_code,
            title=title,
            description=description,
            example_titles=example_titles,
            inclusions=inclusions,
            main_duties=main_duties,
            employment_requirements=employment_requirements,
            additional_information=additional_information,
            exclusions=exclusions,
        )
        embedding_text, embedding = self._create_embedding(info)

        return NOC(
            noc_code=noc_code,
            title=title,
            description=description,
            example_titles=example_titles,
            inclusions=inclusions,
            main_duties=main_duties,
            employment_requirements=employment_requirements,
            additional_information=additional_information,
            exclusions=exclusions,
            teer=teer,
            broad_category_code=broad_category_code,
            broad_category_detail=broad_category_detail,
            major_group_code=major_group_code,
            major_group_detail=major_group_detail,
            sub_major_group_code=sub_major_group_code,
            sub_major_group_detail=sub_major_group_detail,
            minor_group_code=minor_group_code,
            minor_group_detail=minor_group_detail,
            embedding_text=embedding_text,
            embedding=embedding,
        )

    # reciprocal rank fusion
    def _rrf(
        self, vector_result: list[NOC], keyword_result: list[NOC], k: int = K_RRF
    ) -> list[NOC]:
        retriever_results = [vector_result, keyword_result]
        unique_noc_dict: dict[str, NOC] = {}
        for noc in list(set(vector_result + keyword_result)):
            unique_noc_dict[noc.noc_code] = noc
        scores: dict[str, float] = defaultdict(float)
        for idx, retriever in enumerate(retriever_results):
            if idx == 0:
                w = 1
            else:
                w = 0.5
            for rank, noc in enumerate(retriever, start=1):
                scores[noc.noc_code] += w * 1.0 / (k + rank)
        sorted_noc = sorted(
            scores.items(), key=lambda x: -x[1]
        )  # descending order by scores
        result: list[NOC] = []
        for noc in sorted_noc:
            result.append(unique_noc_dict[noc[0]])
        return result

    def get_ideal_pool_count(self, ideal: IdealNOC) -> tuple[int, int]:
        return self.noc_repository.get_ideal_pool_count(ideal)

    def _fetch_and_parse_noc(self, code: str, i: int) -> NOC:
        url = f"https://noc.esdc.gc.ca/Structure/NOCProfile?code={code}&version=2021.0"
        last_error: Exception | None = None
        for attempt in range(1, NOC_FETCH_MAX_ATTEMPTS + 1):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return self._parse_noc(response.text)
            except (requests.RequestException, ValueError, AttributeError, KeyError) as e:
                last_error = e
                if attempt < NOC_FETCH_MAX_ATTEMPTS:
                    logger.warning(
                        "NOC %s (index %d) attempt %d/%d failed: %s; retrying",
                        code,
                        i,
                        attempt,
                        NOC_FETCH_MAX_ATTEMPTS,
                        e,
                    )
                    time.sleep(NOC_FETCH_BACKOFF_SECONDS * attempt)
        raise last_error

    def init_noc_info(self, filepath):
        noc_info_list = []
        failed_codes = []
        noc_code_list = self._get_noc_code_list(filepath)
        logger.info("Fetching %d NOC profiles from %s", len(noc_code_list), filepath)
        for i, code in enumerate(noc_code_list):
            try:
                profile = self._fetch_and_parse_noc(code, i)
            except requests.RequestException as e:
                logger.warning(
                    "Skipping NOC %s (index %d): request failed after %d attempts: %s",
                    code,
                    i,
                    NOC_FETCH_MAX_ATTEMPTS,
                    e,
                )
                failed_codes.append(code)
                continue
            except (ValueError, AttributeError, KeyError) as e:
                logger.warning(
                    "Skipping NOC %s (index %d): failed to parse page after %d attempts: %s",
                    code,
                    i,
                    NOC_FETCH_MAX_ATTEMPTS,
                    e,
                )
                failed_codes.append(code)
                continue
            noc_info_list.append(profile)
            logger.debug("Parsed profile %s, index: %d", profile.noc_code, i)

        if not noc_info_list:
            raise RuntimeError(
                "No NOC profiles were successfully fetched/parsed; nothing to save."
            )

        self.noc_repository.save_all(noc_info_list)

        if failed_codes:
            logger.warning(
                "Completed with %d failed NOC code(s): %s",
                len(failed_codes),
                failed_codes,
            )
        else:
            logger.info("Completed with %d NOC profile(s) saved", len(noc_info_list))

    def noc_semantic_search(self, query: str) -> list[NOC]:
        """Job title NOC search using vector embedding"""
        logger.debug("Running NOC semantic search for query: %r", query)
        emb_model = OpenAIEmbeddings(model="text-embedding-3-large")
        emb_query = emb_model.embed_query(query)
        return self.noc_repository.vector_search(emb_query)

    def noc_keyword_search(self, query: str) -> list[NOC]:
        """Job title NOC search using text search"""
        logger.debug("Running NOC keyword search for query: %r", query)
        return self.noc_repository.keyword_search(query)

    def noc_hybrid_search(self, query: str) -> list[NOC]:
        """Combine both semantic and keyword search result, then rerank using Cohere LLM"""
        semantic_result = self.noc_semantic_search(query)
        keyword_result = self.noc_keyword_search(query)
        rrf_result = self._rrf(semantic_result, keyword_result)[:20]
        rrf_result_text = [
            f"Title: {res.title}\nDuties:\n"
            + "\n".join(res.main_duties or [])
            + "\nExample Titles:\n"
            + "\n".join(res.example_titles or [])
            for res in rrf_result
        ]
        logger.debug("Reranking %d NOC candidates via Cohere", len(rrf_result_text))
        reranked_result = self._rerank_with_retry(rrf_result_text, query)
        result = [rrf_result[r["index"]] for r in reranked_result]
        return result

    def _rerank_with_retry(self, documents: list[str], query: str):
        last_error: TooManyRequestsError | None = None
        for attempt in range(1, COHERE_RERANK_MAX_ATTEMPTS + 1):
            try:
                return self.rerank_engine.rerank(documents=documents, query=query, top_n=10)
            except TooManyRequestsError as e:
                last_error = e
                if attempt < COHERE_RERANK_MAX_ATTEMPTS:
                    logger.warning(
                        "Cohere rerank rate-limited (attempt %d/%d); retrying in %ds",
                        attempt,
                        COHERE_RERANK_MAX_ATTEMPTS,
                        COHERE_RERANK_BACKOFF_SECONDS,
                    )
                    time.sleep(COHERE_RERANK_BACKOFF_SECONDS)
        raise last_error

    def get_one_by_noc_code(self, noc_code: str) -> NOC | None:
        result = self.noc_repository.get_one_by_noc_code(noc_code)
        if not result:
            logger.warning("NOC profile not found for noc code: %s", noc_code)
            raise ValueError(f"NOC profile not found for noc code: {noc_code}")
        return result
