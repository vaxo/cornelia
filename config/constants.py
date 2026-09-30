SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Night sky / background colors
SKY_TOP = (5, 8, 25)
SKY_BOT = (15, 22, 55)
BUILDING_FAR = (12, 15, 38)
BUILDING_MID = (18, 22, 50)
BUILDING_NEAR = (22, 28, 62)
WINDOW_GLOW = (255, 220, 100)
WINDOW_OFF = (20, 25, 45)

# UI colors
UI_BG = (10, 14, 38)
UI_PANEL = (20, 28, 60)
UI_TEXT = (210, 220, 255)
UI_TEXT_DIM = (130, 140, 180)
UI_ACCENT = (90, 140, 255)
UI_ACCENT2 = (50, 200, 160)
UI_BUTTON = (30, 45, 90)
UI_BUTTON_HOVER = (55, 80, 150)
UI_BUTTON_BORDER = (70, 100, 180)
UI_WHITE = (240, 240, 255)
UI_GOLD = (255, 195, 40)
UI_RED = (220, 60, 60)
UI_GREEN = (50, 200, 100)
UI_LOCKED = (60, 60, 80)

# Obstacle
OBSTACLE_COLOR = (75, 80, 92)
OBSTACLE_EDGE = (55, 60, 72)
OBSTACLE_STRIPE = (88, 93, 105)

# Ground
GROUND_COLOR = (18, 22, 45)
GROUND_LINE = (30, 38, 70)

# Clouds (night sky)
CLOUD_BASE = (54, 64, 102)       # body of the cloud
CLOUD_LIT = (116, 132, 180)      # moon-lit crown
CLOUD_COUNT = 10
MOON_CORE = (238, 242, 255)
MOON_GLOW = (150, 170, 225)

# Snow
SNOW_COUNT = 340
SNOW_COLOR = (232, 240, 255)
SNOW_CAP = (226, 236, 252)       # snow settling on the rooftops

# Weather pacing. Weather holds for a long stretch and then CROSSFADES into the
# next kind over WEATHER_FADE_MS - nothing ever pops in or out.
WEATHER_HOLD_MIN = 48000
WEATHER_HOLD_MAX = 88000
WEATHER_FADE_MS = 4200

# Rooftop christmas trees - only lit while it snows.
TREE_GREEN = (26, 82, 50)
TREE_GREEN_LIT = (58, 138, 86)
TREE_TRUNK = (78, 54, 32)
TREE_GLOW = (140, 255, 198)
TREE_STAR = (255, 224, 130)
TREE_BAUBLES = [(255, 120, 110), (255, 214, 120), (130, 205, 255), (200, 150, 255)]
TREE_CHANCE = 0.40               # share of near/mid buildings that get one

# Car
CAR_WINDOW = (90, 130, 195)
CAR_WHEEL = (25, 25, 30)
CAR_WHEEL_RIM = (120, 125, 135)
CAR_HEADLIGHT = (255, 245, 160)
CAR_TAILLIGHT = (255, 50, 50)
CAR_UNDERSIDE = (15, 15, 20)

# Poultry (chicken / chick) shared colors
CHICKEN_BEAK = (248, 176, 48)
CHICKEN_BEAK_DARK = (206, 132, 28)
CHICKEN_LEG = (236, 152, 40)
CHICKEN_EYE = (24, 24, 34)

# Car model colors [body, roof, stripe]
CAR_PALETTE = {
    "camry": {
        "ნაცრისფერი":   [(130,130,135), (100,100,105), (90,90,95)],
        "წითელი":       [(185,45,45),   (150,35,35),   (120,25,25)],
        "ლურჯი":        [(40,85,185),   (30,65,150),   (20,50,120)],
        "მწვანე":       [(35,150,70),   (25,115,55),   (18,85,40)],
        "ყვითელი":      [(215,190,40),  (175,155,30),  (140,120,20)],
        "შავი":         [(25,25,30),    (15,15,20),    (10,10,15)],
        "თეთრი":        [(225,225,235), (205,205,215), (185,185,195)],
    },
    "sport": {
        "ნარინჯისფერი": [(220,80,30),   (185,60,20),   (150,45,15)],
        "ლურჯი":        [(30,70,210),   (20,55,170),   (15,40,130)],
        "მწვანე":       [(40,190,100),  (30,150,80),   (22,115,60)],
        "ოქროსფერი":    [(200,165,30),  (165,130,22),  (130,100,15)],
        "იისფერი":      [(150,60,200),  (120,45,165),  (90,32,130)],
        "შავი":         [(20,20,25),    (12,12,17),    (8,8,12)],
        "თეთრი":        [(235,235,245), (215,215,225), (195,195,205)],
    },
    "retro": {
        "ყავისფერი":    [(165,100,40),  (130,78,28),   (100,58,18)],
        "ღია ლურჯი":   [(80,140,200),  (60,110,165),  (45,85,130)],
        "ბირთვული":    [(60,175,130),  (45,140,100),  (32,108,75)],
        "ქარვისფერი":  [(200,165,85),  (165,130,65),  (130,100,48)],
        "ვარდისფერი":  [(210,120,150), (175,90,120),  (140,65,92)],
        "მუქი":        [(50,42,32),    (38,32,22),    (28,22,14)],
        "ლომური":      [(220,205,170), (185,172,140), (150,138,108)],
    },
    # Flying characters. Triple = [body, accent(cape/fins/wing), detail(emblem/nose)]
    "hero": {
        "წითელი":   [(200,45,45),   (45,70,190),   (255,215,60)],
        "ლურჯი":    [(45,85,200),   (200,45,45),   (255,215,60)],
        "მწვანე":   [(40,165,80),   (25,25,32),    (235,235,240)],
        "შავი":     [(38,38,50),    (95,25,125),   (185,185,195)],
        "ოქროსფერი":[(215,175,45),  (60,40,120),   (255,255,255)],
    },
    "rocket": {
        "წითელი":   [(210,60,50),   (240,200,60),  (235,235,240)],
        "ლურჯი":    [(50,90,205),   (235,235,240), (245,120,45)],
        "თეთრი":    [(230,230,238), (210,60,50),   (60,72,95)],
        "მწვანე":   [(40,170,110),  (240,240,245), (240,200,60)],
        "იისფერი":  [(150,70,200),  (240,240,245), (255,210,90)],
    },
    "plane": {
        "თეთრი":     [(226,228,236), (210,60,60),   (60,90,160)],
        "წითელი":    [(200,60,55),   (240,240,245), (42,42,54)],
        "ლურჯი":     [(60,100,190),  (240,240,245), (250,200,60)],
        "ყვითელი":   [(225,190,50),  (60,72,95),    (210,60,60)],
        "ნაცრისფერი":[(140,145,158), (90,96,112),   (210,80,60)],
    },
    # Bibble (the fluffy pixie). Triple = [fur, accent(mohawk/belly/arms/feet), detail]
    "bibble": {
        "ცისფერი":   [(95,205,205),  (200,70,180),  (255,255,255)],  # teal fur + magenta mohawk (reference)
        "ვარდისფერი":[(245,175,205), (150,80,190),  (255,255,255)],  # pink fur + purple
        "იისფერი":   [(185,155,235), (95,190,205),  (255,255,255)],  # lilac fur + teal
        "მწვანე":    [(150,215,150), (210,90,150),  (255,255,255)],  # green fur + pink
        "ყვითელი":   [(248,225,140), (120,150,235), (255,255,255)],  # yellow fur + blue
    },
    # Chicken (grown hen). Triple = [feathers, wing/tail feathers, comb & wattle]
    "chicken": {
        "თეთრი":      [(240,240,246), (206,209,220), (216,52,52)],
        "ყავისფერი":  [(180,114,58),  (140,82,40),   (212,52,50)],
        "წითელი":     [(176,70,44),   (134,48,30),   (228,72,58)],
        "ოქროსფერი":  [(230,188,82),  (196,150,52),  (216,60,56)],
        "შავი":       [(56,56,68),    (36,36,48),    (222,62,58)],
    },
    # Chick (the fluffy baby). Triple = [down, wing down, cheeks]
    "chick": {
        "ყვითელი":     [(252,222,96),  (234,192,66),  (255,164,150)],
        "ნარინჯისფერი":[(250,186,88),  (226,150,54),  (255,150,140)],
        "თეთრი":       [(246,246,250), (214,216,226), (255,168,158)],
        "ვარდისფერი":  [(250,192,212), (226,158,186), (255,150,160)],
        "ცისფერი":     [(178,218,248), (142,186,226), (255,158,160)],
    },
    # Sun (smiling, freckled). Triple = [face, rays, freckles]
    "sun": {
        "ყვითელი":      [(255,214,64),  (255,178,40),  (196,112,44)],
        "ოქროსფერი":    [(246,190,52),  (238,140,30),  (170,90,36)],
        "ნარინჯისფერი": [(255,168,62),  (240,108,40),  (160,70,34)],
        "ლიმონისფერი":  [(250,236,110), (240,204,60),  (190,130,60)],
        "ვარდისფერი":   [(255,190,150), (250,130,110), (180,86,70)],
    },
    # Dalmatian puppy. Triple = [fur, spots & ears, collar]
    "dalmatian": {
        "წითელი საყელო":  [(246,246,250), (30,30,36),  (214,40,44)],
        "ლურჯი საყელო":   [(246,246,250), (30,30,36),  (52,104,214)],
        "მწვანე საყელო":  [(246,246,250), (30,30,36),  (44,168,90)],
        "ყავისფერი ლაქები": [(248,244,238), (112,66,40), (214,40,44)],
        "ოქროსფერი საყელო": [(246,246,250), (30,30,36), (232,184,48)],
    },
}
CAR_MODEL_NAMES = ["camry", "sport", "retro", "hero", "rocket", "plane", "bibble", "chicken", "chick", "sun", "dalmatian"]
CAR_MODEL_DISPLAY = {
    "camry": "Toyota Camry",
    "sport": "სპორტ კარი",
    "retro": "რეტრო კარი",
    "hero": "სუპერგმირი",
    "rocket": "რაკეტა",
    "plane": "თვითმფრინავი",
    "bibble": "ბიბლი",
    "chicken": "ქათამი",
    "chick": "წიწილა",
    "sun": "მზე",
    "dalmatian": "დალმატინელი",
}

# Physics
GRAVITY = 0.42
LIFT_FORCE = -9.2
MAX_FALL_SPEED = 13.0
MAX_RISE_SPEED = -12.0
CAR_X_POS = 250

# Game speed
INITIAL_GAME_SPEED = 4.5
MAX_GAME_SPEED = 10.5
SPEED_RAMP_RATE = 0.00018

# Obstacles
OBSTACLE_WIDTH = 82
OBSTACLE_INITIAL_GAP = 340
OBSTACLE_MIN_GAP = 255
INITIAL_SPAWN_INTERVAL = 2100
MIN_SPAWN_INTERVAL = 900

# Endless ramp: the vertical gap shrinks from INITIAL to MIN over this many
# points (higher = gentler), and the spawn timer tightens by this many ms per
# point. Both were steeper before and made late runs feel cramped.
GAP_SHRINK_SCORE = 320
SPAWN_INTERVAL_PER_SCORE = 3.5

# Horizontal breathing room: consecutive obstacle pairs are kept at least this
# many pixels apart (centre to centre, so ~OBSTACLE_WIDTH less of clear air).
# The spawn interval is derived from it and the CURRENT speed, so the pairs stay
# this far apart as the game speeds up instead of bunching together.
OBSTACLE_MIN_SPACING = 620
OBSTACLE_MIN_Y_EDGE = 60
OBSTACLE_MAX_Y_EDGE = 60

# Reachability: the vertical distance between one gap and the next is capped so
# the car can always fly from one to the other in the time between them — no
# more "impossible unless you phase" jumps. The cap = a conservative sustained
# climb speed (px/frame) times the number of frames until the next obstacle
# arrives (spawn_interval / frame_time). See ObstacleManager._pick_gap_y.
REACHABLE_VSPEED = 4.2        # px/frame the car can comfortably sustain
MIN_REACHABLE_DELTA = 170     # never tighter than this, so it still varies
MOVING_AMPLITUDE_MARGIN = 90  # room reserved for a moving gap's oscillation

# Moving obstacles - appear after this score/level
MOVING_SCORE_THRESHOLD = 50
MOVING_LEVEL_THRESHOLD = 4

# Scoring
SCORE_PER_PASS = 10
COMBO_BASE_BONUS = 5

# Levels
NUM_LEVELS = 10
LEVEL_DISTANCE = 6000

# Screen shake
SHAKE_DURATION = 520
SHAKE_INTENSITY = 9

# Particle
SPARK_COLORS = [(255,200,50),(255,150,30),(255,85,20),(210,45,10)]
MAX_SPARKS = 35
RAIN_COUNT = 200
RAIN_COLOR = (140, 165, 220)
FOG_ALPHA = 55
LIGHTNING_FLASH_DURATION = 120

# HUD
HUD_FONT_LG = 56
HUD_FONT_MD = 38
HUD_FONT_SM = 26
HUD_PAD = 22

# Menu
BTN_W = 340
BTN_H = 64
BTN_SPACING = 82
TITLE_FONT_SIZE = 96
BTN_FONT_SIZE = 38
SUBTITLE_FONT_SIZE = 30
