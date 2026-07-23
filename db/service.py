from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class DatabaseService:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=True)
        self.SessionLocal = sessionmaker(self.engine)

    def create_extention(self, extentions: list[str]):
        with self.engine.begin() as conn:
            for ext in extentions:
                conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext}"))

    def create_tables(self, base):
        base.metadata.create_all(self.engine)

    def run_sql(self, stmt: str):
        with self.engine.begin() as conn:
            conn.execute(text(stmt))

    # def init_db(self, base):
    #     # create extension
    #     self.create_extention(["vector", "pg_trgm", "unaccent"])
    #     self.create_extention()
    #     with self.engine.begin() as conn:
    #         conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    #         conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    #         conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))

    #     # create tables
    #     base.metadata.create_all(self.engine)

    #     # init search vector
    #     with self.engine.begin() as conn:
    #         conn.execute()

    def create_session(self):
        """Create a db session"""
        return self.SessionLocal()

    def create_connection(self):
        """Create a read only or manually managed connection, must commit"""
        return self.engine.connect()

    def create_transactional_connection(self):
        """Create an auto commit/rollback connection"""
        return self.engine.begin()
