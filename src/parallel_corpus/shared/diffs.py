import enum
from typing import Callable, Dict, Generic, List, Optional, Tuple, TypeVar, Union

import diff_match_patch as dmp_module
from typing_extensions import Self

from parallel_corpus.shared.str_map import str_map

dmp = dmp_module.diff_match_patch()

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class ChangeType(enum.IntEnum):
    DELETED = -1
    CONSTANT = 0
    INSERTED = 1


class Change(Generic[A, B]):
    def __init__(self, change: ChangeType, a: Optional[A] = None, b: Optional[B] = None):
        if change == ChangeType.DELETED and a is None:
            raise ValueError("`a` must be given for DELETED")
        if change == ChangeType.CONSTANT and (a is None or b is None):
            raise ValueError("both `a` and `b` must be given for CONSTANT")
        if change == ChangeType.INSERTED and b is None:
            raise ValueError("`b` must be given for INSERTED")
        self.change = change
        self.a = a
        self.b = b

    @classmethod
    def constant(cls, a: A, b: B) -> Self:
        return cls(ChangeType.CONSTANT, a=a, b=b)

    @classmethod
    def deleted(cls, a: A) -> Self:
        return cls(ChangeType.DELETED, a=a)

    @classmethod
    def inserted(cls, b: B) -> Self:
        return cls(ChangeType.INSERTED, b=b)

    def model_dump(self) -> Dict[str, Union[int, A, B]]:
        out: Dict[str, Union[int, A, B]] = {
            "change": int(self.change),
        }
        if self.a is not None:
            out["a"] = self.a
        if self.b is not None:
            out["b"] = self.b
        return out

    def __eq__(self, other) -> bool:
        if not isinstance(other, Change):
            return NotImplemented
        return self.change == other.change and self.a == other.a and self.b == other.b

    def __repr__(self) -> str:
        return f"Change(change={self.change!r},a={self.a!r},b={self.b!r})"

    def __str__(self) -> str:
        return f"Change(change={self.change},a={self.a},b={self.b})"


def char_stream():
    """Make a stream of all unicode characters

    We need this because the diff-match-patch library is hard-coded to work on characters.

    To make a polymorphic diff each unique element is assigned a unique character.
    We translate them back to the opaque type after diffing via the characters.
    This is used in `hdiff`.

    >>> chars = char_stream()
    >>> assert ord(next(chars)) == 0
    >>> assert ord(next(chars)) == 1
    >>> assert ord(next(chars)) == 2
    >>> assert ord(next(chars)) == 3

    """
    i = 0
    while True:
        yield chr(int(str(i), base=16))
        i += 1


def hdiff(  # noqa: C901
    xs: List[A],
    ys: List[B],
    a_cmp: Callable[[A], str] = str,
    b_cmp: Callable[[B], str] = str,
) -> List[Change[A, B]]:
    to: Dict[str, str] = {}
    a_from: Dict[str, List[A]] = {}
    b_from: Dict[str, List[B]] = {}
    chars = char_stream()

    def assign(c: C, c_cmp: Callable[[C], str], c_from: Dict[str, List[C]]) -> str:
        s = c_cmp(c)
        u = to.get(s)
        if u is None:
            u = next(chars)
            to[s] = u
        arr = c_from.get(u)
        if not arr:
            arr = []
            c_from[u] = arr
        arr.append(c)
        return u

    s1 = "".join((assign(a, a_cmp, a_from) for a in xs))
    s2 = "".join((assign(b, b_cmp, b_from) for b in ys))
    d = dmp.diff_main(s1, s2)

    def str_map_change(change: int) -> Callable[[str, int], Change]:
        def inner(c: str, _: int) -> Change:
            if change == 0:
                a = a_from.get(c, []).pop(0)
                b = b_from.get(c, []).pop(0)
                return Change.constant(a, b)
            if change == -1:
                a = a_from.get(c, []).pop(0)
                return Change.deleted(a)
            if change == 1:
                b = b_from.get(c, []).pop(0)
                return Change.inserted(b)
            raise RuntimeError("diff-match-patch change not in range [-1,1]")

        return inner

    def map_change(change: int, cs):
        return str_map(cs, str_map_change(change))

    out = []
    for changes in (map_change(change, cs) for change, cs in d):
        # print(f"{changes=}")
        out.extend(changes)
    return out


def token_diff(s1: str, s2: str) -> List[Tuple[int, str]]:
    d = dmp.diff_main(s1, s2)
    dmp.diff_cleanupSemantic(d)
    return d
