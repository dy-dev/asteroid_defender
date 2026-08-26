"""
assets.py — Chargement des images fournies par l'étudiant.
VERROUILLÉ : ne pas modifier.

L'étudiant peut remplacer n'importe quel visuel du jeu en déclarant un
chemin dans student_config.py. Si le fichier est absent, illisible ou
d'un format non géré, le moteur revient silencieusement au dessin
géométrique : le jeu ne plante jamais pour une image manquante.
"""

import os

import pygame


_cache = {}
_failed = set()
# assets.py est dans Core/engine/ ; la racine projet (où vit images/)
# est deux niveaux au-dessus.
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(path, size=None):
    """Charge une image et la redimensionne. Renvoie None si impossible.

    Le chemin est relatif à la racine du projet (à côté de main.py).
    Le résultat est mis en cache : une image n'est lue qu'une fois.
    """
    if not path or not isinstance(path, str):
        return None

    key = (path, size)
    if key in _cache:
        return _cache[key]
    if path in _failed:
        return None

    candidate = path if os.path.isabs(path) else os.path.join(_root, path)
    try:
        image = pygame.image.load(candidate).convert_alpha()
        if size:
            image = pygame.transform.smoothscale(image, size)
        _cache[key] = image
        return image
    except Exception:  # noqa: BLE001 - fichier absent, format inconnu, etc.
        _failed.add(path)
        return None


def failures():
    """Chemins qui n'ont pas pu être chargés (affichés dans le menu pause)."""
    return sorted(_failed)


def blit_centered(surf, image, x, y, angle=0.0):
    """Dessine une image centrée sur un point, avec rotation éventuelle."""
    if angle:
        image = pygame.transform.rotate(image, angle)
    surf.blit(image, image.get_rect(center=(int(x), int(y))))
