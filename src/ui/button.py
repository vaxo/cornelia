import pygame
from config.constants import (
    UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_BORDER,
    UI_WHITE, BTN_FONT_SIZE,
)


class Button:
    def __init__(self, x, y, w, h, text, asset_manager, font_size=None, center=True):
        self.w = w
        self.h = h
        self.text = text
        self.assets = asset_manager
        self.font_size = font_size or BTN_FONT_SIZE
        self.hovered = False
        if center:
            self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        else:
            self.rect = pygame.Rect(x, y, w, h)
        self._anim = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self._anim = min(1.0, self._anim + 0.12)
        else:
            self._anim = max(0.0, self._anim - 0.10)

    def render(self, surface):
        scale = 1.0 + self._anim * 0.03
        w = int(self.rect.width * scale)
        h = int(self.rect.height * scale)
        rx = self.rect.centerx - w // 2
        ry = self.rect.centery - h // 2

        # Shadow
        shadow = pygame.Rect(rx + 3, ry + 4, w, h)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=10)

        col = UI_BUTTON_HOVER if self.hovered else UI_BUTTON
        pygame.draw.rect(surface, col, (rx, ry, w, h), border_radius=10)
        pygame.draw.rect(surface, UI_BUTTON_BORDER, (rx, ry, w, h), 2, border_radius=10)

        text_surf = self.assets.render_text(self.text, self.font_size, UI_WHITE, bold=False)
        tx = rx + (w - text_surf.get_width()) // 2
        ty = ry + (h - text_surf.get_height()) // 2
        surface.blit(text_surf, (tx, ty))
