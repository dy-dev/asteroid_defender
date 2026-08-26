# Asteroid Defender

Projet du cours d'introduction à Python.

## ⚠ Version de Python — à lire en premier

Ce projet demande **Python 3.10 à 3.12** (idéalement **3.12**).

pygame, la bibliothèque du jeu, **ne s'installe pas** sur les versions de
Python les plus récentes (3.13, 3.14) : l'installation essaie de tout
recompiler et échoue. Utilise Python 3.12.

## Installation (dans l'ordre, sans sauter d'étape)

L'ordre compte. Si tu ouvres le projet et laisses PyCharm faire, il crée
tout seul un environnement avec la **dernière** version de Python — celle
qui ne marche pas. Tu dois créer l'environnement toi-même **avant**.

1. **Crée l'environnement virtuel en Python 3.12.**
   PyCharm : *Settings → Project → Python Interpreter → Add Interpreter
   → Add Local Interpreter → Virtualenv Environment → New*.
   Choisis **Base interpreter : Python 3.12**.
   (Si 3.12 n'apparaît pas, installe-le d'abord — voir plus bas.)

2. **Installe les dépendances** une fois le venv créé et actif :

       python -m pip install -r requirements.txt

3. **Lance le jeu** : dans le dossier `Core/`, **clic droit sur
   `main.py` → Run 'main'**. Ce clic droit crée automatiquement la
   configuration de lancement ; les fois suivantes, le bouton ▶ en haut
   à droite suffit.

Le jeu se lance **toujours depuis `Core/main.py`**, jamais depuis
`student_config.py`.

### Si Python 3.12 n'est pas sur ta machine

Télécharge-le sur **python.org/downloads** (choisis la 3.12.x), installe,
puis reviens à l'étape 1 : PyCharm proposera 3.12 comme base interpreter.

## Ce que tu vois à la racine

    asteroid_defender/
    ├── student_config.py   ←★ LE SEUL FICHIER À REMPLIR ★
    ├── images/             tes visuels perso (mission bonus)
    ├── README.md           ce fichier
    ├── requirements.txt    dépendances (pygame)
    └── Core/               le moteur — VERROUILLÉ, n'y touche pas

Tout le moteur est rangé dans **Core/**. Tu n'as jamais à l'ouvrir.
Ton seul fichier de travail est `student_config.py`, à la racine.

## Trouver les noms exacts

Mets le jeu en pause avec **Échap** : la carte des notions s'affiche.
Elle liste toutes les fonctionnalités, montre celles qui sont déjà
actives, et donne au survol le **nom exact** à écrire dans
`student_config.py`.

Le nom doit être recopié à la lettre près — mêmes lettres, même casse,
mêmes underscores. `nb_ammo` fonctionne, `nbAmmo` ne débloque rien.

## Commandes

| Touche | Effet |
|--------|-------|
| ← → | déplacer le vaisseau |
| Espace | tirer |
| Tab | changer d'arme |
| Échap | carte des notions / reprendre |
| R | rejouer (écran de fin) |

## Le geste à prendre

Je change une valeur → j'enregistre → je relance `Core/main.py` →
j'observe.
