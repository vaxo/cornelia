"""Weather: rain, fog, storm and snow, held for long stretches and crossfaded.

Weather is not a switch. Each *effect* (rain, fog, snow) has its own intensity
that eases toward the target the current weather asks for, so a change reads as
the rain thinning out while the snow starts drifting in - never as a pop. A kind
of weather holds for WEATHER_HOLD_MIN..MAX ms before the next one is picked.

The intensities are also what the rest of the game reads: the background uses
``snow_level()`` to fade in the rooftop christmas trees and the snow caps, and
``overcast()`` to thicken the clouds.
"""
import pygame
import random
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, RAIN_COUNT, SNOW_COUNT,
    FOG_ALPHA, LIGHTNING_FLASH_DURATION,
    WEATHER_HOLD_MIN, WEATHER_HOLD_MAX, WEATHER_FADE_MS,
)
from src.entities.particle import RainParticle, SnowParticle

# How strongly each kind of weather drives each effect. Storm = heavy rain with
# some murk; snow brings a light haze with it.
MIX = {
    "clear": {"rain": 0.0, "fog": 0.0,  "snow": 0.0},
    "rain":  {"rain": 0.7, "fog": 0.1,  "snow": 0.0},
    "storm": {"rain": 1.0, "fog": 0.55, "snow": 0.0},
    "fog":   {"rain": 0.0, "fog": 1.0,  "snow": 0.0},
    "snow":  {"rain": 0.0, "fog": 0.25, "snow": 1.0},
}
EFFECTS = ("rain", "fog", "snow")


class WeatherManager:
    TYPES = ["clear", "rain", "fog", "storm", "snow"]
    WEIGHTS = [28, 22, 14, 12, 24]

    def __init__(self, audio_manager=None):
        self.audio = audio_manager
        self.current = "clear"
        self._level = {k: 0.0 for k in EFFECTS}
        self._rain = [RainParticle() for _ in range(RAIN_COUNT)]
        self._snow = [SnowParticle() for _ in range(SNOW_COUNT)]
        self._lightning_timer = 0
        self._lightning_alpha = 0
        self._next_lightning = random.randint(4000, 9000)
        self._change_timer = random.randint(WEATHER_HOLD_MIN, WEATHER_HOLD_MAX)
        self._fog_surf = self._new_fullscreen()
        self._fog_alpha = -1          # baked alpha of _fog_surf, -1 = nothing yet
        self._flash_surf = self._new_fullscreen()
        self._flash_alpha = -1

    @staticmethod
    def _new_fullscreen():
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        try:
            return s.convert_alpha()
        except pygame.error:
            return s

    # -- state -----------------------------------------------------------
    def randomize(self, instant=False):
        """Pick the next weather. *instant* snaps the effects to it (used when a
        run starts, so you don't watch the opening weather fade in)."""
        choices = [t for t in self.TYPES if t != self.current] or self.TYPES
        weights = [self.WEIGHTS[self.TYPES.index(t)] for t in choices]
        self.current = random.choices(choices, weights=weights)[0]
        if instant:
            for k in EFFECTS:
                self._level[k] = MIX[self.current][k]

    def snow_level(self):
        return self._level["snow"]

    def overcast(self):
        """How heavy the sky looks - drives the cloud density."""
        return max(self._level["rain"], self._level["fog"], self._level["snow"])

    # -- loop ------------------------------------------------------------
    def update(self, dt):
        self._change_timer -= dt
        if self._change_timer <= 0:
            self.randomize()
            self._change_timer = random.randint(WEATHER_HOLD_MIN, WEATHER_HOLD_MAX)

        # Ease every effect toward what the current weather wants.
        step = dt / float(WEATHER_FADE_MS)
        target = MIX[self.current]
        for k in EFFECTS:
            cur = self._level[k]
            want = target[k]
            if cur < want:
                self._level[k] = min(want, cur + step)
            elif cur > want:
                self._level[k] = max(want, cur - step)

        rain, snow = self._level["rain"], self._level["snow"]
        if rain > 0.01:
            for drop in self._rain[:int(RAIN_COUNT * rain)]:
                drop.update()
        if snow > 0.01:
            for flake in self._snow[:int(SNOW_COUNT * snow)]:
                flake.update()

        # Lightning only once the rain is actually falling.
        if rain > 0.45 and self.current in ("rain", "storm"):
            self._next_lightning -= dt
            if self._next_lightning <= 0:
                self.trigger_lightning()
                if self.current == "storm":
                    self._next_lightning = random.randint(2500, 7000)
                else:
                    self._next_lightning = random.randint(6000, 14000)

        if self._lightning_timer > 0:
            self._lightning_timer -= dt
            ratio = self._lightning_timer / LIGHTNING_FLASH_DURATION
            self._lightning_alpha = max(0, int(120 * ratio))

    def trigger_lightning(self):
        self._lightning_timer = LIGHTNING_FLASH_DURATION
        self._lightning_alpha = 120
        if self.audio:
            self.audio.play_sfx("thunder")

    def render(self, surface):
        rain, fog, snow = self._level["rain"], self._level["fog"], self._level["snow"]

        # Particles go straight onto the frame as small pre-rendered sprites -
        # no full-screen overlay to clear and composite.
        if rain > 0.01:
            for drop in self._rain[:int(RAIN_COUNT * rain)]:
                drop.render(surface, intensity=rain)
        if snow > 0.01:
            for flake in self._snow[:int(SNOW_COUNT * snow)]:
                flake.render(surface, intensity=snow)

        if fog > 0.01:
            # Bake the alpha into the surface and only re-fill it when the level
            # has actually moved: set_alpha would force the slow blit path.
            a = int(FOG_ALPHA * fog)
            if a != self._fog_alpha:
                self._fog_alpha = a
                self._fog_surf.fill((100, 110, 140, a))
            surface.blit(self._fog_surf, (0, 0))

        if self._lightning_alpha > 0:
            if self._lightning_alpha != self._flash_alpha:
                self._flash_alpha = self._lightning_alpha
                self._flash_surf.fill((200, 210, 255, self._lightning_alpha))
            surface.blit(self._flash_surf, (0, 0))
