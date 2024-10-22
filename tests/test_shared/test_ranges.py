import string

import pytest

from parallel_corpus.shared.ranges import edit_range


@pytest.mark.parametrize(
    ("s0", "s"),
    [
        (string.digits, "0189"),
        (string.digits, "01"),
        (string.digits, "89"),
        (string.digits, ""),
        (string.digits, "01xyz89"),
        (string.digits, "01xyz"),
        (string.digits, "xyz89"),
        (string.digits, "xyz"),
        ("", "01"),
    ],
)
def test_edit_range(s0: str, s: str, snapshot) -> None:
    assert edit_range(s0, s) == snapshot
