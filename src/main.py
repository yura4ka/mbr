import argparse
from itertools import pairwise
import random
import sys
from time import time
import tkinter as tk
from tkinter import ttk
from mbr import Point, convexHull, minimum_bounding_rectangle


def generate_random_points(
    n_range=(10, 30), *, x_range=(150, 650), y_range=(100, 500)
) -> list[Point]:
    n = random.randrange(n_range[0], n_range[1])
    result = []
    for _ in range(n):
        x = random.randrange(x_range[0], x_range[1])
        y = random.randrange(y_range[0], y_range[1])
        result.append(Point(x, y))
    return result


class UI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.points: list[Point] = []
        self.hull: list[Point] = []
        self.mbr: list[Point] = []
        self.hull_ids = []
        self.mbr_ids = []

        self.title("Minimum Bound Rectangle")
        self.geometry("800x600")

        self.main_canvas = tk.Canvas(self, bg="white")
        self.main_canvas.pack(fill=tk.BOTH, expand=True)
        self.main_canvas.bind("<Button-1>", self.canvas_clicked)

        self.menu_frame = tk.Frame(self, bg="lightgrey", height=100)
        self.menu_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.ch_visible = tk.BooleanVar(value=True)
        self.mbr_visible = tk.BooleanVar(value=True)
        self.checkbox1 = ttk.Checkbutton(
            self.menu_frame,
            text="Convex Hull",
            variable=self.ch_visible,
            command=self.ch_visible_changed,
        )
        self.checkbox2 = ttk.Checkbutton(
            self.menu_frame,
            text="MBR",
            variable=self.mbr_visible,
            command=self.mbr_visible_changed,
        )
        self.checkbox1.pack(side=tk.LEFT, padx=10, pady=10)
        self.checkbox2.pack(side=tk.LEFT, padx=10, pady=10)

        self.undoBtn = ttk.Button(
            self.menu_frame, text="Undo", command=self.undoBtn_clicked
        )
        self.clearBtn = ttk.Button(
            self.menu_frame, text="Clear", command=self.clearBtn_clicked
        )
        self.randomBtn = ttk.Button(
            self.menu_frame, text="Random", command=self.randomBtn_clicked
        )
        self.undoBtn.pack(side=tk.RIGHT, padx=10, pady=10)
        self.clearBtn.pack(side=tk.RIGHT, padx=10, pady=10)
        self.randomBtn.pack(side=tk.RIGHT, padx=10, pady=10)

    def redraw(self, recalculate=False):
        if recalculate:
            self.hull = convexHull(self.points)
            self.mbr = minimum_bounding_rectangle(self.hull)
        self.main_canvas.delete("all")
        self.draw_hull()
        self.draw_mbr()
        self.draw_vertices()

    def draw_vertices(self):
        for p in self.points:
            self.draw_vertex(p)

    def draw_hull(self):
        if len(self.hull) < 2:
            return
        show = self.ch_visible.get()
        state = "normal" if show else "hidden"
        self.hull_ids = []
        prev = self.hull[-1]
        for p in self.hull:
            id = self.main_canvas.create_line(
                prev.x, prev.y, p.x, p.y, fill="blue", state=state
            )
            self.hull_ids.append(id)
            prev = p

    def draw_mbr(self):
        if len(self.mbr) < 2:
            return
        show = self.mbr_visible.get()
        state = "normal" if show else "hidden"
        self.mbr_ids = []
        prev = self.mbr[-1]
        for p in self.mbr:
            id = self.main_canvas.create_line(
                prev.x, prev.y, p.x, p.y, fill="red", state=state
            )
            self.mbr_ids.append(id)
            prev = p

    def draw_vertex(self, point: Point, *, fill="black"):
        radius = 2.5
        x1, y1 = point.x - radius, point.y - radius
        x2, y2 = point.x + radius, point.y + radius
        self.main_canvas.create_oval(x1, y1, x2, y2, fill=fill, outline="")
        self.main_canvas.create_text(x1, y2, text=f"{round(point.x)}; {round(point.y)}")

    def canvas_clicked(self, event):
        self.points.append(Point(event.x, event.y))
        self.redraw(True)

    def ch_visible_changed(self):
        show = self.ch_visible.get()
        for id in self.hull_ids:
            self.main_canvas.itemconfigure(id, state="normal" if show else "hidden")

    def mbr_visible_changed(self):
        show = self.mbr_visible.get()
        for id in self.mbr_ids:
            self.main_canvas.itemconfigure(id, state="normal" if show else "hidden")

    def undoBtn_clicked(self):
        if self.points:
            self.points.pop()
            self.redraw(True)

    def clearBtn_clicked(self):
        self.main_canvas.delete("all")
        self.points = []

    def randomBtn_clicked(self):
        self.points = generate_random_points()
        self.redraw(True)


def from_input():
    points = []
    while True:
        try:
            if not (n := input()):
                break
        except EOFError:
            break
        points += [float(p) for p in n.split() if p]
    if len(points) & 1:
        print("Error! There must be even number of numbers", file=sys.stderr)
        return
    points = [Point(p[0], p[1]) for p in pairwise(points)]
    mbr = minimum_bounding_rectangle(points)
    for p in mbr:
        print(f"{p.x} {p.y}")


def generate_points(n: int):
    points = generate_random_points(
        (n, n + 1), x_range=(-300, 300), y_range=(-300, 300)
    )
    filename = f"generated_input_{n}_{int(time())}.in"
    with open(filename, "w") as f:
        for p in points:
            f.write(f"{p.x} {p.y}\n")
    mbr = minimum_bounding_rectangle(points)
    for p in mbr:
        print(f"{p.x} {p.y}")


def main():
    parser = argparse.ArgumentParser(description="Minimum bound rectagle")
    parser.add_argument(
        "-i",
        "--input",
        action="store_true",
        default=False,
    )
    parser.add_argument("-g", "--generate", type=int)
    args = parser.parse_args()

    if args.input:
        from_input()
        return
    if args.generate:
        generate_points(args.generate)
        return
    app = UI()
    app.mainloop()


if __name__ == "__main__":
    main()
