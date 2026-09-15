from sqlalchemy import func, select, text

from db.models import NOC
from db.service import DatabaseService
from noc.types import IdealNOC


class NOCRepository:
    """Handle NOC table data access"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def get_one_by_noc_code(self, noc_code: str):
        with self.db_service.create_session() as session:
            noc_profile = session.get(NOC, noc_code)
            return noc_profile

    def save_one(self, noc: NOC):
        with self.db_service.create_session() as session:
            session.add(noc)
            session.commit()

    def save_all(self, noc_list: list[NOC]):
        with self.db_service.create_session() as session:
            for i, noc in enumerate(noc_list):
                session.add(noc)
                print(f"Add {noc.noc_code} profile to db. Index: {i}")
            session.commit()

    def vector_search(self, search_vector: list[float]):
        with self.db_service.create_session() as session:
            query_stmt = (
                select(NOC)
                .order_by(NOC.embedding.cosine_distance(search_vector))
                .limit(50)
            )
            result = session.scalars(query_stmt).all()
            return result

    # BM25 keyword search
    def keyword_search(self, query: str):
        stmt = select(NOC).from_statement(text("""
                    SELECT *
                    FROM noc
                    ORDER BY search_text <@> to_bm25query(:search_query, 'noc_bm25')
                    LIMIT 50;
                """))
        with self.db_service.create_session() as session:
            result = session.scalars(stmt, {"search_query": query}).all()
            return result

    def get_ideal_pool_count(self, ideal: IdealNOC):
        with self.db_service.create_session() as session:
            # minor count
            minor_stmt = select(func.count(NOC.noc_code)).where(
                NOC.minor_group_code == ideal.minor_group_code,
                NOC.noc_code != ideal.noc_code,
            )
            minor_count = session.execute(minor_stmt).scalar() or 0

            # major count
            major_stmt = select(func.count(NOC.noc_code)).where(
                NOC.major_group_code == ideal.major_group_code,
                NOC.noc_code != ideal.noc_code,
                NOC.minor_group_code != ideal.minor_group_code,
            )
            major_count = session.execute(major_stmt).scalar() or 0
            return minor_count, major_count
