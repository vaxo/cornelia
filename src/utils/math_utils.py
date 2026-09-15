"""Small math helpers used across the game."""
import random


def clamp(value, low, high):
    """Constrain *value* to the inclusive range [low, high]."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def lerp(a, b, t):
    """Linear interpolation between a and b by factor t (0..1)."""
    return a + (b - a) * t


def random_range(a, b):
    """Uniform random float in [a, b]."""
    return random.uniform(a, b)


def sign(x):
    return (x > 0) - (x < 0)
