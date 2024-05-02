import copy
from typing import List, Tuple, TypeVar

A = TypeVar("A")


def splice(xs: List[A], start: int, count: int, *insert) -> Tuple[List[A], List[A]]:
    ys = copy.deepcopy(xs)
    zs = ys[start : (start + count)]
    ys[start : (start + count)] = insert
    return ys, zs
