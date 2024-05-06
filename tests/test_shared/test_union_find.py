from parallel_corpus.shared.union_find import UnionFind, poly_union_find, renumber


def test_union_find() -> None:
    uf = UnionFind()
    assert uf.find(10) != uf.find(20)
    uf.union(10, 20)
    assert uf.find(10) == uf.find(20)
    uf.union(20, 30)
    assert uf.find(10) == uf.find(30)
    uf.unions([10, 40, 50])
    assert uf.find(20) == uf.find(40)
    assert uf.find(20) == uf.find(50)


def test_renumber_default() -> None:
    un, num = renumber()  # type: ignore [var-annotated]
    assert num("foo") == 0
    assert num("bar") == 1
    assert num("foo") == 0
    assert un(0) == "foo"
    assert un(1) == "bar"
    assert un(2) is None


def test_renumber_lowercase() -> None:
    un, num = renumber(str.lower)  # type: ignore [var-annotated]

    assert num("foo") == 0
    assert num("FOO") == 0
    assert un(0) == "foo"


def test_poly_union_find() -> None:
    uf = poly_union_find(str.lower)
    assert uf.repr("a") == 0
    assert uf.repr("A") == 0
    assert uf.find("a") == "a"
    assert uf.find("A") == "a"
    assert uf.find("a") != uf.find("b")
    assert uf.union("A", "B")
    assert uf.find("a") == uf.find("b")
