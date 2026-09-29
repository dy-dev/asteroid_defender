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
