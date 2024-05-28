from __future__ import annotations
import copy
from dataclasses import dataclass
from math import sqrt
import numpy as np
from .point import Point


@dataclass
class Box:
    u = [Point(0, 0), Point(0, 0)]
    index = [0, 0, 0, 0]
    sqr_len = 0.0
    area = 0.0

    def __init__(self, p0: Point, p1: Point):
        self.update(p0, p1)

    def __str__(self):
        return f"Box({self.u=}, index={self.index}, {self.sqr_len=})"

    def update(self, p0: Point, p1: Point):
        self.u[0] = p1 - p0
        self.u[0] /= sqrt(self.u[0] @ self.u[0])
        self.u[1] = -self.u[0].perp()
        self.sqr_len = self.u[0] @ self.u[0]

    @classmethod
    def clone(cls, box: Box) -> Box:
        return copy.deepcopy(box)


class MinBoundRect:
    def __init__(self, vertices: list[Point]) -> None:
        self.vertices = vertices
        self.visited = [False] * len(vertices)
        self.support: list[Point] = []

    def get_smallest_box(self, i0: int, i1: int) -> Box:
        box = Box(self.vertices[i0], self.vertices[i1])
        box.index = [i1] * 4
        origin = self.vertices[i1]
        self.support = [Point(0, 0) for _ in range(4)]

        for i, vertex in enumerate(self.vertices):
            diff = vertex - origin
            v = Point(box.u[0] @ diff, box.u[1] @ diff)
            if (
                v.x > self.support[1].x
                or v.x == self.support[1].x
                and v.y > self.support[1].y
            ):
                box.index[1] = i
                self.support[1] = v.clone()

            if (
                v.y > self.support[2].y
                or v.y == self.support[2].y
                and v.x < self.support[2].x
            ):
                box.index[2] = i
                self.support[2] = v.clone()

            if (
                v.x < self.support[3].x
                or v.x == self.support[3].x
                and v.y < self.support[3].y
            ):
                box.index[3] = i
                self.support[3] = v.clone()

        w = self.support[1].x - self.support[3].x
        h = self.support[2].y
        box.area = w * h / box.sqr_len
        return box

    def compute_angles(self, box: Box) -> list[tuple[float, int]]:
        angles = []
        k0 = 3
        for k1 in range(4):
            if box.index[k0] == box.index[k1]:
                continue
            # u[0], u[1], -u[0], -u[1]
            d = -box.u[k0 & 1] if k0 & 2 else box.u[k0 & 1]
            j0 = box.index[k0]
            j1 = (j0 + 1) % len(self.vertices)
            e = self.vertices[j1] - self.vertices[j0]
            dp = d @ e.perp()
            sin_sqr = dp * dp / (e @ e)
            angles.append((sin_sqr, k0))
            k0 = k1
        return angles

    def update_support(self, angles: list[tuple[float, int]], box: Box) -> bool:
        min_angle = angles[0]
        for a in angles:
            if a[0] == min_angle[0]:
                box.index[a[1]] = (box.index[a[1]] + 1) % len(self.vertices)
        bottom = box.index[min_angle[1]]
        if self.visited[bottom]:
            return False
        self.visited[bottom] = True

        next_index = [box.index[(min_angle[1] + k) % 4] for k in range(4)]
        box.index = next_index
        j1 = box.index[0]
        j0 = (j1 - 1) % len(self.vertices)
        box.update(self.vertices[j0], self.vertices[j1])
        d1 = self.vertices[box.index[1]] - self.vertices[box.index[3]]
        d2 = self.vertices[box.index[2]] - self.vertices[box.index[0]]
        box.area = (box.u[0] @ d1) * (box.u[1] @ d2) / box.sqr_len
        return True

    def __call__(self) -> Box:
        min_box = self.get_smallest_box(len(self.vertices) - 1, 0)
        self.visited[min_box.index[0]] = True

        box = Box.clone(min_box)
        for _ in self.vertices:
            angles = self.compute_angles(box)
            if not angles:
                break
            angles.sort(key=lambda x: x[0])
            if not self.update_support(angles, box):
                break

            if box.area < min_box.area:
                min_box = Box.clone(box)

        return min_box

    def boundRectSqr(self) -> Box:
        min_box = Box(self.vertices[0], self.vertices[1])
        min_box.area = -1
        i0 = len(self.vertices) - 1
        for i in range(len(self.vertices)):
            box = self.get_smallest_box(i0, i)
            if min_box.area == -1 or box.area < min_box.area:
                min_box = box
            i0 = i

        return min_box


def min_bound_rect(points: list[Point]) -> list[list[Point]]:
    if len(points) < 3:
        return []

    box = MinBoundRect(points).boundRectSqr()

    sum = [
        points[box.index[1]] + points[box.index[3]],
        points[box.index[2]] + points[box.index[0]],
    ]
    diff = [
        points[box.index[1]] - points[box.index[3]],
        points[box.index[2]] - points[box.index[0]],
    ]
    center = (
        0.5
        * ((box.u[0] @ sum[0]) * box.u[0] + (box.u[1] @ sum[1]) * box.u[1])
        / box.sqr_len
    )
    axes: list[Point] = []
    extent: list[float] = []
    for i in range(2):
        extent.append(0.5 * (box.u[i] @ diff[i]))
        extent[i] = sqrt(extent[i] * extent[i] / box.sqr_len)
        axis = box.u[i]
        inv_max = 1.0 / max(abs(axis.x), abs(axis.y))
        axes.append(Point(axis.x * inv_max, axis.y * inv_max))
        axes[i] /= sqrt(axes[i] @ axes[i])
    result = []
    product = [axes[d] * extent[d] for d in range(2)]
    for i in range(4):
        result.append(center.clone())
        mask = 1
        for d in range(2):
            if (i & mask) > 0:
                result[i] += product[d]
            else:
                result[i] -= product[d]
            mask <<= 1
    return result


def minimum_bounding_rectangle(points: list[Point]) -> list[Point]:
    if len(points) < 3:
        return []

    pi2 = np.pi / 2.0

    hull_points = np.array([(p.x, p.y) for p in points])

    edges = np.zeros((len(hull_points) - 1, 2))
    edges = hull_points[1:] - hull_points[:-1]
    np.append(edges, hull_points[0] - hull_points[-1])

    angles = np.zeros((len(edges)))
    angles = np.arctan2(edges[:, 1], edges[:, 0])

    angles = np.abs(np.mod(angles, pi2))
    angles = np.unique(angles)

    rotations = np.vstack(
        [np.cos(angles), np.cos(angles - pi2), np.cos(angles + pi2), np.cos(angles)]
    ).T

    rotations = rotations.reshape((-1, 2, 2))
    rot_points = np.dot(rotations, hull_points.T)

    min_x = np.nanmin(rot_points[:, 0], axis=1)
    max_x = np.nanmax(rot_points[:, 0], axis=1)
    min_y = np.nanmin(rot_points[:, 1], axis=1)
    max_y = np.nanmax(rot_points[:, 1], axis=1)

    areas = (max_x - min_x) * (max_y - min_y)
    best_idx = np.argmin(areas)

    x1 = max_x[best_idx]
    x2 = min_x[best_idx]
    y1 = max_y[best_idx]
    y2 = min_y[best_idx]
    r = rotations[best_idx]

    rval = np.zeros((4, 2))
    rval[0] = np.dot([x1, y2], r)
    rval[1] = np.dot([x2, y2], r)
    rval[2] = np.dot([x2, y1], r)
    rval[3] = np.dot([x1, y1], r)

    return [Point(p[0], p[1]) for p in rval]
