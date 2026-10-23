"""Escena del refugio."""

import pygame
from engine.hotspot import Hotspot


class RefugioScene:
    """Escena del refugio con hotspots, polígono caminable y dibujo."""

    # Hotspots base del refugio
    HOTSPOTS_BASE = [
        Hotspot((12, 280, 110, 195), "Salir a la isla"),
        Hotspot((350, 180, 190, 220), "Bruno"),
        Hotspot((560, 175, 190, 130), "Nota de las luces"),
        Hotspot((165, 325, 155, 105), "Mesa"),
    ]

    # Hotspots con llave disponible
    HOTSPOTS_WITH_KEY = [
        Hotspot((12, 280, 110, 195), "Salir a la isla"),
        Hotspot((350, 180, 190, 220), "Bruno"),
        Hotspot((650, 330, 190, 95), "Llave vieja"),
        Hotspot((560, 175, 190, 130), "Nota de las luces"),
        Hotspot((165, 325, 155, 105), "Mesa"),
    ]

    # Polígono caminable del refugio
    WALKABLE = [(90, 470), (155, 405), (280, 375), (410, 390),
                (560, 365), (700, 395), (870, 430), (930, 480)]

    def __init__(self, screen):
        """Inicializa la escena del refugio."""
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 34)

    def get_hotspots(self, llave_disponible=False):
        """Retorna la lista de hotspots del refugio según el estado."""
        return self.HOTSPOTS_WITH_KEY if llave_disponible else self.HOTSPOTS_BASE

    def get_walkable(self):
        """Retorna el polígono caminable del refugio."""
        return self.WALKABLE

    def draw(self, inventory, llave_tomada=False, llave_disponible=False):
        """Dibuja la escena del refugio."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)

        self._draw_night_sky((16, 20, 48))
        pygame.draw.rect(self.screen, (49, 35, 37), (0, 0, 960, 490))
        pygame.draw.rect(self.screen, (95, 56, 39), (0, 275, 960, 215))
        pygame.draw.rect(self.screen, (56, 34, 30), (50, 65, 860, 330))
        pygame.draw.rect(self.screen, (123, 74, 43), (74, 82, 812, 294))
        pygame.draw.rect(self.screen, (36, 28, 35), (20, 285, 104, 180))
        pygame.draw.rect(self.screen, (151, 102, 60), (30, 294, 83, 171), 5)
        pygame.draw.rect(self.screen, (65, 42, 35), (42, 307, 58, 158))
        pygame.draw.circle(self.screen, GOLD, (89, 388), 4)
        pygame.draw.rect(self.screen, (43, 29, 28), (140, 115, 680, 84))
        self._draw_text("REFUGIO DEL PUERTO", (480, 157), self.large_font, GOLD, centered=True)
        self._draw_shelf_and_bar()
        pygame.draw.ellipse(self.screen, (38, 25, 25), (160, 375, 660, 65))
        pygame.draw.polygon(self.screen, (139, 86, 47), [(156, 359), (793, 359), (836, 390), (128, 390)])
        pygame.draw.polygon(self.screen, (190, 124, 69), [(156, 350), (793, 350), (793, 371), (156, 371)])
        if llave_disponible and not llave_tomada:
            self._draw_old_key(715, 346, inventory)
        self._draw_note(651, 224)
        self._draw_bartender()
        self._draw_label("REFUGIO", (24, 18))

    # ============ MÉTODOS AUXILIARES DE DIBUJO ============

    def _draw_night_sky(self, base):
        """Dibuja el cielo nocturno."""
        ALTURA_JUEGO = 490
        ANCHO_VENTANA = 960
        for y in range(0, ALTURA_JUEGO, 28):
            shade = min(28, y // 18)
            color = (base[0] + shade, base[1] + shade, min(100, base[2] + shade))
            pygame.draw.rect(self.screen, color, (0, y, ANCHO_VENTANA, 28))
        for index in range(66):
            x = (index * 157 + 43) % ANCHO_VENTANA
            y = (index * 71 + 17) % 245
            size = 2 if index % 5 else 3
            pygame.draw.rect(self.screen, (225, 220, 187), (x, y, size, size))
        pygame.draw.circle(self.screen, (243, 218, 151), (816, 69), 27)
        pygame.draw.circle(self.screen, (17, 25, 63), (828, 57), 23)

    def _draw_shelf_and_bar(self):
        """Dibuja la repisa y el bar."""
        # Estructura de madera simétrica alrededor del centro de la pantalla (480)
        # Soportes verticales distribuidos equitativamente: 9 postes bien espaciados
        for x in (180, 260, 340, 420, 480, 540, 620, 700, 780):
            pygame.draw.rect(self.screen, (53, 33, 29), (x, 205, 9, 110))
        # Repisas horizontales simétricas: de 180 a 780 (ancho 600px, centrado en 480)
        for y in (211, 261):
            pygame.draw.rect(self.screen, (75, 40, 31), (180, y, 600, 9))
        # Botellas posicionadas simétricamente sobre las repisas
        bottle_positions = [(205, 245), (285, 240), (365, 245), (445, 240), (515, 245), (595, 240), (675, 245)]
        bottle_colors = [(115, 180, 138), (180, 113, 92), (165, 145, 195), (195, 115, 85), (140, 165, 135), (175, 130, 160), (125, 155, 185)]
        for i, (bx, by) in enumerate(bottle_positions):
            self._draw_bottle(bx, by, bottle_colors[i])

    def _draw_bottle(self, x, y, color):
        """Dibuja una botella."""
        pygame.draw.rect(self.screen, color, (x, y + 12, 23, 36))
        pygame.draw.rect(self.screen, color, (x + 6, y + 3, 11, 13))
        pygame.draw.rect(self.screen, (197, 158, 95), (x + 4, y, 15, 5))
        pygame.draw.rect(self.screen, (229, 190, 113), (x + 5, y + 20, 5, 18))

    def _draw_old_key(self, x, y, inventory):
        """Dibuja una llave vieja oxidada."""
        # Cabeza de la llave
        pygame.draw.circle(self.screen, (168, 145, 118), (x + 27, y + 15), 15)
        pygame.draw.circle(self.screen, (145, 125, 98), (x + 27, y + 15), 15, 3)
        pygame.draw.circle(self.screen, (118, 102, 85), (x + 27, y + 15), 6)
        # Asta de la llave
        pygame.draw.rect(self.screen, (168, 145, 118), (x + 35, y + 18, 35, 8))
        pygame.draw.rect(self.screen, (145, 125, 98), (x + 35, y + 18, 35, 8), 2)
        # Dientes de la llave
        pygame.draw.rect(self.screen, (168, 145, 118), (x + 65, y + 20, 8, 15))
        pygame.draw.rect(self.screen, (145, 125, 98), (x + 65, y + 20, 8, 15), 2)
        pygame.draw.rect(self.screen, (168, 145, 118), (x + 68, y + 28, 5, 8))
        if not inventory.has("Llave vieja"):
            pygame.draw.circle(self.screen, (232, 193, 127), (x + 27, y + 15), 3)

    def _draw_note(self, x, y):
        """Dibuja una nota."""
        PAPER = (165, 140, 95)
        pygame.draw.rect(self.screen, PAPER, (x, y, 106, 70))
        for i in range(3):
            pygame.draw.line(self.screen, (107, 83, 59), (x + 14, y + 18 + i * 17),
                             (x + 92, y + 18 + i * 17), 2)
        self._draw_text("SOL", (x + 52, y + 17), self.small_font, (75, 51, 41), centered=True)
        self._draw_text("LUNA", (x + 52, y + 34), self.small_font, (75, 51, 41), centered=True)
        self._draw_text("ESTRELLA", (x + 52, y + 51), self.small_font, (75, 51, 41), centered=True)

    def _draw_bartender(self):
        """Dibuja al bartender (Bruno)."""
        PAPER = (241, 220, 169)
        pygame.draw.rect(self.screen, (50, 52, 60), (412, 263, 74, 85))
        pygame.draw.rect(self.screen, (218, 164, 117), (422, 226, 53, 53))
        pygame.draw.rect(self.screen, (92, 47, 35), (418, 217, 62, 18))
        pygame.draw.rect(self.screen, (46, 37, 40), (432, 249, 8, 5))
        pygame.draw.rect(self.screen, (46, 37, 40), (457, 249, 8, 5))
        pygame.draw.line(self.screen, (133, 72, 57), (439, 271), (458, 270), 3)
        self._draw_text("BRUNO", (449, 300), self.small_font, PAPER, centered=True)

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
