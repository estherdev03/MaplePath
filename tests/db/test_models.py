"""Tests for db.models.NOC's plain-Python behavior (no DB required)."""

from db.models import NOC


def _noc(code, **kw):
    return NOC(noc_code=code, **kw)


def test_noc_equality_based_on_noc_code_only():
    """Two NOC instances with the same noc_code but different other fields
    are equal; used by noc.service.NOCService._rrf's set() dedup."""
    a = _noc("12345", title="A")
    b = _noc("12345", title="B")
    c = _noc("99999", title="A")
    assert a == b
    assert a != c


def test_noc_hash_based_on_noc_code_only():
    """Consistent with __eq__ so NOC can live in a set/dict key."""
    a = _noc("12345", title="A")
    b = _noc("12345", title="B")
    assert hash(a) == hash(b)
    assert {a, b} == {a}
