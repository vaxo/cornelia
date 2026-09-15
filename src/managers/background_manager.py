import pygame
import random
import math
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SKY_TOP, SKY_BOT,
    BUILDING_FAR, BUILDING_MID, BUILDING_NEAR,
    WINDOW_GLOW, WINDOW_OFF, GROUND_COLOR, GROUND_LINE,
    SKY_TOP_DAY, SKY_BOT_DAY,
    BUILDING_FAR_DAY, BUILDING_MID_DAY, BUILDING_NEAR_DAY,
    WINDOW_DAY_LIT, WINDOW_DAY_OFF, GROUND_COLOR_DAY, GROUND_LINE_DAY,
    SUN_CORE, SUN_GLOW,
)


class BuildingLayer:
    def __init__(self, color, speed_factor, min_h, max_h, min_w, max_w, density,
                 win_on=WINDOW_GLOW, win_off=WINDOW_OFF, lit_chance=0.35):
        self.color = color
        self.speed_factor = speed_factor
        self.min_h = min_h
        self.max_h = max_h
        self.min_w = min_w
        self.max_w = max_w
        self.density = density
        self.win_on = win_on
        self.win_off = win_off
        self.lit_chance = lit_chance
        self.buildings = []
        self.scroll_x = 0.0
        self._generate()

    def _make_windows(self, x, y, w, h):
        windows = []
        win_gap_x, win_gap_y = 12, 14
        for wy in range(y + 10, y + h - 10, win_gap_y):
            for wx in range(x + 6, x + w - 6, win_gap_x):
                lit = random.random() < self.lit_chance
                windows.append((wx, wy, 5, 5, lit))
        return windows

    def _generate(self):
        x = 0
        while x < SCREEN_WIDTH * 2:
            w = random.randint(self.min_w, self.max_w)
            h = random.randint(self.min_h, self.max_h)
            gap = random.randint(0, int(self.max_w * 0.3))
            y = SCREEN_HEIGHT - h - 50
            self.buildings.append((x, y, w, h, self._make_windows(x, y, w, h)))
            x += w + gap

    def update(self, game_speed):
        self.scroll_x += game_speed * self.speed_factor
        # Recycle buildings
        if self.buildings and self.buildings[0][0] + self.buildings[0][2] < self.scroll_x - 10:
            self.buildings.pop(0)
            last_x = self.buildings[-1][0] + self.buildings[-1][2] if self.buildings else SCREEN_WIDTH * 2
            w = random.randint(self.min_w, self.max_w)
            h = random.randint(self.min_h, self.max_h)
            gap = random.randint(0, int(self.max_w * 0.3))
            x = last_x + gap
            y = SCREEN_HEIGHT - h - 50
            self.buildings.append((x, y, w, h, self._make_windows(x, y, w, h)))

    def render(self, surface):
        offset = int(self.scroll_x) % (SCREEN_WIDTH * 2)
        for (bx, by, bw, bh, windows) in self.buildings:
            draw_x = bx - offset
            if draw_x + bw < 0 or draw_x > SCREEN_WIDTH:
                draw_x2 = draw_x + SCREEN_WIDTH * 2
                if draw_x2 > SCREEN_WIDTH:
                    continue
                draw_x = draw_x2
            rect = pygame.Rect(draw_x, by, bw, bh)
            pygame.draw.rect(surface, self.color, rect)
            for (wx, wy, ww, wh, lit) in windows:
                col = self.win_on if lit else self.win_off
                pygame.draw.rect(surface, col, (wx - offset, wy, ww, wh))


class BackgroundManager:
    def __init__(self, day=False):
        self.day = day
        self._sky = self._make_sky()
        if day:
            self.ground_color = GROUND_COLOR_DAY
            self.ground_line = GROUND_LINE_DAY
            self.layers = [
                BuildingLayer(BUILDING_FAR_DAY,  0.08, 120, 300, 60, 110, 0.7,
                              WINDOW_DAY_LIT, WINDOW_DAY_OFF, 0.5),
                BuildingLayer(BUILDING_MID_DAY,  0.25, 80,  220, 45, 90,  0.8,
                              WINDOW_DAY_LIT, WINDOW_DAY_OFF, 0.5),
                BuildingLayer(BUILDING_NEAR_DAY, 0.55, 50,  140, 30, 70,  0.9,
                              WINDOW_DAY_LIT, WINDOW_DAY_OFF, 0.5),
            ]
        else:
            self.ground_color = GROUND_COLOR
            self.ground_line = GROUND_LINE
            self.layers = [
                BuildingLayer(BUILDING_FAR,  0.08, 120, 300, 60, 110, 0.7),
                BuildingLayer(BUILDING_MID,  0.25, 80,  220, 45, 90,  0.8),
                BuildingLayer(BUILDING_NEAR, 0.55, 50,  140, 30, 70,  0.9),
            ]

    def _make_sky(self):
        top = SKY_TOP_DAY if self.day else SKY_TOP
        bot = SKY_BOT_DAY if self.day else SKY_BOT
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(top[0] + (bot[0] - top[0]) * t)
            g = int(top[1] + (bot[1] - top[1]) * t)
            b = int(top[2] + (bot[2] - top[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        if self.day:
            self._draw_sun(surf)
        else:
            for _ in range(180):
                sx = random.randint(0, SCREEN_WIDTH)
                sy = random.randint(0, SCREEN_HEIGHT // 2)
                sb = random.randint(120, 255)
                surf.set_at((sx, sy), (sb, sb, min(sb + 20, 255)))
        return surf

    def _draw_sun(self, surf):
        sun_x = int(SCREEN_WIDTH * 0.78)
        sun_y = int(SCREEN_HEIGHT * 0.22)
        # Soft glow halo
        for i in range(9, 0, -1):
            radius = 70 + i * 26
            alpha = int(16 * (i / 9.0))
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (SUN_GLOW[0], SUN_GLOW[1], SUN_GLOW[2], alpha),
                               (radius, radius), radius)
            surf.blit(glow, (sun_x - radius, sun_y - radius))
        pygame.draw.circle(surf, SUN_GLOW, (sun_x, sun_y), 82)
        pygame.draw.circle(surf, SUN_CORE, (sun_x, sun_y), 66)
        # A few soft clouds
        for cx, cy, cw in [(int(SCREEN_WIDTH * 0.2), 150, 220),
                           (int(SCREEN_WIDTH * 0.5), 90, 180),
                           (int(SCREEN_WIDTH * 0.62), 210, 150)]:
            cloud = pygame.Surface((cw, cw // 2), pygame.SRCALPHA)
            for k in range(5):
                r = random.randint(cw // 6, cw // 4)
                px = random.randint(r, cw - r)
                py = cw // 4
                pygame.draw.circle(cloud, (245, 250, 255, 60), (px, py), r)
            surf.blit(cloud, (cx, cy))

    def update(self, game_speed):
        for layer in self.layers:
            layer.update(game_speed)

    def render(self, surface):
        surface.blit(self._sky, (0, 0))
        for layer in self.layers:
            layer.render(surface)
        pygame.draw.rect(surface, self.ground_color, (0, SCREEN_HEIGHT - 52, SCREEN_WIDTH, 52))
        pygame.draw.rect(surface, self.ground_line, (0, SCREEN_HEIGHT - 52, SCREEN_WIDTH, 3))
        pygame.draw.rect(surface, self.ground_line, (0, SCREEN_HEIGHT - 35, SCREEN_WIDTH, 2))
