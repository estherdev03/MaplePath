from langchain.chat_models import init_chat_model

from crs.service import CRSService
from eligibility.service import EligibilityService
from graph.state.profile import Occupation, ProfileConfirmFormPayload, ProfileDraft

from dotenv import load_dotenv

from graph.state.shared import UserProfile
from noc.service import NOCService
from user_profile.types import LLMNocResult, NOCCandidate, NOCResult

load_dotenv()


class ProfileService:
    def __init__(
        self,
        noc_service: NOCService,
        crs_service: CRSService,
        eligibility_service: EligibilityService,
    ):
        self.crs_service = crs_service
        self.noc_service = noc_service
        self.eligibility_service = eligibility_service

    def parse(self, profile_text: str) -> ProfileDraft:
        llm = init_chat_model("openai:gpt-5.4-mini")
        structured_llm = llm.with_structured_output(ProfileDraft)
        response = structured_llm.invoke(f"""
        You are MaplePath's Professional Profile Parser.

        Your task is to extract structured profile information from unstructured text.

        # Rules

        - Extract only information explicitly stated in the text.
        - Never infer, assume, estimate, calculate, or invent information.
        - If a value is not provided, return null, add a missing field and a warning.
        - If information is ambiguous, return null and add a warning.
        - Preserve the original meaning of the source text.
        - Output must strictly conform to the target schema.
        - Do not include explanations outside the structured output.

        # Field Extraction

        ## Age
        Extract only if explicitly stated. Add WARNING if age is missing or invalid.

        Valid:
        - "Age: 29"

        Invalid:
        - Birth year only
        - Graduation year only

        ## Job Title
        Extract the user's most recent or current occupation if clearly stated. If not provided, add missing fields and warnings.

        If multiple occupations exist and recency is unclear:
        - return null
        - add warning

        ## Languages

        Extract English and French test results only if explicitly provided.

        Supported English tests:
        - IELTS
        - CELPIP
        - PTE

        Supported French tests:
        - TEF
        - TCF

        If detailed scores are missing:
        - set detail_scores to null, add missing fields and warnings

        Never generate missing scores.

        ## Work Experience

        Extract work experience only when explicitly supported by the text.

        Calculate:
        - total_years
        - canada_years
        - alberta_years

        only when sufficient employment dates or durations are available.

        If duration cannot be determined:
        - return 0 for that value, add missing fields and warnings

        # Missing Fields

        Populate missing_fields with any important profile fields and subfields that could not be extracted.

        Possible values:
        - age
        - job_title
        - languages
        - work_experience
        - etc
                                        
        Example: missing_fields=['languages.english.detail_scores', 'work_experience.canada_years', 'work_experience.alberta_years', etc]

        # Warnings

        Add warnings for:
        - ambiguous information
        - conflicting information
        - incomplete dates
        - partial language results
        - unclear employment history
                                        
        Example: warnings=['English language detailed scores were not provided.', 'Canada and Alberta work experience were not explicitly stated.', 'age is missing', etc]

        # Output

        Return a valid ProfileDraft object.

        Use null for unknown values.

        Never fabricate information.

        Profile Text: {profile_text}               
        """)
        print(response)
        return response

    def create(self, profile: ProfileConfirmFormPayload) -> UserProfile:
        occupation = self._get_occupation(
            profile.job_title, profile.job_responsibility, profile.have_canada_job_offer
        )
        user = UserProfile(
            age=profile.age,
            occupation=occupation,
            languages=profile.languages,
            work_experience=profile.work_experience,
            marital_status=profile.marital_status,
            education=profile.education,
            canada_education=profile.canada_education,
            provincial_nomination=profile.provincial_nomination,
            sibling_in_can=profile.sibling_in_can,
            relative_in_can=profile.relative_in_can,
            spouse=profile.spouse,
            current_available_funds=profile.current_available_funds,
        )
        return user

    def _get_occupation(
        self, job_title: str, job_responsibility: str, have_canada_job_offer: bool
    ) -> Occupation:
        noc = self._parse_NOC(
            job_title=job_title, job_responsibility=job_responsibility
        )
        return Occupation(
            title=noc.title,
            noc_code=noc.noc_code,
            teer=noc.teer,
            major_group_code=noc.major_group_code,
            minor_group_code=noc.minor_group_code,
            submajor_group_code=noc.submajor_group_code,
            noc_confidence=noc.noc_confidence,
            have_canada_job_offer=have_canada_job_offer,
        )

    def _parse_NOC(self, job_title: str, job_responsibility: str) -> NOCResult:
        llm = init_chat_model("openai:gpt-5.4-mini")
        structure_llm = llm.with_structured_output(LLMNocResult)

        search_result = self.noc_service.noc_hybrid_search(job_title)
        noc_candidates = [
            NOCCandidate(
                noc_code=r.noc_code,
                title=r.title,
                description=r.description,
                main_duties=r.main_duties,
                example_titles=r.example_titles,
                inclusions=r.inclusions,
                exclusions=r.exclusions,
            )
            for r in search_result
        ]
        result = structure_llm.invoke(f"""
        You are MaplePath's National Occupational Classification (NOC) Classification Expert.
        Your task is to identify the single best matching Canadian National Occupational Classification (NOC) occupation from the provided candidate occupations.

        ## User Job
        Job Title:
        {job_title}

        Job Responsibilities:
        {job_responsibility}

        ## Candidate NOC Occupations
        {noc_candidates}

        ## Instructions
        Evaluate every candidate carefully.

        Your decision must be based primarily on the user's actual job responsibilities, not the job title.

        When comparing candidates, use the following priority:

        1. Main duties (highest priority)
        2. Occupation description
        3. Example titles
        4. Inclusions
        5. Exclusions (ensure the user's work is not explicitly excluded)

        Do not assume responsibilities that were not explicitly provided.

        Do not infer experience level, industry, or technologies that are not stated.

        Ignore differences such as Junior, Senior, Lead, Principal, or Staff unless they fundamentally change the occupation.

        Do not choose a candidate simply because the title appears similar.

        A candidate should only be selected when the majority of the user's responsibilities align with that candidate's main duties.

        ## Confidence Score

        Return a confidence score between 0.0 and 1.0.

        Use the following guidelines:

        1.00
        Nearly perfect match. The user's responsibilities closely match the candidate's main duties.

        0.90 - 0.99
        Very strong match. Nearly all responsibilities align.

        0.75 - 0.89
        Good match. Most important responsibilities align, with minor differences.

        0.50 - 0.74
        Weak match. Some overlap exists, but important responsibilities differ.

        Below 0.50
        No suitable match.

        If no candidate is a reasonable match, return:

        - noc_code = None
        - title = None
        - main_duties = []
        - noc_confidence = 0.0
        - reasoning = "None of the provided candidates sufficiently match the user's responsibilities."

        ## Reasoning
        Provide a concise explanation (1–3 sentences) describing:
        - why the selected occupation was chosen,
        - which responsibilities matched the candidate's main duties,
        - if applicable, why similar candidates were less appropriate.

        Do not mention the confidence score in the reasoning.

        ## Output
        Return exactly one valid NOCResult object.

        Populate:
        - noc_code
        - title
        - main_duties
        - noc_confidence
        - reasoning

        Do not include markdown.

        Do not include explanations outside the structured output.

        Never invent an occupation that is not present in the candidate list.
        """)

        noc_profile = self.noc_service.get_one_by_noc_code(result.noc_code)

        return NOCResult(
            title=noc_profile.title,
            noc_code=noc_profile.noc_code,
            teer=noc_profile.teer,
            major_group_code=noc_profile.major_group_code,
            minor_group_code=noc_profile.minor_group_code,
            submajor_group_code=noc_profile.sub_major_group_code,
            noc_confidence=result.noc_confidence,
        )

    def calculate_CRS(self, user: UserProfile) -> UserProfile:
        user.crs_score = self.crs_service.calculate_crs(user)
        return user

    def evaluate_express_entry(self, user: UserProfile) -> UserProfile:
        user.eligibility = self.eligibility_service.evaluate_express_entry(user)
        return user
