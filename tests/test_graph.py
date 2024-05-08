from typing import List

import pytest
from parallel_corpus import graph, token
from parallel_corpus.source_target import Side, SourceTarget


def test_graph_init() -> None:
    g = graph.init("w1 w2")
    source = [token.Token(text="w1 ", id="s0"), token.Token(text="w2 ", id="s1")]
    target = [token.Token(text="w1 ", id="t0"), token.Token(text="w2 ", id="t1")]
    edges = graph.edge_record([graph.edge(["s0", "t0"], []), graph.edge(["s1", "t1"], [])])

    assert g.source == source
    assert g.target == target
    assert g.edges == edges


def test_init_from_source_and_target_1() -> None:
    g = graph.init_with_source_and_target(source="apa", target="apa")
    assert g == graph.init("apa")


def test_init_from_source_and_target_2() -> None:
    g = graph.init_with_source_and_target(source="apa bepa", target="apa")
    expected_source = token.identify(token.tokenize("apa bepa"), "s")
    expected_target = token.identify(token.tokenize("apa"), "t")
    g_expected = graph.Graph(
        source=expected_source,
        target=expected_target,
        edges=graph.edge_record([graph.edge(["s0", "t0"], []), graph.edge(["s1"], [])]),
    )
    assert g == g_expected


def test_init_from_source_and_target_3() -> None:
    g = graph.init_with_source_and_target(source="apa", target="bepa apa")
    expected_source = token.identify(token.tokenize("apa"), "s")
    expected_target = token.identify(token.tokenize("bepa apa"), "t")
    g_expected = graph.Graph(
        source=expected_source,
        target=expected_target,
        edges=graph.edge_record([graph.edge(["s0", "t1"], []), graph.edge(["t0"], [])]),
    )
    assert g == g_expected


def test_from_unaligned() -> None:
    g = graph.from_unaligned(
        SourceTarget(
            source=[{"text": "apa ", "labels": []}], target=[{"text": "apa ", "labels": []}]
        )
    )
    assert g == graph.init("apa")


def test_graph_case1() -> None:
    first = "Jonathan saknades , emedan han , med sin vapendragare , redan på annat håll sökt och anträffat fienden ."  # noqa: E501
    second = "Jonat han saknades , emedan han , med sin vapendragare , redan på annat håll sökt och anträffat fienden ."  # noqa: E501

    g = graph.init(first)

    gm = graph.set_target(g, second)
    print(f"{gm=}")
    assert "e-s0-t19-t20" in gm.edges


def test_graph_case2() -> None:
    first = "Jonat han saknades , emedan han , med sin vapendragare , redan på annat håll sökt och anträffat fienden ."  # noqa: E501
    second = "Jonathan saknaes , emedan han , med sin vapendragare , redan på annat håll sökt och anträffat fienden ."  # noqa: E501

    g = graph.init(first)

    gm = graph.set_target(g, second)
    print(f"{gm=}")
    assert "e-s0-s1-t20" in gm.edges


def test_set_source() -> None:
    source = "Jonat han saknades"
    target = "Jonathan saknaes"

    g = graph.init(target)

    gm = graph.set_source(g, source)
    print(f"{gm=}")
    assert "e-s2-s3-t0" in gm.edges


def test_unaligned_set_side() -> None:
    g0 = graph.init("a bc d")
    print(">>> test_unaligned_set_side")
    g = graph.unaligned_set_side(g0, Side.target, "ab c d")
    print("<<< test_unaligned_set_side")

    expected_source = [
        token.Token(id="s0", text="a "),
        token.Token(id="s1", text="bc "),
        token.Token(id="s2", text="d "),
    ]
    expected_g0_target = [
        token.Token(id="t0", text="a "),
        token.Token(id="t1", text="bc "),
        token.Token(id="t2", text="d "),
    ]
    expected_g_target = [
        token.Token(id="t3", text="ab "),
        token.Token(id="t4", text="c "),
        token.Token(id="t5", text="d "),
    ]
    expected_g_edges = {
        "e-s0-s1-s2-t3-t4-t5": graph.Edge(
            id="e-s0-s1-s2-t3-t4-t5",
            ids=["s0", "s1", "s2", "t3", "t4", "t5"],
            labels=[],
            manual=False,
        ),
    }

    assert g0.source == expected_source
    assert g0.target == expected_g0_target
    assert g.source == expected_source
    assert g.target == expected_g_target
    assert g.edges == expected_g_edges


def test_graph_align() -> None:
    g0 = graph.init("a bc d")

    g = graph.unaligned_set_side(g0, Side.target, "ab c d")

    expected_source = [
        token.Token(id="s0", text="a "),
        token.Token(id="s1", text="bc "),
        token.Token(id="s2", text="d "),
    ]
    expected_g0_target = [
        token.Token(id="t0", text="a "),
        token.Token(id="t1", text="bc "),
        token.Token(id="t2", text="d "),
    ]
    expected_g_target = [
        token.Token(id="t3", text="ab "),
        token.Token(id="t4", text="c "),
        token.Token(id="t5", text="d "),
    ]
    expected_g_edges = {
        "e-s0-s1-s2-t3-t4-t5": graph.Edge(
            id="e-s0-s1-s2-t3-t4-t5",
            ids=["s0", "s1", "s2", "t3", "t4", "t5"],
            labels=[],
            manual=False,
        ),
    }
    expected_g_aligned_edges = {
        "e-s0-s1-t3-t4": graph.Edge(
            id="e-s0-s1-t3-t4", ids=["s0", "s1", "t3", "t4"], labels=[], manual=False
        ),
        "e-s2-t5": graph.Edge(id="e-s2-t5", ids=["s2", "t5"], labels=[], manual=False),
    }

    assert g0.source == expected_source
    assert g0.target == expected_g0_target
    assert g.source == expected_source
    assert g.target == expected_g_target
    assert g.edges == expected_g_edges
    g_aligned = graph.align(g)
    assert g_aligned.source == expected_source
    assert g_aligned.target == expected_g_target
    assert g_aligned.edges == expected_g_aligned_edges
    assert len(g_aligned.edges) == 2


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
    assert (
        show_source(graph.unaligned_modify_tokens(g, from_, to, text, Side.source)) == snapshot
    )


@pytest.mark.parametrize(
    "from_, to, text",
    [
        (0, 0, "this "),
    ],
)
def test_unaligned_modify_tokens_ids_source(from_: int, to: int, text: str, snapshot) -> None:
    g = graph.init("test graph hello")
    assert ids_source(graph.unaligned_modify_tokens(g, from_, to, text, Side.source)) == snapshot


#   show(unaligned_modify_tokens(init('a '), 0, 1, ' ')) // => [' ']
#   ids(g) // => 't0 t1 t2'
#   ids(unaligned_modify_tokens(g, 0, 0, 'this '))     // => 't3 t0 t1 t2'
#   ids(unaligned_modify_tokens(g, 0, 1, 'this '))     // => 't3 t1 t2'
#   ids(unaligned_modify_tokens(g, 0, 1, 'this'))      // => 't3 t2'
#   const showS = (g: Graph) => g.source.map(t => t.text)
#   const idsS = (g: Graph) => g.source.map(t => t.id).join(' ')
#   showS(unaligned_modify_tokens(g, 0, 0, 'this ', 'source')) // => ['this ', 'test ', 'graph ', 'hello ']  # noqa: E501
#   idsS(unaligned_modify_tokens(g, 0, 0, 'this ', 'source'))  // => 's3 s0 s1 s2'


def test_unaligned_rearrange() -> None:
    g = graph.init("apa bepa cepa depa")
    gr = graph.unaligned_rearrange(g, 1, 2, 0)
    assert graph.target_text(gr) == "bepa cepa apa depa "  # type: ignore [arg-type]


# target_text(unaligned_rearrange(init(), 1, 2, 0)) // =>
