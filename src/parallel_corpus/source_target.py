from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

# Used to support StrEnum in python 3.8 and 3.9
# Not drop-in of StrEnum in python 3.11
import strenum

A = TypeVar("A")
B = TypeVar("B")


class Side(strenum.StrEnum):
    source = "source"
    target = "target"


@dataclass
class SourceTarget(Generic[A]):
    source: A
    target: A

    def get_side(self, side: Side) -> A:
        return self.source if side == Side.source else self.target


def map_sides(g: SourceTarget[A], f: Callable[[A, Side], B]) -> SourceTarget[B]:
    return SourceTarget(source=f(g.source, Side.source), target=f(g.target, Side.target))
