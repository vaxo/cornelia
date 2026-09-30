import pygame
from src.screens.base_screen import BaseScreen
from src.screens.powerup_effects import PowerupEffectsMixin
from src.screens.character_voice import CharacterVoiceMixin
from src.entities.player_car import PlayerCar
from src.managers.background_manager import BackgroundManager
from src.managers.obstacle_manager import ObstacleManager
from src.managers.collision_manager import CollisionManager
from src.managers.score_manager import ScoreManager
from src.managers.difficulty_manager import DifficultyManager
from src.managers.weather_manager import WeatherManager
from src.managers.powerup_manager import PowerUpManager
from src.entities.particle import create_sparks
from src.ui.hud import HUD
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SHAKE_DURATION, SHAKE_INTENSITY,
    UI_TEXT,
)
import random


class EndlessScreen(CharacterVoiceMixin, PowerupEffectsMixin, BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self._setup()

    def _setup(self):
        model = self.save.selected_car
        color = self.save.selected_color
        self.car = PlayerCar(model, color)
        self.bg = BackgroundManager()
        self.obs_mgr = ObstacleManager()
        self.score_mgr = ScoreManager()
        self.diff_mgr = DifficultyManager()
        self.weather = WeatherManager(self.audio)
        self.hud = HUD(self.assets, mode="endless")
        self.powerup_mgr = PowerUpManager()
        self.init_effects()
        self.init_voice()
        self.particles = []
        self._shake_timer = 0
        self._started = False
        self._dead = False

    def on_enter(self, resume=False, **kwargs):
        # Resuming from pause must keep the run in progress (score, position,
        # obstacles). Only a fresh start rebuilds and resets everything.
        if resume:
            return
        self._setup()
        self.score_mgr.reset(best=self.save.high_score)
        self.obs_mgr.reset()
        self.diff_mgr.reset()
        self.powerup_mgr.reset(enabled=True)
        self.weather.randomize(instant=True)
        self.audio.play_music()

    def _get_shake(self):
        if self._shake_timer > 0:
            intensity = SHAKE_INTENSITY * (self._shake_timer / SHAKE_DURATION)
            return (random.randint(-int(intensity), int(intensity)),
                    random.randint(-int(intensity), int(intensity)))
        return (0, 0)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.USEREVENT + 1 and self._dead:
                self.game.scene.change(
                    "game_over",
                    score=self.score_mgr.get_score(),
                    best=self.score_mgr.get_best(),
                    mode="endless",
                )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self._dead:
                    self.game.scene.change("pause", from_screen="endless")
                if event.key == pygame.K_SPACE and not self._dead:
                    if not self._started:
                        self._started = True
                    self.car.move_up()
                # Fire a held helper (1=phase, 2=time slow, 3=2x score)
                if self._started and not self._dead:
                    self.activate_by_key(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self._dead:
                    if not self._started:
                        self._started = True
                    self.car.move_up()

    def update(self, dt):
        # Visuals that keep animating even during the death/idle pause
        if self._shake_timer > 0:
            self._shake_timer -= dt
        self.tick_effects(dt)
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        if not self._started or self._dead:
            return

        score = self.score_mgr.get_score()
        self.diff_mgr.update_endless(score)
        speed = self.diff_mgr.get_speed()
        gap = self.diff_mgr.get_gap()
        interval = self.diff_mgr.get_spawn_interval()
        use_moving = self.diff_mgr.has_moving_obstacles_endless(score)
        self.obs_mgr.set_params(gap, interval, use_moving)

        # The world's pace = this character's tempo x any slow-mo. Both the
        # scroll speed and the spawn cadence are scaled by it, so the layout
        # stays identical and only the time you get to read it changes.
        tempo = self.world_tempo()
        speed *= tempo

        self.bg.set_weather(self.weather.snow_level(), self.weather.overcast())
        self.bg.update(speed, dt)
        self.car.update(dt)
        self.tick_voice(dt, self.car)
        self.obs_mgr.update(dt, speed, tempo)
        self.powerup_mgr.update(dt, speed, self.obs_mgr)
        self.weather.update(dt)

        for kind in self.powerup_mgr.check_collect(self.car.rect):
            self.collect_powerup(kind)

        passed = self.obs_mgr.check_passed(self.car.x + self.car.w)
        for _ in range(passed):
            # Scoring a gate is silent on purpose - no chime on every pass
            self.score_mgr.on_pass(self.effect_score_mult() * self.car.tempo)

        if not self.is_invulnerable() and (
                CollisionManager.check_obstacle(self.car, self.obs_mgr) or
                CollisionManager.check_bounds(self.car)):
            self._on_death()

    def _on_death(self):
        if self._dead:
            return
        self._dead = True
        self._shake_timer = SHAKE_DURATION
        cx = int(self.car.x + self.car.w // 2)
        cy = int(self.car.y + self.car.h // 2)
        self.particles.extend(create_sparks(cx, cy, 60))
        self.flash((255, 190, 120), 260)
        self.audio.play_sfx("crash")
        self.save.update_high_score(self.score_mgr.get_score())
        pygame.time.set_timer(pygame.USEREVENT + 1, 1400, loops=1)

    def render(self, surface):
        shake = self._get_shake()
        self.bg.render(surface)
        self.weather.render(surface)
        self.obs_mgr.render(surface, shake)
        self.powerup_mgr.render(surface, shake)
        self.car.render(surface, shake)
        for p in self.particles:
            p.render(surface, shake)
        self.hud.render(
            surface,
            self.score_mgr.get_score(),
            self.score_mgr.get_best(),
            self.score_mgr.get_combo(),
        )
        self.render_effects(surface)
        if not self._started:
            hint = self.assets.render_text(
                "დასაწყებად დააჭირე SPACE ან დააკლიკე", 32, UI_TEXT
            )
            surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 100))
