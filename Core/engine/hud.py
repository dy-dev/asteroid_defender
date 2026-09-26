"""
hud.py - Display: HUD, screens, and the pause screen.
LOCKED: do not modify.

In pause, hovering over a game element (the ship, the top bar, the
play area...) opens a tooltip listing the variables of student_config.py
that concern it: exact name, type and effect. Only the entries of the
current chapter and the previous ones appear, and a variable already
written disappears from the tooltip.
"""

import pygame

from engine import assets
from engine import config as C
from engine.i18n import pick, t


# ----------------------------------------------------------------------
#  Catalog of the variables revealed in pause.
#  Each entry: exact name, label, type, effect, chapter, zone.
#   - label and effect: one version per language ({"fr": ..., "en": ...})
#   - type: "variable", "function" or "object"
#   - chapter: shown only if CURRENT_CHAPTER >= this number
#     (99 = not revealed)
#   - zone: element to hover over: "ship", "hud" (top bar),
#     "field" (play area), "asteroid", "bonus"
# ----------------------------------------------------------------------
CATALOG = [
    ("window_title",
     {"fr": "Titre de la fenêtre", "en": "Window title"},
     "variable",
     {"fr": "Donne un titre à la fenêtre du jeu", "en": "Gives the game window a title"},
     1, "hud"),
    ("player_name",
     {"fr": "Nom du joueur", "en": "Player name"},
     "variable",
     {"fr": "Le nom du joueur s'affiche dans le HUD", "en": "The player's name appears in the HUD"},
     1, "hud"),
    ("nb_ammo",
     {"fr": "Munitions", "en": "Ammunition"},
     "variable",
     {"fr": "Le vaisseau peut tirer", "en": "The ship can fire"},
     1, "ship"),
    ("ship_speed",
     {"fr": "Vitesse du vaisseau", "en": "Ship speed"},
     "variable",
     {"fr": "Le vaisseau se déplace", "en": "The ship moves"},
     1, "ship"),
    ("bullet_speed",
     {"fr": "Vitesse des tirs", "en": "Bullet speed"},
     "variable",
     {"fr": "Règle la vitesse des projectiles", "en": "Sets the speed of the bullets"},
     1, "ship"),
    ("starting_lives",
     {"fr": "Nombre de vies", "en": "Number of lives"},
     "variable",
     {"fr": "Fixe le nombre de vies au départ", "en": "Sets the number of lives at the start"},
     1, "ship"),

    ("base_hit_points",
     {"fr": "Points de base", "en": "Base points"},
     "variable",
     {"fr": "Définit les points rapportés par un astéroïde détruit",
      "en": "Sets the points earned for each asteroid destroyed"},
     2, "asteroid"),
    ("points_per_hit",
     {"fr": "Points par tir", "en": "Points per hit"},
     "variable",
     {"fr": "Résultat de base_hit_points × bonus_points",
      "en": "Result of base_hit_points × bonus_points"},
     2, "asteroid"),
    ("combo_multiplier",
     {"fr": "Multiplicateur de combo", "en": "Combo multiplier"},
     "variable",
     {"fr": "Amplifie le score quand les tirs s'enchaînent",
      "en": "Boosts the score when hits follow one another"},
     2, "hud"),
    ("combo_reset_delay",
     {"fr": "Délai de combo", "en": "Combo delay"},
     "variable",
     {"fr": "Secondes sans tir avant remise à zéro du combo",
      "en": "Seconds without firing before the combo resets"},
     2, "hud"),
    ("show_debug",
     {"fr": "Affichage debug", "en": "Debug display"},
     "variable",
     {"fr": "Affiche à l'écran les valeurs importantes du moment",
      "en": "Shows the key values of the moment on screen"},
     2, "hud"),
    ("is_hard",
     {"fr": "Mode difficile", "en": "Hard mode"},
     "variable",
     {"fr": "Résultat de starting_lives < 3 ; mode plus exigeant",
      "en": "Result of starting_lives < 3; a more demanding mode"},
     2, "hud"),
    ("highlight_score",
     {"fr": "Score de mise en avant", "en": "Highlight score"},
     "variable",
     {"fr": "Seuil au-delà duquel le HUD change d'aspect",
      "en": "Threshold above which the HUD changes appearance"},
     2, "hud"),
    ("low_ammo_threshold",
     {"fr": "Seuil munitions basses", "en": "Low ammo threshold"},
     "variable",
     {"fr": "Seuil sous lequel une alerte de munitions s'affiche",
      "en": "Threshold below which a low ammo alert appears"},
     2, "ship"),
    ("bonus_threshold",
     {"fr": "Seuil de bonus", "en": "Bonus threshold"},
     "variable",
     {"fr": "Tous les N points, un bonus apparaît", "en": "Every N points, a bonus appears"},
     2, "hud"),
    ("bonus_points",
     {"fr": "Multiplicateur de bonus", "en": "Bonus multiplier"},
     "variable",
     {"fr": "Multiplie temporairement les points au ramassage",
      "en": "Multiplies the points for a while once picked up"},
     2, "bonus"),
    ("bonus_duration",
     {"fr": "Durée du bonus", "en": "Bonus duration"},
     "variable",
     {"fr": "Durée en secondes du multiplicateur de bonus",
      "en": "Duration in seconds of the bonus multiplier"},
     2, "bonus"),

    # --- Reserve: chapter 99, not revealed yet -------------------------
    ("friendly_fire",
     {"fr": "Tir allié", "en": "Friendly fire"},
     "variable",
     {"fr": "Les tirs du joueur peuvent le toucher", "en": "The player's bullets can hit the ship"},
     99, "ship"),
    ("difficulty_level",
     {"fr": "Paliers de difficulté", "en": "Difficulty tiers"},
     "function",
     {"fr": "La difficulté s'adapte au score", "en": "The difficulty adapts to the score"},
     99, "field"),
    ("spawn_row",
     {"fr": "Formations d'ennemis", "en": "Enemy formations"},
     "function",
     {"fr": "Les ennemis arrivent en rangées", "en": "Enemies arrive in rows"},
     99, "field"),
    ("reload_time",
     {"fr": "Temps de rechargement", "en": "Reload time"},
     "variable",
     {"fr": "L'arme se recharge après épuisement", "en": "The weapon reloads once empty"},
     99, "ship"),
    ("start_countdown",
     {"fr": "Compte à rebours", "en": "Countdown"},
     "variable",
     {"fr": "Un 3-2-1 au début de la partie", "en": "A 3-2-1 at the start of the game"},
     99, "hud"),
    ("should_keep_firing",
     {"fr": "Autorisation de tir", "en": "Fire permission"},
     "function",
     {"fr": "Décide quand le tir est permis", "en": "Decides when firing is allowed"},
     99, "ship"),
    ("hud_text",
     {"fr": "Texte du HUD", "en": "HUD text"},
     "function",
     {"fr": "Compose la ligne d'infos en haut", "en": "Builds the information line at the top"},
     99, "hud"),
    ("game_over_text",
     {"fr": "Texte de fin", "en": "End text"},
     "function",
     {"fr": "Le message de l'écran de fin", "en": "The message of the end screen"},
     99, "hud"),
    ("powerup_colors",
     {"fr": "Couleurs des bonus", "en": "Bonus colors"},
     "variable",
     {"fr": "Colore les power-ups", "en": "Colors the power-ups"},
     99, "field"),
    ("start_position",
     {"fr": "Position de départ", "en": "Start position"},
     "variable",
     {"fr": "Où le vaisseau apparaît", "en": "Where the ship appears"},
     99, "ship"),
    ("weapons",
     {"fr": "Armes disponibles", "en": "Available weapons"},
     "variable",
     {"fr": "Plusieurs armes sélectionnables", "en": "Several selectable weapons"},
     99, "ship"),
    ("damage",
     {"fr": "Calcul des dégâts", "en": "Damage calculation"},
     "function",
     {"fr": "Paramètre les dégâts infligés", "en": "Sets the damage dealt"},
     99, "ship"),
    ("spawn_pattern",
     {"fr": "Composition des vagues", "en": "Wave composition"},
     "function",
     {"fr": "Nombre et vitesse par vague", "en": "Number and speed for each wave"},
     99, "field"),
    ("GLOBAL_DIFFICULTY",
     {"fr": "Difficulté globale", "en": "Overall difficulty"},
     "variable",
     {"fr": "Réglage global de la difficulté", "en": "Overall difficulty setting"},
     99, "field"),
    ("powerups",
     {"fr": "Bonus personnalisés", "en": "Custom bonuses"},
     "object",
     {"fr": "Les power-ups, en objets", "en": "The power-ups, as objects"},
     99, "field"),
    ("weapon",
     {"fr": "Arme encapsulée", "en": "Encapsulated weapon"},
     "object",
     {"fr": "Une arme qui gère son cooldown", "en": "A weapon that manages its cooldown"},
     99, "ship"),
    ("enemy_types",
     {"fr": "Bestiaire d'ennemis", "en": "Enemy bestiary"},
     "variable",
     {"fr": "Des ennemis aux comportements variés", "en": "Enemies with varied behaviors"},
     99, "field"),
    ("save_highscore",
     {"fr": "Sauvegarde des scores", "en": "Score saving"},
     "function",
     {"fr": "Les scores survivent à la partie", "en": "Scores outlive the game"},
     99, "hud"),
    ("load_highscores",
     {"fr": "Lecture des scores", "en": "Score reading"},
     "function",
     {"fr": "Affiche les meilleurs scores", "en": "Shows the high scores"},
     99, "hud"),
]

# Visual bonus missions. Each one appears from the chapter where the
# element it decorates is in play, then follows the same rules as the
# catalog.
BONUS = [
    ("ship_sprite",
     {"fr": "Image du vaisseau", "en": "Ship image"},
     "variable",
     {"fr": "Une image à la place du vaisseau", "en": "A picture in place of the ship"},
     1, "ship"),
    ("bullet_sprite",
     {"fr": "Image des tirs", "en": "Bullet image"},
     "variable",
     {"fr": "Une image pour les projectiles", "en": "A picture for the bullets"},
     1, "ship"),
    ("background_image",
     {"fr": "Image de fond", "en": "Background image"},
     "variable",
     {"fr": "Un décor en fond d'écran", "en": "A backdrop behind the game"},
     1, "hud"),
    ("enemy_sprite",
     {"fr": "Image des ennemis", "en": "Enemy image"},
     "variable",
     {"fr": "Une image pour les ennemis", "en": "A picture for the enemies"},
     5, "field"),
    ("powerup_sprite",
     {"fr": "Image des bonus", "en": "Power-up image"},
     "variable",
     {"fr": "Une image pour les power-ups", "en": "A picture for the power-ups"},
     8, "field"),
    ("asteroid_sprite",
     {"fr": "Image d'astéroïde", "en": "Asteroid image"},
     "variable",
     {"fr": "Remplace l'image des astéroïdes", "en": "Replaces the picture of the asteroids"},
     2, "asteroid"),
    ("bonus_sprite",
     {"fr": "Image de bonus", "en": "Bonus image"},
     "variable",
     {"fr": "Remplace l'image des bonus", "en": "Replaces the picture of the bonuses"},
     2, "bonus"),
]

# Hoverable zones: rectangles computed at display time (see game.py).
ZONE_KEYS = {
    "ship": "zone_ship",
    "hud": "zone_hud",
    "field": "zone_field",
    "asteroid": "zone_asteroid",
    "bonus": "zone_bonus",
}


def zone_label(zone):
    key = ZONE_KEYS.get(zone)
    return t(key) if key else zone.upper()


def kind_label(kind):
    return t("kind_" + kind)


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


# Top bar layout: gap between items, and right limit of the left part
# (the wave text starts at C.WIDTH - 150).
HUD_GAP = 40
HUD_RIGHT = C.WIDTH - 150 - 20


def _fit(font, msg, width):
    """msg cut with an ellipsis so that it is at most `width` px wide
    ("" when not even the ellipsis fits)."""
    msg = str(msg)
    if font.size(msg)[0] <= width:
        return msg
    while msg and font.size(msg + "…")[0] > width:
        msg = msg[:-1]
    return msg + "…" if font.size("…")[0] <= width else ""


def draw_hud(surf, fonts, state):
    """Top bar: HUD text, lives, wave."""
    # Chapter 2: hud_highlight changes the look of the bar.
    # Chapter 3: the hud_danger rule output turns it red.
    danger = getattr(state, "rule_outputs", {}).get("hud_danger", False)
    highlight = getattr(state, "hud_highlight", False)
    if danger:
        bg, line_col = C.PANEL, C.RED
    elif highlight:
        bg, line_col = C.PANEL, C.AMBER
    else:
        bg, line_col = C.DARK, C.BLUE
    pygame.draw.rect(surf, bg, (0, 0, C.WIDTH, 34))
    pygame.draw.line(surf, line_col, (0, 34), (C.WIDTH, 34), 2)

    # Left part of the bar: HUD line, then player rank and shield label
    # (chapter 3 rule outputs). Each item starts HUD_GAP px after the
    # measured end of the previous one and never goes past HUD_RIGHT,
    # which keeps clear of the wave and the lives. An item that does
    # not fit is cut with an ellipsis: the shield label first, then
    # the rank.
    outputs = getattr(state, "rule_outputs", {})
    rank = str(outputs.get("player_rank", "") or "")
    shield_lbl = str(outputs.get("shield_label", "") or "")

    line = _fit(fonts.reg, state.hud_line, HUD_RIGHT - 10)
    x = 10 + text(surf, fonts.reg, line, 10, 8).width

    items = [(it, col) for it, col in ((rank, C.AMBER), (shield_lbl, C.GREEN)) if it]
    ellipsis = fonts.small.size("…")[0]
    for i, (item, col) in enumerate(items):
        x += HUD_GAP
        room = HUD_RIGHT - x
        later = items[i + 1:]
        # whole if it leaves room for the next items, or at least for
        # their ellipsis; otherwise cut to the room left, and stop there
        min_later = sum(HUD_GAP + ellipsis for _ in later)
        if fonts.small.size(item)[0] > room - min_later:
            item = _fit(fonts.small, item, room)
            if item:
                text(surf, fonts.small, item, x, 11, col)
            break
        x += text(surf, fonts.small, item, x, 11, col).width

    # name tease (chapter 3: name_tease rule output)
    tease = getattr(state, "rule_outputs", {}).get("name_tease", "")
    if tease:
        tw = fonts.tiny.size(str(tease))[0]
        text(surf, fonts.tiny, str(tease), (C.WIDTH - tw) // 2, C.HEIGHT - 44, C.GREY)

    # lives, on the right
    for i in range(max(0, state.ship.lives)):
        x = C.WIDTH - 18 - i * 18
        pygame.draw.polygon(surf, C.RED,
                            [(x, 10), (x - 7, 24), (x, 20), (x + 7, 24)])

    text(surf, fonts.small, t("hud_wave", wave=state.wave), C.WIDTH - 150, 11, C.GREY)

    # low ammo alert (chapter 2) or empty magazine (chapter 3 rule output)
    empty = getattr(state, "rule_outputs", {}).get("show_empty_alert", False)
    if getattr(state, "low_ammo_alert", False) or empty:
        msg = t("alert_magazine_empty") if empty else t("alert_low_ammo")
        text(surf, fonts.small, msg, C.WIDTH // 2 - 90, 42, C.ORANGE)

    # critical state (chapter 3 rule output): alert bar
    if getattr(state, "rule_outputs", {}).get("critical_state", False):
        text(surf, fonts.small, t("alert_critical"), C.WIDTH // 2 - 80, 62, C.RED)


# Quantities shown by the debug overlay, with the chapter from which
# each one is displayed.
DEBUG_ROWS = [
    ("debug_score", "score", 1),
    ("debug_ammo", "ammo", 1),
    ("debug_lives", "lives", 1),
    ("debug_points_per_hit", "points_per_hit", 2),
    ("debug_combo", "combo", 2),
    ("debug_bonus", "bonus_mult", 2),
    ("debug_charge", "charge", 4),
    ("debug_fired", "fired", 4),
    ("debug_iterations", "iterations", 4),
]


def draw_debug_overlay(surf, fonts, state, current_chapter):
    """show_debug overlay: the quantities of the current chapter and the
    previous ones."""
    rows = [(t(lbl), key) for lbl, key, ch in DEBUG_ROWS if ch <= current_chapter]
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
    text(surf, fonts.small, t("debug_title"), x + pad, y + pad, C.AMBER)
    cy = y + pad + 22
    for lbl, key in rows:
        val = state.debug_value(key)
        text(surf, fonts.tiny, lbl, x + pad, cy, C.GREY)
        text(surf, fonts.tiny, str(val), x + w - pad - 70, cy, C.WHITE)
        cy += 22


def draw_countdown(surf, fonts, value):
    # the value comes from the student's loop: it may be a float, or
    # something that is not a number at all
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        value = 0
    shown = f"{value:g}" if isinstance(value, float) else str(value)
    label = t("countdown_go") if value <= 0 else shown
    color = C.GREEN if value <= 0 else C.AMBER
    text(surf, fonts.big, label, C.WIDTH // 2, C.HEIGHT // 2, color, center=True)


def draw_loop_error(surf, fonts, msg):
    """Chapter 4: error banner for student_loops.py (infinite loop cut by
    the safety net, error in a loop body, syntax error). The game goes
    on: the faulty loop is simply stopped."""
    lines = _wrap(fonts.small, msg, C.WIDTH - 60)
    h = 14 + 20 * len(lines) + 18
    y = C.HEIGHT - h - 140      # above the ship and its charge bar
    panel = pygame.Surface((C.WIDTH - 24, h), pygame.SRCALPHA)
    panel.fill((70, 18, 18, 230))
    surf.blit(panel, (12, y))
    pygame.draw.rect(surf, C.RED, (12, y, C.WIDTH - 24, h), 2, border_radius=6)
    cy = y + 8
    for line in lines:
        text(surf, fonts.small, line, 24, cy, (255, 170, 170))
        cy += 20
    text(surf, fonts.tiny, t("loop_banner_footer"), 24, cy + 2, (220, 180, 180))


def _wrap(font, msg, width):
    """Splits msg into lines no wider than width (word by word)."""
    words, lines, cur = str(msg).split(" "), [], ""
    for word in words:
        candidate = (cur + " " + word).strip()
        if font.size(candidate)[0] <= width or not cur:
            cur = candidate
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_reloading(surf, fonts, ratio):
    w = 180
    x = C.WIDTH // 2 - w // 2
    y = C.HEIGHT - 40
    pygame.draw.rect(surf, C.PANEL, (x, y, w, 12), border_radius=6)
    pygame.draw.rect(surf, C.ORANGE, (x, y, int(w * ratio), 12), border_radius=6)
    text(surf, fonts.small, t("reloading"), C.WIDTH // 2, y - 12, C.GREY, center=True)


def draw_game_over(surf, fonts, state):
    overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 215))
    surf.blit(overlay, (0, 0))

    text(surf, fonts.big, t("game_over_title"), C.WIDTH // 2, 120, C.WHITE, center=True)
    pygame.draw.line(surf, C.BLUE, (150, 165), (C.WIDTH - 150, 165), 2)
    text(surf, fonts.mid, state.game_over_line, C.WIDTH // 2, 200, C.AMBER, center=True)

    if state.highscores:
        text(surf, fonts.small, t("high_scores"), C.WIDTH // 2, 260, C.GREY, center=True)
        y = 288
        for i, entry in enumerate(state.highscores, start=1):
            name = entry.get("name", "?") if isinstance(entry, dict) else "?"
            score = entry.get("score", 0) if isinstance(entry, dict) else entry
            text(surf, fonts.reg, f"{i}.  {name}", C.WIDTH // 2 - 110, y)
            text(surf, fonts.reg, str(score), C.WIDTH // 2 + 70, y, C.AMBER)
            y += 26

    text(surf, fonts.small, t("game_over_keys"),
         C.WIDTH // 2, C.HEIGHT - 60, C.GREY, center=True)


# ----------------------------------------------------------------------
#  Pause screen: hoverable zones and tooltips
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
#  States readable in student_rules.py (chapter 3+).
#  From chapter 3, the tooltip also lists the states the engine injects
#  into student_rules.py. Each entry:
#    exact injected name, meaning ({"fr": ..., "en": ...}), usage,
#    chapter, zone
#  The displayed name is exactly the injected name.
# ----------------------------------------------------------------------
READABLE_STATES = [
    ("lives",
     {"fr": "Nombre de vies restantes", "en": "Number of lives left"},
     "rules", 3, "ship"),
    ("ammo",
     {"fr": "Munitions courantes", "en": "Current ammunition"},
     "rules", 3, "ship"),
    ("shield",
     {"fr": "Niveau de bouclier (0 à 3)", "en": "Shield level (0 to 3)"},
     "rules", 3, "ship"),
    ("score",
     {"fr": "Score courant", "en": "Current score"},
     "rules", 3, "hud"),
    ("combo",
     {"fr": "Niveau de combo (1 = pas d'enchaînement)", "en": "Combo level (1 = no chain)"},
     "rules", 3, "hud"),
    ("active_bonus",
     {"fr": "Multiplicateur du bonus doré, ou None", "en": "Gold bonus multiplier, or None"},
     "rules", 3, "hud"),
    ("player_name",
     {"fr": "Nom du joueur (chaîne, définie en config)",
      "en": "Player name (string, set in the config)"},
     "rules", 3, "hud"),
]


# ----------------------------------------------------------------------
#  Loop events (chapter 4+): the live file student_loops.py.
#  An event is neither a variable to create nor a state to read: it is a
#  block to write, "if event == name:", holding one loop. Each entry:
#    exact event name, label, states provided in the block, effect,
#    chapter, zone
#  Event and state names are EXACTLY those the engine uses: they are
#  never translated.
# ----------------------------------------------------------------------
LOOP_EVENTS = [
    ("countdown",
     {"fr": "Décompte de départ", "en": "Start countdown"},
     ("countdown",),
     {"fr": "Fait défiler le décompte avant le début de la partie",
      "en": "Runs the countdown before the round starts"},
     4, "ship"),
    ("charging",
     {"fr": "Tir chargé", "en": "Charged shot"},
     ("charge", "charge_rate", "max_charge"),
     {"fr": "Fait monter la puissance du tir tant que la touche est tenue",
      "en": "Builds up shot power while the key is held"},
     4, "ship"),
    ("burst",
     {"fr": "Rafale", "en": "Burst fire"},
     ("burst_count", "fired"),
     {"fr": "Envoie plusieurs projectiles l'un après l'autre (touche B)",
      "en": "Sends several projectiles one after another (B key)"},
     4, "ship"),
]


def loop_event_label(name):
    """Label of a loop event, in lower case, for the error banner."""
    for n, label, _states, _effect, _chap, _zone in LOOP_EVENTS:
        if n == name:
            return pick(label).lower()
    return name


def loop_events(current_chapter, zone, written=()):
    """Loop events to show for a zone, from chapter 4. An event already
    written in student_loops.py disappears from the tooltip."""
    return [(n, pick(label), states, pick(effect))
            for n, label, states, effect, chap, z in LOOP_EVENTS
            if z == zone and chap <= current_chapter and n not in written]


def readable_states(current_chapter, zone):
    """States readable in student_rules.py for a zone, from chapter 3."""
    out = []
    for name, sense, usage, chap, z in READABLE_STATES:
        if z != zone or chap > current_chapter:
            continue
        out.append((name, pick(sense), usage))
    return out


def visible_entries(features, current_chapter, zone):
    """Entries to reveal for a zone.

    Only the entries that:
      - belong to the current chapter or a previous one,
      - are not written yet (the tooltip empties as variables get
        written),
      - are attached to this zone.
    Bonus missions follow the same rule.
    """
    todo = []
    for name, label, kind, effect, chap, z in CATALOG:
        if z != zone or chap > current_chapter:
            continue
        if features.unlocked.get(name):
            continue
        todo.append((name, pick(label), kind_label(kind), pick(effect), False))
    bonus = []
    for name, label, kind, effect, chap, z in BONUS:
        if z != zone or chap > current_chapter:
            continue
        if features.unlocked.get(name):
            continue
        bonus.append((name, pick(label), kind_label(kind), pick(effect), True))
    return todo, bonus


def draw_pause(surf, fonts, features, current_chapter, zones, mouse_pos,
               written_events=()):
    """Pause overlay, zone frames and tooltip on hover.

    `zones`: dict zone -> pygame.Rect (provided by game.py).
    `written_events`: loop events already written in student_loops.py.
    """
    overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 180))
    surf.blit(overlay, (0, 0))

    text(surf, fonts.mid, t("pause_title"), 24, 16)
    if current_chapter >= 4:
        intro = t("pause_intro_loops")
    elif current_chapter >= 3:
        intro = t("pause_intro_states")
    else:
        intro = t("pause_intro_variables")
    text(surf, fonts.small, intro, 24, 54, C.GREY)

    # error message from student_config.py, if any
    if features.problem:
        pygame.draw.rect(surf, (60, 20, 20), (24, 80, C.WIDTH - 48, 46),
                         border_radius=4)
        text(surf, fonts.small, t("config_problem", problem=features.problem),
             34, 86, (255, 150, 150))
        text(surf, fonts.tiny, t("config_problem_help"),
             34, 106, (220, 180, 180))

    # frames around the hoverable zones
    hovered_zone = None
    for zone, rect in zones.items():
        is_hover = rect.collidepoint(mouse_pos)
        col = C.AMBER if is_hover else C.LINE
        width = 3 if is_hover else 1
        pygame.draw.rect(surf, col, rect, width, border_radius=8)
        text(surf, fonts.tiny, zone_label(zone), rect.x + 6, rect.y - 18,
             C.AMBER if is_hover else C.GREY)
        if is_hover:
            hovered_zone = zone

    # help box (controls, bonuses, reload), bottom right
    _draw_help_panel(surf, fonts, current_chapter)

    text(surf, fonts.small, t("resume"), 24, C.HEIGHT - 30, C.GREY)

    copyable = []
    if hovered_zone:
        todo, bonus = visible_entries(features, current_chapter, hovered_zone)
        states = readable_states(current_chapter, hovered_zone)
        events = loop_events(current_chapter, hovered_zone, written_events)
        copyable = _draw_zone_tooltip(surf, fonts, hovered_zone, todo, bonus,
                                      mouse_pos, states, events)

    # "copied" feedback (the game sets _copied_flash after a copy)
    flash = getattr(features, "_copied_flash", None)
    if flash:
        name, frames = flash
        if frames > 0:
            msg = t("copied", name=name)
            tw = fonts.small.size(msg)[0]
            bx = (C.WIDTH - tw) // 2 - 16
            pygame.draw.rect(surf, C.GREEN, (bx, C.HEIGHT - 70, tw + 32, 30),
                             border_radius=6)
            text(surf, fonts.small, msg, bx + 16, C.HEIGHT - 64, (10, 20, 12))

    return copyable


def _draw_help_panel(surf, fonts, current_chapter=1):
    """Help box: controls, meaning of the bonuses, automatic reload."""
    ch4 = current_chapter >= 4
    pw, ph = 340, 214 + (34 if ch4 else 0)
    px = C.WIDTH - pw - 20
    py = C.HEIGHT - ph - 20
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((22, 32, 43, 235))
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, C.BLUE, (px, py, pw, ph), 1, border_radius=8)
    pygame.draw.line(surf, C.BLUE, (px + 14, py + 34), (px + pw - 14, py + 34), 1)

    text(surf, fonts.small, t("help_title"), px + 14, py + 12, C.AMBER)

    y = py + 44
    lines = [
        (t("help_move"), C.WHITE),
        (t("help_fire"), C.WHITE),
    ]
    if ch4:
        lines += [
            (t("help_charged"), C.WHITE),
            (t("help_burst"), C.WHITE),
        ]
    first_bonus = len(lines) + 1
    lines += [
        ("", C.WHITE),
        (t("help_gold"), None),    # None -> gold dot
        (t("help_cyan"), None),    # None -> cyan dot
        (t("help_green"), None),   # None -> green dot
        ("", C.WHITE),
        (t("help_shield"), C.GREY),
        (t("help_magazine"), C.GREY),
    ]
    dot_colors = {first_bonus: C.COLOR_NAMES["gold"],
                  first_bonus + 1: C.COLOR_NAMES["cyan"],
                  first_bonus + 2: C.COLOR_NAMES["green"]}
    for i, (line, col) in enumerate(lines):
        if not line:
            y += 8
            continue
        if col is None:
            # bonus line: small colored dot in front
            pygame.draw.rect(surf, dot_colors[i], (px + 14, y + 3, 9, 9), border_radius=2)
            text(surf, fonts.tiny, line, px + 30, y, C.WHITE)
        else:
            text(surf, fonts.tiny, line, px + 14, y, col)
        y += 17


def _draw_zone_tooltip(surf, fonts, zone, todo, bonus, mouse_pos, states=None,
                       events=None):
    """Tooltip of a zone. Three kinds of lines:
      - the variables to write (todo/bonus, chapters 1 and 2);
      - the states to read in student_rules.py (states, chapter 3+);
      - the loop events to write in student_loops.py (events, chapter 4+).
    Returns the ordered list of copyable names (variables, states, then
    events), so that keys 1..9 copy the matching name."""
    states = states or []
    events = events or []

    lines = []          # (text, color, font)
    lines.append((zone_label(zone), C.AMBER, fonts.small))

    copyable = []       # copyable names, in display order

    # 1) variables to write
    for name, label, kind, effect, is_bonus in todo:
        copyable.append(name)
        lines.append((f"{len(copyable)}. {name}", C.WHITE, fonts.reg))
        lines.append((f"   {kind} · {effect}", C.GREY, fonts.tiny))
    for name, label, kind, effect, is_bonus in bonus:
        copyable.append(name)
        lines.append((f"{len(copyable)}. {name}  {t('tooltip_bonus_tag')}", C.VIOLET, fonts.reg))
        lines.append((f"   {kind} · {effect}", C.GREY, fonts.tiny))

    # 2) states to read in student_rules.py (chapter 3+)
    if states:
        lines.append((t("tooltip_readable"), C.BLUE, fonts.tiny))
        for name, sense, usage in states:
            copyable.append(name)
            lines.append((f"{len(copyable)}. {name}", C.WHITE, fonts.reg))
            lines.append((f"   {sense}", C.GREY, fonts.tiny))

    # 3) loop events to write in student_loops.py (chapter 4+)
    if events:
        lines.append((t("tooltip_loops"), C.VIOLET, fonts.tiny))
        for name, label, ev_states, effect in events:
            copyable.append(name)
            lines.append((f"{len(copyable)}. {name}", C.WHITE, fonts.reg))
            lines.append((f"   {label} · {effect}", C.GREY, fonts.tiny))
            lines.append(("   " + t("tooltip_provides", states=", ".join(ev_states)),
                          C.GREY, fonts.tiny))

    if not copyable:
        lines.append((t("tooltip_all_done"), C.GREEN, fonts.small))
    elif len(copyable) == 1:
        lines.append((t("tooltip_copy_one"), C.BLUE, fonts.tiny))
    else:
        lines.append((t("tooltip_copy_many"), C.BLUE, fonts.tiny))

    # dimensions
    pad = 12
    w = max(font.size(line)[0] for line, _, font in lines) + pad * 2
    w = min(max(w, 240), C.WIDTH - 20)
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
    for line, col, font in lines:
        text(surf, font, line, x + pad, cy, col)
        cy += 28 if font is fonts.reg else (18 if font is fonts.tiny else 24)

    return copyable
