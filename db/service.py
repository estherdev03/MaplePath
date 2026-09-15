import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, db_url: str):
        if not db_url:
            raise ValueError(
                "DB_URL is not set. Define it in your environment or .env file."
            )
        try:
            self.engine = create_engine(db_url, echo=False)
        except ArgumentError as e:
            raise ValueError(f"Invalid DB_URL '{db_url}': {e}") from e
        logger.info("Database engine created for %s", self.engine.url)
        self.SessionLocal = sessionmaker(self.engine)

    def create_extention(self, extentions: list[str]):
        logger.debug("Ensuring database extensions exist: %s", extentions)
        with self.engine.begin() as conn:
            for ext in extentions:
                conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext}"))

    def create_tables(self, base):
        logger.debug("Creating tables from metadata")
        base.metadata.create_all(self.engine)

    def run_sql(self, stmt: str):
        logger.debug("Running raw SQL statement")
        with self.engine.begin() as conn:
            conn.execute(text(stmt))

    def create_session(self):
        """Create a db session"""
        return self.SessionLocal()

    def create_connection(self):
        """Create a read only or manually managed connection, must commit"""
        return self.engine.connect()

    def create_transactional_connection(self):
        """Create an auto commit/rollback connection"""
        return self.engine.begin()
