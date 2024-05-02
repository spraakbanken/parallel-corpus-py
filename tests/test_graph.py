from typing import List

import pytest
from graph import graph, token


def test_graph_init() -> None:
    g = graph.init("w1 w2")
    source = [token.Token(text="w1 ", id="s0"), token.Token(text="w2 ", id="s1")]
    target = [token.Token(text="w1 ", id="t0"), token.Token(text="w2 ", id="t1")]
    edges = graph.edge_record([graph.edge(["s0", "t0"], []), graph.edge(["s1", "t1"], [])])

    assert g.source == source
    assert g.target == target
    assert g.edges == edges


def test_graph_align() -> None:
    g0 = graph.init("a bc d")
    g = graph.unaligned_set_side(g0, "target", "ab c d")

    assert len(graph.align(g).edges) == 2


def show(g: graph.Graph) -> List[str]:
    return [t.text for t in g.target]


def show_source(g: graph.Graph) -> List[str]:
    return [s.text for s in g.source]


def ids(g: graph.Graph) -> str:
    return " ".join((t.id for t in g.target))


def ids_source(g: graph.Graph) -> str:
    return " ".join((s.id for s in g.source))


@pytest.mark.parametrize(
    "i0, i1, word",
    [
        (0, 0, "new"),
        (0, 1, "new"),
        (0, 5, "new "),
        (0, 5, "new"),
        (5, 5, " "),
        (5, 6, " "),
        (0, 15, "_"),
        (0, 16, "_"),
        (0, 17, "_"),
        (16, 16, " !"),
    ],
)
def test_unaligned_modify(i0: int, i1: int, word: str, snapshot):
    g = graph.init("test graph hello")
    assert g is not None
    assert show(graph.unaligned_modify(g, i0, i1, word)) == snapshot


def test_edge_map() -> None:
    g = graph.init("w")
    e = graph.edge(["s0", "t0"], [])
    print(f"{graph.edge_map(g)=}")
    lhs = list(graph.edge_map(g).items())
    rhs = [("s0", e), ("t0", e)]
    assert lhs == rhs


def test_unaligned_modify_tokens() -> None:
    g = graph.init("test graph hello")
    assert show(g) == ["test ", "graph ", "hello "]
    assert ids(g) == "t0 t1 t2"


@pytest.mark.parametrize("text, expected", [("this", True), ("this ", False)])
def test_no_whitespace_at_end(text: str, *, expected: bool) -> None:
    assert (graph.NO_WHITESPACE_AT_END.match(text[-1:]) is not None) is expected


@pytest.mark.parametrize(
    "from_, to, text",
    [
        (0, 0, "this "),
        (0, 1, "this "),
        (0, 1, "  white "),
        (0, 1, "this"),
        (1, 2, "graph"),
        (1, 2, " graph "),
        (0, 1, "for this "),
        (0, 2, ""),
        (0, 2, "  "),
        (1, 3, "  "),
        (3, 3, " !"),
    ],
)
def test_unaligned_modify_tokens_show(from_: int, to: int, text: str, snapshot) -> None:
    g = graph.init("test graph hello")
    assert show(graph.unaligned_modify_tokens(g, from_, to, text)) == snapshot


@pytest.mark.parametrize(
    "from_, to, text",
    [
        (0, 0, "this "),
        (0, 1, "this "),
        (0, 1, "this"),
    ],
)
def test_unaligned_modify_tokens_ids(from_: int, to: int, text: str, snapshot) -> None:
    g = graph.init("test graph hello")
    assert ids(graph.unaligned_modify_tokens(g, from_, to, text)) == snapshot


@pytest.mark.parametrize(
    "from_, to, text",
    [
        (0, 0, "this "),
    ],
)
def test_unaligned_modify_tokens_show_source(from_: int, to: int, text: str, snapshot) -> None:
    g = graph.init("test graph hello")
    assert show_source(graph.unaligned_modify_tokens(g, from_, to, text, "source")) == snapshot


@pytest.mark.parametrize(
    "from_, to, text",
    [
        (0, 0, "this "),
    ],
)
def test_unaligned_modify_tokens_ids_source(from_: int, to: int, text: str, snapshot) -> None:
    g = graph.init("test graph hello")
    assert ids_source(graph.unaligned_modify_tokens(g, from_, to, text, "source")) == snapshot


#   show(unaligned_modify_tokens(init('a '), 0, 1, ' ')) // => [' ']
#   ids(g) // => 't0 t1 t2'
#   ids(unaligned_modify_tokens(g, 0, 0, 'this '))     // => 't3 t0 t1 t2'
#   ids(unaligned_modify_tokens(g, 0, 1, 'this '))     // => 't3 t1 t2'
#   ids(unaligned_modify_tokens(g, 0, 1, 'this'))      // => 't3 t2'
#   const showS = (g: Graph) => g.source.map(t => t.text)
#   const idsS = (g: Graph) => g.source.map(t => t.id).join(' ')
#   showS(unaligned_modify_tokens(g, 0, 0, 'this ', 'source')) // => ['this ', 'test ', 'graph ', 'hello ']
#   idsS(unaligned_modify_tokens(g, 0, 0, 'this ', 'source'))  // => 's3 s0 s1 s2'
