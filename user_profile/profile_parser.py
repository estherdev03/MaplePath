from langchain.chat_models import init_chat_model

from states.graph_states import UserState
from states.profile_states import ProfileDraft

from dotenv import load_dotenv

load_dotenv()


def profile_parser(state: UserState):
    profile_text = state.event.payload.text
    print(profile_text)
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
    return {}


def profile_confirm(state: UserState):
    pass
