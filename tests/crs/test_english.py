"""Tests for crs.english.EnglishService."""

import pytest
from graph.state.profile import CLBScore, EnglishTest, LanguageScore


# ---- IELTS ----
def test_ielts_speaking_to_clb_boundaries(english_service):
    """Each band boundary (7.5/7.0/6.5/6.0/5.5/5.0/4.0) and below-4.0 -> 0."""
    assert english_service._ielts_speaking_to_clb(7.5) == 10
    assert english_service._ielts_speaking_to_clb(7) == 9
    assert english_service._ielts_speaking_to_clb(6.5) == 8
    assert english_service._ielts_speaking_to_clb(6) == 7
    assert english_service._ielts_speaking_to_clb(5.5) == 6
    assert english_service._ielts_speaking_to_clb(5.0) == 5
    assert english_service._ielts_speaking_to_clb(4.0) == 4
    assert english_service._ielts_speaking_to_clb(3) == 0


def test_ielts_writing_to_clb_boundaries(english_service):
    """Each band boundary (7.5/7.0/6.5/6.0/5.5/5.0/4.0) and below-4.0 -> 0."""
    assert english_service._ielts_writing_to_clb(7.5) == 10
    assert english_service._ielts_writing_to_clb(7) == 9
    assert english_service._ielts_writing_to_clb(6.5) == 8
    assert english_service._ielts_writing_to_clb(6) == 7
    assert english_service._ielts_writing_to_clb(5.5) == 6
    assert english_service._ielts_writing_to_clb(5.0) == 5
    assert english_service._ielts_writing_to_clb(4.0) == 4
    assert english_service._ielts_writing_to_clb(3) == 0


def test_ielts_listening_to_clb_boundaries(english_service):
    """Each band boundary (8.5/8.0/7.5/6.0/5.5/5.0/4.5) and below-4.5 -> 0."""
    assert english_service._ielts_listening_to_clb(8.5) == 10
    assert english_service._ielts_listening_to_clb(8.0) == 9
    assert english_service._ielts_listening_to_clb(7.5) == 8
    assert english_service._ielts_listening_to_clb(6.0) == 7
    assert english_service._ielts_listening_to_clb(5.5) == 6
    assert english_service._ielts_listening_to_clb(5.0) == 5
    assert english_service._ielts_listening_to_clb(4.5) == 4
    assert english_service._ielts_listening_to_clb(4.0) == 0


def test_ielts_reading_to_clb_boundaries(english_service):
    """Each band boundary (8.0/7.0/6.5/6.0/5.0/4.0/3.5) and below-3.5 -> 0."""
    assert english_service._ielts_reading_to_clb(8.0) == 10
    assert english_service._ielts_reading_to_clb(7.0) == 9
    assert english_service._ielts_reading_to_clb(6.5) == 8
    assert english_service._ielts_reading_to_clb(6.0) == 7
    assert english_service._ielts_reading_to_clb(5.0) == 6
    assert english_service._ielts_reading_to_clb(4.0) == 5
    assert english_service._ielts_reading_to_clb(3.5) == 4
    assert english_service._ielts_reading_to_clb(3.0) == 0


def test_ielts_to_clb_none_score_returns_zero(english_service):
    """None for any skill -> 0 for that skill (all four helpers)."""
    assert english_service._ielts_speaking_to_clb(None) == 0
    assert english_service._ielts_reading_to_clb(None) == 0
    assert english_service._ielts_listening_to_clb(None) == 0
    assert english_service._ielts_writing_to_clb(None) == 0


def test_ielts_to_clb_combines_all_four_skills(english_service):
    """ielts_to_clb() builds a CLBScore from all four per-skill helpers."""
    score = LanguageScore(speaking=7.5, writing=6.0, listening=8.5, reading=3.5)
    result = english_service.ielts_to_clb(score)
    assert result == CLBScore(speaking=10, writing=7, listening=10, reading=4)


# ---- CELPIP ----
def test_celpip_score_to_clb_boundaries(english_service):
    """Score 10..4 map 1:1 to CLB 10..4; below 4 -> 0; int() truncation."""
    assert english_service._celpip_score_to_clb(10) == 10
    assert english_service._celpip_score_to_clb(9) == 9
    assert english_service._celpip_score_to_clb(8) == 8
    assert english_service._celpip_score_to_clb(7) == 7
    assert english_service._celpip_score_to_clb(6) == 6
    assert english_service._celpip_score_to_clb(5) == 5
    assert english_service._celpip_score_to_clb(4) == 4
    assert english_service._celpip_score_to_clb(3) == 0
    # int() truncates toward zero rather than rounding, so 7.9 stays CLB 7.
    assert english_service._celpip_score_to_clb(7.9) == 7


def test_celpip_to_clb_none_score_returns_zero(english_service):
    result = english_service.celpip_to_clb(LanguageScore())
    assert result == CLBScore(speaking=0, writing=0, listening=0, reading=0)


# ---- PTE ----
def test_pte_speaking_to_clb_boundaries(english_service):
    assert english_service._pte_speaking_to_clb(89) == 10
    assert english_service._pte_speaking_to_clb(84) == 9
    assert english_service._pte_speaking_to_clb(76) == 8
    assert english_service._pte_speaking_to_clb(68) == 7
    assert english_service._pte_speaking_to_clb(59) == 6
    assert english_service._pte_speaking_to_clb(51) == 5
    assert english_service._pte_speaking_to_clb(42) == 4
    assert english_service._pte_speaking_to_clb(41) == 0


def test_pte_writing_to_clb_boundaries(english_service):
    assert english_service._pte_writing_to_clb(90) == 10
    assert english_service._pte_writing_to_clb(88) == 9
    assert english_service._pte_writing_to_clb(79) == 8
    assert english_service._pte_writing_to_clb(69) == 7
    assert english_service._pte_writing_to_clb(60) == 6
    assert english_service._pte_writing_to_clb(51) == 5
    assert english_service._pte_writing_to_clb(41) == 4
    assert english_service._pte_writing_to_clb(40) == 0


def test_pte_listening_to_clb_boundaries(english_service):
    assert english_service._pte_listening_to_clb(89) == 10
    assert english_service._pte_listening_to_clb(82) == 9
    assert english_service._pte_listening_to_clb(71) == 8
    assert english_service._pte_listening_to_clb(60) == 7
    assert english_service._pte_listening_to_clb(50) == 6
    assert english_service._pte_listening_to_clb(39) == 5
    assert english_service._pte_listening_to_clb(28) == 4
    assert english_service._pte_listening_to_clb(27) == 0


def test_pte_reading_to_clb_boundaries(english_service):
    assert english_service._pte_reading_to_clb(88) == 10
    assert english_service._pte_reading_to_clb(78) == 9
    assert english_service._pte_reading_to_clb(69) == 8
    assert english_service._pte_reading_to_clb(60) == 7
    assert english_service._pte_reading_to_clb(51) == 6
    assert english_service._pte_reading_to_clb(42) == 5
    assert english_service._pte_reading_to_clb(33) == 4
    assert english_service._pte_reading_to_clb(32) == 0


def test_pte_to_clb_none_score_returns_zero(english_service):
    result = english_service.pte_to_clb(LanguageScore())
    assert result == CLBScore(speaking=0, writing=0, listening=0, reading=0)


# ---- dispatch ----
def test_english_to_clb_dispatches_ielts_celpip_pte(english_service):
    """english_to_clb() routes to the right *_to_clb() by EnglishTest enum."""
    score = LanguageScore(speaking=7.5, writing=7.5, listening=8.5, reading=8.0)

    assert english_service.english_to_clb(EnglishTest.IELTS, score) == (
        english_service.ielts_to_clb(score)
    )
    assert english_service.english_to_clb(EnglishTest.CELPIP, score) == (
        english_service.celpip_to_clb(score)
    )
    assert english_service.english_to_clb(EnglishTest.PTE, score) == (
        english_service.pte_to_clb(score)
    )


def test_english_to_clb_unsupported_test_raises_value_error(english_service):
    """Unknown EnglishTest -> ValueError"""
    with pytest.raises(ValueError, match="toeic test score is not accepted."):
        english_service.english_to_clb(test="toeic", scores=LanguageScore())


# ---- clb_to_points ----
def test_clb_to_points_first_language_single_all_bands(english_service):
    """CLB 4..10 -> FIRST_LANGUAGE_SINGLE table per skill; below 4 -> 0."""
    table = {4: 6, 5: 6, 6: 9, 7: 17, 8: 23, 9: 31, 10: 34}

    for clb, points in table.items():
        scores = CLBScore(speaking=clb, writing=clb, listening=clb, reading=clb)
        result = english_service.clb_to_points(
            scores, is_married=False, is_first_language=True
        )
        assert result == points * 4

    below = CLBScore(speaking=3, writing=3, listening=3, reading=3)
    assert (
        english_service.clb_to_points(below, is_married=False, is_first_language=True)
        == 0
    )


def test_clb_to_points_first_language_married_all_bands(english_service):
    """CLB 4..10 -> FIRST_LANGUAGE_MARRIED table per skill; below 4 -> 0."""
    table = {4: 6, 5: 6, 6: 8, 7: 16, 8: 22, 9: 29, 10: 32}

    for clb, points in table.items():
        scores = CLBScore(speaking=clb, writing=clb, listening=clb, reading=clb)
        result = english_service.clb_to_points(
            scores, is_married=True, is_first_language=True
        )
        assert result == points * 4

    below = CLBScore(speaking=3, writing=3, listening=3, reading=3)
    assert (
        english_service.clb_to_points(below, is_married=True, is_first_language=True)
        == 0
    )


def test_clb_to_points_second_language_all_bands(english_service):
    """CLB 5..10 -> SECOND_LANGUAGE table per skill; below 5 -> 0."""
    table = {5: 1, 6: 1, 7: 3, 8: 3, 9: 6, 10: 6}

    for clb, points in table.items():
        scores = CLBScore(speaking=clb, writing=4, listening=4, reading=4)
        result = english_service.clb_to_points(
            scores, is_married=False, is_first_language=False
        )
        assert result == points

    below = CLBScore(speaking=4, writing=4, listening=4, reading=4)
    assert (
        english_service.clb_to_points(below, is_married=False, is_first_language=False)
        == 0
    )


def test_clb_to_points_second_language_capped_at_22(english_service):
    """Sum of all four second-language skills is capped at 22."""
    scores = CLBScore(speaking=10, writing=10, listening=10, reading=10)
    result = english_service.clb_to_points(
        scores, is_married=False, is_first_language=False
    )
    assert result == 22
