"""
Math utilities for aim calculation: bezier curves, smoothing, humanization.
"""
import math
import random
import numpy as np


def distance(p1: tuple, p2: tuple) -> float:
    """Euclidean distance between two points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def ease_out_quad(t: float) -> float:
    """Ease-out quadratic curve: fast start, slow end."""
    return t * (2 - t)


def ease_in_out_cubic(t: float) -> float:
    """Ease-in-out cubic: smooth start and end."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def bezier_point(p0: tuple, p1: tuple, p2: tuple, p3: tuple, t: float) -> tuple:
    """Cubic bezier curve evaluation at parameter t."""
    u = 1 - t
    x = (u**3 * p0[0] + 3 * u**2 * t * p1[0] +
         3 * u * t**2 * p2[0] + t**3 * p3[0])
    y = (u**3 * p0[1] + 3 * u**2 * t * p1[1] +
         3 * u * t**2 * p2[1] + t**3 * p3[1])
    return (x, y)


def generate_bezier_path(start: tuple, end: tuple, steps: int = 10,
                         curvature: float = 0.3) -> list:
    """Generate a smooth bezier path from start to end with some randomness."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Random control points offset perpendicular to the line
    perp_x = -dy * curvature * (random.random() * 0.6 + 0.7)
    perp_y = dx * curvature * (random.random() * 0.6 + 0.7)

    cp1 = (
        start[0] + dx * 0.25 + perp_x * random.choice([-1, 1]),
        start[1] + dy * 0.25 + perp_y * random.choice([-1, 1]),
    )
    cp2 = (
        start[0] + dx * 0.75 - perp_x * random.choice([-1, 1]) * 0.5,
        start[1] + dy * 0.75 - perp_y * random.choice([-1, 1]) * 0.5,
    )

    path = []
    for i in range(steps + 1):
        t = i / steps
        # Apply ease-out so movement decelerates at the end
        t_eased = ease_out_quad(t)
        point = bezier_point(start, cp1, cp2, end, t_eased)
        path.append(point)

    return path


def add_jitter(x: float, y: float, amount: float) -> tuple:
    """Add random jitter to a point."""
    jx = random.gauss(0, amount)
    jy = random.gauss(0, amount)
    return (x + jx, y + jy)


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


def calculate_move_delta(current: tuple, target: tuple,
                         smoothing: float, curve: str = "bezier",
                         max_move: float = 80) -> tuple:
    """
    Calculate the mouse move delta for one tick.
    smoothing: 0.0 = instant, 1.0 = barely moves.
    Returns (dx, dy) in pixels.
    """
    dx = target[0] - current[0]
    dy = target[1] - current[1]
    dist = math.hypot(dx, dy)

    if dist < 0.5:
        return (0, 0)

    # Smoothing factor: higher = slower movement
    factor = 1.0 - clamp(smoothing, 0.0, 0.95)

    if curve == "ease_out":
        # Normalize distance to get a 0-1 range for easing
        norm = min(dist / 200, 1.0)
        factor *= ease_out_quad(norm)
    elif curve == "ease_in_out":
        norm = min(dist / 200, 1.0)
        factor *= ease_in_out_cubic(norm)
    elif curve == "bezier":
        # For bezier, we apply slight randomness to factor
        factor *= (0.85 + random.random() * 0.3)

    move_x = dx * factor
    move_y = dy * factor

    # Clamp max move per tick
    move_dist = math.hypot(move_x, move_y)
    if move_dist > max_move:
        scale = max_move / move_dist
        move_x *= scale
        move_y *= scale

    return (move_x, move_y)


def predict_position(current_pos: tuple, velocity: tuple,
                     factor: float = 0.3) -> tuple:
    """Predict future position based on velocity."""
    return (
        current_pos[0] + velocity[0] * factor,
        current_pos[1] + velocity[1] * factor,
    )
