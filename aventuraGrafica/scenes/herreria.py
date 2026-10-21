"""Escena de la herrería."""

import pygame
from engine.hotspot import Hotspot


class HerreriaScene:
    """Escena de la herrería con hotspots, polígono caminable y dibujo."""

    # Hotspots de la herrería
    HOTSPOTS = [
        Hotspot((12, 280, 110, 195), "Salir a la isla"),
        Hotspot((350, 180, 190, 220), "Herrero"),
    ]

    # Polígono caminable de la herrería
    WALKABLE = [(90, 470), (155, 405), (280, 375), (410, 390),
                (560, 365), (700, 395), (870, 430), (930, 480)]

    def __init__(self, screen):
        """Inicializa la escena de la herrería."""
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 34)

    def get_hotspots(self):
        """Retorna la lista de hotspots de la herrería."""
        return self.HOTSPOTS

    def get_walkable(self):
        """Retorna el polígono caminable de la herrería."""
        return self.WALKABLE

    def draw(self, inventory):
        """Dibuja la escena de la herrería."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)

        self._draw_night_sky((20, 18, 45))
        pygame.draw.rect(self.screen, (62, 45, 35), (0, 0, 960, 490))
        pygame.draw.rect(self.screen, (112, 78, 52), (0, 275, 960, 215))
        pygame.draw.rect(self.screen, (78, 55, 42), (50, 65, 860, 330))
        pygame.draw.rect(self.screen, (145, 105, 68), (74, 82, 812, 294))
        pygame.draw.rect(self.screen, (45, 32, 28), (20, 285, 104, 180))
        pygame.draw.rect(self.screen, (168, 125, 78), (30, 294, 83, 171), 5)
        pygame.draw.rect(self.screen, (75, 52, 40), (42, 307, 58, 158))
        pygame.draw.circle(self.screen, GOLD, (89, 388), 4)
        pygame.draw.rect(self.screen, (52, 38, 32), (140, 115, 680, 84))
        self._draw_text("HERRERIA", (480, 155), self.large_font, GOLD, centered=True)

        # Tabla de herramientas en la pared de fondo (centrada, detrás del herrero)
        tool_panel_x = 560
        tool_panel_y = 210
        tool_panel_width = 200
        tool_panel_height = 130

        # Tablón de madera de la pared
        pygame.draw.rect(self.screen, (78, 58, 42), (tool_panel_x, tool_panel_y, tool_panel_width, tool_panel_height))
        pygame.draw.rect(self.screen, (98, 78, 58), (tool_panel_x, tool_panel_y, tool_panel_width, tool_panel_height), 4)
        pygame.draw.line(self.screen, (65, 48, 35), (tool_panel_x, tool_panel_y + 50), (tool_panel_x + tool_panel_width, tool_panel_y + 50), 3)
        pygame.draw.line(self.screen, (65, 48, 35), (tool_panel_x, tool_panel_y + 90), (tool_panel_x + tool_panel_width, tool_panel_y + 90), 3)

        # Martillo grande colgado
        hammer_x = tool_panel_x + 25
        hammer_y = tool_panel_y + 20
        pygame.draw.rect(self.screen, (145, 135, 125), (hammer_x, hammer_y, 45, 12))
        pygame.draw.rect(self.screen, (125, 115, 105), (hammer_x, hammer_y, 45, 12), 2)
        pygame.draw.rect(self.screen, (115, 105, 95), (hammer_x + 15, hammer_y + 12, 15, 35))
        pygame.draw.circle(self.screen, (88, 72, 52), (hammer_x + 22, hammer_y - 6), 4)

        # Tenazas colgadas
        tongs_x = tool_panel_x + 95
        tongs_y = tool_panel_y + 20
        pygame.draw.rect(self.screen, (135, 125, 115), (tongs_x, tongs_y, 7, 45), 2)
        pygame.draw.rect(self.screen, (135, 125, 115), (tongs_x + 10, tongs_y, 7, 45), 2)
        pygame.draw.rect(self.screen, (115, 105, 95), (tongs_x - 2, tongs_y + 18, 21, 8))
        pygame.draw.circle(self.screen, (88, 72, 52), (tongs_x + 8, tongs_y - 6), 4)

        # Punzón colgado
        chisel_x = tool_panel_x + 140
        chisel_y = tool_panel_y + 25
        pygame.draw.rect(self.screen, (145, 135, 125), (chisel_x, chisel_y, 7, 40))
        pygame.draw.rect(self.screen, (125, 115, 105), (chisel_x, chisel_y, 7, 40), 2)
        pygame.draw.circle(self.screen, (88, 72, 52), (chisel_x + 3, chisel_y - 5), 4)

        # Martillo pequeño
        small_hammer_x = tool_panel_x + 30
        small_hammer_y = tool_panel_y + 70
        pygame.draw.rect(self.screen, (145, 135, 125), (small_hammer_x, small_hammer_y, 35, 9))
        pygame.draw.rect(self.screen, (125, 115, 105), (small_hammer_x, small_hammer_y, 35, 9), 2)
        pygame.draw.rect(self.screen, (115, 105, 95), (small_hammer_x + 12, small_hammer_y + 9, 11, 25))
        pygame.draw.circle(self.screen, (88, 72, 52), (small_hammer_x + 17, small_hammer_y - 4), 4)

        # Alicates
        pliers_x = tool_panel_x + 100
        pliers_y = tool_panel_y + 70
        pygame.draw.rect(self.screen, (135, 125, 115), (pliers_x, pliers_y, 6, 35), 2)
        pygame.draw.rect(self.screen, (135, 125, 115), (pliers_x + 8, pliers_y, 6, 35), 2)
        pygame.draw.rect(self.screen, (115, 105, 95), (pliers_x - 1, pliers_y + 15, 16, 6))
        pygame.draw.circle(self.screen, (88, 72, 52), (pliers_x + 7, pliers_y - 4), 4)

        # Mesa grande como la de Bruno
        pygame.draw.ellipse(self.screen, (38, 25, 25), (160, 375, 660, 65))
        pygame.draw.polygon(self.screen, (139, 86, 47), [(156, 359), (793, 359), (836, 390), (128, 390)])
        pygame.draw.polygon(self.screen, (190, 124, 69), [(156, 350), (793, 350), (793, 371), (156, 371)])
        # Horno con fuego (más arriba, sobre la mesa)
        pygame.draw.rect(self.screen, (72, 68, 72), (250, 240, 120, 100))
        pygame.draw.rect(self.screen, (98, 92, 95), (250, 240, 120, 100), 3)
        # Abertura del horno
        pygame.draw.ellipse(self.screen, (28, 24, 32), (270, 270, 80, 50))
        # Fuego dentro del horno
        pygame.draw.ellipse(self.screen, (186, 112, 62), (280, 275, 60, 35))
        pygame.draw.ellipse(self.screen, (218, 168, 92), (290, 278, 40, 28))
        pygame.draw.circle(self.screen, (248, 212, 138), (310, 287), 8)
        self._draw_blacksmith()
        self._draw_label("HERRERIA", (24, 18))

    # ============ MÉTODOS AUXILIARES DE DIBUJO ============

    def _draw_night_sky(self, base):
        """Dibuja el cielo nocturno."""
        WORLD_HEIGHT = 490
        SCREEN_WIDTH = 960
        for y in range(0, WORLD_HEIGHT, 28):
            shade = min(28, y // 18)
            color = (base[0] + shade, base[1] + shade, min(100, base[2] + shade))
            pygame.draw.rect(self.screen, color, (0, y, SCREEN_WIDTH, 28))
        for index in range(66):
            x = (index * 157 + 43) % SCREEN_WIDTH
            y = (index * 71 + 17) % 245
            size = 2 if index % 5 else 3
            pygame.draw.rect(self.screen, (225, 220, 187), (x, y, size, size))
        pygame.draw.circle(self.screen, (243, 218, 151), (816, 69), 27)
        pygame.draw.circle(self.screen, (17, 25, 63), (828, 57), 23)

    def _draw_blacksmith(self):
        """Dibuja al herrero."""
        PAPER = (241, 220, 169)
        # Cuerpo del herrero
        pygame.draw.rect(self.screen, (75, 70, 75), (412, 263, 74, 85))
        # Cabeza
        pygame.draw.rect(self.screen, (198, 145, 92), (422, 226, 53, 53))
        # Gorra de cuero
        pygame.draw.rect(self.screen, (112, 65, 48), (418, 217, 62, 18))
        pygame.draw.rect(self.screen, (125, 75, 55), (415, 220, 68, 5))
        # Ojos
        pygame.draw.rect(self.screen, (58, 52, 55), (432, 249, 8, 5))
        pygame.draw.rect(self.screen, (58, 52, 55), (457, 249, 8, 5))
        # Boca
        pygame.draw.line(self.screen, (153, 98, 72), (439, 271), (458, 270), 3)
        # Delantal de cuero con protección
        pygame.draw.rect(self.screen, (95, 65, 45), (420, 280, 58, 68))
        pygame.draw.rect(self.screen, (115, 80, 55), (420, 280, 58, 68), 3)
        # Bolsillo del delantal
        pygame.draw.rect(self.screen, (85, 55, 40), (435, 310, 28, 20))
        pygame.draw.rect(self.screen, (115, 80, 55), (435, 310, 28, 20), 2)

        self._draw_text("Juan", (449, 300), self.small_font, PAPER, centered=True)

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
