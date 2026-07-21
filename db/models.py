from pgvector import vector
from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Computed, Index, String, ARRAY, text
from sqlalchemy.orm import Mapped, mapped_column
from db.database import db
from sqlalchemy.dialects.postgresql import TSVECTOR

# Database base and engine
Base = db.Base
engine = db.engine

with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))


# NOC profile model
class NOCProfile(Base):
    __tablename__ = "noc_profiles"
    __table_args__ = (Index("noc_search_idx", "search_vector", postgresql_using="gin"),)
    noc_code: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]

    example_titles: Mapped[list[str]] = mapped_column(ARRAY(String))
    inclusions: Mapped[list[str]] = mapped_column(ARRAY(String))

    main_duties: Mapped[list[str]] = mapped_column(ARRAY(String))
    employment_requirements: Mapped[list[str]] = mapped_column(ARRAY(String))
    additional_information: Mapped[list[str]] = mapped_column(ARRAY(String))
    exclusions: Mapped[list[str]] = mapped_column(ARRAY(String))

    teer: Mapped[int]
    broad_category: Mapped[str]
    major_group: Mapped[str]
    sub_major_group: Mapped[str]
    minor_group: Mapped[str]

    # Vector Search
    embedding_text: Mapped[str]
    embedding: Mapped[list[float]] = mapped_column(VECTOR(3072))

    # Full-text Search
    search_vector: Mapped[dict] = mapped_column(TSVECTOR)

    def __eq__(self, other):
        return self.noc_code == other.noc_code

    def __hash__(self):
        return hash(self.noc_code)


Base.metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(text("""
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
        ON noc_profiles;
                      
        CREATE TRIGGER noc_search_vector_trigger
        BEFORE INSERT OR UPDATE
        ON noc_profiles
        FOR EACH ROW
        EXECUTE FUNCTION noc_search_vector_update();
    """))
