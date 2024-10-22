"""SourceTarget."""

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

# Used to support StrEnum in python 3.8 and 3.9
# Not drop-in of StrEnum in python 3.11
import strenum

A = TypeVar("A")
B = TypeVar("B")


class Side(strenum.StrEnum):  # noqa: D101
    source = "source"
    target = "target"


@dataclass
class SourceTarget(Generic[A]):  # noqa: D101
    source: A
    target: A

    def get_side(self, side: Side) -> A:  # noqa: D102
        return self.source if side == Side.source else self.target


def map_sides(g: SourceTarget[A], f: Callable[[A, Side], B]) -> SourceTarget[B]:  # noqa: D103
    return SourceTarget(source=f(g.source, Side.source), target=f(g.target, Side.target))
