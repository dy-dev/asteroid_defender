"""
hud.py — Affichage : HUD, écrans, et mode pause pédagogique.
VERROUILLÉ : ne pas modifier.

En pause, l'étudiant survole les éléments du jeu (le vaisseau, le HUD,
la zone des ennemis…). Chaque zone révèle, dans une info-bulle, les
variables à écrire dans student_config.py qui la concernent : nom exact,
effet, et type. Seules les notions du chapitre courant apparaissent, et
une variable déjà réussie disparaît de la bulle — la liste se vide au fur
et à mesure des réussites.
"""

import pygame

from engine import assets
from engine import config as C


# ----------------------------------------------------------------------
#  Catalogue des notions.
#  Chaque entrée : nom exact, libellé, type, effet visible, chapitre, zone.
#   - chapitre : la notion n'apparaît que si CURRENT_CHAPTER >= ce numéro
#                (0 = mission bonus, toujours visible)
#   - zone     : quel élément survoler pour la voir
#                "ship" (vaisseau) · "hud" (bandeau du haut) ·
#                "field" (zone de jeu / ennemis) · "any"
# ----------------------------------------------------------------------
CATALOG = [
    # nom,              libellé,                  type,       effet,                                      chap, zone
    ("window_title",    "Titre de la fenêtre",    "variable", "Donne un titre à la fenêtre du jeu",        1, "hud"),
    ("player_name",     "Nom du joueur",          "variable", "Ton nom s'affiche dans le HUD",             1, "hud"),
    ("nb_ammo",         "Munitions",              "variable", "Le vaisseau peut tirer",                    1, "ship"),
    ("ship_speed",      "Vitesse du vaisseau",    "variable", "Le vaisseau se déplace",                    1, "ship"),
    ("bullet_speed",    "Vitesse des tirs",       "variable", "Règle la vitesse des projectiles",          1, "ship"),
    ("starting_lives",  "Nombre de vies",         "variable", "Fixe le nombre de vies au départ",          1, "ship"),

    ("base_hit_points", "Points de base",        "variable", "Définit les points rapportés par un astéroïde détruit", 2, "asteroid"),
    ("points_per_hit",  "Points par tir",         "variable", "Résultat de base_hit_points × bonus_points", 2, "asteroid"),
    ("combo_multiplier","Multiplicateur de combo","variable", "Amplifie le score quand les tirs s'enchaînent", 2, "hud"),
    ("combo_reset_delay","Délai de combo",        "variable", "Secondes sans tir avant remise à zéro du combo", 2, "hud"),
    ("show_debug",      "Affichage debug",        "variable", "Affiche à l'écran les valeurs importantes du moment", 2, "hud"),
    ("is_hard",         "Mode difficile",         "variable", "Résultat de starting_lives < 3 ; mode plus exigeant", 2, "hud"),
    ("highlight_score", "Score de mise en avant", "variable", "Seuil au-delà duquel le HUD change d'aspect", 2, "hud"),
    ("low_ammo_threshold","Seuil munitions basses","variable", "Seuil sous lequel une alerte de munitions s'affiche", 2, "ship"),
    ("bonus_threshold", "Seuil de bonus",         "variable", "Tous les N points, un bonus apparaît", 2, "hud"),
    ("bonus_points",    "Multiplicateur de bonus","variable", "Multiplie temporairement les points au ramassage", 2, "bonus"),
    ("bonus_duration",  "Durée du bonus",         "variable", "Durée en secondes du multiplicateur de bonus", 2, "bonus"),

    # --- RÉSERVE (ancien découpage 15) -------------------------------
    # Ces variables sont conservées mais mises HORS du découpage 12
    # (chapitre 99 = jamais révélé, quel que soit CURRENT_CHAPTER).
    # Le nouveau plan est organisé par NOTION Python, pas par feature de
    # jeu ; chaque variable sera reclassée sur son chapitre cible lors de
    # la conception du chapitre concerné, via son handoff.
    #
    # Plan cible 12 chapitres :
    #   Ch3  Les conditions        (if/elif/else)
    #   Ch4  Les boucles           (while, for)
    #   Ch5  Types composés & import (chaînes, listes, dict, import)
    #   Ch6  Fonctions 1/2         (définition, paramètres, retour)
    #   Ch7  Fonctions 2/2         (portée, valeur/référence, récursivité)
    #   Ch8  Classes 1/2           (classes/instances, attributs, méthodes)
    #   Ch9  Classes 2/2           (héritage, polymorphisme, méth/attr classe)
    #   Ch10 Debug & exceptions    (try/except/raise)
    #   Ch11 Les fichiers          (open/read/write, CSV, JSON)
    #   Ch12 Bibliothèques & projet (module, package, pip + appli finale)
    #
    # Candidats naturels (à confirmer en conception) :
    #   difficulty_level, should_keep_firing, spawn_row/spawn_pattern, damage -> fonctions (Ch6/7)
    #   weapons, weapon, powerups, enemy_types, start_position -> classes/objets (Ch8/9)
    #   save_highscore, load_highscores -> fichiers (Ch11)
    #   GLOBAL_DIFFICULTY, powerup_colors -> import/bibliothèques (Ch5/12)
    ("friendly_fire",   "Tir allié",              "variable", "Tes tirs peuvent te toucher",               99, "ship"),
    ("difficulty_level","Paliers de difficulté",  "fonction", "La difficulté s'adapte au score",           99, "field"),
    ("spawn_row",       "Formations d'ennemis",   "fonction", "Les ennemis arrivent en rangées",           99, "field"),
    ("reload_time",     "Temps de rechargement",  "variable", "L'arme se recharge après épuisement",        99, "ship"),
    ("start_countdown", "Compte à rebours",       "variable", "Un 3-2-1 au début de la partie",            99, "hud"),
    ("should_keep_firing","Autorisation de tir",  "fonction", "Décide quand le tir est permis",            99, "ship"),
    ("hud_text",        "Texte du HUD",           "fonction", "Compose la ligne d'infos en haut",          99, "hud"),
    ("game_over_text",  "Texte de fin",           "fonction", "Le message de l'écran de fin",              99, "hud"),
    ("powerup_colors",  "Couleurs des bonus",     "variable", "Colore les power-ups",                      99, "field"),
    ("start_position",  "Position de départ",     "variable", "Où le vaisseau apparaît",                   99, "ship"),
    ("weapons",         "Armes disponibles",      "variable", "Plusieurs armes sélectionnables",           99, "ship"),
    ("damage",          "Calcul des dégâts",      "fonction", "Paramètre les dégâts infligés",             99, "ship"),
    ("spawn_pattern",   "Composition des vagues", "fonction", "Nombre et vitesse par vague",               99, "field"),
    ("GLOBAL_DIFFICULTY","Difficulté globale",    "variable", "Règle global de difficulté",               99, "field"),
    ("powerups",        "Bonus personnalisés",    "objet",    "Tes power-ups, en objets",                 99, "field"),
    ("weapon",          "Arme encapsulée",        "objet",    "Une arme qui gère son cooldown",           99, "ship"),
    ("enemy_types",     "Bestiaire d'ennemis",    "variable", "Des ennemis aux comportements variés",     99, "field"),
    ("save_highscore",  "Sauvegarde des scores",  "fonction", "Les scores survivent à la partie",         99, "hud"),
    ("load_highscores", "Lecture des scores",     "fonction", "Affiche les meilleurs scores",             99, "hud"),
]

# Missions bonus visuelles. Chacune est rattachée au chapitre où la
# notion qui la rend légitime est acquise — elle NE doit jamais donner
# d'avance sur une notion future :
#   - ship_sprite / bullet_sprite / background_image : de la chaîne de
#     caractères + un chemin, acquis au chapitre 1 → dispo dès le ch. 1.
#   - enemy_sprite : n'a de sens qu'une fois les ennemis introduits
#     (formations, séance 5) → chapitre 5.
#   - powerup_sprite : n'a de sens qu'avec les power-ups (collections,
#     séance 8) → chapitre 8.
# Elles suivent ensuite la progressivité normale (comme toute notion).
BONUS = [
    ("ship_sprite",     "Image du vaisseau", "variable", "Ton image à la place du vaisseau",  1, "ship"),
    ("bullet_sprite",   "Image des tirs",    "variable", "Ton image pour les projectiles",    1, "ship"),
    ("background_image","Image de fond",     "variable", "Ton décor en fond d'écran",         1, "hud"),
    ("enemy_sprite",    "Image des ennemis", "variable", "Ton image pour les ennemis",        5, "field"),
    ("powerup_sprite",  "Image des bonus",   "variable", "Ton image pour les power-ups",      8, "field"),
    ("asteroid_sprite", "Image d'astéroïde", "variable", "Remplace l'image des astéroïdes",   2, "asteroid"),
    ("bonus_sprite",    "Image de bonus",    "variable", "Remplace l'image des bonus",        2, "bonus"),
]

# Zones survolables : rectangles calculés à l'affichage (voir game.py).
ZONE_LABELS = {
    "ship": "LE VAISSEAU",
    "hud": "LE BANDEAU (HUD)",
    "field": "LA ZONE DE JEU",
    "asteroid": "UN ASTÉROÏDE",
    "bonus": "UN BONUS",
}


class Fonts:
    def __init__(self):
        pygame.font.init()
        self.big = pygame.font.SysFont("consolas,dejavusansmono,monospace", 42, bold=True)
        self.mid = pygame.font.SysFont("consolas,dejavusansmono,monospace", 24, bold=True)
        self.reg = pygame.font.SysFont("consolas,dejavusansmono,monospace", 17)
        self.small = pygame.font.SysFont("consolas,dejavusansmono,monospace", 14)
        self.tiny = pygame.font.SysFont("consolas,dejavusansmono,monospace", 12)


def text(surf, font, msg, x, y, color=C.WHITE, center=False):
    img = font.render(str(msg), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surf.blit(img, rect)
    return rect


def draw_hud(surf, fonts, state):
    """Bandeau du haut : texte du HUD, vies, vague."""
    # HUD de mise en avant (chapitre 2) : le bandeau change d'aspect
    bg = C.PANEL if getattr(state, "hud_highlight", False) else C.DARK
    pygame.draw.rect(surf, bg, (0, 0, C.WIDTH, 34))
    line_col = C.AMBER if getattr(state, "hud_highlight", False) else C.BLUE
    pygame.draw.line(surf, line_col, (0, 34), (C.WIDTH, 34), 2)

    text(surf, fonts.reg, state.hud_line, 10, 8)

    # vies, à droite
    for i in range(max(0, state.ship.lives)):
        x = C.WIDTH - 18 - i * 18
        pygame.draw.polygon(surf, C.RED,
                            [(x, 10), (x - 7, 24), (x, 20), (x + 7, 24)])

    text(surf, fonts.small, f"vague {state.wave}", C.WIDTH - 150, 11, C.GREY)

    # alerte munitions basses (chapitre 2)
    if getattr(state, "low_ammo_alert", False):
        text(surf, fonts.small, "! MUNITIONS BASSES", C.WIDTH // 2 - 90, 42, C.ORANGE)


# grandeurs affichables par l'overlay debug, avec le chapitre où elles
# deviennent pertinentes (progressivité : jamais avant leur notion).
DEBUG_ROWS = [
    ("score", "score", 1),
    ("munitions", "ammo", 1),
    ("vies", "lives", 1),
    ("points/tir", "points_per_hit", 2),
    ("combo", "combo", 2),
    ("bonus actif", "bonus_mult", 2),
]


def draw_debug_overlay(surf, fonts, state, current_chapter):
    """Overlay show_debug : affiche les grandeurs pertinentes du moment.
    Filtré par la progressivité : n'affiche pas une grandeur d'une notion
    non encore vue."""
    rows = [(lbl, key) for lbl, key, ch in DEBUG_ROWS if ch <= current_chapter]
    if not rows:
        return
    pad = 8
    w = 210
    h = pad * 2 + len(rows) * 22 + 22
    x, y = 10, 44
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((14, 21, 32, 210))
    surf.blit(panel, (x, y))
    pygame.draw.rect(surf, C.LINE, (x, y, w, h), 1, border_radius=6)
    text(surf, fonts.small, "DEBUG", x + pad, y + pad, C.AMBER)
    cy = y + pad + 22
    for lbl, key in rows:
        val = state.debug_value(key)
        text(surf, fonts.tiny, lbl, x + pad, cy, C.GREY)
        text(surf, fonts.tiny, str(val), x + w - pad - 70, cy, C.WHITE)
        cy += 22


def draw_countdown(surf, fonts, value):
    label = "GO !" if value <= 0 else str(value)
    color = C.GREEN if value <= 0 else C.AMBER
    text(surf, fonts.big, label, C.WIDTH // 2, C.HEIGHT // 2, color, center=True)


def draw_reloading(surf, fonts, ratio):
    w = 180
    x = C.WIDTH // 2 - w // 2
    y = C.HEIGHT - 40
    pygame.draw.rect(surf, C.PANEL, (x, y, w, 12), border_radius=6)
    pygame.draw.rect(surf, C.ORANGE, (x, y, int(w * ratio), 12), border_radius=6)
    text(surf, fonts.small, "rechargement", C.WIDTH // 2, y - 12, C.GREY, center=True)


def draw_game_over(surf, fonts, state):
    overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 215))
    surf.blit(overlay, (0, 0))

    text(surf, fonts.big, "PARTIE TERMINÉE", C.WIDTH // 2, 120, C.WHITE, center=True)
    pygame.draw.line(surf, C.BLUE, (150, 165), (C.WIDTH - 150, 165), 2)
    text(surf, fonts.mid, state.game_over_line, C.WIDTH // 2, 200, C.AMBER, center=True)

    if state.highscores:
        text(surf, fonts.small, "MEILLEURS SCORES", C.WIDTH // 2, 260, C.GREY, center=True)
        y = 288
        for i, entry in enumerate(state.highscores, start=1):
            name = entry.get("name", "?") if isinstance(entry, dict) else "?"
            score = entry.get("score", 0) if isinstance(entry, dict) else entry
            text(surf, fonts.reg, f"{i}.  {name}", C.WIDTH // 2 - 110, y)
            text(surf, fonts.reg, str(score), C.WIDTH // 2 + 70, y, C.AMBER)
            y += 26

    text(surf, fonts.small, "R : rejouer     Échap : quitter",
         C.WIDTH // 2, C.HEIGHT - 60, C.GREY, center=True)


# ----------------------------------------------------------------------
#  Mode pause : zones survolables + info-bulles
# ----------------------------------------------------------------------

def visible_entries(features, current_chapter, zone):
    """Notions à révéler pour une zone donnée, filtrées par progressivité.

    On ne montre que :
      - les notions du chapitre courant ou d'un chapitre précédent
        (jamais d'avance sur une notion future — golden rule),
      - qui ne sont PAS encore réussies (la bulle se vide au fil des
        réussites),
      - rattachées à cette zone.
    Les missions bonus suivent la même règle : chacune n'apparaît qu'à
    partir du chapitre où sa notion support est acquise.
    """
    todo = []
    for name, label, kind, effect, chap, z in CATALOG:
        if z != zone or chap > current_chapter:
            continue
        if features.unlocked.get(name):
            continue
        todo.append((name, label, kind, effect, False))
    bonus = []
    for name, label, kind, effect, chap, z in BONUS:
        if z != zone or chap > current_chapter:
            continue
        if features.unlocked.get(name):
            continue
        bonus.append((name, label, kind, effect, True))
    return todo, bonus


def draw_pause(surf, fonts, features, current_chapter, zones, mouse_pos):
    """Voile de pause + surbrillance des zones + info-bulle au survol.

    `zones` : dict zone -> pygame.Rect (fournis par game.py).
    """
    overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 180))
    surf.blit(overlay, (0, 0))

    text(surf, fonts.mid, "PAUSE", 24, 16)
    text(surf, fonts.small,
         "Survole un élément du jeu pour voir ce que tu peux coder dessus",
         24, 54, C.GREY)

    # message d'erreur éventuel du fichier étudiant
    if features.problem:
        pygame.draw.rect(surf, (60, 20, 20), (24, 80, C.WIDTH - 48, 26),
                         border_radius=4)
        text(surf, fonts.small, f"student_config.py : {features.problem}",
             34, 86, (255, 150, 150))

    # cadre les zones survolables
    hovered_zone = None
    for zone, rect in zones.items():
        is_hover = rect.collidepoint(mouse_pos)
        col = C.AMBER if is_hover else C.LINE
        width = 3 if is_hover else 1
        pygame.draw.rect(surf, col, rect, width, border_radius=8)
        label = ZONE_LABELS.get(zone, zone.upper())
        text(surf, fonts.tiny, label, rect.x + 6, rect.y - 18,
             C.AMBER if is_hover else C.GREY)
        if is_hover:
            hovered_zone = zone

    text(surf, fonts.small, "Échap : reprendre",
         24, C.HEIGHT - 30, C.GREY)

    if hovered_zone:
        todo, bonus = visible_entries(features, current_chapter, hovered_zone)
        _draw_zone_tooltip(surf, fonts, hovered_zone, todo, bonus, mouse_pos)


def _draw_zone_tooltip(surf, fonts, zone, todo, bonus, mouse_pos):
    """Info-bulle listant, pour une zone, les notions à coder."""
    zone_label = ZONE_LABELS.get(zone, zone.upper())

    lines = []          # (texte, couleur, police)
    lines.append((zone_label, C.AMBER, fonts.small))

    if not todo and not bonus:
        lines.append(("Tout est fait ici. Bravo !", C.GREEN, fonts.small))
    else:
        for name, label, kind, effect, is_bonus in todo:
            lines.append((f"{name}", C.WHITE, fonts.reg))
            lines.append((f"   {kind} · {effect}", C.GREY, fonts.tiny))
        for name, label, kind, effect, is_bonus in bonus:
            lines.append((f"{name}  (bonus)", C.VIOLET, fonts.reg))
            lines.append((f"   {kind} · {effect}", C.GREY, fonts.tiny))

    # dimensions
    pad = 12
    w = max(font.size(t)[0] for t, _, font in lines) + pad * 2
    w = min(max(w, 240), C.WIDTH - 20)
    line_h = 24
    h = pad * 2 + sum(28 if f is fonts.reg else (18 if f is fonts.tiny else 24)
                      for _, _, f in lines)

    x = mouse_pos[0] + 16
    y = mouse_pos[1] + 16
    if x + w > C.WIDTH - 8:
        x = mouse_pos[0] - w - 16
    if y + h > C.HEIGHT - 8:
        y = C.HEIGHT - h - 8
    x = max(8, x)
    y = max(8, y)

    pygame.draw.rect(surf, C.DARK, (x, y, w, h), border_radius=8)
    pygame.draw.rect(surf, C.AMBER, (x, y, w, h), 2, border_radius=8)

    cy = y + pad
    for t, col, font in lines:
        text(surf, font, t, x + pad, cy, col)
        cy += 28 if font is fonts.reg else (18 if font is fonts.tiny else 24)
