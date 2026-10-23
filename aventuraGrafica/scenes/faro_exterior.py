"""Escena exterior del faro."""

import math
import pygame
from engine.hotspot import Hotspot


class FaroExteriorScene:
    """Escena exterior del faro con hotspots, polígono caminable y dibujo."""

    # Hotspots del faro exterior
    HOTSPOTS = [
        Hotspot((40, 300, 60, 75), "Volver al puerto"),
        Hotspot((398, 235, 56, 75), "Puerta del faro"),
    ]

    # Polígono caminable del faro exterior
    WALKABLE = [(40, 470), (155, 410), (285, 400), (415, 365),
                (550, 395), (690, 355), (830, 390), (950, 430), (950, 480)]

    def __init__(self, screen):
        """Inicializa la escena exterior del faro."""
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)

    def get_hotspots(self):
        """Retorna la lista de hotspots del faro exterior."""
        return self.HOTSPOTS

    def get_walkable(self):
        """Retorna el polígono caminable del faro exterior."""
        return self.WALKABLE

    def draw(self, progreso_luces, faro_desbloqueado=False):
        """Dibuja la escena exterior del faro."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)

        self._draw_night_sky((8, 19, 54))
        pygame.draw.rect(self.screen, (24, 45, 75), (0, 295, 960, 195))
        for i in range(9):
            wave_y = 345 + i * 19
            pygame.draw.arc(self.screen, (41 + i * 2, 83 + i, 117 + i),
                            (i * 41 - 20, wave_y, 180, 35), math.pi, math.tau, 2)
        pygame.draw.polygon(self.screen, (62, 64, 83),
                            [(0, 408), (140, 350), (270, 375), (430, 325),
                             (610, 380), (805, 333), (960, 394), (960, 490), (0, 490)])
        self._draw_cliff_stones()
        self._draw_lighthouse_tower(progreso_luces)
        self._draw_lighthouse_door(faro_desbloqueado)
        self._draw_isla_return_sign()
        self._draw_label("FARO DEL ACANTILADO", (24, 18))

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

    def _draw_cliff_stones(self):
        """Dibuja piedras en el acantilado."""
        ANCHO_VENTANA = 960
        for index in range(28):
            x = (index * 127 + 28) % ANCHO_VENTANA
            y = 408 + (index * 43) % 70
            pygame.draw.rect(self.screen, (85 + index % 20, 82 + index % 15, 98 + index % 12),
                             (x, y, 23 + index % 17, 7), border_radius=2)

    def _draw_lighthouse_tower(self, progreso_luces):
        """Dibuja la torre del faro."""
        pygame.draw.polygon(self.screen, (35, 34, 48),
                            [(327, 318), (350, 135), (498, 135), (525, 318)])
        pygame.draw.polygon(self.screen, (204, 190, 156),
                            [(340, 315), (361, 143), (486, 143), (510, 315)])
        for y in range(180, 310, 42):
            pygame.draw.rect(self.screen, (176, 68, 61), (349, y, 151, 12))
        pygame.draw.rect(self.screen, (44, 37, 45), (345, 122, 164, 24))
        pygame.draw.rect(self.screen, (83, 107, 132), (364, 69, 127, 60))
        pygame.draw.rect(self.screen, (30, 34, 48), (357, 62, 142, 13))
        pygame.draw.polygon(self.screen, (78, 58, 53), [(353, 65), (429, 28), (502, 65)])
        pygame.draw.rect(self.screen, (230, 200, 128), (392, 80, 70, 34))

    def _draw_lighthouse_door(self, gate_unlocked):
        """Dibuja la puerta del faro centrada y plana en la fachada de la torre."""
        # Puerta centrada horizontalmente en la torre (centro torre: 426, ancho puerta: 56)
        door_x = 398
        # Posición plana en la fachada
        door_y = 235
        door_width = 56
        door_height = 75

        # Bisel exterior del marco (integrado al muro)
        pygame.draw.rect(self.screen, (35, 30, 38), (door_x - 8, door_y - 8, door_width + 16, door_height + 16))
        pygame.draw.rect(self.screen, (98, 85, 72), (door_x - 8, door_y - 8, door_width + 16, door_height + 16), 2)

        # Bisel interior (claro para efecto de relieve)
        pygame.draw.rect(self.screen, (58, 48, 52), (door_x - 6, door_y - 6, door_width + 12, door_height + 12))

        # Sombra interna del marco (efecto de profundidad)
        pygame.draw.rect(self.screen, (38, 32, 40), (door_x - 4, door_y - 4, door_width + 8, door_height + 8))

        # Marco principal de la puerta
        pygame.draw.rect(self.screen, (45, 38, 42), (door_x - 4, door_y - 4, door_width + 8, door_height + 8))
        pygame.draw.rect(self.screen, (128, 112, 88), (door_x - 4, door_y - 4, door_width + 8, door_height + 8), 3)

        # Puerta de madera cerrada (relleno marrón de madera)
        door_color = (92, 58, 33) if not gate_unlocked else (98, 65, 40)
        pygame.draw.rect(self.screen, door_color, (door_x, door_y, door_width, door_height))
        pygame.draw.rect(self.screen, (128, 112, 88), (door_x, door_y, door_width, door_height), 3)

        # Tablas/paneles verticales de la puerta
        for x in (door_x + 12, door_x + 28, door_x + 44):
            pygame.draw.line(self.screen, (78, 48, 28), (x, door_y + 5), (x, door_y + door_height - 5), 2)

        # Paneles horizontales decorativos
        pygame.draw.line(self.screen, (128, 112, 88), (door_x, door_y + 22), (door_x + door_width, door_y + 22), 2)
        pygame.draw.line(self.screen, (128, 112, 88), (door_x, door_y + 48), (door_x + door_width, door_y + 48), 2)

        # Picaporte/cerradura dorado
        lock_x = door_x + door_width - 12
        lock_y = door_y + door_height // 2
        pygame.draw.circle(self.screen, (212, 180, 92), (lock_x, lock_y), 7)
        pygame.draw.circle(self.screen, (180, 150, 70), (lock_x, lock_y), 7, 2)
        pygame.draw.circle(self.screen, (240, 210, 130), (lock_x, lock_y), 3)

        # Manija de la puerta
        handle_x = door_x + 10
        handle_y = door_y + door_height // 2 - 5
        pygame.draw.rect(self.screen, (168, 142, 102), (handle_x, handle_y, 8, 18))
        pygame.draw.rect(self.screen, (128, 112, 88), (handle_x, handle_y, 8, 18), 2)
        pygame.draw.circle(self.screen, (180, 150, 70), (handle_x + 4, handle_y + 9), 3)

    def _draw_isla_return_sign(self):
        """Dibuja un cartel indicador del camino a la isla en el borde izquierdo."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)
        pygame.draw.line(self.screen, (89, 75, 52), (50, 280), (50, 420), 8)
        pygame.draw.rect(self.screen, (142, 96, 59), (40, 300, 60, 75))
        pygame.draw.rect(self.screen, (205, 163, 105), (40, 300, 60, 75), 3)
        self._draw_text("ISLA", (70, 322), self.small_font, PAPER, centered=True)
        pygame.draw.polygon(self.screen, (142, 96, 59), [(70, 375), (55, 390), (85, 390)])
        self._draw_text("←", (70, 395), self.small_font, GOLD, centered=True)

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
