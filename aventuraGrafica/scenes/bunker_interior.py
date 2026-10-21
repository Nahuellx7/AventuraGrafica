"""Escena interior del búnker."""

import pygame
from engine.hotspot import Hotspot


class BunkerInteriorScene:
    """Escena interior del búnker con hotspots, polígono caminable y dibujo."""

    # Hotspots del bunker interior
    HOTSPOTS = [
        Hotspot((320, 410, 320, 80), "Salir del bunker"),
        Hotspot((330, 240, 300, 100), "Caja fuerte"),
        Hotspot((380, 250, 200, 100), "Cámara secreta"),
        Hotspot((380, 330, 130, 100), "Palanca secreta"),
    ]

    # Polígono caminable del bunker interior
    WALKABLE = [(100, 470), (200, 420), (400, 380), (600, 400),
                (800, 420), (900, 470), (900, 480)]

    def __init__(self, screen):
        """Inicializa la escena interior del búnker."""
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)

    def get_hotspots(self):
        """Retorna la lista de hotspots del bunker interior."""
        return self.HOTSPOTS

    def get_walkable(self):
        """Retorna el polígono caminable del bunker interior."""
        return self.WALKABLE

    def draw(self, inventory):
        """Dibuja la escena interior del bunker con la cámara secreta."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)
        WORLD_HEIGHT = 490
        SCREEN_WIDTH = 960

        # Fondo de concreto oscuro
        for y in range(0, WORLD_HEIGHT, 20):
            shade = min(12, y // 40)
            color = (28 + shade, 28 + shade, 32 + shade)
            pygame.draw.rect(self.screen, color, (0, y, SCREEN_WIDTH, 20))

        # Paredes de concreto con textura
        pygame.draw.rect(self.screen, (45, 45, 52), (50, 80, 860, 390))
        pygame.draw.rect(self.screen, (52, 52, 60), (50, 80, 860, 390), 4)

        # Líneas de refuerzo en las paredes
        for y in range(120, 420, 50):
            pygame.draw.line(self.screen, (58, 58, 68), (55, y), (905, y), 2)

        # Cámara secreta en el centro
        chamber_x = 380
        chamber_y = 250
        chamber_width = 200
        chamber_height = 100

        # Marco de la cámara
        pygame.draw.rect(self.screen, (38, 38, 45), (chamber_x, chamber_y, chamber_width, chamber_height))
        pygame.draw.rect(self.screen, (128, 128, 145), (chamber_x, chamber_y, chamber_width, chamber_height), 4)

        # Puerta de la cámara
        pygame.draw.rect(self.screen, (52, 52, 62), (chamber_x + 10, chamber_y + 10, chamber_width - 20, chamber_height - 20))
        pygame.draw.rect(self.screen, (98, 98, 115), (chamber_x + 10, chamber_y + 10, chamber_width - 20, chamber_height - 20), 3)

        # Caja fuerte (en frente de la cámara)
        safe_x = 330
        safe_y = 240
        safe_width = 300
        safe_height = 100

        # Cuerpo de la caja fuerte
        pygame.draw.rect(self.screen, (58, 58, 68), (safe_x, safe_y, safe_width, safe_height))
        pygame.draw.rect(self.screen, (98, 98, 115), (safe_x, safe_y, safe_width, safe_height), 4)

        # Panel numérico de la caja fuerte
        panel_x = safe_x + safe_width // 2 - 30
        panel_y = safe_y + safe_height // 2 - 20
        pygame.draw.rect(self.screen, (38, 42, 52), (panel_x, panel_y, 60, 40))
        pygame.draw.rect(self.screen, (168, 172, 185), (panel_x, panel_y, 60, 40), 2)

        # Dígitos del panel
        for row in range(3):
            for col in range(3):
                dot_x = panel_x + 12 + col * 18
                dot_y = panel_y + 10 + row * 12
                pygame.draw.circle(self.screen, (98, 102, 115), (dot_x, dot_y), 3)

        # Palanca secreta
        lever_x = 420
        lever_y = 360
        pygame.draw.rect(self.screen, (72, 68, 65), (lever_x, lever_y, 50, 40))
        pygame.draw.rect(self.screen, (128, 125, 118), (lever_x, lever_y, 50, 40), 3)
        pygame.draw.rect(self.screen, (98, 95, 88), (lever_x + 15, lever_y + 5, 20, 30))
        pygame.draw.circle(self.screen, (168, 165, 158), (lever_x + 25, lever_y + 10), 8)

        # Piso
        pygame.draw.rect(self.screen, (35, 35, 42), (0, 420, SCREEN_WIDTH, 70))
        for x in range(0, SCREEN_WIDTH, 60):
            pygame.draw.line(self.screen, (42, 42, 52), (x, 420), (x + 30, 490), 2)

        # Salida (escalera)
        exit_x = 350
        exit_y = 420
        exit_width = 260
        exit_height = 60

        pygame.draw.rect(self.screen, (45, 42, 48), (exit_x, exit_y, exit_width, exit_height))
        pygame.draw.rect(self.screen, (118, 115, 128), (exit_x, exit_y, exit_width, exit_height), 4)

        # Escalones
        for i in range(5):
            step_y = exit_y + 10 + i * 10
            pygame.draw.line(self.screen, (72, 68, 78), (exit_x + 10, step_y), (exit_x + exit_width - 10, step_y), 2)

        self._draw_text("SALIDA", (exit_x + exit_width // 2, exit_y + exit_height + 15),
                       self.font, GOLD, centered=True)

        self._draw_label("INTERIOR DEL BUNKER", (24, 18))

    # ============ MÉTODOS AUXILIARES DE DIBUJO ============

    def _draw_label(self, text, position):
        """Dibuja una etiqueta."""
        PAPER = (241, 220, 169)
        self._draw_text(text, position, self.small_font, PAPER)

    def _draw_text(self, text, position, font, color, centered=False, right=False):
        """Dibuja texto."""
        image = font.render(text, True, color)
        if centered:
            rect = image.get_rect(center=position)
        elif right:
            rect = image.get_rect(midright=position)
        else:
            rect = image.get_rect(topleft=position)
        self.screen.blit(image, rect)
