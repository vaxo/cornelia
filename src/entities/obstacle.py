import pygame
import random
from config.constants import (
    SCREEN_HEIGHT, OBSTACLE_WIDTH,
    OBSTACLE_COLOR, OBSTACLE_EDGE, OBSTACLE_STRIPE,
    OBSTACLE_MIN_Y_EDGE, OBSTACLE_MAX_Y_EDGE,
)


class Obstacle:
    def __init__(self, x, gap_size, gap_y=None):
        self.x = float(x)
        self.width = OBSTACLE_WIDTH
        self.gap_size = gap_size
        min_edge = OBSTACLE_MIN_Y_EDGE
        max_edge = OBSTACLE_MAX_Y_EDGE
        if gap_y is None:
            gap_y = random.randint(
                min_edge + gap_size // 2,
                SCREEN_HEIGHT - max_edge - gap_size // 2,
            )
        self.gap_y = gap_y
        self.top_h = gap_y - gap_size // 2
        self.bot_y = gap_y + gap_size // 2
        self.bot_h = SCREEN_HEIGHT - self.bot_y
        self.passed = False

    @property
    def rect_top(self):
        return pygame.Rect(int(self.x), 0, self.width, self.top_h)

    @property
    def rect_bot(self):
        return pygame.Rect(int(self.x), self.bot_y, self.width, self.bot_h)

    def update(self, dt, speed, time_scale=1.0):
        self.x -= speed

    def is_offscreen(self):
        return self.x + self.width < 0

    def check_passed(self, car_x):
        if not self.passed and car_x > self.x + self.width:
            self.passed = True
            return True
        return False

    def _draw_pillar(self, surface, rect):
        if rect.height <= 0:
            return
        pygame.draw.rect(surface, OBSTACLE_COLOR, rect)
        # Cylindrical shading: vertical bands, light highlight left-of-centre,
        # darker toward the right edge — makes the flat pillar read as a column.
        light = tuple(min(255, c + 26) for c in OBSTACLE_COLOR)
        light2 = tuple(min(255, c + 12) for c in OBSTACLE_COLOR)
        dark = tuple(max(0, c - 20) for c in OBSTACLE_COLOR)
        pygame.draw.rect(surface, light2, (rect.x + int(rect.width * 0.16), rect.y,
                                           int(rect.width * 0.30), rect.height))
        pygame.draw.rect(surface, light, (rect.x + int(rect.width * 0.26), rect.y,
                                          int(rect.width * 0.12), rect.height))
        pygame.draw.rect(surface, dark, (rect.right - int(rect.width * 0.26), rect.y,
                                         int(rect.width * 0.26), rect.height))
        # Edge shading
        pygame.draw.rect(surface, OBSTACLE_EDGE, (rect.x, rect.y, 4, rect.height))
        pygame.draw.rect(surface, OBSTACLE_EDGE, (rect.right - 4, rect.y, 4, rect.height))
        # Horizontal stripes every 40px
        for sy in range(rect.y + 15, rect.y + rect.height, 40):
            pygame.draw.rect(surface, OBSTACLE_STRIPE, (rect.x + 4, sy, rect.width - 8, 3))
        # Cap
        cap_h = 18
        if rect == self.rect_top:
            cap_y = rect.bottom - cap_h
        else:
            cap_y = rect.top
        cap_rect = pygame.Rect(rect.x - 5, cap_y, rect.width + 10, cap_h)
        pygame.draw.rect(surface, OBSTACLE_EDGE, cap_rect, border_radius=3)
        pygame.draw.rect(surface, OBSTACLE_STRIPE, (cap_rect.x + 3, cap_rect.y + 4, cap_rect.width - 6, 4))

    def render(self, surface, shake=(0, 0)):
        rt = self.rect_top.move(*shake)
        rb = self.rect_bot.move(*shake)
        self._draw_pillar(surface, rt)
        self._draw_pillar(surface, rb)
