from typing import List

import pytest
from parallel_corpus.token import Token, identify, tokenize


def test_can_create_token() -> None:
    token = Token(text="a text", id="s0")

    assert token.id == "s0"
    assert token.text == "a text"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", []),
        (" ", [" "]),
        ("    ", ["    "]),
        ("apa bepa cepa", ["apa ", "bepa ", "cepa "]),
        ("  apa bepa cepa", ["  apa ", "bepa ", "cepa "]),
        ("  apa bepa cepa  ", ["  apa ", "bepa ", "cepa  "]),
    ],
)
def test_tokenize(text: str, expected: List[str], snapshot) -> None:
    actual = tokenize(text)

    assert actual == expected
    assert actual == snapshot


def test_identify() -> None:
    assert identify(["apa", "bepa"], "#") == [
        Token(text="apa", id="#0"),
        Token(text="bepa", id="#1"),
    ]
