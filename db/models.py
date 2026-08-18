from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Index, String, ARRAY, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TSVECTOR
from db.base import Base


# NOC model
class NOC(Base):
    __tablename__ = "noc"
    __table_args__ = (
        Index(
            "noc_bm25",
            "search_text",
            postgresql_using="bm25",
            postgresql_with={"text_config": "'english'", "b": "0.4"},
        ),
    )
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
    broad_category_code: Mapped[str]
    broad_category_detail: Mapped[str]
    major_group_code: Mapped[str]
    major_group_detail: Mapped[str]
    sub_major_group_code: Mapped[str]
    sub_major_group_detail: Mapped[str]
    minor_group_code: Mapped[str]
    minor_group_detail: Mapped[str]

    # Vector Search
    embedding_text: Mapped[str]
    embedding: Mapped[list[float]] = mapped_column(VECTOR(3072))

    # Keyword Search
    search_text: Mapped[str]

    def __eq__(self, other):
        return self.noc_code == other.noc_code

    def __hash__(self):
        return hash(self.noc_code)
