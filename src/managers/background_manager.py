"""The scrolling night city: sky, drifting clouds, parallax buildings, ground.

Two things matter here for performance. Every building is rendered **once** into
its own surface (body, shading and all its windows baked in) and afterwards only
blitted - the old code re-drew every window rect of every building every frame,
which was thousands of draw calls. Clouds and christmas trees are likewise
pre-rendered sprites that are only blitted.

Buildings and clouds live in world coordinates and are drawn at ``x - scroll``;
anything that leaves the left edge is recycled to the right. Nothing off-screen
is drawn.
"""
import pygame
import random
import math
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SKY_TOP, SKY_BOT,
    BUILDING_FAR, BUILDING_MID, BUILDING_NEAR,
    WINDOW_GLOW, WINDOW_OFF, GROUND_COLOR, GROUND_LINE,
    CLOUD_BASE, CLOUD_LIT, CLOUD_COUNT, MOON_CORE, MOON_GLOW,
    SNOW_CAP, TREE_GREEN, TREE_GREEN_LIT, TREE_TRUNK, TREE_GLOW,
    TREE_STAR, TREE_BAUBLES, TREE_CHANCE,
)

GROUND_H = 52


def _lerp_color(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# --------------------------------------------------------------------------
# Rooftop christmas trees (pre-rendered, cached by height)
# --------------------------------------------------------------------------
_TREE_CACHE = {}


def _tree_sprites(height):
    """Return (body, glow) sprites for a rooftop tree *height* px tall.

    Two surfaces so the glowing outline can pulse and fade in with the snow
    independently of the tree itself - both are just blits with an alpha.
    """
    height = int(height)
    cached = _TREE_CACHE.get(height)
    if cached:
        return cached

    pad = 9
    half_base = max(7, int(height * 0.34))
    w = half_base * 2 + pad * 2
    h = height + pad * 2
    cx = w // 2
    trunk_h = max(3, int(height * 0.16))
    foliage_h = height - trunk_h
    base_y = pad + height

    # Three overlapping tiers, widest at the bottom.
    tiers = []
    for i in range(3):
        top_y = pad + int(foliage_h * (i * 0.30))
        bot_y = pad + int(foliage_h * (0.42 + i * 0.29))
        hw = int(half_base * (0.46 + i * 0.27))
        tiers.append([(cx, top_y), (cx - hw, bot_y), (cx + hw, bot_y)])

    body = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(body, TREE_TRUNK,
                     (cx - max(1, int(height * 0.05)), base_y - trunk_h,
                      max(2, int(height * 0.10)), trunk_h))
    for tri in tiers:
        pygame.draw.polygon(body, TREE_GREEN, tri)
        pygame.draw.polygon(body, TREE_GREEN_LIT, tri, 2)
    # Star on top + a few baubles.
    pygame.draw.circle(body, TREE_STAR, (cx, pad + 1), max(2, int(height * 0.08)))
    rng = random.Random(height)
    for i in range(4):
        tri = tiers[rng.randrange(1, 3)]
        x0, x1 = tri[1][0] + 2, tri[2][0] - 2
        y0, y1 = tri[0][1] + 3, tri[1][1] - 2
        if x1 <= x0 or y1 <= y0:        # tiny tree: no room for baubles
            continue
        pygame.draw.circle(body, TREE_BAUBLES[i % len(TREE_BAUBLES)],
                           (rng.randint(x0, x1), rng.randint(y0, y1)), 2)

    # Glowing border: the same silhouette stroked a few times, fat and faint
    # first, thin and bright last.
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for width, alpha in ((7, 34), (5, 60), (3, 100), (1, 170)):
        col = (TREE_GLOW[0], TREE_GLOW[1], TREE_GLOW[2], alpha)
        for tri in tiers:
            pygame.draw.polygon(glow, col, tri, width)
        pygame.draw.circle(glow, col, (cx, pad + 1),
                           max(3, int(height * 0.08)) + width // 2, max(1, width // 2))

    try:
        body, glow = body.convert_alpha(), glow.convert_alpha()
    except pygame.error:
        pass
    _TREE_CACHE[height] = (body, glow)
    return body, glow


# --------------------------------------------------------------------------
# Clouds
# --------------------------------------------------------------------------
def _make_cloud(w, h, rng):
    """One night cloud.

    Built the way a painter would: block in a solid, lumpy silhouette, blur it,
    then light it. The blur is a downscale/upscale round trip (pygame has no
    gaussian), which is what turns a pile of hard discs into vapour. Lighting is
    a vertical gradient multiplied over the white mask - moon-lit on top, dark
    in the belly - and a second vertical ramp fades the underside out so the
    cloud has no bottom edge. All of it happens once, at load.
    """
    sw, sh = w, h
    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    spine = int(sh * 0.66)

    # Lumpy silhouette: one blob per column, heights from an uneven profile.
    n = 12
    profile = [max(0.3, math.sin(math.pi * (i + 0.5) / n) ** 0.45 * rng.uniform(0.6, 1.2))
               for i in range(n)]
    for i, p in enumerate(profile):
        r = max(2, int(sh * 0.40 * p))
        cx = int(sw * (i + 0.5) / n + rng.uniform(-sw * 0.03, sw * 0.03))
        pygame.draw.circle(mask, (255, 255, 255, 255), (cx, spine - int(r * 0.45)), r)
        if p > 0.85:        # a billow on the tall columns
            rr = max(2, int(r * 0.62))
            pygame.draw.circle(mask, (255, 255, 255, 255),
                               (cx + int(rng.uniform(-r * 0.3, r * 0.3)),
                                spine - int(r * 1.05)), rr)
    # Flat base, the way cumulus sit on their condensation level.
    pygame.draw.ellipse(mask, (255, 255, 255, 255),
                        (int(sw * 0.04), spine - int(sh * 0.14),
                         int(sw * 0.92), int(sh * 0.30)))

    # Blur: two down/up round trips. pygame has no gaussian, and smoothscale's
    # bilinear filtering is a decent stand-in when you go far enough down.
    blurred = mask
    for divisor in (7, 4):
        small = pygame.transform.smoothscale(
            blurred, (max(2, w // divisor), max(2, h // divisor)))
        blurred = pygame.transform.smoothscale(small, (w, h))

    # Light it: moon-lit crown fading to a dark belly (RGB only, alpha kept).
    shade = pygame.Surface((w, h))
    for y in range(h):
        shade.fill(_lerp_color(CLOUD_LIT, CLOUD_BASE, min(1.0, (y / float(h)) * 1.5)),
                   (0, y, w, 1))
    blurred.blit(shade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    # Fade the belly out, and hold the whole cloud well below opaque.
    ramp = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / float(h)
        k = 255 if t < 0.52 else int(255 * max(0.0, 1.0 - (t - 0.52) / 0.42) ** 1.1)
        ramp.fill((255, 255, 255, int(k * 0.62)), (0, y, w, 1))
    blurred.blit(ramp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    try:
        return blurred.convert_alpha()
    except pygame.error:
        return blurred


class CloudLayer:
    """A slow drifting bank of clouds. Thickens when the weather closes in."""

    SPAN = SCREEN_WIDTH * 2

    def __init__(self, count=CLOUD_COUNT):
        rng = random.Random(7)
        self.sprites = [
            _make_cloud(rng.randint(460, 820), rng.randint(150, 250), rng)
            for _ in range(6)
        ]
        self.clouds = []
        for i in range(count):
            spr = self.sprites[rng.randrange(len(self.sprites))]
            self.clouds.append([
                spr,
                rng.uniform(0, self.SPAN),                  # world x
                rng.randint(20, int(SCREEN_HEIGHT * 0.38)),  # y
                rng.uniform(0.02, 0.055),                    # parallax factor
                rng.uniform(0.04, 0.12),                     # own drift px/frame
            ])
        self._rng = rng
        self.overcast = 0.0
        self._baked_alpha = -1
        self._faded = {}
        self._rebake(int(255 * 0.40))

    def _rebake(self, alpha):
        """Pre-multiply the cloud sprites to *alpha* once, instead of calling
        set_alpha on every blit (surface-alpha forces SDL's slow blit path)."""
        self._baked_alpha = alpha
        self._faded = {}
        for i, spr in enumerate(self.sprites):
            faded = spr.copy()
            faded.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            try:
                faded = faded.convert_alpha()
            except pygame.error:
                pass
            self._faded[id(spr)] = faded

    def set_overcast(self, level):
        """0 = clear night, 1 = heavy sky (rain / snow / fog)."""
        self.overcast = max(0.0, min(1.0, level))
        # Quantised so a slow weather fade re-bakes ~16 times, not every frame.
        alpha = int(255 * (0.40 + 0.60 * self.overcast)) // 16 * 16
        if alpha != self._baked_alpha:
            self._rebake(alpha)

    def update(self, game_speed):
        for c in self.clouds:
            c[1] -= game_speed * c[3] + c[4]
            if c[1] + c[0].get_width() < -40:
                c[1] += self.SPAN
                c[2] = self._rng.randint(20, int(SCREEN_HEIGHT * 0.38))
                c[0] = self.sprites[self._rng.randrange(len(self.sprites))]

    def render(self, surface):
        for spr, x, y, _f, _d in self.clouds:
            if x > SCREEN_WIDTH or x + spr.get_width() < 0:
                continue
            surface.blit(self._faded[id(spr)], (int(x), y))


# --------------------------------------------------------------------------
# Buildings
# --------------------------------------------------------------------------
class _Building:
    __slots__ = ("x", "y", "w", "h", "surf", "tree_h", "tree_x")

    def __init__(self, x, y, w, h, surf, tree_h, tree_x):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.surf = surf
        self.tree_h = tree_h
        self.tree_x = tree_x


class BuildingLayer:
    def __init__(self, color, speed_factor, min_h, max_h, min_w, max_w,
                 win_on=WINDOW_GLOW, win_off=WINDOW_OFF, lit_chance=0.35,
                 tree_chance=0.0):
        self.color = color
        self.speed_factor = speed_factor
        self.min_h = min_h
        self.max_h = max_h
        self.min_w = min_w
        self.max_w = max_w
        self.win_on = win_on
        self.win_off = win_off
        self.lit_chance = lit_chance
        self.tree_chance = tree_chance
        self.cap_color = _lerp_color(color, SNOW_CAP, 0.85)
        self.buildings = []
        self.scroll_x = 0.0
        self._right_edge = 0.0
        self._generate()

    # -- construction ----------------------------------------------------
    def _bake(self, w, h):
        """Render one building (body, shading, windows) into a surface once."""
        surf = pygame.Surface((w, h))
        surf.fill(self.color)
        # Subtle vertical shading: the street-level end sits deeper in shadow.
        dark = _lerp_color(self.color, (0, 0, 0), 0.35)
        bands = 6
        for i in range(bands):
            t = (i + 1) / float(bands)
            band_h = h // bands + 1
            surf.fill(_lerp_color(self.color, dark, t * t),
                      (0, int(h * i / bands), w, band_h))
        # Roof line + one corner highlight so the blocks read as solid.
        pygame.draw.rect(surf, _lerp_color(self.color, (255, 255, 255), 0.18), (0, 0, w, 3))
        pygame.draw.rect(surf, _lerp_color(self.color, (255, 255, 255), 0.08), (0, 0, 2, h))
        for wy in range(10, h - 10, 14):
            for wx in range(6, w - 6, 12):
                col = self.win_on if random.random() < self.lit_chance else self.win_off
                surf.fill(col, (wx, wy, 5, 5))
        try:
            return surf.convert()
        except pygame.error:
            return surf

    def _make_building(self, x):
        w = random.randint(self.min_w, self.max_w)
        h = random.randint(self.min_h, self.max_h)
        y = SCREEN_HEIGHT - h - 50
        tree_h = 0
        tree_x = 0
        if self.tree_chance and random.random() < self.tree_chance and w >= 34:
            tree_h = random.randint(max(18, int(w * 0.42)), max(24, int(w * 0.62)))
            tree_x = random.randint(6, max(7, w - int(tree_h * 0.7) - 6))
        return _Building(x, y, w, h, self._bake(w, h), tree_h, tree_x)

    def _generate(self):
        x = 0.0
        while x < SCREEN_WIDTH * 2:
            b = self._make_building(x)
            self.buildings.append(b)
            x += b.w + random.randint(0, int(self.max_w * 0.3))
        self._right_edge = x

    # -- loop ------------------------------------------------------------
    def update(self, game_speed):
        self.scroll_x += game_speed * self.speed_factor
        # Recycle anything that has left the screen to the right-hand end.
        while self.buildings and \
                self.buildings[0].x + self.buildings[0].w - self.scroll_x < -20:
            self.buildings.pop(0)
            gap = random.randint(0, int(self.max_w * 0.3))
            b = self._make_building(self._right_edge + gap)
            self._right_edge = b.x + b.w
            self.buildings.append(b)

    def render(self, surface, snow=0.0, glow=1.0):
        scroll = int(self.scroll_x)
        show_trees = snow > 0.02
        # Same for every building in the layer, so mix it once.
        cap_col = _lerp_color(self.color, self.cap_color, snow) if snow > 0.02 else None
        cap_h = max(2, int(2 + 3 * snow))
        for b in self.buildings:
            dx = b.x - scroll
            if dx > SCREEN_WIDTH or dx + b.w < 0:
                continue
            dx = int(dx)
            surface.blit(b.surf, (dx, b.y))
            if cap_col:
                # Snow settling along the roof - a colour lerp instead of an
                # alpha blit, so it costs a single fill.
                surface.fill(cap_col, (dx, b.y, b.w, cap_h))
            if show_trees and b.tree_h:
                body, halo = _tree_sprites(b.tree_h)
                tx = dx + b.tree_x - 9
                ty = b.y - b.tree_h - 9 + 3
                # Plain alpha blits: set_alpha is ignored by the BLEND_* modes,
                # and we need both the tree and its halo to fade with the snow.
                body.set_alpha(int(255 * snow))
                halo.set_alpha(int(255 * snow * glow))
                surface.blit(body, (tx, ty))
                surface.blit(halo, (tx, ty))


class BackgroundManager:
    def __init__(self):
        self.ground_color = GROUND_COLOR
        self.ground_line = GROUND_LINE
        self._sky = self._make_sky()
        self.clouds = CloudLayer()
        self.layers = [
            BuildingLayer(BUILDING_FAR,  0.08, 120, 300, 60, 110),
            BuildingLayer(BUILDING_MID,  0.25, 80,  220, 45, 90,
                          tree_chance=TREE_CHANCE * 0.6),
            BuildingLayer(BUILDING_NEAR, 0.55, 50,  140, 30, 70,
                          tree_chance=TREE_CHANCE),
        ]
        self._snow = 0.0
        self._glow_phase = 0.0
        self._glow = 1.0

    def _make_sky(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            surf.fill(_lerp_color(SKY_TOP, SKY_BOT, t), (0, y, SCREEN_WIDTH, 1))
        for _ in range(180):
            sx = random.randint(0, SCREEN_WIDTH - 1)
            sy = random.randint(0, SCREEN_HEIGHT // 2)
            sb = random.randint(120, 255)
            surf.set_at((sx, sy), (sb, sb, min(sb + 20, 255)))
        self._draw_moon(surf)
        try:
            return surf.convert()
        except pygame.error:
            return surf

    def _draw_moon(self, surf):
        mx, my, r = int(SCREEN_WIDTH * 0.80), int(SCREEN_HEIGHT * 0.17), 46
        # Many thin rings instead of a few fat ones - fewer steps show as
        # visible banding around the halo.
        steps = 34
        glow = pygame.Surface((r * 8, r * 8), pygame.SRCALPHA)
        gc = r * 4
        for i in range(steps, 0, -1):
            rad = int(r + (r * 3.0) * (i / float(steps)))
            a = int(30 * (1.0 - i / float(steps)) ** 1.6) + 1
            pygame.draw.circle(glow, (MOON_GLOW[0], MOON_GLOW[1], MOON_GLOW[2], a),
                               (gc, gc), rad)
        surf.blit(glow, (mx - gc, my - gc))
        pygame.draw.circle(surf, MOON_GLOW, (mx, my), r + 3)
        pygame.draw.circle(surf, MOON_CORE, (mx, my), r)
        # A couple of craters so it isn't a flat disc.
        pygame.draw.circle(surf, _lerp_color(MOON_CORE, MOON_GLOW, 0.5), (mx - 14, my - 8), 9)
        pygame.draw.circle(surf, _lerp_color(MOON_CORE, MOON_GLOW, 0.4), (mx + 12, my + 12), 6)
        pygame.draw.circle(surf, _lerp_color(MOON_CORE, MOON_GLOW, 0.35), (mx + 4, my - 20), 4)

    def set_weather(self, snow=0.0, overcast=0.0):
        """Fed from WeatherManager each frame: how snowy and how heavy the sky is."""
        self._snow = snow
        self.clouds.set_overcast(overcast)

    def update(self, game_speed, dt=16.7):
        self._glow_phase = (self._glow_phase + dt / 1700.0) % 1.0
        self._glow = 0.68 + 0.32 * (0.5 + 0.5 * math.sin(self._glow_phase * math.tau))
        self.clouds.update(game_speed)
        for layer in self.layers:
            layer.update(game_speed)

    def render(self, surface):
        surface.blit(self._sky, (0, 0))
        self.clouds.render(surface)
        for layer in self.layers:
            layer.render(surface, self._snow, self._glow)
        ground = _lerp_color(self.ground_color, SNOW_CAP, self._snow * 0.55)
        line = _lerp_color(self.ground_line, SNOW_CAP, self._snow * 0.35)
        surface.fill(ground, (0, SCREEN_HEIGHT - GROUND_H, SCREEN_WIDTH, GROUND_H))
        surface.fill(line, (0, SCREEN_HEIGHT - GROUND_H, SCREEN_WIDTH, 3))
        surface.fill(line, (0, SCREEN_HEIGHT - 35, SCREEN_WIDTH, 2))
