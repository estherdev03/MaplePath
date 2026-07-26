from __future__ import annotations
from typing import Tuple
from pydantic import BaseModel

from eligibility.constants import (
    ADAPTABILITY_MAX,
    AGE_POINTS,
    ARRANGED_EMPLOYMENT_POINTS,
    EDUCATION_POINTS,
    FIRST_LANGUAGE_POINTS,
    FSW_PASS_SCORE,
    SECOND_LANGUAGE_POINTS,
    WORK_EXPERIENCE_POINTS,
)
from graph.state.eligibility import (
    CanadianExperienceClassEligibility,
    FSWScoreBreakdown,
    FederalSkilledWorkerEligibility,
)
from graph.state.profile import EducationLevel
from graph.state.shared import UserProfile


class EligibilityService:
    def _fsw_calculator(self, user: UserProfile) -> Tuple[int, FSWScoreBreakdown]:
        fsw_score = FSWScoreBreakdown()

        # education
        if user.education and user.education.level:
            fsw_score.education_pts = EDUCATION_POINTS[user.education.level]

        # english is first language
        if (
            user.languages
            and user.languages.english
            and user.languages.english.is_first_language
        ):
            for score in user.languages.english.clb_scores:
                if score >= 7:
                    fsw_score.first_lang_pts += FIRST_LANGUAGE_POINTS[min(score, 10)]
            if user.languages.french and all(
                score >= 5 for score in user.languages.french.nclc_scores
            ):
                fsw_score.second_lang_pts = SECOND_LANGUAGE_POINTS
        # french is first language
        elif (
            user.languages
            and user.languages.french
            and user.languages.french.is_first_language
        ):
            for score in user.languages.french.nclc_scores:
                if score >= 7:
                    fsw_score.first_lang_pts += FIRST_LANGUAGE_POINTS[min(score, 10)]
            if user.languages.english and all(
                score >= 5 for score in user.languages.english.clb_scores
            ):
                fsw_score.second_lang_pts += SECOND_LANGUAGE_POINTS

        # work experience
        if (
            user.work_experience
            and user.work_experience.canada_years + user.work_experience.foreign_years
            > 0
        ):

            fsw_score.work_exp_pts = WORK_EXPERIENCE_POINTS[
                min(
                    user.work_experience.canada_years
                    + user.work_experience.foreign_years,
                    6,
                )
            ]

        # age
        if user.age and user.age >= 18:
            fsw_score.age_pts = AGE_POINTS[min(user.age, 46)]

        # employment
        if user.occupation.is_canada_employed:
            fsw_score.employment_pts = ARRANGED_EMPLOYMENT_POINTS

        # Adaptability
        adapt_pts = 0
        if user.spouse:
            # spouse languages
            if (
                user.spouse.languages
                and user.spouse.languages.english
                and user.spouse.languages.english.is_first_language
            ):
                if all(
                    score >= 4 for score in user.spouse.languages.english.clb_scores
                ):
                    adapt_pts += ADAPTABILITY["spouse_language"]
            elif (
                user.spouse.languages
                and user.spouse.languages.french
                and user.spouse.languages.french.is_first_language
            ):
                if all(
                    score >= 4 for score in user.spouse.languages.french.nclc_scores
                ):
                    adapt_pts += 5
            # spouse education
            if (
                user.spouse.education
                and user.spouse.education.level != EducationLevel.SECONDARY
                and user.spouse.education.level != EducationLevel.ONE_YEAR
            ):
                adapt_pts += 5
            # spouse work exp
            if user.spouse.canadian_experience >= 1:
                adapt_pts += 5

        if user.canada_education and user.canada_education.credential_years >= 1:
            adapt_pts += 5
        if (
            user.work_experience
            and user.work_experience.canada_years >= 1
            and user.occupation
            and user.occupation.teer in [0, 1, 2, 3]
        ):
            adapt_pts += 10
        if user.occupation and user.occupation.is_canada_employed:
            adapt_pts += 5
        if user.relative_in_can or (user.spouse and user.spouse.relative_in_can):
            adapt_pts += 5
        fsw_score.adaptability = min(adapt_pts, ADAPTABILITY_MAX)
        total_pts = sum(fsw_score.model_dump().values())
        return total_pts, fsw_score

    def federal_skilled_worker_evaluator(
        self,
        user: UserProfile,
    ) -> FederalSkilledWorkerEligibility:

        skilled_worker_eligibility = FederalSkilledWorkerEligibility()

        # Teer
        if user.occupation and user.occupation.teer in [0, 1, 2, 3]:
            skilled_worker_eligibility.eligible_teer = True

        # Work experience
        if user.work_experience and (
            user.work_experience.continuous_fulltime_canada_years >= 1
            or user.work_experience.continuous_fulltime_foreign_years >= 1
        ):
            skilled_worker_eligibility.continuous_work_experience = True

        # Languages
        if user.languages:
            # english is first language and french is second language
            if (
                user.languages.english and user.languages.english.is_first_language
            ) and (
                user.languages.french and not user.languages.french.is_first_language
            ):
                clb7_or_more = all(
                    score >= 7 for score in user.languages.english.clb_scores
                )
                nclc5_or_more = all(
                    score >= 5 for score in user.languages.french.nclc_scores
                )
                if clb7_or_more and nclc5_or_more:
                    skilled_worker_eligibility.language_requirement_met = True
            # french is first language and english is second language
            elif (
                user.languages.french and user.languages.french.is_first_language
            ) and (
                user.languages.english and not user.languages.english.is_first_language
            ):
                nclc7_or_more = all(
                    score >= 7 for score in user.languages.french.nclc_scores
                )
                clb5_or_more = all(
                    score >= 5 for score in user.languages.english.clb_scores
                )
                if nclc7_or_more and clb5_or_more:
                    skilled_worker_eligibility.language_requirement_met = True

        # Education
        if user.education and (
            user.education.from_canada or user.education.eca_completed
        ):
            skilled_worker_eligibility.education_requirement_met = True

        # Job offer and funds
        if user.occupation and user.occupation.current_canada_employer:
            skilled_worker_eligibility.settlement_funds_required = False

        if (
            skilled_worker_eligibility.settlement_funds_required
            and user.current_available_funds >= 15263
        ):
            skilled_worker_eligibility.settlement_funds_met = True

        # FSW score
        score, breakdown = self._fsw_calculator(user)
        skilled_worker_eligibility.selection_factor_breakdown = breakdown
        skilled_worker_eligibility.selection_factor_score = score
        skilled_worker_eligibility.selection_factor_passed = score >= FSW_PASS_SCORE
