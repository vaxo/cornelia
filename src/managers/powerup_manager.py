import random
from config.constants import SCREEN_WIDTH
from src.entities.powerup import PowerUp, TYPES


class PowerUpManager:
    """Spawns power-ups INSIDE obstacle gaps so they're always reachable.

    A power-up is attached to an upcoming obstacle's gap and rides along in the
    safe passage — the player collects it by threading that gap, never by
    crashing into a wall.
    """

    def __init__(self):
        self.items = []
        self._timer = 0.0
        self._interval = 5500.0
        self._enabled = True

    def reset(self, enabled=True, interval=5500):
        self.items.clear()
        self._timer = 0.0
        self._interval = interval
        self._enabled = enabled

    def update(self, dt, speed, obstacle_manager=None):
        if self._enabled and obstacle_manager is not None:
            self._timer += dt
            if self._timer >= self._interval:
                # Keep trying each frame until an obstacle is available, so a
                # helper reliably appears (important for the level quests).
                if self._try_attach(obstacle_manager):
                    self._timer = 0.0
        for p in self.items:
            p.update(dt, speed)
        self.items = [p for p in self.items if not p.is_offscreen() and not p.collected]

    def _try_attach(self, obstacle_manager):
        # Attach to the newest obstacle that is still far enough to the right
        # that the player has time to line up for the gap.
        candidates = [o for o in obstacle_manager.obstacles
                      if o.x > SCREEN_WIDTH * 0.55 and not getattr(o, "_has_powerup", False)]
        if not candidates:
            return False
        obstacle = max(candidates, key=lambda o: o.x)
        obstacle._has_powerup = True
        kind = random.choices(TYPES, weights=[3, 2, 3])[0]
        self.items.append(PowerUp(kind, obstacle))
        return True

    def check_collect(self, car_rect):
        """Return list of kinds collected this frame (and mark them consumed)."""
        collected = []
        for p in self.items:
            if not p.collected and car_rect.colliderect(p.rect):
                p.collected = True
                collected.append(p.kind)
        return collected

    def render(self, surface, shake=(0, 0)):
        for p in self.items:
            p.render(surface, shake)
