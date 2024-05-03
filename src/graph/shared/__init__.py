import re
from typing import List, TypeVar

from typing_extensions import Self

from . import diffs

__all__ = ["diffs"]


ENDING_WHITESPACE = re.compile(r"\s$")


def end_with_space(s: str) -> str:
    if not s:
        return s
    # print(f"{s[-1]=}")
    # print(f"{ENDING_WHITESPACE.fullmatch(s[-1])=}")
    return f"{s} " if (ENDING_WHITESPACE.fullmatch(s[-1]) is None) else s

    # return next(
    #     (
    #         xs[-(i - 1) :] if i == 0 else xs[-i:]
    #         for i, e in enumerate(reversed(xs))
    #         if not predicate(e)
    #     ),
    #     xs,
    # )


def uniq(xs: List[str]) -> List[str]:
    used = set()
    return [x for x in xs if x not in used and (used.add(x) or True)]


A = TypeVar("A")
B = TypeVar("B")
