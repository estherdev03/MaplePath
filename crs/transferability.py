from typing import Tuple

from crs.constants import (
    EDUCATION_CAN_EXP,
    EDUCATION_LANGUAGE,
    FOREIGN_CAN_EXP,
    FOREIGN_EXP_LANGUAGE,
)
from crs.english import EnglishService
from crs.french import FrenchService
from states.profile_states import UserProfile


class TransferabilityService:
    def __init__(self, english_service: EnglishService, french_service: FrenchService):
        self.english_service = english_service
        self.french_service = french_service

    def _language_range(self, profile: UserProfile) -> Tuple[bool, bool, bool]:
        # english is first language
        if (
            profile.languages
            and profile.languages.english
            and profile.languages.english.is_first_language
        ):
            eng = profile.languages.english
            if not eng.clb_scores:
                test_name = eng.test_name
                scores = eng.detail_scores
                eng.clb_scores = self.english_service.english_to_clb(test_name, scores)
            clb_scores = eng.clb_scores
            all_clb5_or_higher = all(
                score >= 5 for score in clb_scores.model_dump().values()
            )
            all_clb7_or_higher = all(
                score >= 7 for score in clb_scores.model_dump().values()
            )
            all_clb9_or_higher = all(
                score >= 9 for score in clb_scores.model_dump().values()
            )
            return all_clb5_or_higher, all_clb7_or_higher, all_clb9_or_higher
        # french is first language
        elif (
            profile.languages
            and profile.languages.french
            and profile.languages.french.is_first_language
        ):
            french = profile.languages.french
            if not french.nclc_scores:
                test_name = french.test_name
                scores = french.detail_scores
                french.nclc_scores = self.french_service.french_to_nclc(
                    test_name, scores
                )
            nclc_scores = french.nclc_scores
            all_nclc5_or_higher = all(
                score >= 5 for score in nclc_scores.model_dump().values()
            )
            all_nclc7_or_higher = all(
                score >= 7 for score in nclc_scores.model_dump().values()
            )
            all_nclc9_or_higher = all(
                score >= 9 for score in nclc_scores.model_dump().values()
            )
            return all_nclc5_or_higher, all_nclc7_or_higher, all_nclc9_or_higher
        return False, False, False

    def education_language_points_calc(self, profile: UserProfile) -> int:
        education = profile.education
        # invalid education
        if education and not education.from_canada and not education.eca_completed:
            edu_lang_points = 0
        else:
            _, all_clb7, all_clb9 = self._language_range(profile)
            if all_clb9:
                edu_lang_points = EDUCATION_LANGUAGE[education.level][1]
            elif all_clb7:
                edu_lang_points = EDUCATION_LANGUAGE[education.level][0]
            else:
                edu_lang_points = 0
        return edu_lang_points

    def education_can_exp_points_calc(self, profile: UserProfile) -> int:
        # invalid experience
        if not profile.work_experience or not profile.work_experience.canada_years:
            return 0

        # invalid education
        if (
            not profile.education
            or (
                not profile.education.from_canada
                and not profile.education.eca_completed
            )
            or not profile.education.level
        ):
            return 0

        can_exp = int(profile.work_experience.canada_years)
        if can_exp == 1:
            return EDUCATION_CAN_EXP[profile.education.level][0]
        elif can_exp > 1:
            return EDUCATION_CAN_EXP[profile.education.level][1]
        else:
            return 0

    def foreign_exp_lang_points_calc(self, profile: UserProfile) -> int:
        _, all_clb7, all_clb9 = self._language_range(profile)
        if not profile.work_experience or not profile.work_experience.foreign_years:
            return 0
        yoe = min(int(profile.work_experience.foreign_years), 3)
        if all_clb9:
            return FOREIGN_EXP_LANGUAGE[yoe][1]
        elif all_clb7:
            return FOREIGN_EXP_LANGUAGE[yoe][0]
        else:
            return 0

    def foreign_can_exp_points_calc(self, profile: UserProfile) -> int:
        exp = profile.work_experience
        if (
            not exp
            or not exp.canada_years
            or not exp.foreign_years
            or int(exp.canada_years) <= 0
        ):
            return 0
        else:
            can_yoe = min(int(exp.canada_years), 2)
            foreign_yoe = min(int(exp.foreign_years), 3)
            return FOREIGN_CAN_EXP[foreign_yoe][can_yoe - 1]

    def trade_lang_points_calc(self, profile: UserProfile) -> int:
        if not profile.education or not profile.education.has_COQ:
            return 0
        else:
            all_clb5, all_clb7, _ = self._language_range(profile)
            if all_clb7:
                return 50
            elif all_clb5:
                return 25
            else:
                return 0
