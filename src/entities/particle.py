import pygame
import random
import math
from config.constants import (
    SPARK_COLORS, RAIN_COLOR, SNOW_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT,
)
from src.utils.math_utils import random_range


class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, fade=True):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.fade = fade
        self.alive = True

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25  # gravity on sparks
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def render(self, surface, shake=(0, 0)):
        if not self.alive:
            return
        alpha_ratio = self.life / self.max_life if self.fade else 1.0
        r, g, b = self.color[:3]
        size = max(1, int(self.size * alpha_ratio))
        color = (int(r * alpha_ratio), int(g * alpha_ratio), int(b * alpha_ratio))
        pygame.draw.circle(surface, color,
                           (int(self.x) + shake[0], int(self.y) + shake[1]), size)


def create_sparks(x, y, count=25):
    particles = []
    for _ in range(count):
        angle = random_range(0, math.pi * 2)
        speed = random_range(2, 8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - random_range(1, 4)
        color = random.choice(SPARK_COLORS)
        size = random_range(2, 5)
        life = random.randint(20, 45)
        particles.append(Particle(x, y, vx, vy, color, size, life))
    return particles


# Rain streaks and snow flakes are pre-rendered once per (shape, alpha) and then
# only blitted. Drawing them straight onto the frame beats compositing a
# full-screen alpha overlay: a few hundred tiny blits cost ~0.1 ms, the overlay
# clear + blit cost ~1.4 ms on its own.
_SPRITES = {}
_ALPHA_STEPS = 16


def _quantize(alpha):
    a = int(alpha) // _ALPHA_STEPS * _ALPHA_STEPS
    return max(0, min(255, a))


def _convert(surf):
    try:
        return surf.convert_alpha()
    except pygame.error:
        return surf


def _rain_sprite(length, alpha):
    key = ("r", length, alpha)
    spr = _SPRITES.get(key)
    if spr is None:
        w = max(2, int(length * 0.3) + 2)
        surf = pygame.Surface((w, length + 2), pygame.SRCALPHA)
        r, g, b = RAIN_COLOR
        pygame.draw.line(surf, (r, g, b, alpha), (w - 1, 0), (0, length), 1)
        spr = _SPRITES[key] = _convert(surf)
    return spr


def _snow_sprite(radius, alpha):
    key = ("s", radius, alpha)
    spr = _SPRITES.get(key)
    if spr is None:
        d = radius * 2 + 2
        surf = pygame.Surface((d, d), pygame.SRCALPHA)
        r, g, b = SNOW_COLOR
        pygame.draw.circle(surf, (r, g, b, alpha), (d // 2, d // 2), radius)
        if radius > 1:      # soft halo so the flake doesn't look like a dot
            pygame.draw.circle(surf, (r, g, b, alpha // 3), (d // 2, d // 2), radius + 1, 1)
        spr = _SPRITES[key] = _convert(surf)
    return spr


class RainParticle:
    def __init__(self):
        self.reset()

    def reset(self, start_y=None):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, SCREEN_HEIGHT) if start_y is None else -random.randint(0, 50)
        self.length = random.randint(8, 18)
        self.speed = random.uniform(8, 16)
        self.alpha = random.randint(90, 180)

    def update(self):
        self.y += self.speed
        self.x -= self.speed * 0.3
        if self.y > SCREEN_HEIGHT + 20:
            self.reset(start_y=True)

    def render(self, surface, intensity=1.0):
        spr = _rain_sprite(self.length, _quantize(self.alpha * intensity))
        surface.blit(spr, (int(self.x) - spr.get_width() + 1, int(self.y)))


class SnowParticle:
    """A flake: falls slowly, sways sideways, and drifts with the city breeze."""

    def __init__(self):
        self.reset()
        self.y = random.randint(0, SCREEN_HEIGHT)

    def reset(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = -random.uniform(0, 60)
        self.size = random.uniform(1.4, 3.6)
        # Bigger flakes read as nearer, so they fall faster and brighter.
        self.speed = 0.7 + self.size * 0.55
        self.alpha = int(110 + self.size * 38)
        self.sway = random.uniform(0.25, 0.9)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.phase += 0.02 + self.sway * 0.01
        self.y += self.speed
        self.x += math.sin(self.phase) * self.sway - 0.45
        if self.y > SCREEN_HEIGHT + 8:
            self.reset()
        elif self.x < -8:
            self.x = SCREEN_WIDTH + 6

    def render(self, surface, intensity=1.0):
        spr = _snow_sprite(int(self.size), _quantize(self.alpha * intensity))
        d = spr.get_width() // 2
        surface.blit(spr, (int(self.x) - d, int(self.y) - d))
