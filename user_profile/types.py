from dataclasses import dataclass


@dataclass
class NOCCandidate:
    noc_code: str
    title: str
    description: str
    main_duties: list[str]
    example_titles: list[str]
    inclusions: list[str]
    exclusions: list[str]


@dataclass
class LLMNocResult:
    noc_code: str | None
    title: str | None
    main_duties: list[str]
    noc_confidence: float
    reasoning: str


@dataclass
class NOCResult:
    title: str
    noc_code: str
    teer: int
    major_group_code: str
    minor_group_code: str
    submajor_group_code: str
    noc_confidence: float
