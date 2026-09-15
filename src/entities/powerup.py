import pygame
import math
from config.constants import OBSTACLE_WIDTH
from src.ui.icons import draw_shield, draw_clock, draw_star

# Power-up kinds and their theme colors.
TYPES = ["shield", "slowmo", "score2x"]
COLORS = {
    "shield":  (80, 180, 255),   # blue  — second life
    "slowmo":  (180, 120, 255),  # purple— slows obstacles
    "score2x": (255, 200, 60),   # gold  — double points
}
RADIUS = 26


class PowerUp:
    """A collectible that rides inside an obstacle's gap.

    Anchoring it to an obstacle's gap guarantees it always sits in the safe
    passage — you pick it up by threading the gap, never by crashing into a
    wall. It tracks the gap even for moving obstacles.
    """

    def __init__(self, kind, obstacle):
        self.kind = kind
        self.obstacle = obstacle
        self.r = RADIUS
        self._t = 0.0
        self.collected = False
        self.x = obstacle.x + OBSTACLE_WIDTH / 2
        self.y = float(obstacle.gap_y)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r),
                           self.r * 2, self.r * 2)

    def update(self, dt, speed):
        self._t += dt * 0.005
        # Stay centered in the (possibly moving) gap of its obstacle.
        self.x = self.obstacle.x + OBSTACLE_WIDTH / 2
        self.y = float(self.obstacle.gap_y)

    def is_offscreen(self):
        return self.obstacle.is_offscreen()

    def render(self, surface, shake=(0, 0)):
        bob = math.sin(self._t) * 3
        cx = int(self.x) + shake[0]
        cy = int(self.y + bob) + shake[1]
        col = COLORS[self.kind]

        # Pulsing glow (blends fine on the opaque 24-bit canvas)
        pulse = 0.5 + 0.5 * math.sin(self._t * 1.5)
        glow_r = int(self.r + 8 + pulse * 6)
        gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (col[0], col[1], col[2], 70), (glow_r, glow_r), glow_r)
        surface.blit(gs, (cx - glow_r, cy - glow_r))

        pygame.draw.circle(surface, (18, 24, 48), (cx, cy), self.r)
        pygame.draw.circle(surface, col, (cx, cy), self.r, 3)

        if self.kind == "shield":
            draw_shield(surface, cx, cy, 26, col)
        elif self.kind == "slowmo":
            draw_clock(surface, cx, cy, 24, col)
        else:  # score2x
            draw_star(surface, cx, cy, 14, col)
