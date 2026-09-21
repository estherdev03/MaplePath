from dataclasses import dataclass, field

from pydantic import BaseModel, Field


@dataclass
class NOCCandidate:
    noc_code: str
    title: str
    description: str
    main_duties: list[str]
    example_titles: list[str]
    inclusions: list[str]
    exclusions: list[str]


class LLMNocResult(BaseModel):
    noc_code: str | None = None
    title: str | None = None
    main_duties: list[str] = Field(default_factory=list)
    noc_confidence: float = 0.0
    reasoning: str = ""


@dataclass
class NOCResult:
    title: str
    noc_code: str
    teer: int
    major_group_code: str
    minor_group_code: str
    submajor_group_code: str
    noc_confidence: float
    reasoning: str = ""
    candidates: list[NOCCandidate] = field(default_factory=list)
