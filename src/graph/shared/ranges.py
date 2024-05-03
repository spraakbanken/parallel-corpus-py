import itertools
from typing import TypedDict

import more_itertools

from graph.shared.diffs import token_diff
from graph.shared.functional import take_last_while

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
    print(f"ranges.edit_range; {s0=} {s=}")
    # const patches = token_diff(s0, s)
    patches = token_diff(s0, s)
    print(f"ranges.edit_range; {patches=}")

    # print(f"{patches=}")
    # const pre = R.takeWhile<[number, string]>(i => i[0] == 0, patches)
    pre = itertools.takewhile(lambda i: i[0] == 0, patches)
    # pre = []
    # pre, post = more_itertools.before_and_after(lambda i: i[0] == 0, patches)
    # post = itertools.dropwhile(lambda i: i[0] != 0, post)
    post = take_last_while(lambda i: i[0] == 0, patches)
    pre = list(pre)
    print(f"ranges.edit_range; {pre=}")
    post = list(post)
    print(f"ranges.edit_range; {post=}")
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
    from_ = len("".join((i[1] for i in pre)))
    # print(f"{from_=}")
    # const postlen = post.map(i => i[1]).join('').length
    postlen = len("".join((i[1] for i in post)))
    # print(f"{postlen=}")
    # print(f"{len(s0)=} {len(s)=}")
    # const to = s0.length - postlen
    to = len(s0) - postlen
    # print(f"{to=}")
    # const insert = s.slice(from, s.length - (s0.length - to))
    insert = s[from_ : (len(s) - (len(s0) - to))]
    # print(f"{insert=}")
    return {"from": from_, "to": to, "insert": insert}
