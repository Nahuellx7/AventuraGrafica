"""
Motor 2D del curso de Videojuegos (versión 2027).

El motor soporta DOS enfoques de trabajo:

1) Enfoque Game Loop (herencia):
   Heredar de `GameLoop` y sobrescribir:
       handle_specific_events(event)
       update_game_logic()
       draw_game_elements()
   Ideal para demos y juegos con un único "estado" (por ejemplo el sandbox
   de físicas o el primer Arkanoid).

2) Enfoque Game Scenes (gestor de escenas):
   Heredar de `Game` (que ya es un `GameLoop`) y registrar escenas con
   `add_scene(nombre, clase_de_escena)` y cambiar con `change_scene(nombre)`.
   Cada escena hereda de `Scene` y sobrescribe:
       handle_events(events)
       update()
       draw(surface)
   Ideal para juegos con menú, juego, game over, pausa, niveles, etc.

Ambos enfoques comparten exactamente el mismo bucle y los mismos módulos
(assets, spritesheets, audio, físicas, tilemaps, cámara, UI).
"""

from engine.game_loop import GameLoop, Game
from engine.ui import Scene, Button
from engine.dialogue_manager import DialogueManager
from engine.hotspot import Hotspot
from engine.inventory import Inventory, Item

# El audio depende de librerías/entornos concretos.
# Lo importamos de forma tolerante para que el motor siga siendo utilizable
# aunque no haya tarjeta de sonido.
try:
    from engine.audio import AudioManager
except Exception:  # pragma: no cover
    AudioManager = None

__all__ = [
    "GameLoop",
    "Game",
    "Scene",
    "Button",
    "DialogueManager",
    "Hotspot",
    "Inventory",
    "Item",
    "AudioManager",
]
