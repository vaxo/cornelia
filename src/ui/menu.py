import pygame
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_BG, UI_PANEL,
    UI_TEXT, UI_ACCENT, TITLE_FONT_SIZE,
)


class MenuBase:
    def __init__(self, asset_manager):
        self.assets = asset_manager
        self.buttons = []
        self._overlay = self._make_overlay()

    def _make_overlay(self):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((*UI_BG, 210))
        return s

    def _draw_panel(self, surface, cx, cy, w, h):
        rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        pygame.draw.rect(surface, UI_PANEL, rect, border_radius=16)
        pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=16)

    def _draw_title(self, surface, text, cy, size=None):
        s = size or TITLE_FONT_SIZE
        surf = self.assets.render_text(text, s, UI_TEXT, bold=True)
        surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, cy))

    def handle_events(self, events):
        results = {}
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
            for event in events:
                if btn.handle_event(event):
                    results[btn.text] = True
        return results

    def render_buttons(self, surface):
        for btn in self.buttons:
            btn.render(surface)
