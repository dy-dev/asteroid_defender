"""
config.py — Réglages internes du moteur.
VERROUILLÉ : ne pas modifier. Les réglages du jeu se font dans
student_config.py, à la racine du projet.
"""

WIDTH = 800
HEIGHT = 600
FPS = 60

DEFAULT_TITLE = "TITRE DU JEU (a changer dans student_config.py)"
DEFAULT_START = (WIDTH // 2, HEIGHT - 50)

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

# noms de couleurs utilisables dans powerup_colors
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

# --- entités ---------------------------------------------------------------
SHIP_W, SHIP_H = 34, 30
BULLET_W, BULLET_H = 4, 12
ASTEROID_MIN, ASTEROID_MAX = 18, 34
POWERUP_SIZE = 16

BASE_WAVE_DELAY = 150       # frames entre deux vagues quand rien n'est réglé
INVULN_FRAMES = 90          # invincibilité après un dégât
