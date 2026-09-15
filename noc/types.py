from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class SingleExampleReport:
    case_type: str
    job_title: str
    bm25: Tuple[float, float]  # [NDCG, hit_rate]
    vector: Tuple[float, float]
    rrf: Tuple[float, float]
    hybrid: Tuple[float, float]


@dataclass
class CompleteExamplesReport:
    report: list[SingleExampleReport] = field(default_factory=list)


@dataclass
class RetrievalMethodMeanReport:
    bm25: Tuple[float, float]  # [NDCG, hit_rate]
    vector: Tuple[float, float]
    rrf: Tuple[float, float]
    hybrid: Tuple[float, float]


@dataclass
class IdealNOC:
    noc_code: str
    minor_group_code: str
    major_group_code: str


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
