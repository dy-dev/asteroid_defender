# Convention : les import se placent en tête de fichier.
import random

# =====================================================================
#  student_config.py
#
#  Seul fichier à remplir. Il se remplit au fil des séances : chaque
#  ligne déjà écrite reste, les nouvelles s'ajoutent en dessous.
#
#  -------------------------------------------------------------------
#  Comment écrire un réglage
#  -------------------------------------------------------------------
#
#  Un réglage tient sur une seule ligne, toujours de la même forme :
#
#      nom = valeur
#
#  À gauche, le nom du réglage. À droite, la valeur à lui donner.
#
#  Le texte s'écrit entre guillemets, les nombres s'écrivent sans :
#
#      nom = "du texte entre guillemets"
#      nom = 12
#
#  Un nombre placé entre guillemets devient du texte : le jeu ne peut
#  plus s'en servir comme d'une quantité.
#
#  -------------------------------------------------------------------
#  Où trouver les noms
#  -------------------------------------------------------------------
#
#  Aucun nom n'est donné ici : ils se découvrent dans le jeu.
#  Mettre la partie en pause avec Échap, puis survoler un élément à
#  l'écran : le vaisseau, le bandeau du haut, la zone de jeu. Chaque
#  élément affiche les réglages disponibles, leur nom exact, leur type
#  et leur effet.
#
#  Le nom se recopie à la lettre près : mêmes lettres, même casse,
#  mêmes underscores. Un nom mal orthographié n'active rien, et le jeu
#  continue de tourner sans erreur.
#
#  -------------------------------------------------------------------
#  Voir le résultat
#  -------------------------------------------------------------------
#
#  Écrire la ligne, enregistrer le fichier, puis relancer Core/main.py.
#  L'effet apparaît au lancement suivant.
#
#  Le jeu se lance toujours depuis Core/main.py, jamais depuis ce
#  fichier.
# =====================================================================

# nom affiché dans le HUD
# Le texte est une suite de caractères : on en prend une portion.
full_name = "Nova Starfighter"
player_name = full_name[:4]

# --- Chapitre 6 : afficher et demander --------------------------------
# Ces deux lignes s'executent au lancement, avant l'ouverture de la fenetre.
print("Bienvenue dans Asteroid Defender")
player_name = input("Quel est ton nom de pilote ? ")


# titre affiché en haut de la fenêtre
window_title = f"Asteroid Defender - pilote {player_name}"

# nombre de munitions : le vaisseau peut tirer
nb_ammo = 40

# vitesse de déplacement du vaisseau
ship_speed = 6

# vitesse des projectiles
bullet_speed = 9.0

# nombre de vies au départ
starting_lives = 3

# points de base d'un astéroïde
base_hit_points = 10

# multiplicateur appliqué au ramassage du bonus
bonus_points = 3

# points par tir : un calcul entre variables
points_per_hit = base_hit_points * bonus_points

# le score enchaîné est multiplié par ce nombre
combo_multiplier = 2

# secondes sans tir avant remise à zéro du combo
combo_reset_delay = 3.0

# booléen posé : affiche l'overlay de débogage
show_debug = True

# booléen résultant : mode difficile si moins de 3 vies
is_hard = starting_lives < 3

# seuil au-delà duquel le HUD change
highlight_score = 1000

# seuil sous lequel une alerte s'affiche
low_ammo_threshold = 5

# tous les N points, un bonus apparaît
bonus_threshold = 500

# durée du multiplicateur, en secondes
bonus_duration = 5.0

# --- Chapitre 5 : les collections et le hasard ---------------------------

# Une liste : les couleurs des bonus qui tombent en jeu.
powerup_colors = ["red", "blue", "green"]
powerup_colors.append("pink")

# Un dictionnaire simple : l'effet de chaque couleur de bonus.
# Une couleur absente du dictionnaire donne un bonus qui rend une vie.
powerup_effects = {
    "red": "heal",
    "blue": "ammo_refill",
    "green": "shield_up",
}
powerup_effects["pink"] = "rapid_fire"

# Un dictionnaire de dictionnaires : chaque arme associée à ses caractéristiques.
# Touche Tab pour passer d'une arme à l'autre.
weapons = {
    "laser": {"damage": 1, "cooldown": 8},
    "canon": {"damage": 3, "cooldown": 30},
    "mitraille": {"damage": 1, "cooldown": 3},
}

# Un ensemble : les armes accessibles, sans doublon possible.
unlocked_weapons = {"laser", "canon"}

# Un tuple : la position de départ, qui ne doit pas changer.
# L'abscisse est tirée au hasard à chaque lancement.
start_position = (random.randint(100, 700), 510)

# --- Chapitre 6 : les fonctions ------------------------------------------
# Le jeu appelle ces fonctions au moment où il en a besoin.
# Chacune est définie une seule fois, mais appelée pendant toute la partie.

def hud_text(name, score, ammo):
    """Compose la ligne d'information du haut de l'écran."""
    return f"{name} | Score : {score} | Munitions : {ammo}"

def game_over_text(name, score):
    """Compose le message de fin de partie."""
    return f"Fin de partie, {name} : {score} points"

def difficulty_level(score):
    """Renvoie le palier de difficulté selon le score."""
    if score < 1000:
        return "easy"
    elif score < 3000:
        return "normal"
    else:
        return "hard"

def should_keep_firing(ammo, trigger_held):
    """Autorise le tir s'il reste des munitions et que la touche est tenue."""
    return ammo > 0 and trigger_held

def damage(base, multiplier=1.0):
    """Dégâts infligés ; le multiplicateur est facultatif."""
    return int(base * multiplier)

def spawn_pattern(wave):
    """Nombre d'ennemis et vitesse pour la vague indiquée."""
    count = 3 + wave
    speed = 2.0 + wave * 0.3
    return count, speed

# --- Chapitre 7 : portée, modification, récursion -------------------------

# Difficulté générale : multiplie la vitesse de toutes les vagues.
GLOBAL_DIFFICULTY = 1.0

def harder(level):
    """Renvoie une difficulté plus élevée (forme sans global)."""
    return level * 1.5

GLOBAL_DIFFICULTY = harder(GLOBAL_DIFFICULTY)

# Une liste reçue par une fonction peut être modifiée.
def add_gold(colors):
    """Ajoute une couleur à la liste reçue : la liste d'origine change."""
    colors.append("gold")

add_gold(powerup_colors)

# Un nombre reçu par une fonction ne peut pas être modifié.
def try_refill(n):
    """Renvoie le nombre augmenté ; il faut réaffecter pour que ça compte."""
    return n + 50

nb_ammo = try_refill(nb_ammo)

# Version récursive : remplace la boucle du chapitre 6.
def spawn_row(n):
    """Positions de n ennemis, construites par récursion."""
    if n == 0:
        return []
    return spawn_row(n - 1) + [60 + ((n - 1) * 110) % 680]
