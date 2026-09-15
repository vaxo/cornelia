"""Resolution-independent, DPI-crisp display.

The game is authored at a fixed logical resolution (1920x1080). We use
``pygame.SCALED`` so SDL renders at the display's *native* (Retina/physical)
resolution and GPU-scales the logical frame to fit — sharp, not the soft result
you get from manually downscaling into a low-DPI window. SCALED also maps mouse
events into logical coordinates for us, so hit-testing needs no adjustment.

On desktops smaller than 1920x1080 (e.g. a Retina MacBook's 1470x956 *points*)
a SCALED *window* would overflow, so we automatically go fullscreen there.

Scenes draw onto an off-screen 24-bit canvas (no alpha channel, so translucent
effects — sun glow, clouds, fog, rain, lightning, menu glows — blend into opaque
pixels instead of punching holes). Each frame the canvas is blitted to the
display surface, post-processed (bloom + vignette), and flipped.
"""
import pygame


class Display:
    def __init__(self, logical_w, logical_h, fullscreen=False):
        self.lw = logical_w
        self.lh = logical_h
        self.fullscreen = fullscreen

        # Post-processing (bloom + vignette) — OFF: it softens the image.
        self.bloom_enabled = False
        self._bloom_small = (logical_w // 5, logical_h // 5)
        self._vignette = self._make_vignette(logical_w, logical_h)

        self._build()
        self.canvas = pygame.Surface((logical_w, logical_h), 0, 24)

    def _make_vignette(self, w, h):
        import math
        vw, vh = 128, 72
        vs = pygame.Surface((vw, vh), 0, 24)
        cx, cy = vw / 2, vh / 2
        maxd = math.hypot(cx, cy)
        for yy in range(vh):
            for xx in range(vw):
                d = math.hypot(xx - cx, yy - cy) / maxd
                val = int(80 * max(0.0, (d - 0.38) / 0.62) ** 1.4)
                vs.set_at((xx, yy), (val, val, val))
        return pygame.transform.smoothscale(vs, (w, h))

    def _desktop_size(self):
        try:
            return pygame.display.get_desktop_sizes()[0]
        except Exception:
            info = pygame.display.Info()
            return (info.current_w or self.lw, info.current_h or self.lh)

    def _build(self):
        dw, dh = self._desktop_size()
        # Force fullscreen when a 1920x1080 window wouldn't fit the desktop.
        want_fullscreen = self.fullscreen or dw < self.lw or dh < self.lh
        flags = pygame.SCALED | pygame.DOUBLEBUF
        if want_fullscreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((self.lw, self.lh), flags)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._build()
        return self.fullscreen

    def present(self):
        """Blit the canvas to the display, post-process, and flip."""
        self.screen.blit(self.canvas, (0, 0))
        if self.bloom_enabled:
            self._post_inplace(self.screen)
        pygame.display.flip()

    def _post_inplace(self, surf):
        small = pygame.transform.smoothscale(surf, self._bloom_small)
        small.fill((92, 92, 92), special_flags=pygame.BLEND_RGB_SUB)       # keep bright areas
        small.fill((175, 175, 175), special_flags=pygame.BLEND_RGB_MULT)   # ease intensity
        bloom = pygame.transform.smoothscale(small, (self.lw, self.lh))    # smooth (no pixel blocks)
        surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(self._vignette, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

    def to_logical(self, pos):
        # SCALED already delivers mouse coordinates in logical space.
        return pos
