import pygame
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT, UI_TEXT, UI_ACCENT


class UIManager:
    def __init__(self, asset_manager):
        self.assets = asset_manager

    def draw_text_centered(self, surface, text, size, color, cy, bold=False):
        surf = self.assets.render_text(text, size, color, bold)
        x = (SCREEN_WIDTH - surf.get_width()) // 2
        surface.blit(surf, (x, cy))
        return surf.get_height()

    def draw_text(self, surface, text, size, color, x, y, bold=False):
        surf = self.assets.render_text(text, size, color, bold)
        surface.blit(surf, (x, y))
        return surf.get_width(), surf.get_height()

    def draw_panel(self, surface, cx, cy, w, h, color, border_color=None, alpha=220):
        rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((*color[:3], alpha))
        surface.blit(panel, rect.topleft)
        if border_color:
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=14)
        return rect

    def draw_progress_bar(self, surface, x, y, w, h, progress, fg, bg, border=None):
        pygame.draw.rect(surface, bg, (x, y, w, h), border_radius=h // 2)
        fill = max(0, int(w * progress))
        if fill:
            pygame.draw.rect(surface, fg, (x, y, fill, h), border_radius=h // 2)
        if border:
            pygame.draw.rect(surface, border, (x, y, w, h), 2, border_radius=h // 2)
