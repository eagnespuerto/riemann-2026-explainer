"""Manim scenes for the Riemann 2026 explainer.

Render all scenes (720p, 30 fps) with:
    python manim/render.py

Each scene uses plain Text (no LaTeX needed). Zeta zeros come from mpmath,
so the dots and waves are the real ones, not drawn by hand.
"""

from functools import lru_cache

import mpmath
import numpy as np
from manim import (
    BLUE_C, GREY_B, ORANGE, RED, TEAL_C, WHITE, YELLOW,
    Arrow, Axes, Create, CurvedArrow, DashedLine, Dot, FadeIn, FadeOut,
    GrowArrow, LaggedStart, Line, Rectangle, RoundedRectangle, Scene, Text,
    Transform, VGroup, VMobject, Write, DOWN, LEFT, RIGHT, UP, UL, UR,
)

FONT = "Segoe UI"


@lru_cache(maxsize=None)
def zeta_zero_heights(n):
    """Imaginary parts of the first n non-trivial zeta zeros."""
    return tuple(float(mpmath.zetazero(k).imag) for k in range(1, n + 1))


def label(text, size=28, color=WHITE):
    return Text(text, font=FONT, font_size=size, color=color)


def strip_axes(y_max=52):
    """Complex plane with the critical strip shaded and the critical line dashed."""
    axes = Axes(
        x_range=[-1, 2, 0.5], y_range=[0, y_max, 10],
        x_length=6, y_length=6.4,
        axis_config={"color": GREY_B, "include_tip": False},
    ).shift(LEFT * 2.2)
    strip = Rectangle(
        width=axes.c2p(1, 0)[0] - axes.c2p(0, 0)[0],
        height=axes.c2p(0, y_max)[1] - axes.c2p(0, 0)[1],
        stroke_width=0, fill_color=BLUE_C, fill_opacity=0.18,
    ).move_to(axes.c2p(0.5, y_max / 2))
    line = DashedLine(axes.c2p(0.5, 0), axes.c2p(0.5, y_max), color=YELLOW)
    ticks = VGroup(
        label("0", 22).next_to(axes.c2p(0, 0), DOWN),
        label("½", 22, YELLOW).next_to(axes.c2p(0.5, 0), DOWN),
        label("1", 22).next_to(axes.c2p(1, 0), DOWN),
    )
    return axes, strip, line, ticks


class ZerosOnTheLine(Scene):
    """Parts 2-3: the first ten zeros, all on the critical line."""

    def construct(self):
        axes, strip, line, ticks = strip_axes()
        title = label("The first 10 zeros of zeta", 32).to_edge(UP).shift(RIGHT * 2.6)
        notes = VGroup(
            label("shaded band: critical strip", 24, BLUE_C),
            label("dashed line: real part ½", 24, YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=0.5)

        self.play(Create(axes), FadeIn(strip), FadeIn(ticks))
        self.play(Create(line), Write(title), FadeIn(notes))

        dots, heights = VGroup(), VGroup()
        for t in zeta_zero_heights(10):
            d = Dot(axes.c2p(0.5, t), color=ORANGE, radius=0.07)
            h = label(f"{t:.2f}", 20, ORANGE).next_to(d, RIGHT, buff=0.15)
            dots.add(d)
            heights.add(h)
        self.play(LaggedStart(*[FadeIn(VGroup(d, h), scale=1.6) for d, h in zip(dots, heights)],
                              lag_ratio=0.35, run_time=4))

        claim = label("RH: every one of the infinitely\nmany zeros sits on this line", 26)
        claim.next_to(notes, DOWN, buff=0.8, aligned_edge=LEFT)
        self.play(Write(claim))
        self.wait(2)


def psi_true(x):
    """Chebyshev psi: sum of log p over prime powers p^k <= x."""
    total = 0.0
    for n in range(2, int(x) + 1):
        # n is a prime power p^k exactly when it has one prime factor
        m, p = n, 2
        while p * p <= m and m % p:
            p += 1
        if p * p > m:
            p = m  # n itself is prime
        while m % p == 0:
            m //= p
        if m == 1:
            total += np.log(p)
    return total


def psi_explicit(xs, n_zeros):
    """Riemann-von Mangoldt explicit formula truncated after n_zeros zero pairs."""
    xs = np.asarray(xs)
    out = xs - np.log(2 * np.pi) - 0.5 * np.log(1 - xs ** -2.0)
    for t in zeta_zero_heights(n_zeros) if n_zeros else ():
        rho = 0.5 + 1j * t
        out = out - 2 * np.real(xs ** rho / rho)
    return out


class PrimesFromZeros(Scene):
    """Part 2: adding zeros one 'note' at a time rebuilds the prime staircase."""

    X_MIN, X_MAX = 2, 40

    def curve(self, axes, xs, ys, color, width=3):
        pts = [axes.c2p(x, y) for x, y in zip(xs, ys)]
        return VMobject(color=color, stroke_width=width).set_points_as_corners(pts)

    def construct(self):
        axes = Axes(
            x_range=[0, self.X_MAX, 5], y_range=[0, 45, 10],
            x_length=11, y_length=5.6,
            axis_config={"color": GREY_B, "include_tip": False, "include_numbers": True,
                         "font_size": 22},
        ).shift(DOWN * 0.5)
        title = label("Rebuilding the primes from the zeros", 32).to_edge(UP)

        # true staircase: jumps at every prime power
        xs_step, ys_step, level = [self.X_MIN], [psi_true(self.X_MIN)], psi_true(self.X_MIN)
        for n in range(self.X_MIN + 1, self.X_MAX + 1):
            new = psi_true(n)
            if new != level:
                xs_step += [n, n]
                ys_step += [level, new]
                level = new
        xs_step.append(self.X_MAX)
        ys_step.append(level)
        staircase = self.curve(axes, xs_step, ys_step, WHITE, 4)
        stair_note = label("white: the primes (one step at each prime power)", 22).next_to(axes, DOWN, buff=0.35)

        self.play(Write(title), Create(axes))
        self.play(Create(staircase, run_time=2.5), FadeIn(stair_note))

        xs = np.linspace(self.X_MIN + 0.01, self.X_MAX, 1600)
        counts = [0, 3, 10, 30, 100]
        approx = self.curve(axes, xs, psi_explicit(xs, 0), ORANGE)
        counter = label("smooth trend only (0 zeros)", 26, ORANGE).to_corner(UL).shift(DOWN * 0.9)
        self.play(Create(approx), FadeIn(counter))
        self.wait(0.8)
        for n in counts[1:]:
            new_curve = self.curve(axes, xs, psi_explicit(xs, n), ORANGE)
            new_counter = label(f"trend + {n} zeros", 26, ORANGE).move_to(counter, aligned_edge=LEFT)
            self.play(Transform(approx, new_curve), Transform(counter, new_counter), run_time=1.6)
            self.wait(0.7)
        self.wait(2)


class MirrorStep(Scene):
    """Part 8: the functional equation pairs a zero with its mirror image."""

    def construct(self):
        axes, strip, line, ticks = strip_axes(y_max=40)
        self.add(axes, strip, line, ticks)
        title = label("Step 1: the mirror", 32).to_edge(UP).shift(RIGHT * 2.6)
        self.play(Write(title))

        left = Dot(axes.c2p(0.25, 22), color=RED, radius=0.09)
        right = Dot(axes.c2p(0.75, 22), color=RED, radius=0.09)
        q = label("a zero off the line?", 22, RED).next_to(left, LEFT, buff=0.2)
        self.play(FadeIn(left, scale=1.5), FadeIn(q))
        arc = CurvedArrow(left.get_center() + UP * 0.2, right.get_center() + UP * 0.2,
                          angle=-1.2, color=YELLOW)
        self.play(Create(arc), FadeIn(right, scale=1.5))

        steps = VGroup(
            label("Zeros come in mirror pairs", 24),
            label("across the line ½.", 24),
            label("So if there are none on the right,", 24),
            label("there are none on the left either.", 24),
            label("Every zero must be on the line.", 24, YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(title, DOWN, buff=0.6)
        self.play(FadeIn(steps[:2]))

        cross = VGroup(
            Line(right.get_center() + UL * 0.25, right.get_center() - UL * 0.25, color=WHITE, stroke_width=6),
            Line(right.get_center() + UR * 0.25, right.get_center() - UR * 0.25, color=WHITE, stroke_width=6),
        )
        self.play(FadeIn(steps[2]), Create(cross))
        self.play(FadeIn(steps[3]), FadeOut(left), FadeOut(q), FadeOut(arc))
        self.play(FadeIn(steps[4]), FadeOut(right), FadeOut(cross))

        hard = label("The hard part: show nothing\nlives to the right of ½.", 26, ORANGE)
        hard.next_to(steps, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(Write(hard))
        self.wait(2)


class Multiplicity(Scene):
    """Part 9: (x - 3)^m touches zero and lingers longer as m grows."""

    def construct(self):
        axes = Axes(
            x_range=[1.5, 4.5, 0.5], y_range=[-1.5, 1.5, 0.5],
            x_length=9, y_length=4.2,
            axis_config={"color": GREY_B, "include_tip": False},
        ).shift(UP * 0.1)
        title = label("Multiplicity: zero, many times over", 32).to_edge(UP)
        root = Dot(axes.c2p(3, 0), color=YELLOW)
        root_lbl = label("x = 3", 22, YELLOW).next_to(root, DOWN)

        def graph(m):
            r = min(1.5, 1.5 ** (1 / m))  # keep |y| <= 1.5 so the curve stays on the axes
            return axes.plot(lambda x: (x - 3) ** m, x_range=[3 - r, 3 + r], color=TEAL_C, stroke_width=4)

        g = graph(1)
        tag = label("(x − 3)¹  multiplicity 1", 28, TEAL_C).to_corner(UL).shift(DOWN * 0.9)
        self.play(Write(title), Create(axes))
        self.play(Create(g), FadeIn(root), FadeIn(root_lbl), FadeIn(tag))
        sup = "¹²³⁴⁵⁶⁷⁸⁹"
        for m in range(2, 10):
            new_tag = label(f"(x − 3){sup[m - 1]}  multiplicity {m}", 28, TEAL_C).move_to(tag, aligned_edge=LEFT)
            self.play(Transform(g, graph(m)), Transform(tag, new_tag), run_time=0.9)
        note = label("Higher multiplicity: flatter at the root.\nA polynomial of degree d has at most d roots,\ncounting multiplicity, so deep roots must be few.",
                     22).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note))
        self.wait(2.5)


class ThetaChain(Scene):
    """Part 10: each theta lift acts like one derivative."""

    def construct(self):
        title = label("Step 3: theta lifts as stand-in derivatives", 32).to_edge(UP)
        self.play(Write(title))

        n_boxes = 6
        boxes = VGroup()
        for k in range(n_boxes):
            scale = 0.75 + 0.12 * k
            box = RoundedRectangle(corner_radius=0.12, width=1.25 * scale, height=0.9 * scale,
                                   color=BLUE_C, fill_opacity=0.15)
            name = label(f"U(X{'₀₁₂₃₄₅'[k]})", 22).move_to(box)
            boxes.add(VGroup(box, name))
        boxes.arrange(RIGHT, buff=0.55).shift(UP * 0.4)

        counter = label("multiplicity: 0", 30, ORANGE).next_to(boxes, DOWN, buff=1.0)
        self.play(FadeIn(boxes[0]), FadeIn(counter))
        for k in range(1, n_boxes):
            arrow = Arrow(boxes[k - 1].get_right(), boxes[k].get_left(), buff=0.08,
                          color=YELLOW, stroke_width=4, max_tip_length_to_length_ratio=0.3)
            new_counter = label(f"multiplicity: {k}", 30, ORANGE).move_to(counter)
            self.play(GrowArrow(arrow), FadeIn(boxes[k], shift=RIGHT * 0.3),
                      Transform(counter, new_counter), run_time=0.9)

        bottom = VGroup(
            label("Each lift into a bigger symmetry group adds one level.", 24),
            label("To control primes up to X, the chain needs about √X lifts,", 24),
            label("the same square root RH promises for the noise.", 24, YELLOW),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(b) for b in bottom], lag_ratio=0.5))
        self.wait(2.5)
