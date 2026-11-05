"""Escena de la isla."""

import math
import os
import pygame
from engine.hotspot import Hotspot


class IslaScene:
    """Escena de la isla con hotspots, polígono caminable y dibujo."""

    # Hotspots específicos de la isla
    HOTSPOTS = [
        Hotspot((0, 285, 58, 72), "Camino al bosque"),
        Hotspot((127, 277, 62, 112), "Puerta del refugio"),
        Hotspot((365, 270, 230, 180), "Compuerta del bunker"),
        Hotspot((48, 360, 78, 112), "Barril"),
        Hotspot((860, 300, 60, 75), "Camino al faro"),
        Hotspot((270, 190, 70, 185), "Cartel del puerto"),
        Hotspot((772, 283, 62, 112), "Puerta de la herreria"),
        Hotspot((110, 410, 60, 60), "Barra de hierro"),
    ]

    # Polígono caminable de la isla
    WALKABLE = [(35, 470), (90, 420), (260, 385), (380, 400),
                (510, 380), (650, 408), (815, 375), (950, 425), (950, 480)]

    def __init__(self, screen):
        """Inicializa la escena de la isla."""
        self.screen = screen
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        background_path = os.path.join(project_root, "assets", "sprites", "cielo_aldea.png")
        self.background = pygame.image.load(background_path).convert()

    def get_hotspots(self):
        """Retorna la lista de hotspots de la isla."""
        return self.HOTSPOTS

    def get_walkable(self):
        """Retorna el polígono caminable de la isla."""
        return self.WALKABLE

    def draw(self, inventory, barra_tomada=False, bunker_desbloqueado=False, barril_tomado=False):
        """Dibuja la escena de la isla."""
        self.screen.blit(self.background, (0, 0))
        # Piso con línea superior horizontal perfecta (Y constante de extremo a extremo)
        pygame.draw.rect(self.screen, (60, 57, 81), (0, 365, 960, 125))
        self._draw_cobblestones(375, 490)
        self._draw_building(35, 95, 245, 294, (106, 58, 49), "REFUGIO", True)
        self._draw_building(680, 95, 245, 300, (57, 64, 93), "HERRERIA", False)
        self._draw_bunker_gate(bunker_desbloqueado)
        if not barril_tomado:
            self._draw_barrel(85, 410, inventory)
        if not barra_tomada:
            self._draw_iron_bar(140, 415, inventory)
        self._draw_lighthouse_path_sign()
        self._draw_forest_path_sign()
        self._draw_label("ISLA", (24, 18))

    # ============ MÉTODOS AUXILIARES DE DIBUJO ============

    def _draw_building(self, x, y, width, height, color, sign, tavern):
        """Dibuja un edificio."""
        INK = (20, 19, 35)
        pygame.draw.rect(self.screen, (28, 24, 37), (x - 8, y - 8, width + 16, height + 10))
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        # Techo triangular elevado ligeramente sobre la pared
        roof_center_x = x + width // 2
        roof_base_y = y - 3
        roof_overhang = 12
        pygame.draw.polygon(self.screen, (47, 37, 43),
                            [(x - roof_overhang, roof_base_y), (roof_center_x, y - 63),
                             (x + width + roof_overhang, roof_base_y)])
        pygame.draw.polygon(self.screen, (112, 64, 51),
                            [(x - roof_overhang + 4, roof_base_y + 1), (roof_center_x, y - 46),
                             (x + width + roof_overhang - 4, roof_base_y + 1)], 8)
        for row in range(2):
            for col in range(3):
                # Ventanas distribuidas simétricamente, desplazadas hacia la izquierda
                wx = x + 20 + col * (width - 90) // 2
                wy = y + 30 + row * 80
                pygame.draw.rect(self.screen, (34, 31, 47), (wx, wy, 42, 54))
                pygame.draw.rect(self.screen, (191, 145, 84), (wx + 5, wy + 6, 32, 42))
                pygame.draw.line(self.screen, (60, 43, 42), (wx + 21, wy + 5), (wx + 21, wy + 48), 3)
                pygame.draw.line(self.screen, (60, 43, 42), (wx + 3, wy + 26), (wx + 39, wy + 26), 3)
            break
        # Puerta que arranca exactamente desde el nivel del suelo
        door_y = y + height - 112
        pygame.draw.rect(self.screen, (43, 30, 34), (x + width // 2 - 30, door_y, 62, 112))
        pygame.draw.rect(self.screen, (133, 86, 54), (x + width // 2 - 24, door_y + 6, 50, 106), 4)
        pygame.draw.rect(self.screen, (218, 177, 104), (x + width // 2 - 45, y + 85, 90, 40))
        self._draw_text(sign, (x + width // 2, y + 105), pygame.font.Font(None, 20), INK, centered=True)
        if tavern:
            pygame.draw.rect(self.screen, (244, 190, 90), (x + 28, y + 182, 60, 58))
            pygame.draw.rect(self.screen, (52, 33, 34), (x + 36, y + 190, 44, 42))
            self._draw_text("OPEN", (x + 58, y + 211), pygame.font.Font(None, 20), (255, 236, 174), centered=True)

    def _draw_bunker_gate(self, gate_unlocked):
        """Dibuja la compuerta metálica del bunker empotrada en el suelo."""
        gate_x = 385
        gate_y = 335
        gate_width = 190
        gate_height = 107

        # Base empotrada en el suelo (borde de concreto)
        pygame.draw.rect(self.screen, (45, 48, 55), (gate_x - 10, gate_y - 5, gate_width + 20, gate_height + 15))
        pygame.draw.rect(self.screen, (35, 38, 45), (gate_x - 8, gate_y - 3, gate_width + 16, gate_height + 11))

        # Compuerta metálica principal
        gate_color = (72, 75, 85) if not gate_unlocked else (82, 85, 95)
        pygame.draw.rect(self.screen, gate_color, (gate_x, gate_y, gate_width, gate_height))
        pygame.draw.rect(self.screen, (128, 132, 145), (gate_x, gate_y, gate_width, gate_height), 4)

        # Líneas verticales decorativas (ranuras)
        for i in range(1, 4):
            line_x = gate_x + i * (gate_width // 4)
            pygame.draw.line(self.screen, (55, 58, 68), (line_x, gate_y + 8), (line_x, gate_y + gate_height - 8), 3)

        # Líneas horizontales decorativas
        for i in range(1, 3):
            line_y = gate_y + i * (gate_height // 3)
            pygame.draw.line(self.screen, (55, 58, 68), (gate_x + 8, line_y), (gate_x + gate_width - 8, line_y), 3)

        # Panel numérico en el centro
        panel_x = gate_x + gate_width // 2 - 25
        panel_y = gate_y + gate_height // 2 - 20
        pygame.draw.rect(self.screen, (38, 42, 52), (panel_x, panel_y, 50, 40))
        pygame.draw.rect(self.screen, (168, 172, 185), (panel_x, panel_y, 50, 40), 2)

        # Dígitos del panel (simulados como puntos)
        for row in range(3):
            for col in range(3):
                dot_x = panel_x + 10 + col * 15
                dot_y = panel_y + 10 + row * 12
                pygame.draw.circle(self.screen, (98, 102, 115), (dot_x, dot_y), 3)

        # Cerradura física a la derecha del panel
        lock_x = panel_x + 55
        lock_y = panel_y + 10
        pygame.draw.rect(self.screen, (58, 62, 72), (lock_x, lock_y, 25, 20))

        # Indicador de estado (luz)
        if gate_unlocked:
            pygame.draw.circle(self.screen, (107, 180, 129), (gate_x + gate_width - 20, gate_y + 15), 6)
        else:
            pygame.draw.circle(self.screen, (168, 78, 68), (gate_x + gate_width - 20, gate_y + 15), 6)

    def _draw_barrel(self, x, y, inventory):
        """Dibuja un barril."""
        pygame.draw.ellipse(self.screen, (76, 47, 36), (x, y, 54, 54))
        pygame.draw.rect(self.screen, (112, 65, 43), (x + 4, y + 5, 46, 38))
        for offset in (11, 42):
            pygame.draw.line(self.screen, (190, 135, 72), (x + offset, y + 7), (x + offset, y + 45), 3)
        pygame.draw.arc(self.screen, (188, 139, 79), (x + 3, y + 9, 48, 27), 0, math.pi, 3)

    def _draw_iron_bar(self, x, y, inventory):
        """Dibuja una barra de hierro apoyada contra el barril."""
        if not inventory.has("Barra de hierro"):
            # Barra de hierro
            pygame.draw.rect(self.screen, (145, 145, 155), (x, y - 10, 12, 45))
            pygame.draw.rect(self.screen, (178, 178, 188), (x, y - 10, 12, 45), 2)
            # Óxido
            pygame.draw.circle(self.screen, (168, 145, 125), (x + 6, y), 3)
            pygame.draw.circle(self.screen, (168, 145, 125), (x + 6, y + 20), 2)

    def _draw_lighthouse_path_sign(self):
        """Dibuja un cartel indicador del camino al faro en el borde derecho."""
        GOLD = (230, 184, 104)
        PAPER = (241, 220, 169)
        pygame.draw.line(self.screen, (89, 75, 52), (910, 280), (910, 420), 8)
        pygame.draw.rect(self.screen, (142, 96, 59), (860, 300, 60, 75))
        pygame.draw.rect(self.screen, (205, 163, 105), (860, 300, 60, 75), 3)
        self._draw_text("FARO", (890, 322), pygame.font.Font(None, 20), PAPER, centered=True)
        pygame.draw.polygon(self.screen, (142, 96, 59), [(890, 375), (875, 390), (905, 390)])
        self._draw_text("➜", (890, 395), pygame.font.Font(None, 20), GOLD, centered=True)

    def _draw_forest_path_sign(self):
        """Dibuja la entrada al bosque en el borde izquierdo de la aldea."""
        pygame.draw.line(self.screen, (89, 75, 52), (24, 276), (24, 385), 7)
        pygame.draw.rect(self.screen, (142, 96, 59), (4, 288, 48, 54))
        pygame.draw.rect(self.screen, (205, 163, 105), (4, 288, 48, 54), 3)
        self._draw_text("BOSQUE", (28, 304), pygame.font.Font(None, 16),
                        (241, 220, 169), centered=True)
        self._draw_text("←", (28, 330), pygame.font.Font(None, 19),
                        (230, 184, 104), centered=True)

    def _draw_cobblestones(self, start_y, end_y):
        """Dibuja adoquines."""
        ANCHO_VENTANA = 960
        for row, y in enumerate(range(start_y, end_y, 25)):
            offset = -35 if row % 2 else 0
            for x in range(offset, ANCHO_VENTANA, 70):
                stone = pygame.Rect(x + row % 3 * 4, y, 63, 20)
                pygame.draw.rect(self.screen, (73, 69, 88), stone, border_radius=4)
                pygame.draw.line(self.screen, (97, 91, 107), (stone.x + 8, y + 3),
                                 (stone.right - 9, y + 3), 2)

    def _draw_label(self, text, position):
        """Dibuja una etiqueta."""
        PAPER = (241, 220, 169)
        self._draw_text(text, position, pygame.font.Font(None, 20), PAPER)

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
