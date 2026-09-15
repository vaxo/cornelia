import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from src.core.game_state import GameState
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_TEXT, UI_ACCENT, UI_GOLD, SKY_TOP,
    BTN_W, BTN_H, BTN_SPACING, TITLE_FONT_SIZE,
    SUBTITLE_FONT_SIZE, UI_TEXT_DIM,
)


class MainMenuScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 30

        self.buttons = [
            Button(cx, start_y,                    BTN_W, BTN_H, "უსასრულო რეჟიმი",   self.assets),
            Button(cx, start_y + BTN_SPACING,      BTN_W, BTN_H, "დონეები",           self.assets),
            Button(cx, start_y + BTN_SPACING * 2,  BTN_W, BTN_H, "პერსონაჟები",  self.assets),
            Button(cx, start_y + BTN_SPACING * 3,  BTN_W, BTN_H, "პარამეტრები",       self.assets),
            Button(cx, start_y + BTN_SPACING * 4,  BTN_W, BTN_H, "გასვლა",            self.assets),
        ]
        self._bg = self._make_bg()

    def _make_bg(self):
        import random
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(5 + 15 * t)
            g = int(8 + 20 * t)
            b = int(25 + 45 * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        for _ in range(200):
            sx = random.randint(0, SCREEN_WIDTH)
            sy = random.randint(0, SCREEN_HEIGHT)
            sb = random.randint(80, 200)
            surf.set_at((sx, sy), (sb, sb, min(255, sb + 30)))
        return surf

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
            for event in events:
                if btn.handle_event(event):
                    self.audio.play_sfx("click")
                    if btn.text == "უსასრულო რეჟიმი":
                        self.game.scene.change("endless")
                    elif btn.text == "დონეები":
                        self.game.scene.change("levels_menu")
                    elif btn.text == "პერსონაჟები":
                        self.game.scene.change("car_selection")
                    elif btn.text == "პარამეტრები":
                        self.game.scene.change("settings")
                    elif btn.text == "გასვლა":
                        self.game.running = False

    def update(self, dt):
        pass

    def render(self, surface):
        surface.blit(self._bg, (0, 0))

        # Decorative glow behind title
        glow = pygame.Surface((700, 120), pygame.SRCALPHA)
        glow.fill((80, 130, 255, 18))
        surface.blit(glow, (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 6 - 30))

        # Title
        title_surf = self.assets.render_text("CORNELIA", TITLE_FONT_SIZE, UI_GOLD, bold=True)
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        ty = SCREEN_HEIGHT // 6
        surface.blit(title_surf, (tx, ty))

        # Subtitle
        sub_surf = self.assets.render_text("ღამის ქალაქის სარბოლო", SUBTITLE_FONT_SIZE, UI_TEXT_DIM)
        sx = SCREEN_WIDTH // 2 - sub_surf.get_width() // 2
        surface.blit(sub_surf, (sx, ty + title_surf.get_height() + 4))

        # High score
        hs_text = f"საუკეთესო ქულა: {self.save.high_score}"
        hs_surf = self.assets.render_text(hs_text, SUBTITLE_FONT_SIZE, UI_ACCENT)
        hx = SCREEN_WIDTH // 2 - hs_surf.get_width() // 2
        surface.blit(hs_surf, (hx, ty + title_surf.get_height() + 44))

        for btn in self.buttons:
            btn.render(surface)
