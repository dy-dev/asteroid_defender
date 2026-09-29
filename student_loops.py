# student_loops.py — le fichier des répétitions
#
# Chaque bloc correspond à un événement du jeu. Quand l'événement se
# déclenche, le jeu exécute sa boucle un tour à la fois, étalé dans le
# temps : l'effet de chaque tour apparaît à l'écran.
# Aucune fonction ici : uniquement des boucles dans des blocs d'événement.
#
# Événements disponibles (découverts en pause en survolant le vaisseau) :
#   countdown · charging · burst

# --- Décompte de départ : répéter tant que le compteur n'est pas à zéro ---
if event == "countdown":
    while countdown > 0:
        countdown -= 1

# --- Tir chargé : monter jusqu'au maximum, puis sortir de la boucle -------
if event == "charging":
    while True:
        charge += charge_rate
        if charge >= max_charge:
            break

# --- Rafale : répéter un nombre connu de fois, en sautant un tour sur deux -
if event == "burst":
    for i in range(burst_count):
        if i % 2 == 1:
            continue
        fired += 1
