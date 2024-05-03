import pytest
from parallel_corpus.shared.ranges import edit_range


@pytest.mark.parametrize(
    "s0, s",
    [
        ("0123456789", "0189"),
        ("0123456789", "01"),
        ("0123456789", "89"),
        ("0123456789", ""),
        ("0123456789", "01xyz89"),
        ("0123456789", "01xyz"),
        ("0123456789", "xyz89"),
        ("0123456789", "xyz"),
        ("", "01"),
    ],
)
def test_edit_range(s0: str, s: str, snapshot):
    assert edit_range(s0, s) == snapshot
