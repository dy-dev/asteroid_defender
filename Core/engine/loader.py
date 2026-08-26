"""
loader.py — Détection des notions codées par l'étudiant.
VERROUILLÉ : ne pas modifier.

Principe : le moteur n'exige rien. Il regarde ce qui existe dans
student_config.py et adapte le jeu. Si une notion n'est pas encore
codée, un comportement par défaut « dégradé » prend le relais.
Le jeu tourne donc toujours, dès la première séance.
"""

import importlib
import sys

from engine import config as C


# ----------------------------------------------------------------------
#  Import tolérant du fichier étudiant
# ----------------------------------------------------------------------

def import_student_config():
    """Importe student_config.py sans jamais faire planter le jeu.

    Si le fichier contient une erreur de syntaxe ou une exception au
    chargement, on renvoie un module vide : le jeu démarre en mode
    entièrement dégradé et affiche le problème dans le menu pause.
    """
    problem = None
    module = None
    try:
        if "student_config" in sys.modules:
            module = importlib.reload(sys.modules["student_config"])
        else:
            module = importlib.import_module("student_config")
    except SyntaxError as exc:
        problem = f"Erreur de syntaxe ligne {exc.lineno} : {exc.msg}"
    except Exception as exc:  # noqa: BLE001 - on veut vraiment tout attraper
        problem = f"{type(exc).__name__} : {exc}"

    if module is None:
        module = type(sys)("student_config_vide")
    return module, problem


# ----------------------------------------------------------------------
#  Accès sécurisés
# ----------------------------------------------------------------------

def get_value(cfg, name, default, expected=None):
    """Lit une variable de l'étudiant, sinon renvoie le défaut dégradé.

    expected : type ou tuple de types attendus. Si la valeur ne
    correspond pas, on garde le défaut (l'étudiant a écrit quelque
    chose, mais pas du type utilisable — le jeu ne doit pas casser).
    """
    if not hasattr(cfg, name):
        return default, False
    value = getattr(cfg, name)
    if expected is not None and not isinstance(value, expected):
        return default, False
    return value, True


def has_callable(cfg, name):
    """Vrai si l'étudiant a défini une fonction (ou tout appelable)."""
    return callable(getattr(cfg, name, None))


def safe_call(cfg, name, default, *args, **kwargs):
    """Appelle une fonction de l'étudiant en filet de sécurité.

    Si la fonction n'existe pas, plante, ou renvoie None, on retombe
    sur le défaut. L'étudiant ne voit jamais de traceback.
    """
    fn = getattr(cfg, name, None)
    if not callable(fn):
        return default, False
    try:
        result = fn(*args, **kwargs)
    except Exception:  # noqa: BLE001
        return default, False
    if result is None:
        return default, False
    return result, True


# ----------------------------------------------------------------------
#  Normalisation dict / objet
# ----------------------------------------------------------------------
#  Séance 8, l'étudiant décrit ses armes et power-ups avec des dicts.
#  Séance 11-12, il les réécrit en objets. Le moteur doit accepter les
#  deux formes sans rupture pendant toute la transition.

def field(item, name, default=None):
    """Lit un champ, que l'item soit un dict ou un objet."""
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def normalize_powerup(item):
    """Ramène un power-up (dict ou objet PowerUp) à une forme unique."""
    return {
        "color": field(item, "color", "white"),
        "effect": field(item, "effect", "heal"),
        "duration": field(item, "duration", 0),
        "source": item,
    }


def normalize_weapon(name, item):
    """Ramène une arme (dict ou objet Weapon) à une forme unique.

    Un objet Weapon (séance 12) gère lui-même son cooldown via ses
    méthodes : le moteur ne touche jamais à son état interne, il
    appelle can_fire() / fire() / tick(). Un dict (séance 8) n'a pas
    de méthodes : c'est le moteur qui compte le temps à sa place.
    """
    is_object = not isinstance(item, dict) and (
        callable(getattr(item, "fire", None))
        or callable(getattr(item, "can_fire", None))
    )
    return {
        "name": field(item, "name", name),
        "damage": field(item, "damage", field(item, "_damage", 1)),
        "cooldown": field(item, "cooldown", field(item, "_cooldown", 12)),
        "object": item if is_object else None,
    }


# ----------------------------------------------------------------------
#  Chargement complet de la configuration
# ----------------------------------------------------------------------

class StudentFeatures:
    """État de toutes les notions : valeur utilisée + activée ou non.

    `unlocked` sert au menu pause : il affiche à l'étudiant ce qui est
    déjà branché et ce qui reste à coder, avec le nom exact attendu.
    """

    def __init__(self):
        self.cfg = None
        self.problem = None
        self.unlocked = {}

    # -- utilitaires internes -------------------------------------------------
    def _val(self, name, default, expected=None):
        value, ok = get_value(self.cfg, name, default, expected)
        self.unlocked[name] = ok
        return value

    def _fn(self, name):
        ok = has_callable(self.cfg, name)
        self.unlocked[name] = ok
        return ok

    # -- chargement -----------------------------------------------------------
    def load(self):
        self.cfg, self.problem = import_student_config()
        cfg = self.cfg

        # --- Séance 1 & 2 : premières variables ---------------------------
        self.window_title = self._val("window_title", C.DEFAULT_TITLE, str)
        self.player_name = self._val("player_name", "??? (a definir)", str)
        self.nb_ammo = self._val("nb_ammo", 0, (int, float))
        self.ship_speed = self._val("ship_speed", 0, (int, float))
        self.bullet_speed = self._val("bullet_speed", 8.0, (int, float))
        self.starting_lives = self._val("starting_lives", 3, int)

        # --- Séance 3 : score ---------------------------------------------
        self.score_per_hit = self._val("score_per_hit", 0, (int, float))
        self.combo_multiplier = self._val("combo_multiplier", 1, (int, float))
        self.bonus_threshold = self._val("bonus_threshold", 10 ** 9, (int, float))

        # --- Séance 4 : booléens et conditions -----------------------------
        self.friendly_fire = self._val("friendly_fire", False, bool)
        self.has_difficulty = self._fn("difficulty_level")

        # --- Séance 5 : boucle for -----------------------------------------
        self.has_spawn_row = self._fn("spawn_row")

        # --- Séance 6 : boucle while ---------------------------------------
        self.reload_time = self._val("reload_time", 0, (int, float))
        self.start_countdown = self._val("start_countdown", 0, (int, float))
        self.has_keep_firing = self._fn("should_keep_firing")

        # --- Séance 7 : chaînes --------------------------------------------
        self.has_hud_text = self._fn("hud_text")
        self.has_game_over_text = self._fn("game_over_text")

        # --- Séance 8 : collections ----------------------------------------
        self.powerup_colors = self._val("powerup_colors", [], (list, tuple))
        self.start_position = self._val("start_position", C.DEFAULT_START, (tuple, list))
        self.unlocked_weapons = self._val("unlocked_weapons", set(), (set, frozenset))
        raw_weapons = self._val("weapons", {}, dict)

        # --- Séance 9 : fonctions ------------------------------------------
        self.has_damage = self._fn("damage")
        self.has_spawn_pattern = self._fn("spawn_pattern")

        # --- Séance 10 : modules et portée ---------------------------------
        self.global_difficulty = self._val("GLOBAL_DIFFICULTY", 1.0, (int, float))

        # --- Séance 11 : classes -------------------------------------------
        raw_powerups = self._val("powerups", [], (list, tuple))
        self.powerups = [normalize_powerup(p) for p in raw_powerups]

        # --- Séance 12 : encapsulation -------------------------------------
        single_weapon = getattr(cfg, "weapon", None)
        self.unlocked["weapon"] = single_weapon is not None

        # Table d'armes unifiée (dicts de la séance 8 + objet de la 12)
        self.weapons = {}
        for name, item in (raw_weapons or {}).items():
            self.weapons[name] = normalize_weapon(name, item)
        if single_weapon is not None:
            wname = field(single_weapon, "name", "weapon")
            self.weapons[wname] = normalize_weapon(wname, single_weapon)
        if not self.weapons:
            self.weapons = {"laser": {"name": "laser", "damage": 1,
                                      "cooldown": 12, "object": None}}

        # --- Séance 13 : héritage et polymorphisme --------------------------
        raw_types = self._val("enemy_types", [], (list, tuple))
        self.enemy_types = [t for t in raw_types if isinstance(t, type)]

        # --- Séance 14 : fichiers et exceptions ------------------------------
        self.has_save_highscore = self._fn("save_highscore")
        self.has_load_highscores = self._fn("load_highscores")

        # --- Séance 15 : point d'extension libre -----------------------------
        self.has_student_update = self._fn("student_update")
        self.has_student_draw = self._fn("student_draw")

        # --- Bonus (toutes séances) : visuels personnels ---------------------
        # Chemins d'images déclarés par l'étudiant. Absents ou illisibles,
        # le moteur revient au dessin géométrique.
        self.ship_sprite = self._val("ship_sprite", None, str)
        self.enemy_sprite = self._val("enemy_sprite", None, str)
        self.bullet_sprite = self._val("bullet_sprite", None, str)
        self.powerup_sprite = self._val("powerup_sprite", None, str)
        self.background_image = self._val("background_image", None, str)

        return self

    # -- appels aux fonctions étudiantes, toujours protégés -------------------

    def difficulty(self, score):
        value, _ = safe_call(self.cfg, "difficulty_level", "easy", score)
        return value if isinstance(value, str) else "easy"

    def row_positions(self, n):
        default = [C.WIDTH // 2]
        value, ok = safe_call(self.cfg, "spawn_row", default, n)
        if not ok or not isinstance(value, (list, tuple)):
            return default
        clean = [p for p in value if isinstance(p, (int, float))]
        return clean or default

    def keep_firing(self, ammo, trigger_held):
        default = ammo > 0 and trigger_held
        value, ok = safe_call(self.cfg, "should_keep_firing", default,
                              ammo, trigger_held)
        return bool(value) if ok else default

    def hud(self, name, score, ammo):
        default = f"Score: {score}   Ammo: {ammo}"
        value, ok = safe_call(self.cfg, "hud_text", default, name, score, ammo)
        return str(value) if ok else default

    def game_over(self, name, score):
        default = f"Game Over — score : {score}"
        value, ok = safe_call(self.cfg, "game_over_text", default, name, score)
        return str(value) if ok else default

    def compute_damage(self, base, multiplier=1.0):
        value, ok = safe_call(self.cfg, "damage", base, base, multiplier)
        if not ok or not isinstance(value, (int, float)):
            return base
        return int(value)

    def wave_pattern(self, wave):
        default = (1, 2.0)
        value, ok = safe_call(self.cfg, "spawn_pattern", default, wave)
        if not ok:
            return default
        try:
            count, speed = value
            return int(count), float(speed)
        except (TypeError, ValueError):
            return default

    def save_score(self, name, score):
        safe_call(self.cfg, "save_highscore", None, name, score)

    def load_scores(self):
        value, ok = safe_call(self.cfg, "load_highscores", [])
        if not ok or not isinstance(value, (list, tuple)):
            return []
        return list(value)[:C.HIGHSCORE_SHOWN]
