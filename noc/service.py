from collections import defaultdict
from dataclasses import asdict
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_cohere import CohereRerank
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import requests

from db.models import NOC
from noc.repository import NOCRepository
from noc.types import EmbeddingInfo, IdealNOC

load_dotenv()

K_RRF = 60


class NOCService:
    def __init__(self, noc_repository: NOCRepository):
        self.noc_repository = noc_repository
        self.rerank_engine = CohereRerank(
            cohere_api_key=os.getenv("COHERE_API_KEY"), model="rerank-english-v3.0"
        )

    def _get_noc_code_list(self, filepath: str) -> list[str]:
        df = pd.read_csv(filepath, dtype={"Code - NOC 2021 V1.0": str})
        return df.loc[
            df["Hierarchical structure"] == "Unit Group", "Code - NOC 2021 V1.0"
        ].to_numpy()

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
        full_title = title_h2.get_text(" ", strip=True)
        noc_code, title = full_title.split("–", 1)
        noc_code = noc_code.strip()
        title = title.strip()

        # description
        description = title_h2.find_next("p").get_text(" ", strip=True)

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
                inclusions = [li.get_text(" ", strip=True) for li in ul.find_all("li")]

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
            for dt in section.find_all("dt"):
                dd = dt.find_next_sibling("dd")
                if dd:
                    summary[dt.get_text(" ", strip=True)] = dd.get_text(
                        " ",
                        strip=True,
                    )

        teer = int(summary["TEER"].split("–")[0].strip())

        # Broad category
        broad_category_code = (
            summary["Broad occupational category"].split("–")[0].strip()
        )

        broad_category_detail = (
            summary["Broad occupational category"].split("–")[1].strip()
        )

        # Major group
        major_group_code = summary["Major group"].split("–")[0].strip()
        major_group_detail = summary["Major group"].split("–")[1].strip()

        # Sub major group
        sub_major_group_code = summary["Sub-major group"].split("–")[0].strip()
        sub_major_group_detail = summary["Sub-major group"].split("–")[1].strip()

        # Minor group
        minor_group_code = summary["Minor group"].split("–")[0].strip()
        minor_group_detail = summary["Minor group"].split("–")[1].strip()

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

    def init_noc_info(self, filepath):
        noc_info_list = []
        noc_code_list = self._get_noc_code_list(filepath)
        for i, code in enumerate(noc_code_list):
            url = f"https://noc.esdc.gc.ca/Structure/NOCProfile?code={code}&version=2021.0"
            html = requests.get(url).text
            profile = self._parse_noc(html)
            noc_info_list.append(profile)
            print(f"Add profile {profile.noc_code}, index: {i}")
        self.noc_repository.save_all(noc_info_list)

    def noc_semantic_search(self, query: str) -> list[NOC]:
        """Job title NOC search using vector embedding"""
        emb_model = OpenAIEmbeddings(model="text-embedding-3-large")
        emb_query = emb_model.embed_query(query)
        return self.noc_repository.vector_search(emb_query)

    def noc_keyword_search(self, query: str) -> list[NOC]:
        """Job title NOC search using text search"""
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
        reranked_result = self.rerank_engine.rerank(
            documents=rrf_result_text, query=query, top_n=10
        )
        result = [rrf_result[r["index"]] for r in reranked_result]
        return result

    def get_one_by_noc_code(self, noc_code: str) -> NOC | None:
        result = self.noc_repository.get_one_by_noc_code(noc_code)
        if not result:
            raise ValueError(f"NOC profile not found for noc code: {noc_code}")
        return result
