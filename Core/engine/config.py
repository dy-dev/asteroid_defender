"""
config.py - Internal engine settings.
LOCKED: do not modify. The game settings go in student_config.py,
at the project root.
"""

WIDTH = 800
HEIGHT = 600
FPS = 60

DEFAULT_START = (WIDTH // 2, HEIGHT - 90)

HIGHSCORE_SHOWN = 5

# --- palette ---------------------------------------------------------------
BLACK = (8, 10, 18)
DARK = (16, 22, 34)
PANEL = (24, 32, 48)
LINE = (52, 68, 92)
WHITE = (238, 244, 252)
GREY = (150, 165, 188)
BLUE = (91, 155, 213)
ORANGE = (237, 125, 49)
AMBER = (255, 192, 0)
GREEN = (112, 173, 71)
RED = (196, 32, 32)
VIOLET = (168, 122, 220)

# color names usable in powerup_colors
COLOR_NAMES = {
    "red": (222, 62, 62),
    "blue": (78, 150, 232),
    "green": (86, 196, 108),
    "gold": (240, 190, 60),
    "yellow": (240, 214, 70),
    "purple": (170, 110, 220),
    "cyan": (80, 210, 216),
    "orange": (240, 140, 50),
    "white": WHITE,
    "pink": (238, 120, 180),
}

# --- entities ---------------------------------------------------------------
SHIP_W, SHIP_H = 34, 30
BULLET_W, BULLET_H = 4, 12
ASTEROID_MIN, ASTEROID_MAX = 18, 34
POWERUP_SIZE = 16

BASE_WAVE_DELAY = 150       # frames between two waves when nothing is set
INVULN_FRAMES = 90          # invulnerability after a hit

# --- Internal spawn settings (engine only) ----------------------------------
# Default values for asteroid spawning. The scatter randomness and the
# swarm management stay inside Core/: neither student_config nor
# student_rules expose them.
SPAWN_INTERVAL = 55         # frames between two asteroid spawns
MAX_ASTEROIDS = 6           # max number of asteroids on screen at once
SPAWN_MARGIN = 40           # side margin for the X scatter
RELOAD_FALLBACK = 90        # fallback reload delay (frames) at 0 ammo
BONUS_AMMO_REFILL = 15      # ammo given back by an "ammo" bonus

# --- Visible damage (chapter 5+) --------------------------------------------
ASTEROID_HP = 3             # hit points of an asteroid from chapter 5
DAMAGE_POPUP_FRAMES = FPS // 2  # how long a damage value stays on screen
HIT_FLASH_FRAMES = 8        # white flash of an asteroid hit but not destroyed
GOLD = (255, 204, 0)        # color of the damage values
