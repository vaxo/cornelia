"""Vector-drawn UI icons.

Drawn with pygame primitives instead of font glyphs so they render identically
on every OS — emoji and arrow glyphs (🔒 ✓ 🏁 ◀ ▶) are missing from many system
fonts and would otherwise show as tofu boxes.
"""
import math
import pygame


def draw_star(surface, cx, cy, r, color, points=5):
    pts = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surface, color, pts)


def draw_shield(surface, cx, cy, size, color):
    w = size * 0.8
    h = size
    pts = [
        (cx - w / 2, cy - h / 2),
        (cx + w / 2, cy - h / 2),
        (cx + w / 2, cy + h * 0.05),
        (cx, cy + h / 2),
        (cx - w / 2, cy + h * 0.05),
    ]
    pygame.draw.polygon(surface, color, pts)
    # inner check mark
    draw_check(surface, int(cx), int(cy - size * 0.02), int(size * 0.5), (20, 26, 50), 3)


def draw_clock(surface, cx, cy, size, color, width=3):
    r = size // 2
    pygame.draw.circle(surface, color, (cx, cy), r, width)
    pygame.draw.line(surface, color, (cx, cy), (cx, cy - r + 4), width)      # minute hand
    pygame.draw.line(surface, color, (cx, cy), (cx + r - 6, cy + 2), width)  # hour hand


def draw_left_arrow(surface, cx, cy, size, color):
    h = size // 2
    pygame.draw.polygon(surface, color, [
        (cx + h, cy - h), (cx - h, cy), (cx + h, cy + h)])


def draw_right_arrow(surface, cx, cy, size, color):
    h = size // 2
    pygame.draw.polygon(surface, color, [
        (cx - h, cy - h), (cx + h, cy), (cx - h, cy + h)])


def draw_check(surface, cx, cy, size, color, width=3):
    h = size // 2
    pygame.draw.lines(surface, color, False, [
        (cx - h, cy), (cx - h // 3, cy + h), (cx + h, cy - h)], width)


def draw_lock(surface, cx, cy, size, color):
    body_w = size
    body_h = int(size * 0.72)
    body = pygame.Rect(cx - body_w // 2, cy - body_h // 2 + size // 6, body_w, body_h)
    # Shackle (the arch on top)
    r = size // 3
    arc_rect = pygame.Rect(cx - r, body.top - r, 2 * r, 2 * r)
    pygame.draw.arc(surface, color, arc_rect, 0.2, 3.14159 - 0.2, max(2, size // 8))
    # Body
    pygame.draw.rect(surface, color, body, border_radius=3)
    # Keyhole
    pygame.draw.circle(surface, (30, 30, 40), (cx, cy + size // 6), max(2, size // 9))


def draw_finish_flag(surface, x, y, size, dark=(30, 34, 45), light=(235, 235, 245)):
    """Small checkered flag on a short pole, top-left anchored at (x, y)."""
    pole = max(2, size // 12)
    pygame.draw.rect(surface, (150, 150, 160), (x, y, pole, size))
    flag_x = x + pole
    flag_w = size
    flag_h = int(size * 0.62)
    cells = 4
    cw = flag_w / cells
    ch = flag_h / cells
    for row in range(cells):
        for col in range(cells):
            col_color = light if (row + col) % 2 == 0 else dark
            pygame.draw.rect(surface, col_color, (
                int(flag_x + col * cw), int(y + row * ch),
                int(cw + 1), int(ch + 1)))
