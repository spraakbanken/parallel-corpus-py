import re
from dataclasses import dataclass
from typing import List, Sequence, TypedDict

from parallel_corpus import shared


@dataclass
class Text:
    text: str


@dataclass
class Token(Text):
    id: str


@dataclass
class Span:
    begin: int
    end: int


def text(ts: Sequence[Text]) -> str:
    """The text in some tokens

    >>> text(identify(tokenize('apa bepa cepa '), '#'))
    'apa bepa cepa '

    """
    return "".join(texts(ts))


def texts(ts: Sequence[Text]) -> List[str]:
    """The texts in some tokens

    >>> texts(identify(tokenize('apa bepa cepa '), '#'))
    ['apa ', 'bepa ', 'cepa ']
    """
    return [t.text for t in ts]


def tokenize(s: str) -> List[str]:
    """Tokenizes text on whitespace, prefers to have trailing whitespace."""
    return list(
        map(
            shared.end_with_space,
            re.findall(r"\s*\S+\s*", s) or re.findall(r"^\s+$", s) or [],
        )
    )


def identify(toks: List[str], prefix: str) -> List[Token]:
    return [Token(text=text, id=f"{prefix}{i}") for i, text in enumerate(toks)]


class TokenAt(TypedDict):
    token: int
    offset: int


def token_at(tokens: List[str], character_offset: int) -> TokenAt:
    """
    >>> abc = ['012', '3456', '789']
    >>> token_at(abc, 0)
    {'token': 0, 'offset': 0}

    >>> token_at(abc, 2)
    {'token': 0, 'offset': 2}

    token_at(abc, 3) // => {token: 1, offset: 0}
    token_at(abc, 6) // => {token: 1, offset: 3}
    token_at(abc, 7) // => {token: 2, offset: 0}
    token_at(abc, 9) // => {token: 2, offset: 2}
    token_at(abc, 10) // => {token: 3, offset: 0}
    Utils.throws(() => token_at(abc, 11)) // => true
    """
    passed = 0
    for i in range(len(tokens)):
        w = len(tokens[i])
        passed += w
        if passed > character_offset:
            return {"token": i, "offset": character_offset - passed + w}
    if character_offset == len("".join(tokens)):
        return {"token": len(tokens), "offset": 0}
    raise IndexError(f"Out of bounds: tokens={tokens}, character_offset={character_offset}")
