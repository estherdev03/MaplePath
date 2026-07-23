from crs.constants import FIRST_LANGUAGE_MARRIED, FIRST_LANGUAGE_SINGLE, SECOND_LANGUAGE
from states.profile_states import CLBScore, EnglishTest, LanguageScore


class EnglishService:
    # ================= IELTS ==========================================
    def ielts_to_clb(self, score: LanguageScore) -> CLBScore:
        return CLBScore(
            speaking=self._ielts_speaking_to_clb(score.speaking),
            writing=self._ielts_writing_to_clb(score.writing),
            listening=self._ielts_listening_to_clb(score.listening),
            reading=self._ielts_reading_to_clb(score.reading),
        )

    def _ielts_speaking_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 7.5:
            return 10
        if score >= 7.0:
            return 9
        if score >= 6.5:
            return 8
        if score >= 6.0:
            return 7
        if score >= 5.5:
            return 6
        if score >= 5.0:
            return 5
        if score >= 4.0:
            return 4

        return 0

    def _ielts_writing_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 7.5:
            return 10
        if score >= 7.0:
            return 9
        if score >= 6.5:
            return 8
        if score >= 6.0:
            return 7
        if score >= 5.5:
            return 6
        if score >= 5.0:
            return 5
        if score >= 4.0:
            return 4

        return 0

    def _ielts_listening_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 8.5:
            return 10
        if score >= 8.0:
            return 9
        if score >= 7.5:
            return 8
        if score >= 6.0:
            return 7
        if score >= 5.5:
            return 6
        if score >= 5.0:
            return 5
        if score >= 4.5:
            return 4

        return 0

    def _ielts_reading_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 8.0:
            return 10
        if score >= 7.0:
            return 9
        if score >= 6.5:
            return 8
        if score >= 6.0:
            return 7
        if score >= 5.0:
            return 6
        if score >= 4.0:
            return 5
        if score >= 3.5:
            return 4

        return 0

    # ================= CELPIP ==========================================
    def celpip_to_clb(self, score: LanguageScore) -> CLBScore:
        return CLBScore(
            speaking=self.celpip_score_to_clb(score.speaking),
            writing=self._celpip_score_to_clb(score.writing),
            listening=self._celpip_score_to_clb(score.listening),
            reading=self._celpip_score_to_clb(score.reading),
        )

    def _celpip_score_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        score = int(score)

        if score >= 10:
            return 10
        if score >= 9:
            return 9
        if score >= 8:
            return 8
        if score >= 7:
            return 7
        if score >= 6:
            return 6
        if score >= 5:
            return 5
        if score >= 4:
            return 4

        return 0

    # ================= PTE ============================================
    def pte_to_clb(self, score: LanguageScore) -> CLBScore:
        return CLBScore(
            speaking=self._pte_speaking_to_clb(score.speaking),
            writing=self._pte_writing_to_clb(score.writing),
            listening=self._pte_listening_to_clb(score.listening),
            reading=self._pte_reading_to_clb(score.reading),
        )

    def _pte_speaking_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 89:
            return 10
        if score >= 84:
            return 9
        if score >= 76:
            return 8
        if score >= 68:
            return 7
        if score >= 59:
            return 6
        if score >= 51:
            return 5
        if score >= 42:
            return 4

        return 0

    def _pte_writing_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 90:
            return 10
        if score >= 88:
            return 9
        if score >= 79:
            return 8
        if score >= 69:
            return 7
        if score >= 60:
            return 6
        if score >= 51:
            return 5
        if score >= 41:
            return 4

        return 0

    def _pte_listening_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 89:
            return 10
        if score >= 82:
            return 9
        if score >= 71:
            return 8
        if score >= 60:
            return 7
        if score >= 50:
            return 6
        if score >= 39:
            return 5
        if score >= 28:
            return 4

        return 0

    def _pte_reading_to_clb(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 88:
            return 10
        if score >= 78:
            return 9
        if score >= 69:
            return 8
        if score >= 60:
            return 7
        if score >= 51:
            return 6
        if score >= 42:
            return 5
        if score >= 33:
            return 4

        return 0

    def english_to_clb(self, test: EnglishTest, scores: LanguageScore):
        match test:
            case EnglishTest.IELTS:
                return self.ielts_to_clb(scores)
            case EnglishTest.PTE:
                return self.pte_to_clb(scores)
            case EnglishTest.CELPIP:
                return self.celpip_to_clb(scores)
            case _:
                raise ValueError("{test} test score is not accepted.")

    def clb_to_points(
        self,
        scores: CLBScore,
        is_married: bool = False,
        is_first_language: bool = False,
    ):
        # first language and single
        if is_first_language and not is_married:
            writing_points = (
                FIRST_LANGUAGE_SINGLE[min(scores.writing, 10)]
                if scores.writing >= 4
                else 0
            )
            reading_points = (
                FIRST_LANGUAGE_SINGLE[min(scores.reading, 10)]
                if scores.reading >= 4
                else 0
            )
            speaking_points = (
                FIRST_LANGUAGE_SINGLE[min(scores.speaking, 10)]
                if scores.speaking >= 4
                else 0
            )
            listening_points = (
                FIRST_LANGUAGE_SINGLE[min(scores.listening, 10)]
                if scores.listening >= 4
                else 0
            )

            return writing_points + reading_points + speaking_points + listening_points
        # first language and married
        elif is_first_language and is_married:
            writing_points = (
                FIRST_LANGUAGE_MARRIED[min(scores.writing, 10)]
                if scores.writing >= 4
                else 0
            )
            reading_points = (
                FIRST_LANGUAGE_MARRIED[min(scores.reading, 10)]
                if scores.reading >= 4
                else 0
            )
            speaking_points = (
                FIRST_LANGUAGE_MARRIED[min(scores.speaking, 10)]
                if scores.speaking >= 4
                else 0
            )
            listening_points = (
                FIRST_LANGUAGE_MARRIED[min(scores.listening, 10)]
                if scores.listening >= 4
                else 0
            )
            return writing_points + reading_points + speaking_points + listening_points

        # second language
        elif not is_first_language:
            writing_points = (
                SECOND_LANGUAGE[min(scores.writing, 10)] if scores.writing >= 5 else 0
            )
            reading_points = (
                SECOND_LANGUAGE[min(scores.reading, 10)] if scores.reading >= 5 else 0
            )
            speaking_points = (
                SECOND_LANGUAGE[min(scores.speaking, 10)] if scores.speaking >= 5 else 0
            )
            listening_points = (
                SECOND_LANGUAGE[min(scores.listening, 10)]
                if scores.listening >= 5
                else 0
            )
            return min(
                writing_points + reading_points + speaking_points + listening_points, 22
            )
