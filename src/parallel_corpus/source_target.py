import enum
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class Side(enum.StrEnum):
    source = "source"
    target = "target"


@dataclass
class SourceTarget(Generic[A]):
    source: A
    target: A

    def get_side(self, side: Side) -> A:
        if side == Side.source:
            return self.source
        if side == Side.target:
            return self.target


def map_sides(g: SourceTarget[A], f: Callable[[A, Side], B]) -> SourceTarget[B]:
    return SourceTarget(source=f(g.source, Side.source), target=f(g.target, Side.target))
