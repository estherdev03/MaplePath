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
noc_repository=NOCRepository(db_service=db_service)
noc_service = NOCService(noc_repository=noc_repository)

# Extentions
db_service.create_extention(["vector", "pg_trgm", "unaccent"])

# Tables
db_service.create_tables(Base)

# Search vector
search_vector_stmt = """
                    CREATE OR REPLACE FUNCTION noc_search_vector_update()
                    RETURNS trigger AS $$
                    BEGIN
                        NEW.search_vector :=
                            setweight(to_tsvector('english', coalesce(NEW.title,'')), 'A') ||
                            setweight(to_tsvector('english', array_to_string(NEW.example_titles,' ')), 'A') ||
                            setweight(to_tsvector('english', array_to_string(NEW.inclusions,' ')), 'A') ||
                            setweight(to_tsvector('english', coalesce(NEW.description,'')), 'B') ||
                            setweight(to_tsvector('english', array_to_string(NEW.main_duties,' ')), 'C');

                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    DROP TRIGGER IF EXISTS noc_search_vector_trigger
                    ON noc;

                    CREATE TRIGGER noc_search_vector_trigger
                    BEFORE INSERT OR UPDATE
                    ON noc
                    FOR EACH ROW
                    EXECUTE FUNCTION noc_search_vector_update();
                """
db_service.run_sql(search_vector_stmt)


# NOC table
noc_filepath = Path(__file__).parent/"data"/"noc.csv"
noc_service.init_noc_info(noc_filepath)



    