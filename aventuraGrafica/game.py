"""Aventura gráfica point-and-click: La Isla Olvidada."""

import os
import pygame

from engine.game_loop import Game
from engine.audio import AudioManager
from aventuraGrafica.scenes.menu_scene import MenuScene
from aventuraGrafica.scenes.game_scene import GameScene
from aventuraGrafica.scenes.victory_scene import VictoryScene
from aventuraGrafica.scenes.game_over_scene import GameOverScene


# Constantes del juego
ANCHO_VENTANA = 960
ALTO_VENTANA = 640
ALTURA_JUEGO = 490
FPS = 60


class AventuraGrafica(Game):
    """Controla la aventura usando el gestor de escenas del motor."""

    def __init__(self):
        super().__init__(ANCHO_VENTANA, ALTO_VENTANA, "La Isla Olvidada - Aventura Gráfica", FPS)

        self.game_dir = os.path.dirname(os.path.abspath(__file__))

        # Inicializar AudioManager
        self.audio = AudioManager(num_channels=16)

        # Desactivar cursor nativo del sistema (todas las escenas usan cursor personalizado)
        pygame.mouse.set_visible(False)

        # Registrar escenas
        self.add_scene("menu", MenuScene)
        self.add_scene("game", GameScene)
        self.add_scene("victory", VictoryScene)
        self.add_scene("game_over", GameOverScene)

        # Guardar referencia al juego para poder reanudar
        self.game_scene = None
        self.game_started = False

        # Iniciar en el menú
        self.change_scene("menu")


if __name__ == "__main__":
    AventuraGrafica().run()
