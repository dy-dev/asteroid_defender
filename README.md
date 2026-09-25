# Asteroid Defender

Projet du cours d'introduction à Python.

## ⚠ Version de Python — à lire en premier

Ce projet demande **Python 3.10 à 3.12** (idéalement **3.12**).

pygame, la bibliothèque du jeu, **ne s'installe pas** sur les versions de
Python les plus récentes (3.13, 3.14) : l'installation essaie de tout
recompiler et échoue. Utiliser Python 3.12.

## Installation (dans l'ordre, sans sauter d'étape)

L'ordre compte. Ouvrir le projet en laissant PyCharm faire aboutit à un
environnement créé tout seul avec la **dernière** version de Python —
celle qui ne marche pas. L'environnement doit être créé manuellement
**avant**.

1. **Créer l'environnement virtuel en Python 3.12.**
   Deux chemins mènent au même écran dans PyCharm, au choix :

   - par les réglages : *Settings → Project → Python Interpreter →
     Add Interpreter → Add Local Interpreter*
   - ou, plus court : cliquer sur le **sélecteur d'interpréteur**, en
     bas à droite de la barre d'état, puis *Add New Interpreter →
     Add Local Interpreter*

   Dans les deux cas, choisir ensuite *Virtualenv Environment → New*,
   puis **Base interpreter : Python 3.12**.
   (Si 3.12 n'apparaît pas, l'installer d'abord — voir plus bas.)

2. **Installer les dépendances** une fois le venv créé et actif :

       python -m pip install -r requirements.txt

3. **Lancer le jeu** : dans le dossier `Core/`, **clic droit sur
   `main.py` → Run 'main'**. Ce clic droit crée automatiquement la
   configuration de lancement ; les fois suivantes, le bouton ▶ en haut
   à droite suffit.

Le jeu se lance **toujours depuis `Core/main.py`**, jamais depuis
`student_config.py`.

### Si Python 3.12 n'est pas sur la machine

Le télécharger sur **python.org/downloads** (choisir la 3.12.x),
l'installer, puis revenir à l'étape 1 : PyCharm proposera 3.12 comme
base interpreter.

## Ce que contient la racine

    asteroid_defender/
    ├── student_config.py   ★ des valeurs, lues une fois au démarrage
    ├── student_rules.py    ★ des règles, relues en permanence
    ├── student_loops.py    ★ des répétitions, jouées quand un événement se déclenche
    ├── images/             visuels perso (mission bonus)
    ├── README.md           ce fichier
    ├── requirements.txt    dépendances (pygame)
    └── Core/               le moteur — VERROUILLÉ, ne pas y toucher

Tout le moteur est rangé dans **Core/**, qui n'a jamais à être ouvert.
Les fichiers de travail sont les trois fichiers `student_*.py`, à la
racine.

## Trouver les noms exacts

Mettre le jeu en pause avec **Échap** : la carte des notions s'affiche.
Elle liste toutes les fonctionnalités, montre celles qui sont déjà
actives, et donne au survol le **nom exact** à écrire dans
`student_config.py`.

Le nom doit être recopié à la lettre près — mêmes lettres, même casse,
mêmes underscores. `nb_ammo` fonctionne, `nbAmmo` ne débloque rien.

La même bulle donne aussi les états à lire dans `student_rules.py`
(rubrique « À LIRE dans les règles ») et les événements à écrire dans
`student_loops.py` (rubrique « RÉPÉTITIONS »).

## Commandes

| Touche | Effet |
|--------|-------|
| ← → | déplacer le vaisseau |
| Espace | tirer |
| Espace maintenu | tir chargé (relâcher pour tirer) |
| B | rafale |
| Tab | changer d'arme |
| Échap | carte des notions / reprendre |
| R | rejouer (écran de fin) |

## Le geste à prendre

Changer une valeur → enregistrer → relancer `Core/main.py` →
observer.
