from parallel_corpus.shared.ids import next_id


def test_next_id():
    assert next_id([]) == 0
    assert next_id(["t1", "t2", "t3"]) == 4
    assert next_id(["u2v5k1", "b3", "a0"]) == 6
    assert next_id(["77j66"]) == 78
