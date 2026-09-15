import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from src.ui.icons import draw_star
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BTN_W, BTN_H, BTN_SPACING,
    UI_TEXT, UI_GOLD, UI_ACCENT, UI_RED, UI_PANEL, UI_TEXT_DIM,
)


class GameOverScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 30
        self._score = 0
        self._best = 0
        self._mode = "endless"
        self._level = 1
        self.buttons_endless = [
            Button(cx, cy + 20,              BTN_W, BTN_H, "თავიდან",       self.assets),
            Button(cx, cy + 20 + BTN_SPACING, BTN_W, BTN_H, "მთავარი მენიუ", self.assets),
        ]
        self.buttons_level = [
            Button(cx, cy + 20,                  BTN_W, BTN_H, "თავიდან დონე",  self.assets),
            Button(cx, cy + 20 + BTN_SPACING,    BTN_W, BTN_H, "ხელახლა",        self.assets),
            Button(cx, cy + 20 + BTN_SPACING * 2, BTN_W, BTN_H, "მთავარი მენიუ", self.assets),
        ]

    def on_enter(self, score=0, best=0, mode="endless", level=1, **kwargs):
        self._score = score
        self._best = best
        self._mode = mode
        self._level = level

    def _get_buttons(self):
        return self.buttons_level if self._mode == "level" else self.buttons_endless

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._get_buttons():
            btn.update(mouse_pos)
        for event in events:
            for btn in self._get_buttons():
                if btn.handle_event(event):
                    self.audio.play_sfx("click")
                    if btn.text in ("თავიდან", "ხელახლა", "თავიდან დონე"):
                        if self._mode == "level":
                            self.game.scene.change("level_game", level=self._level)
                        else:
                            self.game.scene.change("endless")
                    elif btn.text == "მთავარი მენიუ":
                        self.game.scene.change("main_menu")

    def render(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, 200))
        surface.blit(overlay, (0, 0))

        pw, ph = 700, 520 if self._mode == "level" else 400
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2 - 20
        pygame.draw.rect(surface, UI_PANEL, (px, py, pw, ph), border_radius=16)
        pygame.draw.rect(surface, UI_RED, (px, py, pw, ph), 2, border_radius=16)

        # Title
        title = self.assets.render_text("თამაში დასრულდა", 58, UI_RED, bold=True)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 28))

        # Score
        score_txt = self.assets.render_text(f"ქულა: {self._score}", 50, UI_TEXT, bold=True)
        surface.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, py + 110))

        # Best
        new_best = self._score >= self._best and self._score > 0
        best_col = UI_GOLD if new_best else UI_TEXT_DIM
        best_label = "ახალი რეკორდი!" if new_best else f"საუკეთესო: {self._best}"
        best_txt = self.assets.render_text(best_label, 36, best_col)
        bx = SCREEN_WIDTH // 2 - best_txt.get_width() // 2
        surface.blit(best_txt, (bx, py + 170))
        if new_best:
            draw_star(surface, bx - 26, py + 188, 16, UI_GOLD)
            draw_star(surface, bx + best_txt.get_width() + 26, py + 188, 16, UI_GOLD)

        for btn in self._get_buttons():
            btn.render(surface)
