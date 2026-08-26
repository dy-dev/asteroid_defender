# =====================================================================
#  student_config.py — CORRECTION du chapitre 1
#
#  Ceci est le corrigé attendu à la fin de la séance 1 : les six
#  variables de prise en main, chacune commentée. L'étudiant les
#  découvre en survolant le vaisseau et le bandeau du haut (Échap).
#
#  Le jeu se lance depuis Core/main.py, jamais depuis ce fichier.
# =====================================================================


# --- Sur le bandeau du haut (HUD) ---

# titre affiché en haut de la fenêtre du jeu
window_title = "Mon Asteroid Defender"

# nom du joueur, affiché plus tard dans le HUD
player_name = "Nova"


# --- Sur le vaisseau ---

# nombre de munitions : le vaisseau peut désormais tirer
nb_ammo = 25

# vitesse de déplacement du vaisseau
ship_speed = 6

# vitesse des projectiles (nombre à virgule → un point, pas une virgule)
bullet_speed = 9.0

# nombre de vies au départ de la partie
starting_lives = 2