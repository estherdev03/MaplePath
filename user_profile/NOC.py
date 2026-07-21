from dataclasses import asdict, dataclass
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_cohere import CohereRerank
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import requests
from sqlalchemy import select, text
from sqlalchemy.orm import Session
import truststore
from db.database import db
from db.models import NOCProfile
from pydantic import BaseModel

truststore.inject_into_ssl()

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


class NOC:
    def __init__(self):
        df = pd.read_csv("noc.csv", dtype={"Code - NOC 2021 V1.0": str})
        self.noc_codes_list = df.loc[
            df["Hierarchical structure"] == "Unit Group", "Code - NOC 2021 V1.0"
        ].to_numpy()
        self.db = db

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

    def _parse_noc(self, html: str) -> NOCProfile:

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

        return NOCProfile(
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
            broad_category=summary["Broad occupational category"],
            major_group=summary["Major group"],
            sub_major_group=summary["Sub-major group"],
            minor_group=summary["Minor group"],
            embedding_text=embedding_text,
            embedding=embedding,
        )

    def collect_all_profiles_to_db(self):
        with Session(self.db.engine) as session:
            for i, code in enumerate(self.noc_codes_list):
                url = f"https://noc.esdc.gc.ca/Structure/NOCProfile?code={code}&version=2021.0"
                html = requests.get(url).text
                profile = self._parse_noc(html)
                self.noc_profiles_list.append(profile)
                session.add(profile)
                print(f"Add {code} profile to db. Index: {i}")
            session.commit()

    def noc_semantic_search(self, text: str) -> list[NOCProfile]:
        """NOC search based on meaning"""
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
        emb_query = embedding_model.embed_query(text)
        with Session(self.db.engine) as session:
            query_stmt = (
                select(NOCProfile)
                .order_by(NOCProfile.embedding.cosine_distance(emb_query))
                .limit(30)
            )
            result = session.scalars(query_stmt).all()
        return result

    def noc_keyword_search(self, query: str) -> list[NOCProfile]:
        """NOC text search based on query string"""
        stmt = select(NOCProfile).from_statement(text("""
            SELECT
                *,
                ts_rank(search_vector, query) as rank
            FROM 
                noc_profiles,
                phraseto_tsquery('english', :search_query) query
            WHERE search_vector @@ query
            ORDER BY rank DESC 
            LIMIT 30;
        """))
        with Session(self.db.engine) as session:
            result = session.scalars(stmt, {"search_query": query}).all()
            return result

    def hybrid_search(self, query: str) -> list[NOCProfile]:
        """Combine both semantic and keyword search, then rerank using llm, return the top 5 result"""
        co = CohereRerank(
            cohere_api_key=os.getenv("COHERE_API_KEY"), model="rerank-english-v3.0"
        )
        semantic_res = self.noc_semantic_search(query)
        keyword_res = self.noc_keyword_search(query)
        combined_res = list(set(semantic_res + keyword_res))
        rerank_text = [r.embedding_text for r in combined_res]
        rerank_result = co.rerank(documents=rerank_text, query=query, top_n=5)
        search_result = [combined_res[r["index"]] for r in rerank_result]
        return search_result


noc = NOC()
profiles = noc.hybrid_search("software")
for p in profiles:
    print("=============================")
    print(p.noc_code)
    print(p.title)
    print(p.description)
