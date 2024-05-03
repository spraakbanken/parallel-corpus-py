from typing import Callable, List, TypeVar

A = TypeVar("A")


def str_map(s: str, f: Callable[[str, int], A]) -> List[A]:
    return [f(s[i], i) for i in range(len(s))]
