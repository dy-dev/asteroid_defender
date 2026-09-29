"""
i18n.py - Display language for every on-screen text.
LOCKED: do not modify.

The language comes from Core/language.py, which holds a single line:
LANGUAGE = "fr" or LANGUAGE = "en". A missing file, a missing name or
an unknown value falls back to French, without any error.

Every displayed text lives in TEXTS, with one version per language.
t(key) returns the version of the current language.
"""

import importlib
import sys

SUPPORTED = ("fr", "en")
DEFAULT = "fr"


def _read_language():
    """Reads LANGUAGE from Core/language.py. Never raises."""
    try:
        if "language" in sys.modules:
            module = importlib.reload(sys.modules["language"])
        else:
            module = importlib.import_module("language")
        value = getattr(module, "LANGUAGE", DEFAULT)
    except Exception:  # noqa: BLE001 - a broken file must not stop the game
        return DEFAULT
    if isinstance(value, str) and value.strip().lower() in SUPPORTED:
        return value.strip().lower()
    return DEFAULT


LANGUAGE = _read_language()


def pick(versions):
    """Returns the current-language entry of a {"fr": ..., "en": ...} dict."""
    if not isinstance(versions, dict):
        return versions
    return versions.get(LANGUAGE, versions.get(DEFAULT, ""))


def t(key, **values):
    """Text of `key` in the current language, formatted with `values`.
    An unknown key is returned as is, so a typo never crashes the game."""
    entry = TEXTS.get(key)
    if entry is None:
        return key
    msg = pick(entry)
    if values:
        try:
            return msg.format(**values)
        except (KeyError, IndexError, ValueError):
            return msg
    return msg


TEXTS = {
    # --- window and defaults ---------------------------------------------
    "default_title": {
        "fr": "TITRE DU JEU (à changer dans student_config.py)",
        "en": "GAME TITLE (to change in student_config.py)",
    },
    "default_player_name": {
        "fr": "??? (à définir)",
        "en": "??? (to be set)",
    },
    "default_hud_line": {
        "fr": "{name}   Score : {score}   Munitions : {ammo}",
        "en": "{name}   Score: {score}   Ammo: {ammo}",
    },
    "missing_hud_text": {
        "fr": "HUD : hud_text() à écrire",
        "en": "HUD: hud_text() to write",
    },
    "missing_game_over_text": {
        "fr": "Fin de partie : game_over_text() à écrire",
        "en": "Game over: game_over_text() to write",
    },
    "default_game_over_line": {
        "fr": "{name} — Partie terminée — score : {score}",
        "en": "{name} — Game over — score: {score}",
    },

    # --- catalog types ----------------------------------------------------
    "kind_variable": {"fr": "variable", "en": "variable"},
    "kind_function": {"fr": "fonction", "en": "function"},
    "kind_object": {"fr": "objet", "en": "object"},

    # --- hoverable zones --------------------------------------------------
    "zone_ship": {"fr": "LE VAISSEAU", "en": "THE SHIP"},
    "zone_hud": {"fr": "LE BANDEAU (HUD)", "en": "THE TOP BAR (HUD)"},
    "zone_field": {"fr": "LA ZONE DE JEU", "en": "THE PLAY AREA"},
    "zone_asteroid": {"fr": "UN ASTÉROÏDE", "en": "AN ASTEROID"},
    "zone_bonus": {"fr": "UN BONUS", "en": "A BONUS"},

    # --- HUD --------------------------------------------------------------
    "hud_wave": {"fr": "vague {wave}", "en": "wave {wave}"},
    "hud_weapon": {"fr": "arme : {name}", "en": "weapon: {name}"},
    "alert_magazine_empty": {"fr": "! CHARGEUR VIDE", "en": "! MAGAZINE EMPTY"},
    "alert_low_ammo": {"fr": "! MUNITIONS BASSES", "en": "! LOW AMMO"},
    "alert_critical": {"fr": "!! ÉTAT CRITIQUE !!", "en": "!! CRITICAL STATE !!"},
    "reloading": {"fr": "rechargement", "en": "reloading"},
    "countdown_go": {"fr": "GO !", "en": "GO!"},

    # --- debug overlay ----------------------------------------------------
    "debug_title": {"fr": "DEBUG", "en": "DEBUG"},
    "debug_score": {"fr": "score", "en": "score"},
    "debug_ammo": {"fr": "munitions", "en": "ammo"},
    "debug_lives": {"fr": "vies", "en": "lives"},
    "debug_points_per_hit": {"fr": "points/tir", "en": "points/hit"},
    "debug_combo": {"fr": "combo", "en": "combo"},
    "debug_bonus": {"fr": "bonus actif", "en": "active bonus"},
    "debug_charge": {"fr": "charge", "en": "charge"},
    "debug_fired": {"fr": "tirs partis", "en": "shots fired"},
    "debug_iterations": {"fr": "tours", "en": "turns"},
    "debug_damage": {"fr": "dégâts", "en": "damage"},
    "debug_colours": {"fr": "couleurs", "en": "colours"},

    # --- game over --------------------------------------------------------
    "game_over_title": {"fr": "PARTIE TERMINÉE", "en": "GAME OVER"},
    "high_scores": {"fr": "MEILLEURS SCORES", "en": "HIGH SCORES"},
    "game_over_keys": {
        "fr": "R : rejouer     Échap : quitter",
        "en": "R: replay     Esc: quit",
    },
    "ship_destroyed": {"fr": "Vaisseau détruit", "en": "Ship destroyed"},
    "game_frozen": {
        "fr": "Le jeu est figé.  R : relancer",
        "en": "The game is frozen.  R: restart",
    },
    "start_hint": {
        "fr": "Échap : carte des notions    ←/→ : bouger    Espace : tirer",
        "en": "Esc: concept map    ←/→: move    Space: fire",
    },
    "start_hint_ch4": {
        "fr": "Échap : carte des notions    ←/→ : bouger    Espace : tirer    B : rafale",
        "en": "Esc: concept map    ←/→: move    Space: fire    B: burst",
    },

    # --- pause screen -----------------------------------------------------
    "pause_title": {"fr": "PAUSE", "en": "PAUSE"},
    "pause_intro_variables": {
        "fr": "Survoler un élément du jeu pour voir les variables à coder dessus",
        "en": "Hover over a game element to see the variables to code on it",
    },
    "pause_intro_states": {
        "fr": "Survoler un élément pour voir les états à lire dans les règles",
        "en": "Hover over an element to see the states to read in the rules",
    },
    "pause_intro_loops": {
        "fr": "Survoler un élément pour voir les états à lire et les répétitions",
        "en": "Hover over an element to see the states to read and the repetitions",
    },
    "config_problem": {
        "fr": "student_config.py : {problem}",
        "en": "student_config.py: {problem}",
    },
    "config_problem_help": {
        "fr": "Le jeu continue en ignorant les lignes fautives, pour ne pas bloquer. "
              "L'erreur reste à corriger.",
        "en": "The game keeps running and ignores the faulty lines. "
              "The error still needs fixing.",
    },
    "config_more": {"fr": "(+{n} autre(s))", "en": "(+{n} more)"},
    "config_banner_footer": {
        "fr": "Le jeu continue : seules les lignes fautives sont ignorées. "
              "Détail en pause (Échap).",
        "en": "The game keeps running: only the faulty lines are ignored. "
              "Details in pause (Esc).",
    },
    "config_hint_rules": {
        "fr": "une condition s'écrit dans student_rules.py, pas dans la configuration",
        "en": "a condition goes in student_rules.py, not in the configuration",
    },
    "error_syntax": {
        "fr": "erreur de syntaxe ligne {line} ({msg}) : {code}",
        "en": "syntax error on line {line} ({msg}): {code}",
    },
    "error_name": {
        "fr": "ligne {line} : nom inconnu « {name} » : {code}",
        "en": "line {line}: unknown name '{name}': {code}",
    },
    "error_runtime": {
        "fr": "erreur ligne {line} ({kind}) : {code}",
        "en": "error on line {line} ({kind}): {code}",
    },
    "error_runtime_noline": {
        "fr": "erreur au chargement ({kind})",
        "en": "error while loading ({kind})",
    },
    "resume": {"fr": "Échap : reprendre", "en": "Esc: resume"},
    "copied": {"fr": "« {name} » copié", "en": "'{name}' copied"},

    # --- help panel -------------------------------------------------------
    "help_title": {"fr": "COMMENT JOUER", "en": "HOW TO PLAY"},
    "help_move": {
        "fr": "Déplacement : flèches gauche / droite",
        "en": "Move: left / right arrows",
    },
    "help_fire": {"fr": "Tir : barre Espace", "en": "Fire: Space bar"},
    "help_charged": {
        "fr": "Tir chargé : maintenir Espace, puis relâcher",
        "en": "Charged shot: hold Space, then release",
    },
    "help_burst": {"fr": "Rafale : touche B", "en": "Burst fire: B key"},
    "help_gold": {
        "fr": "Bonus doré : le score monte plus vite",
        "en": "Gold bonus: the score rises faster",
    },
    "help_cyan": {
        "fr": "Bonus cyan : les munitions remontent",
        "en": "Cyan bonus: the ammo refills",
    },
    "help_green": {
        "fr": "Bonus vert : un cran de bouclier en plus",
        "en": "Green bonus: one more shield level",
    },
    "help_shield": {
        "fr": "Bouclier : absorbe un coup par cran.",
        "en": "Shield: absorbs one hit per level.",
    },
    "help_magazine": {
        "fr": "Chargeur vide : rechargement automatique.",
        "en": "Empty magazine: automatic reload.",
    },

    # --- tooltip ----------------------------------------------------------
    "tooltip_bonus_tag": {"fr": "(bonus)", "en": "(bonus)"},
    "tooltip_readable": {
        "fr": "À LIRE dans les règles :",
        "en": "TO READ in the rules:",
    },
    "tooltip_all_done": {
        "fr": "Tout est fait ici. Bravo !",
        "en": "Everything is done here. Well done!",
    },
    "tooltip_copy_one": {
        "fr": "Touche C : copier le nom",
        "en": "C key: copy the name",
    },
    "tooltip_copy_many": {
        "fr": "Chiffres du haut du clavier : copier le nom",
        "en": "Top-row digit keys: copy the name",
    },
    "tooltip_loops": {
        "fr": "RÉPÉTITIONS dans student_loops.py :",
        "en": "REPETITIONS in student_loops.py:",
    },
    "tooltip_provides": {"fr": "fournit : {states}", "en": "provides: {states}"},

    # --- student_loops.py errors (chapter 4, red banner) ------------------
    # {error} is the raw Python message: it stays as Python writes it.
    "loop_banner_block": {
        "fr": "bloc \"{name}\" ({label}) : {error}",
        "en": "block \"{name}\" ({label}): {error}",
    },
    "loop_banner_footer": {
        "fr": "Le jeu continue : seule la boucle fautive a été arrêtée.",
        "en": "The game keeps running: only the faulty loop was stopped.",
    },
    "loop_error_setup": {
        "fr": "erreur avant la boucle : {error}",
        "en": "error before the loop: {error}",
    },
    "loop_error_range": {
        "fr": "erreur dans la plage de la boucle : {error}",
        "en": "error in the loop range: {error}",
    },
    "loop_error_body": {
        "fr": "erreur dans le corps de la boucle : {error}",
        "en": "error in the loop body: {error}",
    },
    "loop_error_limit": {
        "fr": "la boucle a dépassé {limit} tours : boucle infinie ? "
              "Le moteur l'a arrêtée.",
        "en": "the loop went past {limit} turns: infinite loop? "
              "The engine stopped it.",
    },
    "loop_error_syntax": {
        "fr": "erreur de syntaxe ligne {line} : {msg}",
        "en": "syntax error on line {line}: {msg}",
    },

    # --- startup checks (Core/main.py, printed in the console) ------------
    "py_wrong_title": {
        "fr": "MAUVAISE VERSION DE PYTHON",
        "en": "WRONG PYTHON VERSION",
    },
    "py_wrong_body": {
        "fr": "  Ce projet demande Python {min} à {max}.\n"
              "  L'environnement utilise Python {cur}.\n\n"
              "  pygame ne s'installe pas sur les versions trop récentes.\n\n"
              "  À FAIRE :\n"
              "   1. Supprimer l'environnement virtuel actuel (dossier .venv).\n"
              "   2. Le recréer avec Python {max} (PyCharm : Add Interpreter\n"
              "      > Virtualenv > Base interpreter).\n"
              "   3. Réinstaller les dépendances : "
              "python -m pip install -r requirements.txt\n",
        "en": "  This project needs Python {min} to {max}.\n"
              "  The environment uses Python {cur}.\n\n"
              "  pygame does not install on versions that are too recent.\n\n"
              "  TO DO:\n"
              "   1. Delete the current virtual environment (.venv folder).\n"
              "   2. Create it again with Python {max} (PyCharm: Add Interpreter\n"
              "      > Virtualenv > Base interpreter).\n"
              "   3. Install the dependencies again: "
              "python -m pip install -r requirements.txt\n",
    },
    "py_wrong_window": {
        "fr": "Asteroid Defender — version de Python",
        "en": "Asteroid Defender — Python version",
    },
    "pygame_missing": {
        "fr": "  pygame n'est pas installé dans cet environnement.\n",
        "en": "  pygame is not installed in this environment.\n",
    },
    "pygame_install": {
        "fr": "  Installer les dépendances :\n"
              "     python -m pip install -r requirements.txt\n",
        "en": "  Install the dependencies:\n"
              "     python -m pip install -r requirements.txt\n",
    },
}
