import re
from typing import Iterable

DIGITS = re.compile(r"\d+")


def next_id(xs: Iterable[str]) -> int:
    """Calculate the next id to use from these identifiers

    next_id([]) // => 0
    next_id(['t1', 't2', 't3']) // => 4
    next_id(['u2v5k1', 'b3', 'a0']) // => 6
    next_id(['77j66']) // => 78

    """
    curr_max = -1
    for x in xs:
        for digit in DIGITS.finditer(x):
            curr_max = max(curr_max, int(digit[0]))
    # xs.forEach(x => (x.match(/\d+/g) || []).forEach(i => (max = Math.max(max, parseInt(i)))))
    return curr_max + 1
