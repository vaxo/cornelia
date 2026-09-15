import pygame


class Label:
    def __init__(self, x, y, text, font_size, color, asset_manager, center=True, bold=False):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = color
        self.assets = asset_manager
        self.center = center
        self.bold = bold

    def render(self, surface, text=None):
        txt = text if text is not None else self.text
        surf = self.assets.render_text(txt, self.font_size, self.color, self.bold)
        if self.center:
            x = self.x - surf.get_width() // 2
            y = self.y - surf.get_height() // 2
        else:
            x, y = self.x, self.y
        surface.blit(surf, (x, y))
