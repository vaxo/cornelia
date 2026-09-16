import pygame
import math
import random
from config.constants import (
    SCREEN_HEIGHT, SCREEN_WIDTH, CAR_X_POS,
    GRAVITY, LIFT_FORCE, MAX_FALL_SPEED, MAX_RISE_SPEED,
    CAR_PALETTE, CAR_MODEL_NAMES,
    CAR_WINDOW, CAR_WHEEL, CAR_WHEEL_RIM,
    CAR_HEADLIGHT, CAR_TAILLIGHT, CAR_UNDERSIDE,
    CHICKEN_BEAK, CHICKEN_BEAK_DARK, CHICKEN_LEG, CHICKEN_EYE,
)
from src.utils.math_utils import clamp

CAR_SIZES = {
    "camry": (110, 50),
    "sport": (115, 44),
    "retro": (108, 52),
    "hero": (92, 76),
    "rocket": (116, 48),
    "plane": (116, 48),
    "bibble": (120, 100),
    "chicken": (112, 90),
    "chick": (82, 72),
}

# Characters with a voice call out on a timer while you fly (see
# CharacterVoiceMixin); the value is the SFX key in AudioManager.
CHARACTER_VOICE = {
    "chicken": "chicken",
    "chick": "chick",
}

# How fast each flapping character beats, relative to the base flap rate.
# Smaller wings beat faster, so the chick is the quickest.
FLAP_RATE = {
    "bibble": 1.0,
    "chicken": 1.6,
    "chick": 2.3,
}


class PlayerCar:
    def __init__(self, model="camry", color="წითელი"):
        self.model = model
        self.color_name = color
        self.w, self.h = CAR_SIZES.get(model, (110, 50))
        self.x = float(CAR_X_POS)
        self.y = float(SCREEN_HEIGHT // 2 - self.h // 2)
        self.vel_y = 0.0
        self.tilt = 0.0  # visual tilt in degrees
        self.trail = []  # exhaust/speed puffs behind the vehicle
        self._trail_color = {
            "rocket": (255, 170, 60),
            "plane": (220, 235, 255),
            "hero": (120, 170, 255),
            "bibble": (200, 240, 255),
            "chicken": (255, 238, 205),
            "chick": (255, 246, 200),
        }.get(model, (150, 180, 240))
        self._flap_rate = FLAP_RATE.get(model, 1.0)
        self.voice = CHARACTER_VOICE.get(model)   # SFX key, None for the cars
        # Characters that flap have a pre-rendered frame list (see _build_surface);
        # single-surface models leave this None and use self._surf directly.
        self._frames = None
        self._anim_phase = 0.0
        self._build_surface()
        self._update_rects()

    def _build_surface(self):
        palette = CAR_PALETTE.get(self.model, CAR_PALETTE["camry"])
        colors = palette.get(self.color_name, list(palette.values())[0])
        body_col, roof_col, stripe_col = colors[0], colors[1], colors[2]
        w, h = self.w, self.h

        # Flapping characters (Bibble's arms, the chicken's and chick's wings) are
        # pre-rendered as a small cycle of frames that render() cycles through:
        # the limb sweeps down -> up -> down over the cycle. All other models keep
        # the single-surface fast path untouched.
        flap_drawers = {
            "bibble": self._draw_bibble,
            "chicken": self._draw_chicken,
            "chick": self._draw_chick,
        }
        flap_drawer = flap_drawers.get(self.model)
        if flap_drawer:
            self._frames = []
            n = 10
            for i in range(n):
                flap_t = math.sin(2 * math.pi * i / n)  # -1 .. +1 .. -1 over the cycle
                frame = pygame.Surface((w, h), pygame.SRCALPHA)
                flap_drawer(frame, w, h, body_col, roof_col, stripe_col, flap_t)
                self._apply_shading(frame)
                self._frames.append(frame)
            # frame 0 is the neutral mid-flap pose; keep _surf pointing at it so the
            # character-select preview (which blits _surf) still works unchanged.
            self._surf = self._frames[0]
            return

        self._frames = None
        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self._surf.fill((0, 0, 0, 0))

        drawers = {
            "camry": self._draw_camry,
            "sport": self._draw_sport,
            "retro": self._draw_retro,
            "hero": self._draw_hero,
            "rocket": self._draw_rocket,
            "plane": self._draw_plane,
        }
        drawer = drawers.get(self.model, self._draw_camry)
        drawer(self._surf, w, h, body_col, roof_col, stripe_col)
        self._apply_shading(self._surf)

    def _apply_shading(self, surf):
        """Overlay a top-light / bottom-shadow gradient so flat shapes read as
        3D. Only opaque pixels are affected (transparent stay invisible)."""
        w, h = surf.get_size()
        light = pygame.Surface((w, h))   # black; RGB values = amount to ADD
        shade = pygame.Surface((w, h))   # black; RGB values = amount to SUBTRACT
        for y in range(h):
            t = y / h
            hi = max(0, int(55 * (1 - t * 2.4)))   # highlight fades out by ~40% down
            lo = max(0, int(60 * (t * 1.5 - 0.5)))  # shadow grows toward the bottom
            if hi:
                pygame.draw.line(light, (hi, hi, hi), (0, y), (w, y))
            if lo:
                pygame.draw.line(shade, (lo, lo, lo), (0, y), (w, y))
        surf.blit(light, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(shade, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

    def _draw_camry(self, surf, w, h, body, roof, stripe):
        # Underside
        pygame.draw.rect(surf, CAR_UNDERSIDE, (8, h - 16, w - 16, 10), border_radius=3)
        # Main body
        pygame.draw.rect(surf, body, (0, h - 28, w, 22), border_radius=5)
        # Stripe along middle
        pygame.draw.rect(surf, stripe, (0, h - 28, w, 4))
        # Cabin/roof
        cabin_x = int(w * 0.18)
        cabin_w = int(w * 0.56)
        cabin_h = int(h * 0.48)
        cabin_y = h - 28 - cabin_h
        pygame.draw.rect(surf, roof, (cabin_x, cabin_y, cabin_w, cabin_h + 4), border_radius=6)
        # Windows
        win_pad = 6
        win_y = cabin_y + win_pad
        win_h = cabin_h - win_pad * 2
        pygame.draw.rect(surf, CAR_WINDOW, (cabin_x + win_pad, win_y, int(cabin_w * 0.42), win_h), border_radius=3)
        pygame.draw.rect(surf, CAR_WINDOW, (cabin_x + win_pad + int(cabin_w * 0.44), win_y, int(cabin_w * 0.38), win_h), border_radius=3)
        # Wheels
        wr = 11
        wcy = h - 12
        for wx in [int(w * 0.2), int(w * 0.78)]:
            pygame.draw.circle(surf, CAR_WHEEL, (wx, wcy), wr)
            pygame.draw.circle(surf, CAR_WHEEL_RIM, (wx, wcy), wr - 4)
            pygame.draw.circle(surf, CAR_WHEEL, (wx, wcy), wr - 6)
        # Headlight
        pygame.draw.rect(surf, CAR_HEADLIGHT, (w - 10, h - 26, 8, 6), border_radius=2)
        # Taillight
        pygame.draw.rect(surf, CAR_TAILLIGHT, (2, h - 26, 6, 5), border_radius=2)

    def _draw_sport(self, surf, w, h, body, roof, stripe):
        # Low slung body
        pygame.draw.rect(surf, CAR_UNDERSIDE, (6, h - 14, w - 12, 8), border_radius=2)
        pygame.draw.rect(surf, body, (0, h - 24, w, 18), border_radius=4)
        # Spoiler at rear
        pygame.draw.rect(surf, stripe, (4, h - 28, 10, 5), border_radius=2)
        # Sleek cabin
        cabin_x = int(w * 0.22)
        cabin_w = int(w * 0.50)
        cabin_h = int(h * 0.40)
        cabin_y = h - 24 - cabin_h
        pygame.draw.rect(surf, roof, (cabin_x, cabin_y, cabin_w, cabin_h + 3), border_radius=8)
        # Windows
        win_pad = 5
        win_y = cabin_y + win_pad
        win_h = cabin_h - win_pad * 2
        full_w = cabin_w - win_pad * 2
        pygame.draw.rect(surf, CAR_WINDOW, (cabin_x + win_pad, win_y, int(full_w * 0.44), win_h), border_radius=3)
        pygame.draw.rect(surf, CAR_WINDOW, (cabin_x + win_pad + int(full_w * 0.47), win_y, int(full_w * 0.35), win_h), border_radius=3)
        # Wheels
        wr = 10
        wcy = h - 10
        for wx in [int(w * 0.21), int(w * 0.79)]:
            pygame.draw.circle(surf, CAR_WHEEL, (wx, wcy), wr)
            pygame.draw.circle(surf, CAR_WHEEL_RIM, (wx, wcy), wr - 3)
            pygame.draw.circle(surf, CAR_WHEEL, (wx, wcy), wr - 5)
        # Lights
        pygame.draw.rect(surf, CAR_HEADLIGHT, (w - 8, h - 22, 7, 5), border_radius=1)
        pygame.draw.rect(surf, CAR_TAILLIGHT, (1, h - 22, 5, 4), border_radius=1)

    def _draw_retro(self, surf, w, h, body, roof, stripe):
        # Boxy retro look
        pygame.draw.rect(surf, CAR_UNDERSIDE, (8, h - 16, w - 16, 10), border_radius=2)
        pygame.draw.rect(surf, body, (0, h - 30, w, 24), border_radius=3)
        pygame.draw.rect(surf, stripe, (0, h - 32, w, 4))
        # Boxy cabin
        cabin_x = int(w * 0.14)
        cabin_w = int(w * 0.60)
        cabin_h = int(h * 0.50)
        cabin_y = h - 30 - cabin_h
        pygame.draw.rect(surf, roof, (cabin_x, cabin_y, cabin_w, cabin_h + 4), border_radius=3)
        # Windows
        win_pad = 5
        win_y = cabin_y + win_pad
        win_h = cabin_h - win_pad * 2
        pygame.draw.rect(surf, CAR_WINDOW, (cabin_x + win_pad, win_y, int(cabin_w * 0.40), win_h), border_radius=2)
        pygame.draw.rect(surf, CAR_WINDOW, (cabin_x + win_pad + int(cabin_w * 0.44), win_y, int(cabin_w * 0.36), win_h), border_radius=2)
        # Chrome bumpers
        pygame.draw.rect(surf, (160, 165, 170), (w - 6, h - 28, 5, 14), border_radius=1)
        pygame.draw.rect(surf, (160, 165, 170), (1, h - 28, 5, 14), border_radius=1)
        # Wheels
        wr = 12
        wcy = h - 12
        for wx in [int(w * 0.19), int(w * 0.79)]:
            pygame.draw.circle(surf, CAR_WHEEL, (wx, wcy), wr)
            pygame.draw.circle(surf, CAR_WHEEL_RIM, (wx, wcy), wr - 4)
            pygame.draw.circle(surf, CAR_WHEEL, (wx, wcy), wr - 6)
        # Lights
        pygame.draw.rect(surf, CAR_HEADLIGHT, (w - 10, h - 28, 8, 7), border_radius=2)
        pygame.draw.rect(surf, CAR_TAILLIGHT, (2, h - 28, 6, 6), border_radius=2)

    def _draw_hero(self, surf, w, h, body, cape, detail):
        skin = (240, 200, 170)
        cy = int(h * 0.46)
        # Cape trailing behind (left), drawn first so the body sits on top
        pygame.draw.polygon(surf, cape, [
            (int(w * 0.58), int(h * 0.30)),
            (int(w * 0.30), int(h * 0.16)),
            (int(w * 0.06), int(h * 0.40)),
            (int(w * 0.16), int(h * 0.66)),
            (int(w * 0.40), int(h * 0.58)),
            (int(w * 0.58), int(h * 0.62)),
        ])
        # Legs trailing back
        for dy in (-6, 6):
            pygame.draw.line(surf, body, (int(w * 0.42), cy + dy),
                             (int(w * 0.16), cy + dy + 10), 8)
            pygame.draw.rect(surf, (30, 34, 60),
                             (int(w * 0.12), cy + dy + 6, 10, 8), border_radius=2)
        # Torso (horizontal flying pose)
        pygame.draw.rect(surf, body, (int(w * 0.30), cy - 12, int(w * 0.42), 24), border_radius=11)
        # Chest emblem
        pygame.draw.circle(surf, detail, (int(w * 0.50), cy), 6)
        # Rear arm along body
        pygame.draw.line(surf, body, (int(w * 0.52), cy - 4), (int(w * 0.70), cy + 6), 7)
        # Head
        pygame.draw.circle(surf, skin, (int(w * 0.76), cy - 6), 12)
        # Hair / mask top
        pygame.draw.arc(surf, cape, (int(w * 0.76) - 12, cy - 20, 24, 22), 0.2, 3.14, 5)
        # Front arm + fist punching forward
        pygame.draw.line(surf, body, (int(w * 0.70), cy - 6), (int(w * 0.90), cy - 12), 8)
        pygame.draw.circle(surf, skin, (int(w * 0.92), cy - 13), 6)

    def _draw_rocket(self, surf, w, h, body, fins, nose):
        cy = h // 2
        # Fins
        pygame.draw.polygon(surf, fins, [
            (int(w * 0.28), cy - 8), (int(w * 0.10), int(h * 0.10)), (int(w * 0.30), cy - 2)])
        pygame.draw.polygon(surf, fins, [
            (int(w * 0.28), cy + 8), (int(w * 0.10), int(h * 0.90)), (int(w * 0.30), cy + 2)])
        # Flame from the tail
        pygame.draw.polygon(surf, (255, 180, 40), [
            (int(w * 0.10), cy - 7), (int(w * -0.02), cy), (int(w * 0.10), cy + 7)])
        pygame.draw.polygon(surf, (255, 230, 120), [
            (int(w * 0.10), cy - 4), (int(w * 0.03), cy), (int(w * 0.10), cy + 4)])
        # Body capsule
        pygame.draw.rect(surf, body, (int(w * 0.14), cy - int(h * 0.26),
                                      int(w * 0.62), int(h * 0.52)), border_radius=13)
        # Nose cone
        pygame.draw.polygon(surf, nose, [
            (int(w * 0.72), cy - int(h * 0.24)),
            (int(w * 0.72), cy + int(h * 0.24)),
            (int(w * 0.98), cy)])
        # Window
        pygame.draw.circle(surf, (150, 210, 245), (int(w * 0.44), cy), 8)
        pygame.draw.circle(surf, (40, 70, 110), (int(w * 0.44), cy), 8, 2)

    def _draw_plane(self, surf, w, h, body, wing, tail):
        cy = h // 2
        # Tail fin
        pygame.draw.polygon(surf, tail, [
            (int(w * 0.10), cy), (int(w * 0.10), int(h * 0.14)), (int(w * 0.26), cy - 2)])
        # Rear stabilizer
        pygame.draw.polygon(surf, wing, [
            (int(w * 0.12), cy + 2), (int(w * 0.02), cy + 12), (int(w * 0.24), cy + 4)])
        # Fuselage
        pygame.draw.rect(surf, body, (int(w * 0.10), cy - int(h * 0.17),
                                      int(w * 0.82), int(h * 0.34)), border_radius=12)
        # Wing
        pygame.draw.polygon(surf, wing, [
            (int(w * 0.40), cy), (int(w * 0.62), cy),
            (int(w * 0.50), cy + int(h * 0.42)), (int(w * 0.30), cy + int(h * 0.40))])
        # Cockpit
        pygame.draw.circle(surf, (150, 210, 245), (int(w * 0.74), cy - 3), 7)
        pygame.draw.circle(surf, (40, 70, 110), (int(w * 0.74), cy - 3), 7, 2)
        # Propeller at the nose
        pygame.draw.line(surf, (40, 44, 60), (int(w * 0.93), cy - 14), (int(w * 0.93), cy + 14), 4)

    def _draw_bibble(self, surf, w, h, fur, accent, detail, arm_t=0.0):
        """Teal furry pixie with a magenta mohawk (see reference art). `arm_t` in
        [-1, 1] flaps the arms: -1 = down/out, +1 = raised high. Everything is
        kept within the wxh canvas so the hitbox and tilt-rotation are unaffected."""
        cx = w // 2
        cy = int(h * 0.58)
        r = int(min(w, h) * 0.40)
        fur_dark = tuple(max(0, c - 28) for c in fur)
        acc_dark = tuple(max(0, c - 40) for c in accent)
        acc_light = tuple(min(255, c + 45) for c in accent)

        # --- Arms (behind body; hands stay visible past the fur) ---
        for sx in (-1, 1):
            shoulder = (cx + sx * int(r * 0.55), cy - int(r * 0.02))
            hand_y = cy - int(r * 0.35) - int(arm_t * r * 0.60)
            hand = (cx + sx * int(r * 1.12), hand_y)
            elbow = (cx + sx * int(r * 0.92), (shoulder[1] + hand_y) // 2)
            pygame.draw.line(surf, fur, shoulder, elbow, int(r * 0.32))
            pygame.draw.circle(surf, fur, elbow, int(r * 0.16))
            pygame.draw.line(surf, accent, elbow, hand, int(r * 0.28))
            pygame.draw.circle(surf, accent, hand, int(r * 0.22))          # paw
            pygame.draw.circle(surf, acc_light, (hand[0] - sx * 2, hand[1] - 2), int(r * 0.09))

        # --- Legs / feet (behind and below the body) ---
        for sx in (-1, 1):
            hip = (cx + sx * int(r * 0.34), cy + int(r * 0.70))
            foot = (cx + sx * int(r * 0.44), cy + int(r * 0.88))
            pygame.draw.line(surf, fur, hip, foot, int(r * 0.30))
            pygame.draw.ellipse(surf, accent,
                                (foot[0] - int(r * 0.20), foot[1] - int(r * 0.06),
                                 int(r * 0.42), int(r * 0.24)))

        # --- Ears (little pointed tufts behind the head) ---
        for sx in (-1, 1):
            base = (cx + sx * int(r * 0.60), cy - int(r * 0.62))
            pygame.draw.polygon(surf, fur, [
                (base[0] - int(r * 0.12), base[1] + int(r * 0.12)),
                (base[0] + int(r * 0.12), base[1] + int(r * 0.12)),
                (base[0] + sx * int(r * 0.10), base[1] - int(r * 0.24))])
            pygame.draw.polygon(surf, acc_dark, [
                (base[0] - int(r * 0.05), base[1] + int(r * 0.08)),
                (base[0] + int(r * 0.05), base[1] + int(r * 0.08)),
                (base[0] + sx * int(r * 0.05), base[1] - int(r * 0.12))])

        # --- Magenta mohawk (spiky tufts, tallest in the middle) ---
        moh_y = cy - int(r * 0.86)
        for fx, fh in ((-0.55, 0.55), (-0.28, 0.85), (0.0, 1.02), (0.28, 0.88), (0.55, 0.58)):
            bx = cx + int(fx * r)
            tip_y = moh_y - int(fh * r * 0.55)
            pygame.draw.polygon(surf, accent, [
                (bx - int(r * 0.15), moh_y + int(r * 0.10)),
                (bx + int(r * 0.15), moh_y + int(r * 0.10)),
                (bx + int(fx * r * 0.12), tip_y)])
            pygame.draw.polygon(surf, acc_light, [
                (bx - int(r * 0.06), moh_y - int(r * 0.04)),
                (bx + int(r * 0.06), moh_y - int(r * 0.04)),
                (bx + int(fx * r * 0.12), tip_y + int(r * 0.06))])

        # --- Fluffy body: perimeter fur bumps + main puff ---
        for i in range(16):
            ang = 2 * math.pi * i / 16
            bx = cx + int(math.cos(ang) * r * 0.92)
            by = cy + int(math.sin(ang) * r * 0.92)
            pygame.draw.circle(surf, fur, (bx, by), int(r * 0.24))
        pygame.draw.circle(surf, fur, (cx, cy), r)

        # --- Purple belly/chest accent running down the front (lower body only,
        # so it sits below the face and doesn't read as an open mouth) ---
        belly = pygame.Rect(cx - int(r * 0.32), cy + int(r * 0.26),
                            int(r * 0.64), int(r * 0.72))
        pygame.draw.ellipse(surf, accent, belly)

        # --- Cheeks (blush) ---
        for sx in (-1, 1):
            pygame.draw.circle(surf, (255, 150, 175),
                               (cx + sx * int(r * 0.60), cy + int(r * 0.08)), int(r * 0.13))

        # --- Big blue eyes with lashes and sparkles ---
        er = int(r * 0.28)
        for sx in (-1, 1):
            ex = cx + sx * int(r * 0.33)
            ey = cy - int(r * 0.26)
            pygame.draw.circle(surf, (255, 255, 255), (ex, ey), er)
            pygame.draw.circle(surf, (72, 150, 225), (ex, ey), int(er * 0.80))
            pygame.draw.circle(surf, (34, 88, 165), (ex, ey), int(er * 0.80), 2)
            pygame.draw.circle(surf, (24, 30, 46), (ex, ey), int(er * 0.42))
            pygame.draw.circle(surf, (255, 255, 255),
                               (ex - int(er * 0.26), ey - int(er * 0.30)), max(2, int(er * 0.24)))
            pygame.draw.circle(surf, (255, 255, 255),
                               (ex + int(er * 0.22), ey + int(er * 0.20)), max(1, int(er * 0.11)))
            # eyelashes on the outer top
            pygame.draw.line(surf, (30, 30, 46),
                             (ex + sx * int(er * 0.75), ey - int(er * 0.55)),
                             (ex + sx * int(er * 1.15), ey - int(er * 0.95)), 2)
            pygame.draw.line(surf, (30, 30, 46),
                             (ex + sx * int(er * 0.45), ey - int(er * 0.85)),
                             (ex + sx * int(er * 0.6), ey - int(er * 1.20)), 2)

        # --- Nose ---
        pygame.draw.circle(surf, acc_dark, (cx, cy - int(r * 0.05)), max(2, int(r * 0.06)))

        # --- Happy open grin with a tooth (on the face, above the belly) ---
        sm_y = cy + int(r * 0.10)
        pygame.draw.lines(surf, (78, 48, 74), False, [
            (cx - int(r * 0.26), sm_y - int(r * 0.02)),
            (cx, sm_y + int(r * 0.14)),
            (cx + int(r * 0.26), sm_y - int(r * 0.02))], 3)
        pygame.draw.rect(surf, (255, 255, 255),
                         (cx - int(r * 0.05), sm_y + int(r * 0.02),
                          max(2, int(r * 0.1)), max(2, int(r * 0.08))), border_radius=1)

    def _draw_bird_wing(self, surf, pivot, length, angle, col, edge, feathers=4):
        """One wing, rotated `angle` radians around `pivot` (negative = raised,
        positive = swept down). The wing points back (toward -x on screen) from
        the shoulder, so the same helper serves the chicken and the chick."""
        px, py = pivot
        ca, sa = math.cos(angle), math.sin(angle)
        chord = max(6, int(length * 0.36))

        def P(x, y):
            # local (x = out along the span, y = down across the chord) -> screen
            return (int(px - (x * ca - y * sa)), int(py + (x * sa + y * ca)))

        outline = [
            P(0, -chord * 0.45),
            P(length * 0.38, -chord * 0.62),
            P(length * 0.78, -chord * 0.28),
            P(length, chord * 0.22),
            P(length * 0.70, chord * 0.80),
            P(length * 0.32, chord * 0.86),
            P(0, chord * 0.58),
        ]
        pygame.draw.polygon(surf, col, outline)
        pygame.draw.polygon(surf, edge, outline, 2)
        # primary feathers fanning out toward the trailing edge
        for i in range(feathers):
            f = 0.40 + 0.55 * (i / max(1, feathers - 1))
            pygame.draw.line(surf, edge,
                             P(length * f * 0.50, -chord * 0.05),
                             P(length * f, chord * (0.84 - 0.55 * f)), 2)

    def _draw_chicken(self, surf, w, h, feathers, wing_col, comb, wing_t=0.0):
        """Side-on hen in flight. `wing_t` in [-1, 1] drives the wingbeat:
        -1 = wings raised high, +1 = swept down through the power stroke."""
        body = feathers
        body_hi = tuple(min(255, c + 20) for c in body)
        wing_dark = tuple(max(0, c - 42) for c in wing_col)
        wing_edge = tuple(max(0, c - 24) for c in wing_dark)

        cx, cy = int(w * 0.44), int(h * 0.56)
        bw, bh = int(w * 0.62), int(h * 0.52)
        wing_len = int(w * 0.46)
        ang_near = wing_t * 0.80
        ang_far = wing_t * 0.66 + 0.10   # the far wing trails a touch behind

        # --- far wing (behind everything, darker so it reads as depth) ---
        self._draw_bird_wing(surf, (cx + int(w * 0.06), cy - int(h * 0.20)),
                             int(wing_len * 0.92), ang_far, wing_dark, wing_edge, 3)

        # --- tail feathers fanning up and back ---
        tx, ty = cx - int(bw * 0.48), cy - int(h * 0.02)
        for i, (dx, dy) in enumerate(((-0.30, -0.34), (-0.35, -0.16), (-0.30, 0.02))):
            pygame.draw.polygon(surf, wing_col if i % 2 == 0 else wing_dark, [
                (tx + int(w * 0.05), ty - int(h * 0.06)),
                (tx + int(w * dx), ty + int(h * dy)),
                (tx + int(w * (dx + 0.11)), ty + int(h * (dy + 0.17)))])

        # --- legs tucked back under the body ---
        leg_w = max(3, int(w * 0.035))
        for off in (-0.06, 0.06):
            hip = (cx + int(w * off), cy + int(bh * 0.38))
            foot = (hip[0] - int(w * 0.05), hip[1] + int(h * 0.13))
            pygame.draw.line(surf, CHICKEN_LEG, hip, foot, leg_w)
            for ty2 in (-0.04, 0.0, 0.04):
                pygame.draw.line(surf, CHICKEN_LEG, foot,
                                 (foot[0] - int(w * 0.09), foot[1] + int(h * ty2)), 3)

        # --- neck + body ---
        pygame.draw.ellipse(surf, body, (cx + int(w * 0.10), cy - int(h * 0.30),
                                         int(w * 0.26), int(h * 0.34)))
        pygame.draw.ellipse(surf, body, (cx - bw // 2, cy - bh // 2, bw, bh))
        pygame.draw.ellipse(surf, body_hi, (cx + int(bw * 0.04), cy - int(bh * 0.24),
                                            int(bw * 0.44), int(bh * 0.62)))

        # --- head ---
        hx, hy = cx + int(w * 0.30), cy - int(h * 0.28)
        hr = int(w * 0.135)
        pygame.draw.circle(surf, body, (hx, hy), hr)

        # --- comb (three bumps) and wattle ---
        for ox, oy, rr in ((-0.45, -0.86, 0.34), (0.02, -1.02, 0.40), (0.46, -0.82, 0.30)):
            pygame.draw.circle(surf, comb, (hx + int(hr * ox), hy + int(hr * oy)),
                               max(3, int(hr * rr)))
        pygame.draw.circle(surf, comb, (hx + int(hr * 0.62), hy + int(hr * 0.95)),
                           max(3, int(hr * 0.30)))

        # --- beak ---
        by = hy + int(hr * 0.12)
        pygame.draw.polygon(surf, CHICKEN_BEAK, [
            (hx + int(hr * 0.55), by - int(hr * 0.34)),
            (hx + int(hr * 0.55), by + int(hr * 0.34)),
            (hx + int(hr * 1.80), by)])
        pygame.draw.line(surf, CHICKEN_BEAK_DARK,
                         (hx + int(hr * 0.60), by), (hx + int(hr * 1.72), by), 2)

        # --- eye ---
        ex, ey = hx + int(hr * 0.30), hy - int(hr * 0.22)
        pygame.draw.circle(surf, (255, 255, 255), (ex, ey), max(3, int(hr * 0.32)))
        pygame.draw.circle(surf, CHICKEN_EYE, (ex, ey), max(2, int(hr * 0.18)))
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey - 2), max(1, int(hr * 0.09)))

        # --- near wing, in front of the body ---
        self._draw_bird_wing(surf, (cx + int(w * 0.10), cy - int(h * 0.10)),
                             wing_len, ang_near, wing_col, wing_dark, 4)

    def _draw_chick(self, surf, w, h, down, wing_col, cheek, wing_t=0.0):
        """Fluffy baby chick: two down puffs, stubby wings that beat about twice
        as fast as the hen's (see FLAP_RATE). `wing_t` works as in _draw_chicken."""
        down_hi = tuple(min(255, c + 22) for c in down)
        wing_dark = tuple(max(0, c - 58) for c in wing_col)
        wing_edge = tuple(max(0, c - 30) for c in wing_dark)

        cx, cy = int(w * 0.44), int(h * 0.56)
        r = int(min(w, h) * 0.34)
        wing_len = int(w * 0.36)
        ang_near = wing_t * 0.95        # stubby wings swing through a wider arc
        ang_far = wing_t * 0.78 + 0.12

        # --- far wing ---
        self._draw_bird_wing(surf, (cx + int(w * 0.06), cy - int(h * 0.12)),
                             int(wing_len * 0.90), ang_far, wing_dark, wing_edge, 3)

        # --- tail: two little feathers fanning back ---
        tx, ty = cx - int(r * 0.85), cy - int(h * 0.02)
        for i, (dx, dy) in enumerate(((-0.17, -0.20), (-0.19, -0.04))):
            pygame.draw.polygon(surf, wing_col if i % 2 == 0 else wing_dark, [
                (tx + int(w * 0.05), ty - int(h * 0.06)),
                (tx + int(w * dx), ty + int(h * dy)),
                (tx + int(w * (dx + 0.10)), ty + int(h * (dy + 0.15)))])

        # --- legs ---
        for off in (-0.05, 0.05):
            hip = (cx + int(w * off), cy + int(r * 0.78))
            foot = (hip[0] - int(w * 0.04), hip[1] + int(h * 0.10))
            pygame.draw.line(surf, CHICKEN_LEG, hip, foot, max(3, int(w * 0.035)))
            for ty2 in (-0.035, 0.0, 0.035):
                pygame.draw.line(surf, CHICKEN_LEG, foot,
                                 (foot[0] - int(w * 0.08), foot[1] + int(h * ty2)), 2)

        # --- body: down bumps around the rim, then the main puff ---
        for i in range(14):
            ang = 2 * math.pi * i / 14
            pygame.draw.circle(surf, down,
                               (cx + int(math.cos(ang) * r * 0.90),
                                cy + int(math.sin(ang) * r * 0.90)), int(r * 0.22))
        pygame.draw.circle(surf, down, (cx, cy), r)
        pygame.draw.circle(surf, down_hi, (cx + int(r * 0.30), cy + int(r * 0.10)), int(r * 0.42))

        # --- head ---
        hx, hy = cx + int(w * 0.24), cy - int(h * 0.26)
        hr = int(r * 0.66)
        for i in range(10):
            ang = 2 * math.pi * i / 10
            pygame.draw.circle(surf, down,
                               (hx + int(math.cos(ang) * hr * 0.88),
                                hy + int(math.sin(ang) * hr * 0.88)), int(hr * 0.24))
        pygame.draw.circle(surf, down, (hx, hy), hr)

        # --- head tuft (three little down feathers) ---
        for fx, fh in ((-0.42, 0.45), (0.0, 0.65), (0.42, 0.42)):
            bx = hx + int(fx * hr)
            pygame.draw.polygon(surf, down_hi, [
                (bx - int(hr * 0.18), hy - int(hr * 0.80)),
                (bx + int(hr * 0.18), hy - int(hr * 0.80)),
                (bx + int(fx * hr * 0.30), hy - int(hr * (0.80 + fh * 0.55)))])

        # --- cheek blush ---
        pygame.draw.circle(surf, cheek, (hx + int(hr * 0.10), hy + int(hr * 0.44)),
                           max(2, int(hr * 0.24)))

        # --- eye ---
        ex, ey = hx + int(hr * 0.34), hy - int(hr * 0.14)
        pygame.draw.circle(surf, (255, 255, 255), (ex, ey), max(3, int(hr * 0.32)))
        pygame.draw.circle(surf, CHICKEN_EYE, (ex, ey), max(2, int(hr * 0.20)))
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey - 2), max(1, int(hr * 0.09)))

        # --- little beak ---
        by = hy + int(hr * 0.18)
        pygame.draw.polygon(surf, CHICKEN_BEAK, [
            (hx + int(hr * 0.62), by - int(hr * 0.28)),
            (hx + int(hr * 0.62), by + int(hr * 0.28)),
            (hx + int(hr * 1.55), by)])
        pygame.draw.line(surf, CHICKEN_BEAK_DARK,
                         (hx + int(hr * 0.66), by), (hx + int(hr * 1.46), by), 2)

        # --- near wing ---
        self._draw_bird_wing(surf, (cx + int(w * 0.10), cy - int(h * 0.04)),
                             wing_len, ang_near, wing_col, wing_dark, 3)

    def _update_rects(self):
        # Slightly inset hitbox for fairness
        pad = 6
        self.rect = pygame.Rect(
            int(self.x) + pad,
            int(self.y) + pad,
            self.w - pad * 2,
            self.h - pad * 2,
        )

    def move_up(self):
        self.vel_y = LIFT_FORCE

    def apply_gravity(self, dt):
        self.vel_y = clamp(self.vel_y + GRAVITY, MAX_RISE_SPEED, MAX_FALL_SPEED)
        self.y += self.vel_y
        # Clamp to screen
        self.y = clamp(self.y, 0, SCREEN_HEIGHT - self.h)
        self._update_rects()

    def update_tilt(self):
        target_tilt = clamp(self.vel_y * 3.5, -30, 30)
        self.tilt += (target_tilt - self.tilt) * 0.18

    def update(self, dt):
        self.apply_gravity(dt)
        self.update_tilt()
        self._update_trail()
        self._update_anim(dt)

    def _update_anim(self, dt):
        """Advance the flap cycle. dt is in milliseconds (pygame clock.tick).
        Beat faster while rising so it reads as effort producing lift."""
        if not self._frames:
            return
        freq = (2.6 if self.vel_y < 0 else 1.4) * self._flap_rate  # flaps per second
        self._anim_phase = (self._anim_phase + freq * dt / 1000.0) % 1.0

    def _current_frame(self):
        if self._frames:
            idx = int(self._anim_phase * len(self._frames)) % len(self._frames)
            return self._frames[idx]
        return self._surf

    def _update_trail(self):
        # Emit an exhaust puff at the rear (left) of the vehicle
        ex = self.x + self.w * 0.06
        ey = self.y + self.h * 0.66
        self.trail.append([ex, ey, 1.0, random.uniform(-0.4, 0.4)])
        for p in self.trail:
            p[0] -= 7          # drift back
            p[1] += p[3]       # slight vertical wander
            p[2] -= 0.07       # fade
        self.trail = [p for p in self.trail if p[2] > 0]

    def _render_trail(self, screen, shake_offset):
        r0, g0, b0 = self._trail_color
        for x, y, life, _ in self.trail:
            r = int(9 * life) + 2
            a = int(110 * life)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (r0, g0, b0, a), (r, r), r)
            screen.blit(s, (int(x) - r + shake_offset[0], int(y) - r + shake_offset[1]))

    def render(self, screen, shake_offset=(0, 0)):
        self._render_trail(screen, shake_offset)
        cx = int(self.x) + shake_offset[0]
        cy = int(self.y) + shake_offset[1]
        surf = self._current_frame()
        if abs(self.tilt) > 0.5:
            rotated = pygame.transform.rotate(surf, -self.tilt)
            rx = cx + (self.w - rotated.get_width()) // 2
            ry = cy + (self.h - rotated.get_height()) // 2
            screen.blit(rotated, (rx, ry))
        else:
            screen.blit(surf, (cx, cy))

    def reset(self):
        self.y = float(SCREEN_HEIGHT // 2 - self.h // 2)
        self.vel_y = 0.0
        self.tilt = 0.0
        self.trail = []
        self._anim_phase = 0.0
        self._update_rects()

    def change_appearance(self, model, color):
        self.model = model
        self.color_name = color
        self.w, self.h = CAR_SIZES.get(model, (110, 50))
        self._flap_rate = FLAP_RATE.get(model, 1.0)
        self.voice = CHARACTER_VOICE.get(model)
        self._build_surface()
        self._update_rects()
