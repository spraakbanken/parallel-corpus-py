import itertools
from typing import TypedDict

from parallel_corpus.shared.diffs import token_diff
from parallel_corpus.shared.functional import take_last_while

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
    patches = token_diff(s0, s)
    pre = list(itertools.takewhile(lambda i: i[0] == 0, patches))
    post = take_last_while(lambda i: i[0] == 0, patches)
    from_ = len("".join((i[1] for i in pre)))
    postlen = len("".join((i[1] for i in post)))
    to = len(s0) - postlen
    insert = s[from_ : (len(s) - (len(s0) - to))]
    return {"from": from_, "to": to, "insert": insert}
