"""
assets.py - Loads the images declared in student_config.py.
LOCKED: do not modify.

Any visual of the game can be replaced by declaring an image path in
student_config.py. If the file is missing, unreadable or in an
unsupported format, the engine silently falls back to the geometric
drawing: a missing image never crashes the game.
"""

import os

import pygame


_cache = {}
_failed = set()
# assets.py is in Core/engine/; the project root (where images/ lives)
# is two levels above.
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(path, size=None):
    """Loads an image and resizes it. Returns None if impossible.

    The path is relative to the project root (the folder above Core/).
    The result is cached: an image is read only once.
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
    except Exception:  # noqa: BLE001 - missing file, unknown format, etc.
        _failed.add(path)
        return None


def failures():
    """Paths that could not be loaded (shown in the pause menu)."""
    return sorted(_failed)


def blit_centered(surf, image, x, y, angle=0.0):
    """Draws an image centered on a point, with optional rotation."""
    if angle:
        image = pygame.transform.rotate(image, angle)
    surf.blit(image, image.get_rect(center=(int(x), int(y))))
