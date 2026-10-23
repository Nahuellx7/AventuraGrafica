"""Escena de la ventana del faro."""

import pygame
from engine.hotspot import Hotspot


class VentanaFaroScene:
    """Escena de la ventana del faro con hotspots, polígono caminable y dibujo."""

    # Hotspots de la ventana del faro
    HOTSPOTS = [
        Hotspot((350, 420, 260, 60), "Volver"),
    ]

    # Polígono caminable de la ventana del faro
    WALKABLE = [(100, 470), (200, 420), (400, 380), (600, 400),
                (800, 420), (900, 470), (900, 480)]

    def __init__(self, screen):
        """Inicializa la escena de la ventana del faro."""
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)

    def get_hotspots(self):
        """Retorna la lista de hotspots de la ventana del faro."""
        return self.HOTSPOTS

    def get_walkable(self):
        """Retorna el polígono caminable de la ventana del faro."""
        return self.WALKABLE

    def draw(self, puzle_luces_resuelto=False):
        """Dibuja la vista ampliada de la ventana del faro con el patrón de estrellas."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)
        ALTURA_JUEGO = 490
        ANCHO_VENTANA = 960

        # Fondo de cielo nocturno ampliado
        for y in range(0, ALTURA_JUEGO, 25):
            shade = min(20, y // 25)
            color = (12 + shade, 15 + shade, 35 + shade)
            pygame.draw.rect(self.screen, color, (0, y, ANCHO_VENTANA, 25))

        # Ventana arqueada grande que enmarca el cielo
        window_x = 100
        window_y = 50
        window_width = 760
        window_height = 380

        # Marco de la ventana
        pygame.draw.rect(self.screen, (62, 58, 72), (window_x - 15, window_y - 15, window_width + 30, window_height + 30), 12)
        pygame.draw.rect(self.screen, (98, 92, 108), (window_x - 10, window_y - 10, window_width + 20, window_height + 20), 4)

        # Cielo dentro de la ventana
        pygame.draw.rect(self.screen, (18, 22, 48), (window_x, window_y, window_width, window_height))

        # Estrellas normales
        for index in range(80):
            x = window_x + (index * 47 + 23) % window_width
            y = window_y + (index * 31 + 17) % window_height
            size = 2 if index % 4 else 3
            pygame.draw.rect(self.screen, (225, 220, 187), (x, y, size, size))

        # Luna grande y brillante
        moon_x = window_x + window_width // 2
        moon_y = window_y + 100
        pygame.draw.circle(self.screen, (243, 218, 151), (moon_x, moon_y), 45)
        pygame.draw.circle(self.screen, (17, 25, 63), (moon_x + 12, moon_y - 12), 38)

        if puzle_luces_resuelto:
            # Patrón numérico 4-7-2-9 formado por estrellas más brillantes
            pattern_stars = [
                (window_x + 200, window_y + 200, "4"),
                (window_x + 350, window_y + 180, "7"),
                (window_x + 500, window_y + 220, "2"),
                (window_x + 600, window_y + 160, "9"),
            ]

            for px, py, number in pattern_stars:
                # Estrella brillante
                pygame.draw.circle(self.screen, (255, 255, 240), (px, py), 8)
                pygame.draw.circle(self.screen, (255, 248, 200), (px, py), 5)

                # Número junto a la estrella
                self._draw_text(number, (px + 15, py - 5), self.small_font, (255, 248, 200))

        # Botón de salida en la parte inferior
        self._draw_window_exit_button()

        # Etiqueta de la escena
        self._draw_label("VISTA DEL CIELO", (24, 18))

    # ============ MÉTODOS AUXILIARES DE DIBUJO ============

    def _draw_window_exit_button(self):
        """Dibuja el botón de salida en la vista de la ventana."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)
        button_x = 350
        button_y = 420
        button_width = 260
        button_height = 60

        # Marco del botón
        pygame.draw.rect(self.screen, (62, 52, 58), (button_x, button_y, button_width, button_height))
        pygame.draw.rect(self.screen, (128, 112, 88), (button_x, button_y, button_width, button_height), 5)

        # Texto "VOLVER"
        self._draw_text("VOLVER", (button_x + button_width // 2, button_y + button_height // 2),
                       self.font, GOLD, centered=True)

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
