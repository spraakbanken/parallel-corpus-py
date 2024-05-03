from graph import graph, rich_diff


def test_enrichen() -> None:
    g = graph.init("aporna bepa cepa depa", manual=True)

    gr = graph.rearrange(g, 1, 2, 0)
    assert graph.target_text(gr) == "bepa cepa aporna depa "

    gm = graph.modify(gr, 10, 10, "h")
    assert graph.target_text(gm) == "bepa cepa haporna depa "

    rd = rich_diff.enrichen(gm)

    expected_rd0 = {}

    assert rd[0] == expected_rd0
