from sqlalchemy import select, text

from db.models import NOC
from db.service import DatabaseService


class NOCRepository:
    """Handle NOC table data access"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

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
                .limit(30)
            )
            result = session.scalars(query_stmt).all()
            return result

    def text_search(self, query: str):
        stmt = select(NOC).from_statement(text("""
                    SELECT
                        *,
                        ts_rank(search_vector, query) as rank
                    FROM 
                        noc,
                        phraseto_tsquery('english', :search_query) query
                    WHERE search_vector @@ query
                    ORDER BY rank DESC 
                    LIMIT 30;
                """))
        with self.db_service.create_session() as session:
            result = session.scalars(stmt, {"search_query": query}).all()
            return result
