from __future__ import annotations
from dataclasses import dataclass
from math import atan2


@dataclass
class Point:
    x: float
    y: float

    def angle(self, p1: Point) -> float:
        return atan2(p1.y - self.y, p1.x - self.x)

    def distance(self, p1: Point) -> float:
        return (p1.x - self.x) ** 2 + (p1.y - self.y) ** 2

    def perp(self: Point) -> Point:
        return Point(self.y, -self.x)

    def clone(self) -> Point:
        return Point(self.x, self.y)

    def dot(self, p: Point) -> float:
        return self.x * p.x + self.y * p.y

    def __add__(self, p: Point) -> Point:
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p: Point) -> Point:
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, other) -> Point:
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        return Point(self.x * other, self.y * other)

    def __rmul__(self, other) -> Point:
        return self.__mul__(other)

    def __truediv__(self, p: float) -> Point:
        return Point(self.x / p, self.y / p)

    def __matmul__(self, p: Point) -> float:
        return self.dot(p)

    def __neg__(self) -> Point:
        return Point(-self.x, -self.y)
