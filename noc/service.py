from dataclasses import asdict, dataclass
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_cohere import CohereRerank
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import requests

from db.models import NOC
from db.service import DatabaseService
from noc.repository import NOCRepository

load_dotenv()


@dataclass
class EmbeddingInfo:
    noc_code: str
    title: str
    description: str
    example_titles: list[str]
    inclusions: list[str]
    main_duties: list[str]
    employment_requirements: list[str]
    additional_information: list[str]
    exclusions: list[str]


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
        return self.noc_repository.text_search(query)

    def noc_hybrid_search(self, query: str) -> list[NOC]:
        """Combine both semantic and keyword search result, then rerank using Cohere LLM"""
        semantic_result = self.noc_semantic_search(query)
        keyword_result = self.noc_keyword_search(query)
        combined_result = list(set(semantic_result + keyword_result))
        combined_result_text = [res.embedding_text for res in combined_result]
        reranked_result = self.rerank_engine.rerank(
            documents=combined_result_text, query=query, top_n=5
        )
        result = [combined_result[r["index"]] for r in reranked_result]
        return result

    def get_one_by_noc_code(self, noc_code: str) -> NOC | None:
        result = self.noc_repository.get_one_by_noc_code(noc_code)
        if not result:
            raise ValueError(f"NOC profile not found for noc code: {noc_code}")
        return result


db = DatabaseService(os.getenv("DB_URL"))
repo = NOCRepository(db)
service = NOCService(repo)
res = service.get_one_by_noc_code("21231")
for key, val in vars(res).items():
    print(f"{key}: {val}")
