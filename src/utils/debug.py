"""Lightweight debug helpers. Set DEBUG=True to enable console logging."""

DEBUG = False


def log(*args):
    if DEBUG:
        print("[cornelia]", *args)


def draw_rect_outline(surface, rect, color=(255, 0, 0), width=1):
    """Draw a hitbox outline; handy while debugging collisions."""
    import pygame
    pygame.draw.rect(surface, color, rect, width)
