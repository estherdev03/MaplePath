from __future__ import annotations
from typing import Tuple

from eligibility.constants import (
    ADAPTABILITY_MAX,
    AGE_POINTS,
    ARRANGED_EMPLOYMENT_POINTS,
    EDUCATION_POINTS,
    FIRST_LANGUAGE_POINTS,
    FSW_PASS_SCORE,
    SECOND_LANGUAGE_POINTS,
    SETTLEMENT_FUNDS,
    SETTLEMENT_FUNDS_PER_ADDITIONAL_MEMBER,
    WORK_EXPERIENCE_POINTS,
)
from graph.state.eligibility import (
    CanadianExperienceClassEligibility,
    EligibilityResult,
    ExpressEntryEligibility,
    FSWScoreBreakdown,
    FederalSkilledTradesEligibility,
    FederalSkilledWorkerEligibility,
)
from graph.state.profile import MaritalStatus
from graph.state.shared import UserProfile


class EligibilityService:
    def _settlement_funds_needed(self, user: UserProfile) -> int:
        # family = applicant + spouse + dependent children (theirs or the spouse's)
        family_size = (
            1
            + (1 if user.marital_status == MaritalStatus.MARRIED else 0)
            + user.dependent_children
        )
        if family_size in SETTLEMENT_FUNDS:
            return SETTLEMENT_FUNDS[family_size]
        return SETTLEMENT_FUNDS[7] + SETTLEMENT_FUNDS_PER_ADDITIONAL_MEMBER * (
            family_size - 7
        )

    def _settlement_funds_waived(self, user: UserProfile) -> bool:
        # no proof of funds needed when authorized to work in Canada with a valid job offer
        return bool(
            user.authorized_to_work_in_canada
            and user.occupation
            and user.occupation.have_canada_job_offer
        )

    def _calculate_fsw(self, user: UserProfile) -> Tuple[int, FSWScoreBreakdown]:
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
            for score in user.languages.english.clb_scores.model_dump().values():
                if score >= 7:
                    fsw_score.first_lang_pts += FIRST_LANGUAGE_POINTS[min(score, 10)]
            if user.languages.french and all(
                score >= 5
                for score in user.languages.french.nclc_scores.model_dump().values()
            ):
                fsw_score.second_lang_pts = SECOND_LANGUAGE_POINTS
        # french is first language
        elif (
            user.languages
            and user.languages.french
            and user.languages.french.is_first_language
        ):
            for score in user.languages.french.nclc_scores.model_dump().values():
                if score >= 7:
                    fsw_score.first_lang_pts += FIRST_LANGUAGE_POINTS[min(score, 10)]
            if user.languages.english and all(
                score >= 5
                for score in user.languages.english.clb_scores.model_dump().values()
            ):
                fsw_score.second_lang_pts += SECOND_LANGUAGE_POINTS

        # work experience
        if (
            user.work_experience
            and user.work_experience.canada_years + user.work_experience.foreign_years
            >= 1
        ):

            fsw_score.work_exp_pts = WORK_EXPERIENCE_POINTS[
                min(
                    int(
                        user.work_experience.canada_years
                        + user.work_experience.foreign_years
                    ),
                    6,
                )
            ]

        # age
        if user.age and 18 <= user.age <= 46:
            fsw_score.age_pts = AGE_POINTS[user.age]

        # employment
        if user.occupation and user.occupation.have_canada_job_offer:
            fsw_score.employment_pts = ARRANGED_EMPLOYMENT_POINTS

        # Adaptability
        adapt_pts = 0
        if user.spouse:
            # spouse languages, CLB/NCLC 4+ in all abilities in either official language
            if user.spouse.languages:
                spouse_english = user.spouse.languages.english
                spouse_french = user.spouse.languages.french
                spouse_scores = [
                    spouse_english.clb_scores if spouse_english else None,
                    spouse_french.nclc_scores if spouse_french else None,
                ]
                if any(
                    scores
                    and all(score >= 4 for score in scores.model_dump().values())
                    for scores in spouse_scores
                ):
                    adapt_pts += 5
            # spouse past study in Canada, at least 2 academic years full-time
            if user.spouse.canada_study_years >= 2:
                adapt_pts += 5
            # spouse work exp
            if user.spouse.canadian_experience >= 1:
                adapt_pts += 5

        # at least 2 academic years of full-time study in Canada
        if user.canada_education and user.canada_education.credential_years >= 2:
            adapt_pts += 5
        if (
            user.work_experience
            and user.work_experience.canada_years >= 1
            and user.occupation
            and user.occupation.teer in [0, 1, 2, 3]
        ):
            adapt_pts += 10
        if user.occupation and user.occupation.have_canada_job_offer:
            adapt_pts += 5
        if user.relative_in_can or (user.spouse and user.spouse.relative_in_can):
            adapt_pts += 5
        fsw_score.adaptability_pts = min(adapt_pts, ADAPTABILITY_MAX)
        total_pts = sum(fsw_score.model_dump().values())
        return total_pts, fsw_score

    def _evaluate_federal_skilled_worker(
        self, user: UserProfile
    ) -> FederalSkilledWorkerEligibility:

        skilled_worker_eligibility = FederalSkilledWorkerEligibility()

        # Teer
        if user.occupation and user.occupation.teer in [0, 1, 2, 3]:
            skilled_worker_eligibility.eligible_teer_met = True

        # Work experience
        if user.work_experience and (
            user.work_experience.continuous_fulltime_canada_years >= 1
            or user.work_experience.continuous_fulltime_foreign_years >= 1
        ):
            skilled_worker_eligibility.continuous_work_experience_met = True

        # Languages: CLB/NCLC 7 in the first official language only, a second
        # language is not required (it only adds selection points)
        if user.languages:
            if user.languages.english and user.languages.english.is_first_language:
                clb7_or_more = all(
                    score >= 7
                    for score in user.languages.english.clb_scores.model_dump().values()
                )
                if clb7_or_more:
                    skilled_worker_eligibility.language_requirement_met = True
            elif user.languages.french and user.languages.french.is_first_language:
                nclc7_or_more = all(
                    score >= 7
                    for score in user.languages.french.nclc_scores.model_dump().values()
                )
                if nclc7_or_more:
                    skilled_worker_eligibility.language_requirement_met = True

        # Education
        if user.education and (
            user.education.from_canada or user.education.eca_completed
        ):
            skilled_worker_eligibility.education_requirement_met = True

        # Job offer and funds
        if self._settlement_funds_waived(user):
            skilled_worker_eligibility.settlement_funds_required = False
        else:
            skilled_worker_eligibility.settlement_funds_met = (
                user.current_available_funds >= self._settlement_funds_needed(user)
            )

        # FSW score
        score, breakdown = self._calculate_fsw(user)
        skilled_worker_eligibility.selection_factor_breakdown = breakdown
        skilled_worker_eligibility.selection_factor_score = score
        skilled_worker_eligibility.selection_factor_passed = score >= FSW_PASS_SCORE

        return skilled_worker_eligibility

    def _evaluate_canadian_exp_class(
        self, user: UserProfile
    ) -> CanadianExperienceClassEligibility:
        can_exp_class_eligibility = CanadianExperienceClassEligibility()

        # work experience
        if (
            user.work_experience
            and user.work_experience.canada_work_exp_within_3_years >= 1
        ):
            can_exp_class_eligibility.canadian_work_experience_met = True

        # occupation
        if user.occupation and user.occupation.teer in [0, 1, 2, 3]:
            can_exp_class_eligibility.eligible_teer_met = True

        # languages
        if user.languages:
            if user.occupation and user.occupation.teer in [0, 1]:
                if user.languages.english and user.languages.english.is_first_language:
                    clb7_or_more = all(
                        score >= 7
                        for score in user.languages.english.clb_scores.model_dump().values()
                    )
                    if clb7_or_more:
                        can_exp_class_eligibility.language_requirement_met = True
                elif user.languages.french and user.languages.french.is_first_language:
                    nclc7_or_more = all(
                        score >= 7
                        for score in user.languages.french.nclc_scores.model_dump().values()
                    )
                    if nclc7_or_more:
                        can_exp_class_eligibility.language_requirement_met = True
            elif user.occupation and user.occupation.teer in [2, 3]:
                if user.languages.english and user.languages.english.is_first_language:
                    clb5_or_more = all(
                        score >= 5
                        for score in user.languages.english.clb_scores.model_dump().values()
                    )
                    if clb5_or_more:
                        can_exp_class_eligibility.language_requirement_met = True
                elif user.languages.french and user.languages.french.is_first_language:
                    nclc5_or_more = all(
                        score >= 5
                        for score in user.languages.french.nclc_scores.model_dump().values()
                    )
                    if nclc5_or_more:
                        can_exp_class_eligibility.language_requirement_met = True
        return can_exp_class_eligibility

    def _evaluate_federal_skilled_trades(
        self, user: UserProfile
    ) -> FederalSkilledTradesEligibility:
        skilled_trade_eligilibility = FederalSkilledTradesEligibility()

        # Work experience
        if user.work_experience and user.work_experience.trade_exp_within_5_years >= 2:
            skilled_trade_eligilibility.skilled_trade_experience_within_5_years_met = (
                True
            )

        # Eligible trade
        if user.occupation and (
            user.occupation.major_group_code in ["72", "73", "82", "83", "92", "93"]
            or user.occupation.minor_group_code in ["6320"]
            or user.occupation.noc_code in ["62200"]
        ):
            skilled_trade_eligilibility.eligible_trade_met = True
            if (
                user.occupation.major_group_code == "72"
                and user.occupation.submajor_group_code == "726"
            ):
                skilled_trade_eligilibility.eligible_trade_met = False
            if (
                user.occupation.major_group_code == "93"
                and user.occupation.submajor_group_code == "932"
            ):
                skilled_trade_eligilibility.eligible_trade_met = False

        # Language
        if (
            user.languages
            and user.languages.english
            and user.languages.english.is_first_language
            and user.languages.english.clb_scores
        ):
            skilled_trade_eligilibility.speaking_listening_requirement_met = all(
                user.languages.english.clb_scores.model_dump()[skill] >= 5
                for skill in ["speaking", "listening"]
            )
            skilled_trade_eligilibility.reading_writing_requirement_met = all(
                user.languages.english.clb_scores.model_dump()[skill] >= 4
                for skill in ["reading", "writing"]
            )
        elif (
            user.languages
            and user.languages.french
            and user.languages.french.is_first_language
            and user.languages.french.nclc_scores
        ):
            skilled_trade_eligilibility.speaking_listening_requirement_met = all(
                user.languages.french.nclc_scores.model_dump()[skill] >= 5
                for skill in ["speaking", "listening"]
            )
            skilled_trade_eligilibility.reading_writing_requirement_met = all(
                user.languages.french.nclc_scores.model_dump()[skill] >= 4
                for skill in ["reading", "writing"]
            )

        # Job offer or trade certificate
        if (user.occupation and user.occupation.have_canada_job_offer) or (
            user.education and user.education.has_COQ
        ):
            skilled_trade_eligilibility.valid_job_offer_or_certificate_met = True

        # Proof of funds
        if self._settlement_funds_waived(user):
            skilled_trade_eligilibility.settlement_funds_required = False
        else:
            skilled_trade_eligilibility.settlement_funds_met = (
                user.current_available_funds >= self._settlement_funds_needed(user)
            )
        return skilled_trade_eligilibility

    def evaluate_express_entry(self, user: UserProfile) -> ExpressEntryEligibility:
        federal_skilled_worker_result = EligibilityResult()
        federal_skilled_trade_result = EligibilityResult()
        canadian_exp_class_result = EligibilityResult()

        # Federal Skilled Worker
        federal_skilled_worker_result.breakdown = self._evaluate_federal_skilled_worker(
            user
        )
        if (
            federal_skilled_worker_result.breakdown.continuous_work_experience_met
            and federal_skilled_worker_result.breakdown.eligible_teer_met
            and federal_skilled_worker_result.breakdown.language_requirement_met
            and federal_skilled_worker_result.breakdown.education_requirement_met
            and federal_skilled_worker_result.breakdown.selection_factor_passed
            and (
                federal_skilled_worker_result.breakdown.settlement_funds_met
                or not federal_skilled_worker_result.breakdown.settlement_funds_required
            )
        ):
            federal_skilled_worker_result.eligible = True

        # Federal Skilled Trade
        federal_skilled_trade_result.breakdown = self._evaluate_federal_skilled_trades(
            user
        )
        if (
            federal_skilled_trade_result.breakdown.skilled_trade_experience_within_5_years_met
            and federal_skilled_trade_result.breakdown.eligible_trade_met
            and federal_skilled_trade_result.breakdown.speaking_listening_requirement_met
            and federal_skilled_trade_result.breakdown.reading_writing_requirement_met
            and federal_skilled_trade_result.breakdown.valid_job_offer_or_certificate_met
            and (
                federal_skilled_trade_result.breakdown.settlement_funds_met
                or not federal_skilled_trade_result.breakdown.settlement_funds_required
            )
        ):
            federal_skilled_trade_result.eligible = True

        # Canadian Experience Class
        canadian_exp_class_result.breakdown = self._evaluate_canadian_exp_class(user)
        if (
            canadian_exp_class_result.breakdown.canadian_work_experience_met
            and canadian_exp_class_result.breakdown.eligible_teer_met
            and canadian_exp_class_result.breakdown.language_requirement_met
        ):
            canadian_exp_class_result.eligible = True

        return ExpressEntryEligibility(
            federal_skilled_worker=federal_skilled_worker_result,
            canadian_exp_class=canadian_exp_class_result,
            federal_skilled_trade=federal_skilled_trade_result,
        )
