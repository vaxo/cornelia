import pygame
import random
import math
from config.constants import SPARK_COLORS, RAIN_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT
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

    def render(self, surface, wind=0):
        end_x = int(self.x - self.length * 0.3 + wind)
        end_y = int(self.y + self.length)
        try:
            r, g, b = RAIN_COLOR
            pygame.draw.line(
                surface, (r, g, b, self.alpha),
                (int(self.x), int(self.y)),
                (end_x, end_y), 1,
            )
        except Exception:
            pygame.draw.line(
                surface, RAIN_COLOR,
                (int(self.x), int(self.y)),
                (end_x, end_y), 1,
            )
