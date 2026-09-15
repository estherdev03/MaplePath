"""Tests for crs.french.FrenchService."""

import pytest
from graph.state.profile import FrenchTest, LanguageScore, NCLCScore


# ---- TEF ----
def test_tef_speaking_to_nclc_boundaries(french_service):
    """Boundaries 393/371/349/310/271/226/181 (scale /450); below-181 -> 0."""
    assert french_service._tef_speaking_to_nclc(393) == 10
    assert french_service._tef_speaking_to_nclc(371) == 9
    assert french_service._tef_speaking_to_nclc(349) == 8
    assert french_service._tef_speaking_to_nclc(310) == 7
    assert french_service._tef_speaking_to_nclc(271) == 6
    assert french_service._tef_speaking_to_nclc(226) == 5
    assert french_service._tef_speaking_to_nclc(181) == 4
    assert french_service._tef_speaking_to_nclc(180) == 0


def test_tef_writing_to_nclc_boundaries(french_service):
    """Same bands as speaking (scale /450)."""
    assert french_service._tef_writing_to_nclc(393) == 10
    assert french_service._tef_writing_to_nclc(371) == 9
    assert french_service._tef_writing_to_nclc(349) == 8
    assert french_service._tef_writing_to_nclc(310) == 7
    assert french_service._tef_writing_to_nclc(271) == 6
    assert french_service._tef_writing_to_nclc(226) == 5
    assert french_service._tef_writing_to_nclc(181) == 4
    assert french_service._tef_writing_to_nclc(180) == 0


def test_tef_listening_to_nclc_boundaries(french_service):
    """Boundaries 316/298/280/249/217/181/145 (scale /360)."""
    assert french_service._tef_listening_to_nclc(316) == 10
    assert french_service._tef_listening_to_nclc(298) == 9
    assert french_service._tef_listening_to_nclc(280) == 8
    assert french_service._tef_listening_to_nclc(249) == 7
    assert french_service._tef_listening_to_nclc(217) == 6
    assert french_service._tef_listening_to_nclc(181) == 5
    assert french_service._tef_listening_to_nclc(145) == 4
    assert french_service._tef_listening_to_nclc(144) == 0


def test_tef_reading_to_nclc_boundaries(french_service):
    """Boundaries 263/248/233/207/181/151/121 (scale /300) -- distinct table
    from listening despite overlapping raw numbers; assert they diverge."""
    assert french_service._tef_reading_to_nclc(263) == 10
    assert french_service._tef_reading_to_nclc(248) == 9
    assert french_service._tef_reading_to_nclc(233) == 8
    assert french_service._tef_reading_to_nclc(207) == 7
    assert french_service._tef_reading_to_nclc(181) == 6
    assert french_service._tef_reading_to_nclc(151) == 5
    assert french_service._tef_reading_to_nclc(121) == 4
    assert french_service._tef_reading_to_nclc(120) == 0

    # Same raw score (181) lands on NCLC 6 for reading but NCLC 5 for
    # listening -- the two tables must not be aliases of one another.
    assert french_service._tef_reading_to_nclc(181) == 6
    assert french_service._tef_listening_to_nclc(181) == 5


def test_tef_to_nclc_none_score_returns_zero(french_service):
    assert french_service._tef_speaking_to_nclc(None) == 0
    assert french_service._tef_writing_to_nclc(None) == 0
    assert french_service._tef_listening_to_nclc(None) == 0
    assert french_service._tef_reading_to_nclc(None) == 0


# ---- TCF Canada ----
def test_tcf_speaking_to_nclc_boundaries(french_service):
    """Boundaries 16/14/12/10/7/6/4."""
    assert french_service._tcf_speaking_to_nclc(16) == 10
    assert french_service._tcf_speaking_to_nclc(14) == 9
    assert french_service._tcf_speaking_to_nclc(12) == 8
    assert french_service._tcf_speaking_to_nclc(10) == 7
    assert french_service._tcf_speaking_to_nclc(7) == 6
    assert french_service._tcf_speaking_to_nclc(6) == 5
    assert french_service._tcf_speaking_to_nclc(4) == 4
    assert french_service._tcf_speaking_to_nclc(3) == 0


def test_tcf_writing_to_nclc_boundaries(french_service):
    """Same bands as speaking."""
    assert french_service._tcf_writing_to_nclc(16) == 10
    assert french_service._tcf_writing_to_nclc(14) == 9
    assert french_service._tcf_writing_to_nclc(12) == 8
    assert french_service._tcf_writing_to_nclc(10) == 7
    assert french_service._tcf_writing_to_nclc(7) == 6
    assert french_service._tcf_writing_to_nclc(6) == 5
    assert french_service._tcf_writing_to_nclc(4) == 4
    assert french_service._tcf_writing_to_nclc(3) == 0


def test_tcf_listening_to_nclc_boundaries(french_service):
    """Boundaries 549/523/503/458/398/369/331."""
    assert french_service._tcf_listening_to_nclc(549) == 10
    assert french_service._tcf_listening_to_nclc(523) == 9
    assert french_service._tcf_listening_to_nclc(503) == 8
    assert french_service._tcf_listening_to_nclc(458) == 7
    assert french_service._tcf_listening_to_nclc(398) == 6
    assert french_service._tcf_listening_to_nclc(369) == 5
    assert french_service._tcf_listening_to_nclc(331) == 4
    assert french_service._tcf_listening_to_nclc(330) == 0


def test_tcf_reading_to_nclc_boundaries(french_service):
    """Boundaries 549/524/499/453/406/375/342 -- distinct from listening."""
    assert french_service._tcf_reading_to_nclc(549) == 10
    assert french_service._tcf_reading_to_nclc(524) == 9
    assert french_service._tcf_reading_to_nclc(499) == 8
    assert french_service._tcf_reading_to_nclc(453) == 7
    assert french_service._tcf_reading_to_nclc(406) == 6
    assert french_service._tcf_reading_to_nclc(375) == 5
    assert french_service._tcf_reading_to_nclc(342) == 4
    assert french_service._tcf_reading_to_nclc(341) == 0

    # 523 clears the listening NCLC-9 bar but not the reading one.
    assert french_service._tcf_listening_to_nclc(523) == 9
    assert french_service._tcf_reading_to_nclc(523) == 8


def test_tcf_to_nclc_none_score_returns_zero(french_service):
    assert french_service._tcf_speaking_to_nclc(None) == 0
    assert french_service._tcf_writing_to_nclc(None) == 0
    assert french_service._tcf_listening_to_nclc(None) == 0
    assert french_service._tcf_reading_to_nclc(None) == 0


# ---- dispatch ----
def test_french_to_nclc_dispatches_tef_tcf(french_service):
    """french_to_nclc() routes to the right *_to_nclc() by FrenchTest enum."""
    tef_score = LanguageScore(speaking=393, writing=393, listening=316, reading=263)
    tcf_score = LanguageScore(speaking=16, writing=16, listening=549, reading=549)

    assert french_service.french_to_nclc(FrenchTest.TEF, tef_score) == (
        french_service.tef_to_nclc(tef_score)
    )
    assert french_service.french_to_nclc(FrenchTest.TCF, tcf_score) == (
        french_service.tcf_to_nclc(tcf_score)
    )


def test_french_to_nclc_unsupported_test_raises_value_error(french_service):
    """Unknown FrenchTest -> ValueError (same missing-f-prefix caveat as
    EnglishService.english_to_clb -- see tests/crs/test_english.py)."""
    with pytest.raises(ValueError, match="ielts test score is not accepted"):
        french_service.french_to_nclc(test="ielts", scores=LanguageScore())


# ---- nclc_to_points ----
def test_nclc_to_points_first_language_single_all_bands(french_service):
    """NCLC 4..10 -> FIRST_LANGUAGE_SINGLE table per skill; below 4 -> 0."""
    table = {4: 6, 5: 6, 6: 9, 7: 17, 8: 23, 9: 31, 10: 34}

    for nclc, points in table.items():
        scores = NCLCScore(speaking=nclc, writing=nclc, listening=nclc, reading=nclc)
        result = french_service.nclc_to_points(
            scores, is_married=False, is_first_language=True
        )
        assert result == points * 4

    below = NCLCScore(speaking=3, writing=3, listening=3, reading=3)
    assert (
        french_service.nclc_to_points(below, is_married=False, is_first_language=True)
        == 0
    )


def test_nclc_to_points_first_language_married_all_bands(french_service):
    """NCLC 4..10 -> FIRST_LANGUAGE_MARRIED table per skill; below 4 -> 0."""
    table = {4: 6, 5: 6, 6: 8, 7: 16, 8: 22, 9: 29, 10: 32}

    for nclc, points in table.items():
        scores = NCLCScore(speaking=nclc, writing=nclc, listening=nclc, reading=nclc)
        result = french_service.nclc_to_points(
            scores, is_married=True, is_first_language=True
        )
        assert result == points * 4

    below = NCLCScore(speaking=3, writing=3, listening=3, reading=3)
    assert (
        french_service.nclc_to_points(below, is_married=True, is_first_language=True)
        == 0
    )


def test_nclc_to_points_second_language_all_bands(french_service):
    """NCLC 5..10 -> SECOND_LANGUAGE table per skill; below 5 -> 0."""
    table = {5: 1, 6: 1, 7: 3, 8: 3, 9: 6, 10: 6}

    for nclc, points in table.items():
        scores = NCLCScore(speaking=nclc, writing=4, listening=4, reading=4)
        result = french_service.nclc_to_points(
            scores, is_married=False, is_first_language=False
        )
        assert result == points

    below = NCLCScore(speaking=4, writing=4, listening=4, reading=4)
    assert (
        french_service.nclc_to_points(below, is_married=False, is_first_language=False)
        == 0
    )


def test_nclc_to_points_second_language_capped_at_22(french_service):
    """Sum of all four second-language skills is capped at 22."""
    scores = NCLCScore(speaking=10, writing=10, listening=10, reading=10)
    result = french_service.nclc_to_points(
        scores, is_married=False, is_first_language=False
    )
    assert result == 22
