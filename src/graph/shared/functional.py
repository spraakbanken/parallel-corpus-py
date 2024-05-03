from typing import List


def take_last_while(predicate, xs: List) -> List:
    end = -1
    start = 0
    for i, e in enumerate(reversed(xs)):
        print(f"take_last_while; {i=}: {e=} {predicate(e)=} {start=} {end=}")
        if not predicate(e):
            break
        if predicate(e):
            start -= 1
        # if not predicate(e):
        #     if start is None:
        #         start = -(1) if i == 0 else -i
        #     if end is None:
        #         print(f"{i=}: {e=}")
        #         end = len(xs) - i
        #     break
        # return xs[start:]
    print(f"take_last_while;  {start=} {end=}")
    if start < 0:
        return xs[start:]
    return []
