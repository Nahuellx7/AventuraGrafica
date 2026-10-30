"""Vista ampliada de la luna para el futuro puzle lunar."""

import os
import pygame
from engine.hotspot import Hotspot


class LunaScene:
    """Pantalla vacía de observación lunar con botón para volver."""

    BUTTON_RECT = pygame.Rect(24, 414, 150, 54)
    HOTSPOTS = [Hotspot(BUTTON_RECT, "Volver")]
    WALKABLE = [(100, 470), (200, 420), (400, 380), (600, 400),
                (800, 420), (900, 470), (900, 480)]

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        image_path = os.path.join(project_root, "assets", "sprites", "luna.png")
        self.background = pygame.image.load(image_path).convert()

    def get_hotspots(self):
        return self.HOTSPOTS

    def get_walkable(self):
        return self.WALKABLE

    def draw(self):
        """Dibuja la imagen lunar y el botón para volver."""
        self.screen.blit(self.background, (0, 0))
        pygame.draw.rect(self.screen, (62, 52, 58), self.BUTTON_RECT)
        pygame.draw.rect(self.screen, (128, 112, 88), self.BUTTON_RECT, 5)
        label = self.font.render("Volver", True, (230, 184, 104))
        self.screen.blit(label, label.get_rect(center=self.BUTTON_RECT.center))
