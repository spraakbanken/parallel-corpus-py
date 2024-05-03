import re
from typing import List, TypeVar

from typing_extensions import Self

from . import diffs

__all__ = ["diffs"]


ENDING_WHITESPACE = re.compile(r"\s$")


def end_with_space(s: str) -> str:
    if not s:
        return s
    return f"{s} " if (ENDING_WHITESPACE.fullmatch(s[-1]) is None) else s


def uniq(xs: List[str]) -> List[str]:
    used = set()
    return [x for x in xs if x not in used and (used.add(x) or True)]


A = TypeVar("A")
B = TypeVar("B")
