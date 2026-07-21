from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

db_url = os.getenv("DB_URL")


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self):
        self.engine = create_engine(db_url)
        self.Base = Base


db = Database()
