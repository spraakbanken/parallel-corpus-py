from typing import List


def take_last_while(predicate, xs: List) -> List:
    start = 0
    for e in reversed(xs):
        if not predicate(e):
            break
        start -= 1
    return xs[start:] if start < 0 else []
