from parallel_corpus.shared import functional


def test_take_last_while_list() -> None:
    source = [1, 2, 3, 4]
    assert functional.take_last_while(is_not_none, source) == [2, 3, 4]
    assert source == [1, 2, 3, 4]


def test_take_last_while_str() -> None:
    assert functional.take_last_while(lambda x: x != "R", "Ramda") == "amda"


def is_not_none(x: int) -> bool:
    return x != 1
