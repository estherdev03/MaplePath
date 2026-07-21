from __future__ import annotations
from states.profile_states import (
    CLBScore,
    CRSBreakdown,
    CRSScore,
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
    SpouseBreakdown,
    SpouseProfile,
    UserProfile,
)
from user_profile.CRS.english_convertor import clb_to_points, english_to_clb
from user_profile.CRS.french_convertor import french_to_nclc, nclc_to_points
from user_profile.CRS.transferability_calculator import (
    education_can_exp_points_calc,
    education_language_points_calc,
    foreign_can_exp_points_calc,
    foreign_exp_lang_points_calc,
    trade_lang_points_calc,
)
from user_profile.utils.constants import (
    AGE_POINTS_MARRIED,
    AGE_POINTS_SINGLE,
    CANADIAN_EXPERIENCE_MARRIED,
    CANADIAN_EXPERIENCE_SINGLE,
    EDUCATION_POINTS_MARRIED,
    EDUCATION_POINTS_SINGLE,
    SPOUSE_CANADIAN_EXPERIENCE,
    SPOUSE_EDUCATION,
    SPOUSE_LANGUAGE_POINTS,
)


class CRSCalculator:
    def calculate(self, profile: UserProfile) -> CRSScore:
        breakdown = CRSBreakdown()

        breakdown.age = self._age_points(profile)
        breakdown.education = self._education_points(profile)
        breakdown.first_language = self._first_language_points(profile)
        breakdown.second_language = self._second_language_points(profile)
        breakdown.canadian_experience = self._canadian_experience_points(profile)

        if profile.marital_status == MaritalStatus.MARRIED:
            breakdown.spouse_total, spouse_breakdown = self._spouse_points(profile)

        breakdown.skill_transferability = self._skill_transferability_points(profile)

        # Additional
        breakdown.provincial_nomination = 600 if profile.provincial_nomination else 0

        breakdown.canadian_study = self._canadian_study_points(profile)

        breakdown.french_bonus = self._french_bonus_points(profile)

        breakdown.sibling_in_canada = 15 if profile.sibling_in_can else 0

        if (
            breakdown.provincial_nomination
            + breakdown.french_bonus
            + breakdown.sibling_in_canada
            + breakdown.canadian_study
            <= 600
        ):
            total = sum(breakdown.model_dump().values())
        else:
            # Additional points are capped at 600
            total = (
                sum(breakdown.model_dump().values())
                - (
                    breakdown.provincial_nomination
                    + breakdown.french_bonus
                    + breakdown.sibling_in_canada
                    + breakdown.canadian_study
                )
                + 600
            )

        if profile.marital_status == MaritalStatus.MARRIED:
            return CRSScore(
                total=total,
                breakdown=breakdown,
                spouse_breakdown=spouse_breakdown,
            )
        else:
            return CRSScore(
                total=total,
                breakdown=breakdown,
            )

    def _age_points(self, profile: UserProfile) -> int:
        age = profile.age or 0

        if profile.marital_status == MaritalStatus.MARRIED:
            table = AGE_POINTS_MARRIED
        else:
            table = AGE_POINTS_SINGLE

        if age < 18:
            return 0

        if age >= 45:
            return 0

        return table[age]

    def _education_points(self, profile: UserProfile) -> int:
        # no profile -> 0
        if not profile.education:
            return 0

        # not from canada and not eca -> 0
        if not profile.education.eca_completed and not profile.education.from_canada:
            return 0

        if profile.marital_status == MaritalStatus.MARRIED:
            return EDUCATION_POINTS_MARRIED[profile.education.level]
        return EDUCATION_POINTS_SINGLE[profile.education.level]

    def _first_language_points(self, profile: UserProfile) -> int:
        is_married = profile.marital_status == MaritalStatus.MARRIED
        if profile.languages.english and profile.languages.english.is_first_language:
            test_name = profile.languages.english.test_name
            scores = profile.languages.english.detail_scores
            profile.languages.english.clb_scores = english_to_clb(test_name, scores)
            return clb_to_points(profile.languages.english.clb_scores, is_married, True)
        if profile.languages.french and profile.languages.french.is_first_language:
            test_name = profile.languages.french.test_name
            scores = profile.languages.french.detail_scores
            profile.languages.french.nclc_scores = french_to_nclc(test_name, scores)
            return nclc_to_points(
                profile.languages.french.nclc_scores, is_married, True
            )
        return 0

    def _second_language_points(self, profile: UserProfile) -> int:
        if (
            profile.languages.english
            and not profile.languages.english.is_first_language
        ):
            test_name = profile.languages.english.test_name
            scores = profile.languages.english.detail_scores
            profile.languages.english.clb_scores = english_to_clb(test_name, scores)
            return clb_to_points(scores=profile.languages.english.clb_scores)
        elif (
            profile.languages.french and not profile.languages.french.is_first_language
        ):
            test_name = profile.languages.french.test_name
            scores = profile.languages.french.detail_scores
            profile.languages.french.nclc_scores = french_to_nclc(test_name, scores)
            return nclc_to_points(scores=profile.languages.french.nclc_scores)
        return 0

    def _canadian_experience_points(self, profile: UserProfile):
        if not profile.work_experience:
            return 0
        years = profile.work_experience.canada_years
        if years < 1:
            return 0
        if profile.marital_status == MaritalStatus.MARRIED:
            return CANADIAN_EXPERIENCE_MARRIED[min(int(years), 5)]
        return CANADIAN_EXPERIENCE_SINGLE[min(int(years), 5)]

    def _spouse_points(self, profile: UserProfile) -> tuple[int, SpouseBreakdown]:
        # no profile or (not from canada and not eca)
        if not profile.spouse.education or (
            not profile.spouse.education.eca_completed
            and not profile.spouse.education.from_canada
        ):
            education_points = 0
        else:
            education_points = SPOUSE_EDUCATION[profile.spouse.education.level]

        if not profile.spouse.languages:
            language_points = 0
        elif profile.spouse.languages.english:
            english = profile.spouse.languages.english
            if english.test_name and english.detail_scores:
                clb_score = english_to_clb(english.test_name, english.detail_scores)
                writing_points = (
                    SPOUSE_LANGUAGE_POINTS[min(clb_score.writing, 10)]
                    if clb_score.writing >= 4
                    else 0
                )
                reading_points = (
                    SPOUSE_LANGUAGE_POINTS[min(clb_score.reading, 10)]
                    if clb_score.reading >= 4
                    else 0
                )
                speaking_points = (
                    SPOUSE_LANGUAGE_POINTS[min(clb_score.speaking, 10)]
                    if clb_score.speaking >= 4
                    else 0
                )
                listening_points = (
                    SPOUSE_LANGUAGE_POINTS[min(clb_score.listening, 10)]
                    if clb_score.listening >= 4
                    else 0
                )

                language_points = (
                    writing_points + reading_points + speaking_points + listening_points
                )
            else:
                language_points = 0
        elif profile.spouse.languages.french:
            french = profile.spouse.languages.french
            if french.test_name and french.detail_scores:
                nclc_score = french_to_nclc(french.test_name, french.detail_scores)
                writing_points = (
                    SPOUSE_LANGUAGE_POINTS[min(nclc_score.writing, 10)]
                    if nclc_score.writing >= 4
                    else 0
                )
                reading_points = (
                    SPOUSE_LANGUAGE_POINTS[min(nclc_score.reading, 10)]
                    if nclc_score.reading >= 4
                    else 0
                )
                speaking_points = (
                    SPOUSE_LANGUAGE_POINTS[min(nclc_score.speaking, 10)]
                    if nclc_score.speaking >= 4
                    else 0
                )
                listening_points = (
                    SPOUSE_LANGUAGE_POINTS[min(nclc_score.listening, 10)]
                    if nclc_score.listening >= 4
                    else 0
                )

                language_points = (
                    writing_points + reading_points + speaking_points + listening_points
                )
            else:
                language_points = 0
        else:
            language_points = 0

        can_exp_points = SPOUSE_CANADIAN_EXPERIENCE[
            min(int(profile.spouse.canadian_experience), 5)
        ]
        # update Spouse Breakdown
        spouse_breakdown = SpouseBreakdown(
            education=education_points,
            language=language_points,
            canadian_experience=can_exp_points,
        )
        total = education_points + language_points + can_exp_points
        return total, spouse_breakdown

    def _skill_transferability_points(self, profile: UserProfile) -> int:
        # education-languages
        education_lang_point = education_language_points_calc(profile)
        education_can_exp_points = education_can_exp_points_calc(profile)
        foreign_exp_lang_points = foreign_exp_lang_points_calc(profile)
        foreign_can_exp_points = foreign_can_exp_points_calc(profile)
        trade_lang_points = trade_lang_points_calc(profile)
        return (
            education_lang_point
            + education_can_exp_points
            + foreign_exp_lang_points
            + foreign_can_exp_points
            + trade_lang_points
        )

    def _canadian_study_points(self, profile: UserProfile):
        if (
            not profile.canada_education
            or not profile.canada_education.completed
            or profile.canada_education.credential_years == 0
        ):
            return 0
        else:
            if profile.canada_education.credential_years <= 2:
                return 15
            else:
                return 30

    def _french_bonus_points(self, profile: UserProfile):
        if profile.languages and profile.languages.french:
            french = profile.languages.french
            if french.detail_scores and not french.nclc_scores:
                test_name = french.test_name
                scores = french.detail_scores
                nclc_scores = french_to_nclc(test_name, scores)
                french.nclc_scores = nclc_scores
            elif french.nclc_scores:
                nclc_scores = french.nclc_scores
            is_nclc7_or_higher = all(
                score >= 7 for score in nclc_scores.model_dump().values()
            )
            if is_nclc7_or_higher:
                english = profile.languages.english
                if english:
                    if english.detail_scores and not english.clb_scores:
                        test_name = english.test_name
                        scores = english.detail_scores
                        clb_scores = english_to_clb(test_name, scores)
                    elif english.clb_scores:
                        clb_scores = english.clb_scores
                    is_clb5_or_higher = all(
                        score >= 5 for score in clb_scores.model_dump().values()
                    )
                    # NCLC7+ and CLB5+
                    if is_clb5_or_higher:
                        return 50
                # NCLC7+ and (no English result or CLB4-)
                return 25
        return 0


cal = CRSCalculator()

profile = UserProfile(
    age=29,
    job_title="Software Engineer",
    noc_code="21232",
    teer=1,
    noc_confidence=0.98,
    marital_status=MaritalStatus.MARRIED,
    education=Education(
        level=EducationLevel.MASTERS,
        from_canada=False,
        eca_completed=True,
    ),
    canada_education=CanadaEducation(
        completed=False,
        credential_years=0,
    ),
    work_experience=Experience(
        foreign_years=3,
        canada_years=1,
        alberta_years=1,
    ),
    languages=Languages(
        english=EnglishScore(
            test_name=EnglishTest.IELTS,
            overall_score=8.0,
            detail_scores=LanguageScore(
                listening=8.5,
                reading=8.0,
                writing=7.5,
                speaking=7.5,
            ),
            clb_scores=CLBScore(
                listening=10,
                reading=9,
                writing=10,
                speaking=10,
            ),
            is_first_language=True,
        ),
        french=FrenchScore(
            test_name=FrenchTest.TEF,
            overall_score=None,
            detail_scores=LanguageScore(
                listening=470,
                reading=470,
                writing=480,
                speaking=500,
            ),
            nclc_scores=NCLCScore(
                listening=8,
                reading=8,
                writing=8,
                speaking=8,
            ),
            is_first_language=False,
        ),
    ),
    provincial_nomination=True,
    sibling_in_can=True,
    spouse=SpouseProfile(
        education=Education(
            level=EducationLevel.BACHELOR,
            from_canada=False,
            eca_completed=True,
        ),
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                overall_score=6.5,
                detail_scores=LanguageScore(
                    listening=6.0,
                    reading=6.0,
                    writing=6.0,
                    speaking=6.0,
                ),
                clb_scores=CLBScore(
                    listening=7,
                    reading=7,
                    writing=7,
                    speaking=7,
                ),
                is_first_language=True,
            ),
            french=None,
        ),
        canadian_experience=1,
    ),
)

# profile = UserProfile(
#     age=32,
#     job_title="Administrative Assistant",
#     noc_code="13110",
#     teer=3,
#     noc_confidence=0.99,
#     marital_status=MaritalStatus.SINGLE,
#     education=Education(
#         level=EducationLevel.BACHELOR,
#         from_canada=False,
#         eca_completed=True,
#     ),
#     canada_education=CanadaEducation(
#         completed=False,
#         credential_years=0,
#     ),
#     work_experience=Experience(
#         foreign_years=5,
#         canada_years=0,
#         alberta_years=0,
#     ),
#     languages=Languages(
#         english=EnglishScore(
#             test_name=EnglishTest.IELTS,
#             overall_score=7.5,
#             detail_scores=LanguageScore(
#                 listening=8.0,
#                 reading=7.0,
#                 writing=7.0,
#                 speaking=7.0,
#             ),
#             clb_scores=CLBScore(
#                 listening=9,
#                 reading=9,
#                 writing=9,
#                 speaking=9,
#             ),
#             is_first_language=True,
#         ),
#         french=None,
#     ),
#     provincial_nomination=False,
#     sibling_in_can=False,
#     spouse=None,
# )

print(cal.calculate(profile))
