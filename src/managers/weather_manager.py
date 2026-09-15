import pygame
import random
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, RAIN_COUNT,
    FOG_ALPHA, LIGHTNING_FLASH_DURATION,
)
from src.entities.particle import RainParticle


class WeatherManager:
    TYPES = ["clear", "rain", "fog", "storm"]

    def __init__(self, audio_manager=None):
        self.audio = audio_manager
        self.current = "clear"
        self._rain = [RainParticle() for _ in range(RAIN_COUNT)]
        self._lightning_timer = 0
        self._lightning_alpha = 0
        self._next_lightning = random.randint(3000, 8000)
        self._change_timer = random.randint(8000, 20000)
        self._fog_surf = self._make_fog()
        self._rain_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def _make_fog(self):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((100, 110, 140, FOG_ALPHA))
        return s

    def randomize(self):
        weights = [35, 30, 20, 15]
        self.current = random.choices(self.TYPES, weights=weights)[0]

    def update(self, dt):
        self._change_timer -= dt
        if self._change_timer <= 0:
            self.randomize()
            self._change_timer = random.randint(10000, 25000)

        if self.current in ("rain", "storm"):
            for drop in self._rain:
                drop.update()

        # Lightning during any rainy weather (rain or storm); storms strike more
        # often than light rain.
        if self.current in ("rain", "storm"):
            self._next_lightning -= dt
            if self._next_lightning <= 0:
                self.trigger_lightning()
                if self.current == "storm":
                    self._next_lightning = random.randint(2000, 6000)
                else:  # lighter, occasional flashes in plain rain
                    self._next_lightning = random.randint(5000, 12000)

        if self._lightning_timer > 0:
            self._lightning_timer -= dt
            ratio = self._lightning_timer / LIGHTNING_FLASH_DURATION
            self._lightning_alpha = int(120 * ratio)

    def trigger_lightning(self):
        self._lightning_timer = LIGHTNING_FLASH_DURATION
        self._lightning_alpha = 120
        if self.audio:
            self.audio.play_sfx("thunder")

    def render(self, surface):
        if self.current in ("rain", "storm"):
            self._rain_surf.fill((0, 0, 0, 0))
            for drop in self._rain:
                drop.render(self._rain_surf)
            surface.blit(self._rain_surf, (0, 0))

        if self.current in ("fog", "storm"):
            surface.blit(self._fog_surf, (0, 0))

        if self._lightning_alpha > 0:
            self._flash_surf.fill((200, 210, 255, self._lightning_alpha))
            surface.blit(self._flash_surf, (0, 0))
