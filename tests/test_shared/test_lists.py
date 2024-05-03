from parallel_corpus.shared import lists


def test_splice_1():
    (*s_chars,) = "abcdef"
    ex, rm = lists.splice(s_chars, 3, 1, " ", "_")
    assert "".join(ex) == "abc _ef"
    assert "".join(rm) == "d"


def test_splice_2():
    (*s_chars,) = "abcdef"
    (ex, rm) = lists.splice(s_chars, 3, 2, " ", "_")
    assert "".join(ex) == "abc _f"
    assert "".join(rm) == "de"
