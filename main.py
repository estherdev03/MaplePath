from logging_config import configure_logging
from graph.state.profile import (
    CLBScore,
    CanadaEducation,
    Education,
    EducationLevel,
    EnglishScore,
    EnglishTest,
    Experience,
    FrenchScore,
    FrenchTest,
    LanguageScore,
    Languages,
    MaritalStatus,
    NCLCScore,
    ProfileConfirmEvent,
    ProfileConfirmFormPayload,
    ProfileDraftEvent,
    ProfileDraftPayload,
    SpouseProfile,
)
from graph.construct import compiled_graph

configure_logging()

# text = """
# I'm 28 years old,
# I'm a software engineer,
# I have 2 years working in Alberta, 1 year in Toronto, 1 year in Europe
# My IELTS is 8.5
# """

# payload = ProfileDraftPayload(text=text)
# event = ProfileDraftEvent(
#     event_type="profile_draft",
#     payload=payload,
# )

profile_payload = ProfileConfirmFormPayload(
    age=31,
    job_title="Software Developer",
    job_responsibility=(
        "Design, build and maintain backend REST APIs in Python, write unit "
        "tests, review code, and deploy services to AWS."
    ),
    have_canada_job_offer=False,
    languages=Languages(
        english=EnglishScore(
            test_name=EnglishTest.IELTS,
            overall_score=8.0,
            detail_scores=LanguageScore(
                speaking=7.5,
                writing=7.0,
                listening=8.5,
                reading=8.0,
            ),
            is_first_language=True,
        ),
        french=FrenchScore(
            test_name=FrenchTest.TEF,
            overall_score=371,
            detail_scores=LanguageScore(
                speaking=349,
                writing=316,
                listening=316,
                reading=263,
            ),
            is_first_language=False,
        ),
    ),
    work_experience=Experience(
        foreign_years=5,
        canada_years=2,
        alberta_years=1,
        continuous_fulltime_foreign_years=4,
        continuous_fulltime_canada_years=2,
        canada_work_exp_within_3_years=2,
        trade_exp_within_5_years=0,
    ),
    marital_status=MaritalStatus.MARRIED,
    education=Education(
        level=EducationLevel.MASTERS,
        has_COQ=False,
        from_canada=False,
        eca_completed=True,
    ),
    canada_education=CanadaEducation(
        completed=True,
        credential_years=2,
    ),
    provincial_nomination=False,
    sibling_in_can=True,
    relative_in_can=False,
    spouse=SpouseProfile(
        education=Education(
            level=EducationLevel.BACHELOR,
            has_COQ=False,
            from_canada=False,
            eca_completed=True,
        ),
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.CELPIP,
                overall_score=7,
                detail_scores=LanguageScore(
                    speaking=7,
                    writing=7,
                    listening=8,
                    reading=6,
                ),
                is_first_language=True,
            ),
            french=None,
        ),
        canadian_experience=1,
        relative_in_can=False,
    ),
    current_available_funds=25000,
)

event = ProfileConfirmEvent(event_type="profile_confirm", payload=profile_payload)

result = compiled_graph.invoke({"event": event})
print(result["profile"].advice)
