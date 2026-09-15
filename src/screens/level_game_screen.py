import pygame
import math
from src.screens.base_screen import BaseScreen
from src.screens.powerup_effects import PowerupEffectsMixin
from src.entities.player_car import PlayerCar
from src.managers.background_manager import BackgroundManager
from src.managers.obstacle_manager import ObstacleManager
from src.managers.collision_manager import CollisionManager
from src.managers.score_manager import ScoreManager
from src.managers.difficulty_manager import DifficultyManager
from src.managers.level_manager import LevelManager
from src.managers.weather_manager import WeatherManager
from src.managers.powerup_manager import PowerUpManager
from src.entities.particle import create_sparks
from src.ui.hud import HUD
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SHAKE_DURATION, SHAKE_INTENSITY,
    UI_TEXT, UI_GOLD, UI_ACCENT, UI_GREEN,
)
import random


TUNNEL_W = 180
TUNNEL_H = SCREEN_HEIGHT


class LevelGameScreen(PowerupEffectsMixin, BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.level_mgr = LevelManager(game.save)
        self._current_level = 1
        self._tunnel_surf = self._make_tunnel_surf()
        self._finish_label = self.assets.render_text("ფინიში!", 36, (255, 220, 80), bold=True)
        self._setup()

    def _make_tunnel_surf(self):
        surf = pygame.Surface((TUNNEL_W, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.fill((40, 45, 55, 255))
        glow_w = TUNNEL_W - 20
        for i in range(20):
            alpha = int(40 * (1 - i / 20))
            glow = pygame.Surface((glow_w, SCREEN_HEIGHT - 10), pygame.SRCALPHA)
            glow.fill((255, 220, 80, alpha))
            surf.blit(glow, (10 - i, 5))
        center = pygame.Surface((TUNNEL_W - 60, SCREEN_HEIGHT - 20), pygame.SRCALPHA)
        center.fill((255, 230, 120, 90))
        surf.blit(center, (30, 10))
        return surf

    def _setup(self):
        model = self.save.selected_car
        color = self.save.selected_color
        self.car = PlayerCar(model, color)
        self.bg = BackgroundManager(day=self.save.settings.day_mode)
        self.obs_mgr = ObstacleManager()
        self.score_mgr = ScoreManager()
        self.diff_mgr = DifficultyManager()
        self.weather = WeatherManager(self.audio)
        self.hud = HUD(self.assets, mode="level")
        self.powerup_mgr = PowerUpManager()
        self.init_effects()
        self.particles = []
        self._shake_timer = 0
        self._started = False
        self._dead = False
        self._finished = False
        self._tunnel_x = float(SCREEN_WIDTH + 100)
        self._finish_shown = False
        self._entry_anim = 0.0

    def on_enter(self, level=1, resume=False, **kwargs):
        # Resuming from pause keeps the in-progress run; only a fresh start resets.
        if resume:
            return
        self._current_level = level
        self._setup()
        data = self.level_mgr.get_level_data(level)
        self.level_mgr.load_level(level)
        gap = data.get("gap", 265)
        interval = data.get("spawn_interval", 2100)
        speed = data.get("speed", 4.5)
        use_moving = data.get("moving_obstacles", False)
        self.diff_mgr.reset(speed=speed, gap=gap, interval=interval)
        self.obs_mgr.reset(gap=gap, spawn_interval=interval, use_moving=use_moving)
        self.score_mgr.reset(best=self.save.high_score)
        self.powerup_mgr.reset(enabled=True)
        self.weather.randomize()
        self.audio.play_music()

    def _get_shake(self):
        if self._shake_timer > 0:
            intensity = SHAKE_INTENSITY * (self._shake_timer / SHAKE_DURATION)
            return (random.randint(-int(intensity), int(intensity)),
                    random.randint(-int(intensity), int(intensity)))
        return (0, 0)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.USEREVENT + 2 and self._dead:
                self.game.scene.change(
                    "game_over",
                    score=self.score_mgr.get_score(),
                    best=self.score_mgr.get_best(),
                    mode="level",
                    level=self._current_level,
                )
            if event.type == pygame.USEREVENT + 3 and self._finished:
                self.game.scene.change(
                    "level_complete",
                    score=self.score_mgr.get_score(),
                    best=self.score_mgr.get_best(),
                    level=self._current_level,
                )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self._dead and not self._finished:
                    self.game.scene.change("pause", from_screen="level_game", level=self._current_level)
                if event.key == pygame.K_SPACE and not self._dead and not self._finished:
                    if not self._started:
                        self._started = True
                    self.car.move_up()
                # Fire a held helper (1=phase, 2=time slow, 3=2x score)
                if self._started and not self._dead and not self._finished:
                    self.activate_by_key(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self._dead and not self._finished:
                    if not self._started:
                        self._started = True
                    self.car.move_up()

    def update(self, dt):
        # Visuals that keep animating even during the death/finish pause
        if self._shake_timer > 0:
            self._shake_timer -= dt
        self.tick_effects(dt)
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        if not self._started or self._dead or self._finished:
            return

        speed = self.diff_mgr.get_speed() * self.effect_speed_mult()

        self.bg.update(speed)
        self.car.update(dt)
        self.obs_mgr.update(dt, speed, self.effect_speed_mult())
        self.powerup_mgr.update(dt, speed, self.obs_mgr)
        self.weather.update(dt)

        for kind in self.powerup_mgr.check_collect(self.car.rect):
            self.collect_powerup(kind)

        self.level_mgr.advance_distance(speed)
        progress = self.level_mgr.get_progress()

        # Show tunnel when ~90% done
        if progress >= 0.9 and not self._finish_shown:
            self._finish_shown = True
            self._tunnel_x = float(SCREEN_WIDTH + TUNNEL_W)

        if self._finish_shown:
            self._tunnel_x -= speed
            # Car enters tunnel
            if self.car.x + self.car.w >= self._tunnel_x - 10:
                self._on_finish()
                return

        passed = self.obs_mgr.check_passed(self.car.x + self.car.w)
        for _ in range(passed):
            self.score_mgr.on_pass(self.effect_score_mult())
            self.audio.play_sfx("score")

        if not self.is_invulnerable() and (
                CollisionManager.check_obstacle(self.car, self.obs_mgr) or
                CollisionManager.check_bounds(self.car)):
            self._on_death()

    def _on_death(self):
        self._dead = True
        self._shake_timer = SHAKE_DURATION
        cx = int(self.car.x + self.car.w // 2)
        cy = int(self.car.y + self.car.h // 2)
        self.particles.extend(create_sparks(cx, cy, 60))
        self.flash((255, 190, 120), 260)
        self.audio.play_sfx("crash")
        self.save.update_high_score(self.score_mgr.get_score())
        pygame.time.set_timer(pygame.USEREVENT + 2, 1400, loops=1)

    def _on_finish(self):
        self._finished = True
        self.level_mgr.unlock_next()
        self.save.update_high_score(self.score_mgr.get_score())
        pygame.time.set_timer(pygame.USEREVENT + 3, 1200, loops=1)

    def _draw_tunnel(self, surface, shake):
        if not self._finish_shown:
            return
        tx = int(self._tunnel_x) + shake[0]
        surface.blit(self._tunnel_surf, (tx, 0))
        pygame.draw.arc(surface, (255, 220, 80),
                        (tx - 10, -20, TUNNEL_W + 20, 120), 0, math.pi, 5)
        lw = self._finish_label.get_width()
        surface.blit(self._finish_label, (tx + TUNNEL_W // 2 - lw // 2, SCREEN_HEIGHT // 2 - 30))

    def render(self, surface):
        shake = self._get_shake()
        self.bg.render(surface)
        self._draw_tunnel(surface, shake)
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
            level=self._current_level,
            progress=self.level_mgr.get_progress(),
        )
        self.render_effects(surface)

        if not self._started:
            hint = self.assets.render_text(
                "დასაწყებად დააჭირე SPACE ან დააკლიკე", 32, UI_TEXT
            )
            surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 100))
