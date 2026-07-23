from crs.constants import FIRST_LANGUAGE_MARRIED, FIRST_LANGUAGE_SINGLE, SECOND_LANGUAGE
from states.profile_states import FrenchTest, LanguageScore, NCLCScore


class FrenchService:
    def tef_to_nclc(self, score: LanguageScore) -> NCLCScore:
        return NCLCScore(
            speaking=self._tef_speaking_to_nclc(score.speaking),
            writing=self._tef_writing_to_nclc(score.writing),
            listening=self._tef_listening_to_nclc(score.listening),
            reading=self._tef_reading_to_nclc(score.reading),
        )

    def _tef_speaking_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 556:
            return 10
        if score >= 518:
            return 9
        if score >= 494:
            return 8
        if score >= 456:
            return 7
        if score >= 422:
            return 6
        if score >= 387:
            return 5
        if score >= 328:
            return 4

        return 0

    def _tef_writing_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 558:
            return 10
        if score >= 512:
            return 9
        if score >= 472:
            return 8
        if score >= 428:
            return 7
        if score >= 379:
            return 6
        if score >= 330:
            return 5
        if score >= 268:
            return 4

        return 0

    def _tef_listening_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 546:
            return 10
        if score >= 503:
            return 9
        if score >= 462:
            return 8
        if score >= 434:
            return 7
        if score >= 393:
            return 6
        if score >= 352:
            return 5
        if score >= 306:
            return 4

        return 0

    def _tef_reading_to_nclc(self, score: float | None) -> int:
        if score is None:
            return 0

        if score >= 546:
            return 10
        if score >= 503:
            return 9
        if score >= 462:
            return 8
        if score >= 434:
            return 7
        if score >= 393:
            return 6
        if score >= 352:
            return 5
        if score >= 306:
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
