from .point import Point


def orientation(p1: Point, p2: Point, p3: Point) -> int:
    val = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)
    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return -1


def convexHull(points: list[Point]) -> list[Point]:
    if len(points) <= 3:
        return points

    start = min(points, key=lambda p: (p.y, p.x))
    sorted_points = sorted(points, key=lambda p: (start.angle(p), start.distance(p)))

    hull = [start, sorted_points[1]]

    for point in sorted_points[2:]:
        while len(hull) > 1 and orientation(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)

    return hull
