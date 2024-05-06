from typing import Callable, Sequence, TypeVar

A = TypeVar("A")


def take_last_while(predicate: Callable[[A], bool], xs: Sequence[A]) -> Sequence[A]:
    start = 0
    for e in reversed(xs):
        if not predicate(e):
            break
        start -= 1
    return xs[start:] if start < 0 else xs[:0]
