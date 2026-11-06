"""
engine/shared_assets.py

Los sonidos y la música comunes viven en `2027/assets/` (generados por
`herramientas/genlib.py`). Este módulo da rutas absolutas a esos archivos
desde cualquier juego, sin depender de dónde se ejecute.
"""

import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta 2027
MUSIC_VOLUME = 0.30


def sfx_path(name, extension="wav"):
    """Ruta al efecto de sonido `name`, con la extensión indicada."""
    return os.path.join(_ROOT, "assets", "sounds", f"{name}.{extension}")


def music_path(name, extension="wav"):
    """Ruta a la música `name` con la extensión indicada."""
    return os.path.join(_ROOT, "assets", "music", f"{name}.{extension}")


def shared_dir():
    return os.path.join(_ROOT, "assets")
