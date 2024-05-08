"""Parallel corpus as a graph."""

import itertools
import logging
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, TypedDict, TypeVar

import parallel_corpus.shared.ranges
import parallel_corpus.shared.str_map
import parallel_corpus.shared.union_find
from parallel_corpus import shared, token
from parallel_corpus.shared import dicts, diffs, ids, lists
from parallel_corpus.shared.unique_check import UniqueCheck
from parallel_corpus.source_target import Side, SourceTarget, map_sides
from parallel_corpus.token import Token

A = TypeVar("A")
B = TypeVar("B")


ALL_WHITESPACE = re.compile(r"^\s+$")
NO_WHITESPACE_AT_END = re.compile(r"\S$")

logger = logging.getLogger(__name__)


@dataclass
class Edge:
    # a copy of the identifier used in the edges object of the graph
    id: str
    # these are ids to source and target tokens
    ids: List[str]
    # labels on this edge
    labels: List[str]
    # is this manually or automatically aligned
    manual: bool
    comment: Optional[str] = None


Edges = Dict[str, Edge]


@dataclass
class Graph(SourceTarget[List[Token]]):
    edges: Edges
    comment: Optional[str] = None

    def copy_with_updated_side_and_edges(
        self, side: Side, new_tokens: List[Token], edges: Edges
    ) -> "Graph":
        source = self.source if side == Side.target else new_tokens
        target = new_tokens if side == Side.target else self.target
        return Graph(source=source, target=target, edges=edges, comment=self.comment)

    def copy_with_edges(self, edges: Edges) -> "Graph":
        return Graph(source=self.source, target=self.target, edges=edges, comment=self.comment)


def next_id(g: Graph) -> int:
    return ids.next_id(itertools.chain((t.id for t in g.target), (s.id for s in g.source)))


def edge(
    ids: List[str],
    labels: List[str],
    *,
    comment: Optional[str] = None,
    manual: bool = False,
) -> Edge:
    ids_sorted = sorted(ids)
    labels_nub = shared.uniq(labels)
    return Edge(
        id=f"e-{'-'.join(ids_sorted)}",
        ids=ids_sorted,
        labels=labels_nub,
        manual=manual,
        comment=comment,
    )


def edge_record(es: Iterable[Edge]) -> Dict[str, Edge]:
    return {e.id: e for e in es}


def init(s: str, *, manual: bool = False) -> Graph:
    return init_from(token.tokenize(s), manual=manual)


def init_with_source_and_target(source: str, target: str, *, manual: bool = False) -> Graph:
    return init_from_source_and_target(
        source=token.tokenize(source), target=token.tokenize(target), manual=manual
    )


def init_from(tokens: List[str], *, manual: bool = False) -> Graph:
    return align(
        Graph(
            source=token.identify(tokens, "s"),
            target=token.identify(tokens, "t"),
            edges=edge_record(
                (edge([f"s{i}", f"t{i}"], [], manual=manual) for i, _ in enumerate(tokens))
            ),
        )
    )


def init_from_source_and_target(
    source: List[str], target: List[str], *, manual: bool = False
) -> Graph:
    source_tokens = token.identify(source, "s")
    target_tokens = token.identify(target, "t")
    return align(
        Graph(
            source=source_tokens,
            target=target_tokens,
            edges=edge_record(
                itertools.chain(
                    (edge([s.id], [], manual=manual) for s in source_tokens),
                    (edge([t.id], [], manual=manual) for t in target_tokens),
                )
            ),
        )
    )


class TextLabels(TypedDict):
    text: str
    labels: List[str]


def from_unaligned(st: SourceTarget[List[TextLabels]]) -> Graph:
    """Initialize a graph from unaligned tokens"""
    edges: Dict[str, Edge] = {}

    def proto_token_to_token(tok: TextLabels, i: int, prefix: str) -> Token:
        id_ = f"{prefix}{i}"
        e = edge([id_], tok["labels"], manual=False)
        edges[id_] = e
        return Token(tok["text"], id_)

    def proto_tokens_to_tokens(toks: List[TextLabels], side: Side) -> List[Token]:
        return [
            proto_token_to_token(tok, i, "s" if side == Side.source else "t")
            for i, tok in enumerate(toks)
        ]

    g = map_sides(st, proto_tokens_to_tokens)

    return align(Graph(source=g.source, target=g.target, edges=edges))


def modify(g: Graph, from_: int, to: int, text: str, side: Side = Side.target) -> Graph:
    return align(unaligned_modify(g, from_, to, text, side))


def set_source(g: Graph, text: str) -> Graph:
    return align(unaligned_set_side(g, Side.source, text))


def set_target(g: Graph, text: str) -> Graph:
    return align(unaligned_set_side(g, Side.target, text))


def merge_edges(*es) -> Edge:
    ids = []
    labels = []
    manual = False
    comments = []
    for e in es:
        ids.extend(iter(e.ids))
        labels.extend(iter(e.labels))
        manual = manual or e.manual
        if e.comment is not None:
            comments.append(e.comment)
    return edge(
        ids=ids,
        labels=labels,
        manual=manual,
        comment="\n\n".join(comments) if comments else None,
    )


zero_edge = merge_edges()


def align(g: Graph) -> Graph:
    # Use a union-find to group characters into edges.
    uf = parallel_corpus.shared.union_find.poly_union_find(lambda u: u)
    em = edge_map(g)
    chars = map_sides(
        g,
        lambda tokens, _side: list(
            itertools.chain(
                *map(to_char_ids, filter(lambda token: not em[token.id].manual, tokens))
            )
        ),
    )
    char_diff = diffs.hdiff(chars.source, chars.target, lambda u: u.char, lambda u: u.char)
    for c in char_diff:
        # these undefined makes the alignment skip spaces.
        # they originate from to_char_ids
        if c.change == diffs.ChangeType.CONSTANT and (
            c.a is not None and c.b is not None and c.a.id is not None and c.b.id is not None
        ):
            uf.union(c.a.id, c.b.id)
    proto_edges = {k: e for k, e in g.edges.items() if e.manual}
    first: UniqueCheck[str] = UniqueCheck()

    def update_edges(tokens, _side):
        for tok in tokens:
            e_repr = em[tok.id]
            if not e_repr.manual:
                labels = e_repr.labels if first(e_repr.id) else []
                e_token = edge([tok.id], labels, manual=False, comment=e_repr.comment)
                dicts.modify(
                    proto_edges,
                    uf.find(tok.id),
                    zero_edge,
                    lambda e: merge_edges(e, e_token),  # noqa: B023
                )

    map_sides(g, update_edges)
    edges = edge_record(dicts.traverse(proto_edges, lambda e, _: e))
    return g.copy_with_edges(edges)


def rearrange(g: Graph, begin: int, end: int, dest: int) -> Graph:
    return align(unaligned_rearrange(g, begin, end, dest))


def target_text(g: SourceTarget[List[token.Text]]) -> str:
    return token.text(g.target)


@dataclass
class CharIdPair:
    char: str
    id: Optional[str] = None


def to_char_ids(token: Token) -> List[CharIdPair]:
    return parallel_corpus.shared.str_map.str_map(
        token.text,
        lambda char, _i: CharIdPair(char=char, id=None if char == " " else token.id),
    )


def edge_map(g: Graph) -> Dict[str, Edge]:
    """Map from token ids to edges

    Args:
        g (Graph): the Graph to build the edge map from.

    Returns:
        Dict[str, Edge]: a map from token ids to edges
    """
    edges = {}
    for e in g.edges.values():
        for i in e.ids:
            edges[i] = e
    return edges


def unaligned_set_side(g: Graph, side: Side, text: str) -> Graph:
    text0 = get_side_text(g, side)
    edits = parallel_corpus.shared.ranges.edit_range(text0, text)

    from_, to = edits["from"], edits["to"]
    new_text = text[from_ : (len(text) - (len(text0) - to))]
    return unaligned_modify(g, from_, to, new_text, side)


def unaligned_modify(
    g: Graph, from_: int, to: int, text: str, side: Side = Side.target
) -> Graph:
    """Replace the text at some position, merging the spans it touches upon.

    >>> show = lambda g: [t.text for t in g.target]
    >>> ids = lambda g: " ".join(t.id for t in g.target)
    >>> g = init('test graph hello')
    >>> assert show(g) == ['test ', 'graph ', 'hello ']
    >>> show(unaligned_modify(g, 0, 0, 'new'))
    ['newtest ', 'graph ', 'hello ']

    >>> show(unaligned_modify(g, 0, 1, 'new'))
    ['newest ', 'graph ', 'hello ']

    >>> show(unaligned_modify(g, 0, 5, 'new '))
    ['new ', 'graph ', 'hello ']

    >>> show(unaligned_modify(g, 0, 5, 'new'))
    ['newgraph ', 'hello ']

    >>> show(unaligned_modify(g, 5, 5, ' '))
    ['test ', ' graph ', 'hello ']

    >>> show(unaligned_modify(g, 5, 6, ' '))
    ['test ', ' raph ', 'hello ']

    >>> show(unaligned_modify(g, 0, 15, '_'))
    ['_o ']

    >>> show(unaligned_modify(g, 0, 16, '_'))
    ['_ ']

    >>> show(unaligned_modify(g, 0, 17, '_'))
    ['_ ']

    >>> show(unaligned_modify(g, 16, 16, ' !'))
    ['test ', 'graph ', 'hello ', '! ']


    Indexes are character offsets (use CodeMirror's doc.posFromIndex and doc.indexFromPos to convert)
    """  # noqa: E501

    tokens = get_side_texts(g, side)
    token_at = token.token_at(tokens, from_)
    from_token, from_ix = token_at["token"], token_at["offset"]
    pre = (tokens[from_token] if from_token < len(tokens) else "")[:from_ix]
    if to == len(get_side_text(g, side)):
        return unaligned_modify_tokens(g, from_token, len(g.get_side(side)), pre + text, side)
    to_token_at = token.token_at(tokens, to)
    to_token, to_ix = to_token_at["token"], to_token_at["offset"]
    post = (tokens[to_token] or "")[to_ix:]
    return unaligned_modify_tokens(g, from_token, to_token + 1, pre + text + post, side)


def get_side_text(g: Graph, side: Side) -> str:
    return token.text(g.get_side(side))


def get_side_texts(g: Graph, side: Side) -> List[str]:
    return token.texts(g.get_side(side))


def unaligned_modify_tokens(  # noqa: C901
    g: Graph, from_: int, to: int, text: str, side: Side = Side.target
) -> Graph:
    """Replace the text at some position, merging the spans it touches upon.

    #   const show = (g: Graph) => g.target.map(t => t.text)
    #   const ids = (g: Graph) => g.target.map(t => t.id).join(' ')
    #   const g = init('test graph hello')
    #   show(g) // => ['test ', 'graph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 0, 0, 'this '))     // => ['this ', 'test ', 'graph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 0, 1, 'this '))     // => ['this ', 'graph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 0, 1, '  white '))  // => ['  white ', 'graph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 0, 1, 'this'))      // => ['thisgraph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 1, 2, 'graph'))     // => ['test ', 'graphhello ']
    #   show(unaligned_modify_tokens(g, 1, 2, ' graph '))   // => ['test ', ' graph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 0, 1, 'for this ')) // => ['for ', 'this ', 'graph ', 'hello ']
    #   show(unaligned_modify_tokens(g, 0, 2, '')) // => ['hello ']
    #   show(unaligned_modify_tokens(g, 0, 2, '  ')) // => ['  hello ']
    #   show(unaligned_modify_tokens(g, 1, 3, '  ')) // => ['test   ']
    #   show(unaligned_modify_tokens(g, 3, 3, ' !')) // => ['test ', 'graph ', 'hello  ', '! ']
    #   show(unaligned_modify_tokens(init('a '), 0, 1, ' ')) // => [' ']
    #   ids(g) // => 't0 t1 t2'
    #   ids(unaligned_modify_tokens(g, 0, 0, 'this '))     // => 't3 t0 t1 t2'
    #   ids(unaligned_modify_tokens(g, 0, 1, 'this '))     // => 't3 t1 t2'
    #   ids(unaligned_modify_tokens(g, 0, 1, 'this'))      // => 't3 t2'
    #   const showS = (g: Graph) => g.source.map(t => t.text)
    #   const idsS = (g: Graph) => g.source.map(t => t.id).join(' ')
    #   showS(unaligned_modify_tokens(g, 0, 0, 'this ', 'source')) // => ['this ', 'test ', 'graph ', 'hello ']
    #   idsS(unaligned_modify_tokens(g, 0, 0, 'this ', 'source'))  // => 's3 s0 s1 s2'

    Indexes are token offsets
    """  # noqa: E501

    if (
        from_ < 0
        or to < 0
        or from_ > len(g.get_side(side))
        or to > len(g.get_side(side))
        or from_ > to
    ):
        raise ValueError(f"Invalid coordinates {g} {from_} {to} {text}")

    if _ := ALL_WHITESPACE.fullmatch(text):
        # replacement text is only whitespace: need to find some token to put it on
        if from_ > 0:
            return unaligned_modify_tokens(
                g, from_ - 1, to, g.get_side(side)[from_ - 1].text + text, side
            )
        elif to < len(g.get_side(side)):
            return unaligned_modify_tokens(
                g, from_, to + 1, text + g.get_side(side)[to].text, side
            )

        else:
            logger.warn("Introducing whitespace into empty graph")

    if NO_WHITESPACE_AT_END.match(text[-1:]) is not None and to < len(g.get_side(side)):
        #     if replacement text does not end with whitespace, grab the next word as well
        return unaligned_modify_tokens(g, from_, to + 1, text + g.get_side(side)[to].text, side)

    if from_ > 0 and from_ == len(g.get_side(side)) and to == len(g.get_side(side)):
        # we're adding a word at the end but the last token might not end in whitespace:
        # glue them together

        return unaligned_modify_tokens(
            g, from_ - 1, to, g.get_side(side)[from_ - 1].text + text, side
        )

    id_offset = next_id(g)

    tokens = [
        Token(t, f"{side[0]}{(id_offset + i)}") for i, t in enumerate(token.tokenize(text))
    ]

    new_tokens, removed = lists.splice(g.get_side(side), from_, to - from_, *tokens)

    ids_removed = {t.id for t in removed}

    new_edge_ids = {t.id for t in tokens}
    new_edge_labels = set()
    new_edge_manual = False

    def fun(e: Edge, _id: str) -> bool:
        if any(id_ in ids_removed for id_ in e.ids):
            for id_ in e.ids:
                if id_ not in ids_removed:
                    new_edge_ids.add(id_)
            for lbl in e.labels:
                new_edge_labels.add(lbl)
            return False
        return True

    edges = dicts.filter_dict(g.edges, fun)

    if new_edge_ids:
        e = edge(list(new_edge_ids), list(new_edge_labels), manual=new_edge_manual)
        edges[e.id] = e

    return g.copy_with_updated_side_and_edges(side, new_tokens, edges)


def unaligned_rearrange(g: Graph, begin: int, end: int, dest: int) -> Graph:
    """Moves a slice of the target tokens and puts it at a new destination.

      target_text(unaligned_rearrange(init('apa bepa cepa depa'), 1, 2, 0)) // => 'bepa cepa apa depa '

    Indexes are token offsets"""  # noqa: E501
    em = edge_map(g)
    edge_ids_to_update = {em[t.id].id for t in g.target[begin : (end + 1)]}
    new_edges = {}
    new_edges.update(g.edges)
    for id_ in edge_ids_to_update:
        new_edges[id_] = merge_edges(g.edges[id_], edge([], [], manual=True))
    return g.copy_with_updated_side_and_edges(
        Side.target, lists.rearrange(g.target, begin, end, dest), new_edges
    )
