"""
main.py — Point d'entrée du jeu.
VERROUILLÉ : ne pas modifier.

C'est ce fichier que l'on lance (clic droit > Run), jamais
student_config.py.
"""

import os
import sys

# Ce fichier vit dans Core/. On garantit que Python trouve :
#  - le moteur (engine/), à côté de ce fichier, dans Core/
#  - le fichier de l'étudiant (student_config.py) et le dossier images/,
#    à la racine du projet, un niveau au-dessus de Core/
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.chdir(_ROOT)


# ---------------------------------------------------------------------
#  Contrôle de version Python
#  pygame n'a pas de version prête pour les Python les plus récents :
#  sur un Python trop neuf, l'installation échoue en essayant de tout
#  recompiler. On vérifie ici et on affiche un message clair plutôt
#  que de laisser un plantage incompréhensible.
# ---------------------------------------------------------------------
_PY_MIN = (3, 10)
_PY_MAX = (3, 12)   # dernière version avec un pygame prêt à installer


def _check_python_version():
    v = sys.version_info
    if _PY_MIN <= (v.major, v.minor) <= _PY_MAX:
        return
    cur = f"{v.major}.{v.minor}.{v.micro}"
    msg = (
        "\n" + "=" * 62 + "\n"
        "  MAUVAISE VERSION DE PYTHON\n"
        + "=" * 62 + "\n"
        f"  Ce projet demande Python {_PY_MIN[0]}.{_PY_MIN[1]} "
        f"a {_PY_MAX[0]}.{_PY_MAX[1]}.\n"
        f"  Ton environnement utilise Python {cur}.\n\n"
        "  pygame ne s'installe pas sur les versions trop recentes.\n\n"
        "  A FAIRE :\n"
        "   1. Supprime l'environnement virtuel actuel (dossier .venv).\n"
        f"   2. Recree-le avec Python {_PY_MAX[0]}.{_PY_MAX[1]} "
        "(PyCharm : Add Interpreter\n"
        "      > Virtualenv > Base interpreter).\n"
        "   3. Reinstalle les dependances : python -m pip install -r "
        "requirements.txt\n"
        + "=" * 62 + "\n"
    )
    print(msg)
    # Tente aussi une fenêtre graphique si Tk est là (plus visible qu'une console)
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showerror("Asteroid Defender - version de Python", msg)
        root.destroy()
    except Exception:  # noqa: BLE001
        pass
    sys.exit(1)


_check_python_version()

try:
    import pygame
except ModuleNotFoundError:
    print(
        "\n" + "=" * 62 + "\n"
        "  pygame n'est pas installe dans cet environnement.\n"
        + "=" * 62 + "\n"
        "  Installe les dependances :\n"
        "     python -m pip install -r requirements.txt\n"
        + "=" * 62 + "\n"
    )
    sys.exit(1)

from engine import config as C
from engine.game import Game
from engine.hud import Fonts


def main():
    pygame.init()
    screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
    clock = pygame.time.Clock()
    fonts = Fonts()

    game = Game(screen, fonts)
    pygame.display.set_caption(str(game.features.window_title))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game.handle_event(event):
                running = False

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(C.FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
