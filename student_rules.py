# student_rules.py — le fichier vivant des règles
#
# Ce fichier est relu à chaque instant pendant la partie. Les conditions
# ci-dessous décident de ce qui se passe selon l'état courant du jeu.
# Aucune fonction ici : uniquement des conditions.
#
# États disponibles (à lire, découverts en pause sur les éléments du jeu) :
#   lives, ammo, shield, score, combo, active_bonus, player_name

# --- Fin de partie : transforme la fin brute en vrai game over ---------
if lives == 0:
    game_over = True

# --- Alerte chargeur vide ----------------------------------------------
if ammo == 0:
    show_empty_alert = True

# --- Mise en danger du HUD en dernière vie (if / else) -----------------
if lives <= 1:
    hud_danger = True
else:
    hud_danger = False

# --- Rang du joueur selon le score (if / elif / else : intervalles) ----
if score < 500:
    player_rank = "Rookie"
elif score < 2000:
    player_rank = "Ace"
else:
    player_rank = "Legend"

# --- État critique : plus de munitions ET dernière vie (and) -----------
if ammo == 0 and lives == 1:
    critical_state = True
else:
    critical_state = False

# --- Bonus actif : le vaisseau brille pendant l'effet (is None) --------
# active_bonus vaut None quand aucun bonus doré n'est en cours, sinon le
# multiplicateur (ex. 2). Le vaisseau prend une couleur pendant l'effet.
if active_bonus is None:
    ship_glow = ""              # pas de bonus : vaisseau normal
else:
    ship_glow = "yellow"        # bonus actif : le vaisseau devient jaune

# --- Salut selon le nom (in sur une chaîne) -----------------------------
# Teste si un motif appartient au nom du joueur, et répond par un clin d'œil.
if "player" in player_name:
    name_tease = "« player » dans le nom : pas très original"
elif "admin" in player_name:
    name_tease = "Tentative d'accès administrateur repérée"
elif "pro" in player_name:
    name_tease = "Le talent se prouve, il ne se déclare pas"
elif "xx" in player_name:
    name_tease = "Style de l'an 2000 détecté"
elif "noob" in player_name:
    name_tease = "L'humilité est une belle qualité"
else:
    name_tease = ""

# --- Bouclier selon son niveau (match / case : cas discrets) -----------
# Le bouclier prend 4 valeurs exactes : 0, 1, 2, 3.
match shield:
    case 3:
        shield_label = "Bouclier plein"
        shield_color = "cyan"
    case 2:
        shield_label = "Bouclier entamé"
        shield_color = "green"
    case 1:
        shield_label = "Bouclier faible"
        shield_color = "orange"
    case _:
        shield_label = "Sans bouclier"
        shield_color = "red"
