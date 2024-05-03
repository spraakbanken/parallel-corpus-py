from typing import Callable, Dict, List, TypeVar

A = TypeVar("A")
B = TypeVar("B")
K = TypeVar("K")
V = TypeVar("V")


def modify(x: Dict[K, V], k: K, default: V, f: Callable[[V], V]) -> V:
    x[k] = f(x.get(k) or default)
    return x[k]


def traverse(x: Dict[K, A], k: Callable[[A, K], B], *, sort_keys: bool = False) -> List[B]:
    ks = sorted(x.keys()) if sort_keys else x.keys()
    return [k(x[i], i) for i in ks]


def filter_dict(x: Dict[K, A], k: Callable[[A, K], bool]) -> Dict[K, A]:
    return {id_: a for id_, a in x.items() if k(a, id_)}
