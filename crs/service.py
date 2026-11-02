from crs.constants import (
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
from crs.english import EnglishService
from crs.french import FrenchService
from crs.transferability import TransferabilityService
from graph.state.profile import (
    CRSBreakdown,
    CRSScore,
    MaritalStatus,
    SpouseBreakdown,
)
from graph.state.shared import UserProfile


class CRSService:
    def __init__(
        self,
        english_service: EnglishService,
        french_service: FrenchService,
        transferability_service: TransferabilityService,
    ):
        self.english_service = english_service
        self.french_service = french_service
        self.transferability_service = transferability_service

    def calculate_crs(self, profile: UserProfile):
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
        if (
            profile.languages
            and profile.languages.english
            and profile.languages.english.is_first_language
        ):
            profile.languages.english.clb_scores = self.english_service.resolve_clb(
                profile.languages.english
            )
            return self.english_service.clb_to_points(
                profile.languages.english.clb_scores, is_married, True
            )
        if (
            profile.languages
            and profile.languages.french
            and profile.languages.french.is_first_language
        ):
            profile.languages.french.nclc_scores = self.french_service.resolve_nclc(
                profile.languages.french
            )
            return self.french_service.nclc_to_points(
                profile.languages.french.nclc_scores, is_married, True
            )
        return 0

    def _second_language_points(self, profile: UserProfile) -> int:
        is_married = profile.marital_status == MaritalStatus.MARRIED
        if (
            profile.languages.english
            and not profile.languages.english.is_first_language
        ):
            profile.languages.english.clb_scores = self.english_service.resolve_clb(
                profile.languages.english
            )
            return self.english_service.clb_to_points(
                scores=profile.languages.english.clb_scores, is_married=is_married
            )
        elif (
            profile.languages.french and not profile.languages.french.is_first_language
        ):
            profile.languages.french.nclc_scores = self.french_service.resolve_nclc(
                profile.languages.french
            )
            return self.french_service.nclc_to_points(
                scores=profile.languages.french.nclc_scores, is_married=is_married
            )
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

        spouse_languages = profile.spouse.languages
        english = spouse_languages.english if spouse_languages else None
        french = spouse_languages.french if spouse_languages else None
        # convert every spouse test, FSW adaptability accepts either official language
        if english and english.test_name and english.detail_scores:
            english.clb_scores = self.english_service.english_to_clb(
                english.test_name, english.detail_scores
            )
        if french and french.test_name and french.detail_scores:
            french.nclc_scores = self.french_service.french_to_nclc(
                french.test_name, french.detail_scores
            )

        # CRS scores the spouse's first official language only
        if english and english.is_first_language:
            first_language_scores = english.clb_scores
        elif french and french.is_first_language:
            first_language_scores = french.nclc_scores
        else:
            first_language_scores = None

        if first_language_scores:
            language_points = sum(
                SPOUSE_LANGUAGE_POINTS[min(score, 10)] if score >= 4 else 0
                for score in first_language_scores.model_dump().values()
            )
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
        education_lang_point = (
            self.transferability_service.education_language_points_calc(profile)
        )
        education_can_exp_points = (
            self.transferability_service.education_can_exp_points_calc(profile)
        )
        foreign_exp_lang_points = (
            self.transferability_service.foreign_exp_lang_points_calc(profile)
        )
        foreign_can_exp_points = (
            self.transferability_service.foreign_can_exp_points_calc(profile)
        )
        trade_lang_points = self.transferability_service.trade_lang_points_calc(profile)
        # each group (education, foreign work experience, certificate of
        # qualification) is capped at 50, the section at 100
        return min(
            min(education_lang_point + education_can_exp_points, 50)
            + min(foreign_exp_lang_points + foreign_can_exp_points, 50)
            + min(trade_lang_points, 50),
            100,
        )

    def _canadian_study_points(self, profile: UserProfile):
        if (
            not profile.canada_education
            or not profile.canada_education.completed
            or profile.canada_education.credential_years < 1
        ):
            return 0
        else:
            # 1-2 year credential -> 15, 3+ year credential -> 30
            if profile.canada_education.credential_years < 3:
                return 15
            else:
                return 30

    def _french_bonus_points(self, profile: UserProfile):
        if profile.languages and profile.languages.french:
            french = profile.languages.french
            if french.detail_scores and not french.nclc_scores:
                test_name = french.test_name
                scores = french.detail_scores
                nclc_scores = self.french_service.french_to_nclc(test_name, scores)
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
                        clb_scores = self.english_service.english_to_clb(
                            test_name, scores
                        )
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
