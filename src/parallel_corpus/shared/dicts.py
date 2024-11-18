"""dicts."""

from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

    K = TypeVar("K", bound=SupportsRichComparison)  # type: ignore [syntax]
else:
    K = TypeVar("K")

A = TypeVar("A")
B = TypeVar("B")
V = TypeVar("V")


def modify(x: dict[K, V], k: K, default: V, f: Callable[[V], V]) -> V:  # noqa: D103
    x[k] = f(x.get(k) or default)
    return x[k]


def traverse(x: dict[K, A], k: Callable[[A, K], B], *, sort_keys: bool = False) -> list[B]:  # noqa: D103
    ks = sorted(x.keys()) if sort_keys else x.keys()
    return [k(x[i], i) for i in ks]


def filter_dict(x: dict[K, A], k: Callable[[A, K], bool]) -> dict[K, A]:  # noqa: D103
    return {id_: a for id_, a in x.items() if k(a, id_)}
