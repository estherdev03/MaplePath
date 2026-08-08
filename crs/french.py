from crs.constants import FIRST_LANGUAGE_MARRIED, FIRST_LANGUAGE_SINGLE, SECOND_LANGUAGE
from graph.state.profile import FrenchTest, LanguageScore, NCLCScore


class FrenchService:
    def tef_to_nclc(self, score: LanguageScore) -> NCLCScore:
        return NCLCScore(
            speaking=self._tef_speaking_to_nclc(score.speaking),
            writing=self._tef_writing_to_nclc(score.writing),
            listening=self._tef_listening_to_nclc(score.listening),
            reading=self._tef_reading_to_nclc(score.reading),
        )

    def _tef_speaking_to_nclc(self, score: float | None) -> int:
        # TEF Canada "Équivalence ancien score" (pre-2019-09-30 chart).
        # Express Entry requires this table regardless of test date. Scale: /450.
        if score is None:
            return 0

        if score >= 393:
            return 10
        if score >= 371:
            return 9
        if score >= 349:
            return 8
        if score >= 310:
            return 7
        if score >= 271:
            return 6
        if score >= 226:
            return 5
        if score >= 181:
            return 4

        return 0

    def _tef_writing_to_nclc(self, score: float | None) -> int:
        # Scale: /450. Same bands as speaking.
        if score is None:
            return 0

        if score >= 393:
            return 10
        if score >= 371:
            return 9
        if score >= 349:
            return 8
        if score >= 310:
            return 7
        if score >= 271:
            return 6
        if score >= 226:
            return 5
        if score >= 181:
            return 4

        return 0

    def _tef_listening_to_nclc(self, score: float | None) -> int:
        # Scale: /360.
        if score is None:
            return 0

        if score >= 316:
            return 10
        if score >= 298:
            return 9
        if score >= 280:
            return 8
        if score >= 249:
            return 7
        if score >= 217:
            return 6
        if score >= 181:
            return 5
        if score >= 145:
            return 4

        return 0

    def _tef_reading_to_nclc(self, score: float | None) -> int:
        # Scale: /300. Note this differs from listening — do not share a table.
        if score is None:
            return 0

        if score >= 263:
            return 10
        if score >= 248:
            return 9
        if score >= 233:
            return 8
        if score >= 207:
            return 7
        if score >= 181:
            return 6
        if score >= 151:
            return 5
        if score >= 121:
            return 4

        return 0

    # ================= TCF CANADA =====================================
    def tcf_to_nclc(self, score: LanguageScore) -> NCLCScore:
        return NCLCScore(
            speaking=self._tcf_speaking_to_nclc(score.speaking),
            writing=self._tcf_writing_to_nclc(score.writing),
            listening=self._tcf_listening_to_nclc(score.listening),
            reading=self._tcf_reading_to_nclc(score.reading),
        )

    def _tcf_speaking_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 16:
            return 10
        if score >= 14:
            return 9
        if score >= 12:
            return 8
        if score >= 10:
            return 7
        if score >= 7:
            return 6
        if score >= 6:
            return 5
        if score >= 4:
            return 4

        return 0

    def _tcf_writing_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 16:
            return 10
        if score >= 14:
            return 9
        if score >= 12:
            return 8
        if score >= 10:
            return 7
        if score >= 7:
            return 6
        if score >= 6:
            return 5
        if score >= 4:
            return 4

        return 0

    def _tcf_listening_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 549:
            return 10
        if score >= 523:
            return 9
        if score >= 503:
            return 8
        if score >= 458:
            return 7
        if score >= 398:
            return 6
        if score >= 369:
            return 5
        if score >= 331:
            return 4

        return 0

    def _tcf_reading_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 549:
            return 10
        if score >= 524:
            return 9
        if score >= 499:
            return 8
        if score >= 453:
            return 7
        if score >= 406:
            return 6
        if score >= 375:
            return 5
        if score >= 342:
            return 4

        return 0

    def french_to_nclc(self, test: FrenchTest, scores: LanguageScore):
        match test:
            case FrenchTest.TCF:
                return self.tcf_to_nclc(scores)
            case FrenchTest.TEF:
                return self.tef_to_nclc(scores)
            case _:
                raise ValueError("{test} test score is not accepted.")

    def nclc_to_points(
        self,
        scores: NCLCScore,
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
