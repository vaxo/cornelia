"""Shared power-up ("helper") state for the gameplay screens.

Mixed into EndlessScreen and LevelGameScreen so both handle collecting and
using helpers identically.

Helpers are NOT used the moment you pick them up. Collecting one drops it into
your inventory; you fire it yourself with a keyboard key, when you actually
need it:

  * [1] phase     — a few seconds of invulnerability; you pass straight THROUGH
                    obstacles (great for a tight run of gates)
  * [2] time slow — temporarily slows the whole world down
  * [3] 2x score  — temporarily doubles points

You can stock more than one of each and set them off whenever you like.
Timers are driven by dt (not wall-clock) so they correctly freeze on pause.
"""
import pygame
from config.constants import SCREEN_HEIGHT, UI_WHITE, UI_TEXT_DIM
from src.entities.powerup import COLORS, TYPES
from src.ui.icons import draw_shield, draw_clock, draw_star

# Keyboard keys that fire each helper.
HELPER_KEYS = {
    pygame.K_1: "shield",
    pygame.K_2: "slowmo",
    pygame.K_3: "score2x",
}
# Number shown next to each helper's icon (the key you press).
KEY_LABEL = {"shield": "1", "slowmo": "2", "score2x": "3"}
# Short name shown under each helper (the on-screen key legend).
NAME_LABEL = {"shield": "ფაზა", "slowmo": "შენელება", "score2x": "x2 ქულა"}
INV_MAX = 9  # how many of one helper you can stockpile


class PowerupEffectsMixin:
    PHASE_MS = 2800       # invulnerable "phase through obstacles" window
    SLOWMO_MS = 4000
    SCORE2X_MS = 6000
    INVULN_MS = 1300
    FLASH_MS = 400
    SLOWMO_FACTOR = 0.55
    TEMPO_FLOOR = 0.45    # slowest the world may ever run (character x slow-mo)

    def init_effects(self):
        # Held helpers, fired on keypress (not auto-used on pickup).
        self.inventory = {k: 0 for k in TYPES}
        self.slowmo_timer = 0.0
        self.score2x_timer = 0.0
        self.invuln_timer = 0.0
        self._flash_timer = 0.0
        self._flash_max = self.FLASH_MS
        self._flash_color = (120, 200, 255)

    def flash(self, color, ms):
        self._flash_color = color
        self._flash_timer = ms
        self._flash_max = ms

    # ---- collecting & using -------------------------------------------
    def collect_powerup(self, kind):
        """Pick a helper up — store it, don't fire it."""
        if kind in self.inventory and self.inventory[kind] < INV_MAX:
            self.inventory[kind] += 1
        self.audio.play_sfx("powerup")

    def activate_by_key(self, key):
        """Fire the helper bound to `key`. Returns True if `key` is a helper key."""
        kind = HELPER_KEYS.get(key)
        if kind is None:
            return False
        self.activate_powerup(kind)
        return True

    def activate_powerup(self, kind):
        """Spend one held helper of `kind` and set its effect running."""
        if self.inventory.get(kind, 0) <= 0:
            return False
        self.inventory[kind] -= 1
        if kind == "shield":  # "phase": pass through obstacles for a while
            self.invuln_timer = max(self.invuln_timer, self.PHASE_MS)
            self.flash((120, 200, 255), self.FLASH_MS)
            self.audio.play_sfx("shield")
        elif kind == "slowmo":
            self.slowmo_timer = self.SLOWMO_MS
            self.audio.play_sfx("powerup")
        elif kind == "score2x":
            self.score2x_timer = self.SCORE2X_MS
            self.audio.play_sfx("powerup")
        return True

    def tick_effects(self, dt):
        for attr in ("slowmo_timer", "score2x_timer", "invuln_timer", "_flash_timer"):
            setattr(self, attr, max(0.0, getattr(self, attr) - dt))

    def effect_speed_mult(self):
        return self.SLOWMO_FACTOR if self.slowmo_timer > 0 else 1.0

    def world_tempo(self):
        """How fast the world runs right now: the character's own pace times any
        slow-mo, floored so the two can never stack into a crawl."""
        tempo = getattr(self.car, "tempo", 1.0) * self.effect_speed_mult()
        return max(self.TEMPO_FLOOR, tempo)

    def effect_score_mult(self):
        return 2 if self.score2x_timer > 0 else 1

    def is_invulnerable(self):
        return self.invuln_timer > 0

    # ---- rendering -----------------------------------------------------
    def _draw_helper_icon(self, surface, kind, cx, cy, col):
        if kind == "shield":
            draw_shield(surface, cx, cy, 26, col)
        elif kind == "slowmo":
            draw_clock(surface, cx, cy, 24, col)
        else:
            draw_star(surface, cx, cy, 14, col)

    def _active_timer(self, kind):
        if kind == "shield":
            return self.invuln_timer
        if kind == "slowmo":
            return self.slowmo_timer
        return self.score2x_timer

    def _draw_key_cap(self, surface, label, cx, top, col):
        """Little keyboard-cap badge showing which key fires this helper."""
        w, h = 30, 26
        rect = pygame.Rect(cx - w // 2, top, w, h)
        pygame.draw.rect(surface, (12, 16, 34), rect, border_radius=6)
        pygame.draw.rect(surface, col, rect, 2, border_radius=6)
        t = self.assets.render_text(label, 20, col, bold=True)
        surface.blit(t, (rect.centerx - t.get_width() // 2,
                         rect.centery - t.get_height() // 2))

    def render_effects(self, surface):
        # Bright flash (phase fired, or a crash)
        if self._flash_timer > 0:
            a = int(150 * (self._flash_timer / self._flash_max))
            fs = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            fs.fill((*self._flash_color, a))
            surface.blit(fs, (0, 0))

        # Helper legend + inventory along the bottom-left: one slot per helper,
        # always shown so the keys are learnable. Each slot = key cap, icon,
        # name, a count of how many you hold, and a live countdown when running.
        slot_w = 108
        x = 30
        y = SCREEN_HEIGHT - 108
        for kind in TYPES:
            count = self.inventory.get(kind, 0)
            timer = self._active_timer(kind)
            active = timer > 0
            col = COLORS[kind]
            has = count > 0 or active
            fg = col if has else UI_TEXT_DIM
            cx = x + 34
            cy = y + 54

            # Key cap at the top
            self._draw_key_cap(surface, KEY_LABEL[kind], cx, y, fg)

            # Icon disc; a bright ring while the effect is running
            pygame.draw.circle(surface, (18, 24, 48), (cx, cy), 26)
            pygame.draw.circle(surface, fg, (cx, cy), 26, 3 if has else 2)
            if active:
                pygame.draw.circle(surface, UI_WHITE, (cx, cy), 30, 2)
            self._draw_helper_icon(surface, kind, cx, cy, fg)

            # Name under the icon — this is the legend
            nm = self.assets.render_text(NAME_LABEL[kind], 18, fg, bold=True)
            surface.blit(nm, (cx - nm.get_width() // 2, cy + 30))

            if active:
                # Running: bright countdown badge at top-right of the disc
                secs = int(timer / 1000) + 1
                self._draw_corner_badge(surface, str(secs), cx + 22, cy - 22, col, UI_WHITE)
            elif count > 0:
                # Idle: how many you hold, at top-right of the disc
                self._draw_corner_badge(surface, str(count), cx + 22, cy - 22, col, UI_WHITE)
            x += slot_w

    def _draw_corner_badge(self, surface, text, cx, cy, ring, fg):
        pygame.draw.circle(surface, (12, 16, 34), (cx, cy), 14)
        pygame.draw.circle(surface, ring, (cx, cy), 14, 2)
        t = self.assets.render_text(text, 18, fg, bold=True)
        surface.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))
