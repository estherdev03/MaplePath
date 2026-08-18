import os
from pathlib import Path
from db.base import Base
from db.service import DatabaseService
from dotenv import load_dotenv
import db.models
from noc.repository import NOCRepository
from noc.service import NOCService
from truststore import inject_into_ssl

load_dotenv()
inject_into_ssl()

db_service = DatabaseService(db_url=os.getenv("DB_URL"))
noc_repository = NOCRepository(db_service=db_service)
noc_service = NOCService(noc_repository=noc_repository)

# Extentions
db_service.create_extention(["vector", "pg_textsearch"])

# Tables
db_service.create_tables(Base)

# Search vector
search_text_stmt = """
                    CREATE OR REPLACE FUNCTION noc_search_text_update()
                    RETURNS trigger AS $$
                    BEGIN
                        NEW.search_text :=
                            coalesce(NEW.title,'') || ' ' ||
                            coalesce(array_to_string(NEW.example_titles,' '),'') || ' ' ||
                            coalesce(array_to_string(NEW.inclusions,' '),'') || ' ' ||
                            coalesce(NEW.description,'') || ' ' ||
                            coalesce(array_to_string(NEW.main_duties,' '),'');
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    DROP TRIGGER IF EXISTS noc_search_text_trigger ON noc;

                    CREATE TRIGGER noc_search_text_trigger
                    BEFORE INSERT OR UPDATE ON noc
                    FOR EACH ROW
                    EXECUTE FUNCTION noc_search_text_update();
                """
db_service.run_sql(search_text_stmt)

# NOC table
noc_filepath = Path(__file__).parent / "data" / "noc.csv"
noc_service.init_noc_info(noc_filepath)
