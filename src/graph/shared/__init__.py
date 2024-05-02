import itertools
import re
from typing import List, Optional, Tuple, TypeVar, TypedDict
from typing_extensions import Self

import ramda
import more_itertools
import diff_match_patch as dmp_module


from . import diffs

__all__ = ["diffs"]

dmp = dmp_module.diff_match_patch()

ENDING_WHITESPACE = re.compile(r"\s$")


def end_with_space(s: str) -> str:
    if not s:
        return s
    # print(f"{s[-1]=}")
    # print(f"{ENDING_WHITESPACE.fullmatch(s[-1])=}")
    return f"{s} " if (ENDING_WHITESPACE.fullmatch(s[-1]) is None) else s


def token_diff(s1: str, s2: str) -> List[Tuple[int, str]]:
    d = dmp.diff_main(s1, s2)
    dmp.diff_cleanupSemantic(d)
    return d


EditRange = TypedDict("EditRange", {"from": int, "to": int, "insert": str})


def edit_range(s0: str, s: str) -> EditRange:
    """
    >>> edit_range('0123456789', '0189')
    {'from': 2, 'to': 8, 'insert': ''}

    >>> edit_range('0123456789', '01')
    {'from': 2, 'to': 10, 'insert': ''}

    >>> edit_range('0123456789', '89')
    {'from': 0, 'to': 8, 'insert': ''}

    >>> edit_range('0123456789', '')
    {'from': 0, 'to': 10, 'insert': ''}

    >>> edit_range('0123456789', '01xyz89')
    {'from': 2, 'to': 8, 'insert': 'xyz'}

    >>> edit_range('0123456789', '01xyz')
    {'from': 2, 'to': 10, 'insert': 'xyz'}

    >>> edit_range('0123456789', 'xyz89')
    {'from': 0, 'to': 8, 'insert': 'xyz'}

    >>> edit_range('0123456789', 'xyz')
    {'from': 0, 'to': 10, 'insert': 'xyz'}

    >>> edit_range('', '01')
    {'from': 0, 'to': 0, 'insert': '01'}
    """
    # const patches = token_diff(s0, s)
    patches = token_diff(s0, s)
    # print(f"{patches=}")
    # const pre = R.takeWhile<[number, string]>(i => i[0] == 0, patches)
    pre, post = more_itertools.before_and_after(lambda i: i[0] == 0, patches)
    post = itertools.dropwhile(lambda i: i[0] != 0, post)
    pre = list(pre)
    post = list(post)
    # print(f"{list(pre)=}")
    # print(f"{list(post)=}")

    # pre = ramda.take_while(lambda i: i[0] == 0, patches)
    # print(f"{pre=}")
    # const post = R.takeLastWhile<[number, string]>(i => i[0] == 0, R.drop(pre.length, patches))
    # post = take_last_while(lambda i: i[0] == 0, ramda.drop(len(pre), patches))
    # print(f"{post=}")
    # post = ramda.take_while(lambda i: i[0] == 0, ramda.drop(len(pre), patches))
    # print(f"{post=}")
    # const from = pre.map(i => i[1]).join('').length
    from_ = len("".join(map(lambda i: i[1], pre)))
    # print(f"{from_=}")
    # const postlen = post.map(i => i[1]).join('').length
    postlen = len("".join(map(lambda i: i[1], post)))
    # print(f"{postlen=}")
    # print(f"{len(s0)=} {len(s)=}")
    # const to = s0.length - postlen
    to = len(s0) - postlen
    # print(f"{to=}")
    # const insert = s.slice(from, s.length - (s0.length - to))
    insert = s[from_ : (len(s) - (len(s0) - to))]
    # print(f"{insert=}")
    return {"from": from_, "to": to, "insert": insert}


def take_last_while(predicate, xs: List) -> List:
    end = None
    start = None
    for i, e in enumerate(reversed(xs)):
        if not predicate(e) and start is None:
            start = -(i - 1) if i == 0 else -i
        elif not predicate(e) and end is None:
            print(f"{i=}: {e=}")
            end = len(xs) - i
            # return xs[start:]
    if start is not None:
        if end is not None:
            return xs[end:start]
        else:
            return xs[start:]
    return xs

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
