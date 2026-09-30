import pygame
import random
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    OBSTACLE_MIN_Y_EDGE, OBSTACLE_MAX_Y_EDGE,
    REACHABLE_VSPEED, MIN_REACHABLE_DELTA, MOVING_AMPLITUDE_MARGIN,
)
from src.entities.obstacle import Obstacle
from src.entities.moving_obstacle import MovingObstacle


class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self._spawn_timer = 0.0
        self._spawn_interval = 2100.0
        self._gap = 265
        self._use_moving = False
        self._last_gap_y = None
        self._time_scale = 1.0

    def reset(self, gap=None, spawn_interval=None, use_moving=False):
        self.obstacles.clear()
        self._spawn_timer = 0.0
        self._last_gap_y = None
        if gap is not None:
            self._gap = gap
        if spawn_interval is not None:
            self._spawn_interval = spawn_interval
        self._use_moving = use_moving

    def set_params(self, gap, spawn_interval, use_moving):
        self._gap = gap
        self._spawn_interval = spawn_interval
        self._use_moving = use_moving

    def update(self, dt, game_speed, time_scale=1.0):
        self._time_scale = max(0.1, time_scale)
        # time_scale (<1 during slow-mo) also slows the spawn cadence and the
        # moving obstacles' bobbing, so the whole world slows together.
        self._spawn_timer += dt * time_scale
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer -= self._spawn_interval
            self._spawn()

        for obs in self.obstacles:
            obs.update(dt, game_speed, time_scale)

        self.obstacles = [o for o in self.obstacles if not o.is_offscreen()]

    def _spawn(self):
        x = SCREEN_WIDTH + 20
        moving = self._use_moving and random.random() < 0.4
        gap_y = self._pick_gap_y(moving)
        if moving:
            obs = MovingObstacle(x, self._gap, gap_y=gap_y)
        else:
            obs = Obstacle(x, self._gap, gap_y=gap_y)
        self.obstacles.append(obs)
        self._last_gap_y = gap_y

    def _reachable_delta(self):
        """Max vertical gap-to-gap jump the car can still make in time."""
        frame_ms = 1000.0 / FPS
        # The spawn timer advances at dt * time_scale, so the REAL time between
        # two gates is interval / time_scale. A fast character therefore gets
        # fewer frames to climb than the raw interval suggests - ignoring that
        # would hand it jumps it cannot make.
        frames_between = self._spawn_interval / self._time_scale / frame_ms
        return max(MIN_REACHABLE_DELTA, REACHABLE_VSPEED * frames_between)

    def _pick_gap_y(self, moving):
        """Choose the next gap centre so it's always reachable from the last one.

        The full valid band keeps the gap on-screen; for a moving obstacle we
        pull the edges in so its oscillation can't shove the gap off-screen. The
        new centre is then kept within _reachable_delta of the previous gap.
        """
        half = self._gap // 2
        low = OBSTACLE_MIN_Y_EDGE + half
        high = SCREEN_HEIGHT - OBSTACLE_MAX_Y_EDGE - half
        if moving:
            low += MOVING_AMPLITUDE_MARGIN
            high -= MOVING_AMPLITUDE_MARGIN
        if low > high:                       # gap almost as tall as the screen
            low = high = (low + high) // 2
        if self._last_gap_y is None:
            return random.randint(int(low), int(high))
        delta = self._reachable_delta()
        lo = max(low, self._last_gap_y - delta)
        hi = min(high, self._last_gap_y + delta)
        if lo > hi:                          # previous gap sat outside this band
            lo, hi = low, high
        return random.randint(int(lo), int(hi))

    def check_passed(self, car_x):
        count = 0
        for obs in self.obstacles:
            if obs.check_passed(car_x):
                count += 1
        return count

    def get_rects(self):
        rects = []
        for obs in self.obstacles:
            rects.append(obs.rect_top)
            rects.append(obs.rect_bot)
        return rects

    def render(self, surface, shake=(0, 0)):
        for obs in self.obstacles:
            obs.render(surface, shake)

    def clear(self):
        self.obstacles.clear()
