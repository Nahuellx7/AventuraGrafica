"""Escena interior del faro."""

import os
import pygame
from engine.hotspot import Hotspot


class FaroInteriorScene:
    """Escena interior del faro con hotspots, polígono caminable y dibujo."""

    # Constantes
    GOLD = (230, 184, 104)
    PAPER = (241, 220, 169)

    # Hotspots del faro interior
    HOTSPOTS = [
        Hotspot((350, 420, 260, 60), "Bajar"),
        Hotspot((305, 230, 80, 80), "Luz de la luna"),
        Hotspot((431, 230, 80, 80), "Luz de la estrella"),
        Hotspot((557, 230, 80, 80), "Luz del sol"),
        Hotspot((330, 325, 30, 30), "Botón de la luna"),
        Hotspot((456, 325, 30, 30), "Botón de la estrella"),
        Hotspot((582, 325, 30, 30), "Botón del sol"),
        Hotspot((380, 370, 200, 70), "Interruptor de encendido"),
        Hotspot((825, 52, 100, 100), "Luna"),
        Hotspot((80, 30, 200, 180), "Cielo nocturno"),
        Hotspot((750, 370, 60, 40), "Tarjeta de acceso"),
    ]

    # Polígono caminable del faro interior
    WALKABLE = [(100, 470), (200, 420), (400, 380), (600, 400),
                (800, 420), (900, 470), (900, 480)]

    def __init__(self, screen):
        """Inicializa la escena interior del faro."""
        self.screen = screen
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        background_path = os.path.join(project_root, "assets", "sprites", "cielo_farol.png")
        self.background = pygame.image.load(background_path).convert()
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 34)

    def get_hotspots(self):
        """Retorna la lista de hotspots del faro interior."""
        return self.HOTSPOTS

    def get_walkable(self):
        """Retorna el polígono caminable del faro interior."""
        return self.WALKABLE

    def draw(self, progreso_luces, inventory, puzle_luces_resuelto=False):
        """Dibuja la escena interior del faro con el panel de luces."""
        self.screen.blit(self.background, (0, 0))
        self._draw_hidden_stars(puzle_luces_resuelto)

        # Mesa de madera principal
        table_x = 260
        table_y = 200
        table_width = 440
        table_height = 240
        self._draw_wooden_table(table_x, table_y, table_width, table_height)

        # Sobre la mesa - Panel de luces grande e interruptor
        self._draw_beacon_panel_on_table(progreso_luces, table_x, table_y, table_width)
        self._draw_lighthouse_switch_on_table(progreso_luces, table_x, table_y, table_width)

        # Mesa pequeña en la esquina
        self._draw_lighthouse_table()
        # Tarjeta de acceso sobre la mesa
        if not inventory.has("Tarjeta de acceso"):
            self._draw_lighthouse_card()

        # Salida visible del faro
        self._draw_interior_exit()

        # Etiqueta de la escena
        self._draw_label("SALA DEL FARO", (24, 18))

    # ============ MÉTODOS AUXILIARES DE DIBUJO ============

    def _draw_hidden_stars(self, puzle_luces_resuelto=False):
        """Dibuja las estrellas que revelan el código al resolver el puzle."""
        if puzle_luces_resuelto:
            # Estrellas con patrón numérico visible
            star_positions = [
                (420, 50), (450, 70), (480, 45), (510, 65), (535, 55),
                (435, 85), (465, 95), (495, 80), (520, 90)
            ]
            for sx, sy in star_positions:
                pygame.draw.circle(self.screen, (225, 220, 187), (sx, sy), 2)

            # Patrón numérico 4-7-2-9 formado por estrellas más brillantes
            pattern_stars = [
                (430, 55), (460, 75), (490, 50), (520, 70)
            ]
            for i, (sx, sy) in enumerate(pattern_stars):
                pygame.draw.circle(self.screen, (255, 250, 220), (sx, sy), 4)
                # Números junto a cada estrella
                numbers = ["4", "7", "2", "9"]
                self._draw_text(numbers[i], (sx + 8, sy - 8), self.small_font, (248, 212, 138))
        else:
            # Estrellas normales sin patrón visible
            star_positions = [
                (420, 50), (450, 70), (480, 45), (510, 65), (535, 55),
                (435, 85), (465, 95), (495, 80), (520, 90)
            ]
            for sx, sy in star_positions:
                pygame.draw.circle(self.screen, (225, 220, 187), (sx, sy), 2)

    def _draw_wooden_table(self, x, y, width, height):
        """Dibuja una mesa de madera centrada."""
        # Sombra debajo de la mesa
        pygame.draw.ellipse(self.screen, (25, 22, 30), (x + 10, y + height - 10, width - 20, 30))

        # Tablero principal de la mesa
        pygame.draw.rect(self.screen, (98, 78, 55), (x, y, width, height))
        pygame.draw.rect(self.screen, (142, 118, 82), (x, y, width, height), 5)

        # Textura de madera (vetas)
        for i in range(5):
            vega_y = y + 30 + i * 40
            pygame.draw.line(self.screen, (114, 94, 68), (x + 10, vega_y), (x + width - 10, vega_y), 2)

        # Borde superior resaltado
        pygame.draw.rect(self.screen, (168, 142, 102), (x + 5, y + 5, width - 10, 8), 3)

        # Patas de la mesa (visibles abajo)
        leg_width = 25
        pygame.draw.rect(self.screen, (85, 68, 48), (x + 20, y + height - 5, leg_width, 25))
        pygame.draw.rect(self.screen, (85, 68, 48), (x + width - 45, y + height - 5, leg_width, 25))

    def _draw_beacon_panel_on_table(self, progreso_luces, table_x, table_y, table_width):
        """Dibuja el panel de luces grande en la parte superior de la mesa."""
        # Panel de luces centrado en la parte superior de la mesa
        panel_x = table_x + 30
        panel_y = table_y + 20
        panel_width = table_width - 60
        panel_height = 140

        # Base del panel
        pygame.draw.rect(self.screen, (46, 43, 52), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (178, 144, 97), (panel_x, panel_y, panel_width, panel_height), 4)

        # Tres luces grandes sobre soportes
        # Orden visual (izquierda a derecha): Luna, Estrella, Sol
        luces_colors = [(72, 133, 209), (175, 103, 205), (226, 171, 63)]
        names = ("L", "*", "S")
        # Mapeo de progreso a índice visual según secuencia (Sol, Luna, Estrella)
        # progreso_luces = 1 → ilumina Sol (índice 2)
        # progreso_luces = 2 → ilumina Luna (índice 0)
        # progreso_luces = 3 → ilumina Estrella (índice 1)
        progress_to_index = {1: 2, 2: 0, 3: 1}
        # Centrar las 3 luces simétricamente
        luces_width = 80
        spacing = (panel_width - 3 * luces_width) / 4

        for index in range(3):
            luces_x = panel_x + spacing + index * (luces_width + spacing)
            luces_y = panel_y + 10

            # Soporte de la luz (centrado bajo la luz)
            pygame.draw.rect(self.screen, (128, 100, 68), (luces_x + 20, luces_y + 80, 40, 15))

            # Color de la luz según el progreso actual
            is_illuminated = False
            for progress, illuminated_index in progress_to_index.items():
                if progreso_luces >= progress and index == illuminated_index:
                    is_illuminated = True
                    break
            color = luces_colors[index] if is_illuminated else (74, 77, 91)

            # Luz grande (esfera más grande)
            pygame.draw.ellipse(self.screen, color, (luces_x, luces_y, 80, 80))
            pygame.draw.ellipse(self.screen, (237, 225, 190), (luces_x + 18, luces_y + 18, 44, 44), 4)

            # Símbolo grande
            self._draw_text(names[index], (luces_x + 40, luces_y + 40), self.large_font, self.PAPER, centered=True)

            # Botón debajo de cada luz (centrado y alineado)
            button_x = luces_x + 25
            button_y = luces_y + 95
            button_size = 30

            # Base del botón
            button_color = (98, 85, 72) if is_illuminated else (72, 60, 55)
            pygame.draw.rect(self.screen, button_color, (button_x, button_y, button_size, button_size), border_radius=4)
            pygame.draw.rect(self.screen, (128, 112, 88), (button_x, button_y, button_size, button_size), 2, border_radius=4)

            # Indicador luminoso en el botón
            if is_illuminated:
                pygame.draw.circle(self.screen, (107, 180, 129), (button_x + button_size // 2, button_y + button_size // 2), 6)
            else:
                pygame.draw.circle(self.screen, (72, 60, 55), (button_x + button_size // 2, button_y + button_size // 2), 6)

    def _draw_interior_exit(self):
        """Dibuja una trampilla de salida visible en el suelo."""
        exit_x = 350
        exit_y = 420
        exit_width = 260
        exit_height = 60

        # Marco de la trampilla
        pygame.draw.rect(self.screen, (62, 52, 58), (exit_x, exit_y, exit_width, exit_height))
        pygame.draw.rect(self.screen, (128, 112, 88), (exit_x, exit_y, exit_width, exit_height), 5)

        # Bisagras
        pygame.draw.rect(self.screen, (107, 92, 68), (exit_x + 15, exit_y - 5, 20, 12))
        pygame.draw.rect(self.screen, (107, 92, 68), (exit_x + exit_width - 35, exit_y - 5, 20, 12))

        # Manija de la trampilla (más grande)
        pygame.draw.circle(self.screen, (168, 142, 102), (exit_x + exit_width // 2, exit_y + exit_height // 2), 15)
        pygame.draw.circle(self.screen, (128, 112, 88), (exit_x + exit_width // 2, exit_y + exit_height // 2), 15, 4)
        pygame.draw.circle(self.screen, (180, 150, 70), (exit_x + exit_width // 2, exit_y + exit_height // 2), 6)

        # Texto "BAJAR" más grande
        self._draw_text("BAJAR", (exit_x + exit_width // 2, exit_y + exit_height + 20),
                       self.font, self.GOLD, centered=True)

    def _draw_lighthouse_switch_on_table(self, progreso_luces, table_x, table_y, table_width):
        """Dibuja el interruptor en la parte inferior de la mesa."""
        # Interruptor centrado debajo de las luces (más grande)
        switch_x = table_x + table_width // 2 - 100
        switch_y = table_y + 170
        switch_width = 200
        switch_height = 70

        # Base del interruptor
        pygame.draw.rect(self.screen, (72, 60, 55), (switch_x, switch_y, switch_width, switch_height), border_radius=6)
        pygame.draw.rect(self.screen, (128, 112, 88), (switch_x, switch_y, switch_width, switch_height), 4, border_radius=6)

        # Palanca centrada (siempre marrón)
        lever_x = switch_x + switch_width // 2 - 16
        pygame.draw.rect(self.screen, (107, 92, 68), (lever_x, switch_y + 12, 32, 46), border_radius=3)
        pygame.draw.rect(self.screen, (153, 133, 98), (lever_x, switch_y + 12, 32, 46), 3, border_radius=3)

        # Circulito dentro de la palanca (verde cuando está activado, gris cuando no)
        circle_color = (72, 60, 55) if progreso_luces < 3 else (107, 180, 129)
        pygame.draw.circle(self.screen, circle_color, (lever_x + 16, switch_y + 35), 12)

        # Indicador de estado (círculo verde abajo del interruptor)
        indicator_color = (72, 60, 55) if progreso_luces < 3 else (107, 180, 129)
        indicator_x = switch_x + switch_width // 2
        indicator_y = switch_y + switch_height + 15
        pygame.draw.circle(self.screen, indicator_color, (indicator_x, indicator_y), 10)

        # Texto del interruptor (dentro de la mesa)
        label = "ENCENDIDO" if progreso_luces == 3 else "APAGADO"
        label_color = (107, 180, 129) if progreso_luces == 3 else (161, 151, 134)
        self._draw_text(label, (switch_x + switch_width // 2, switch_y + switch_height + 18),
                       self.small_font, label_color, centered=True)

    def _draw_lighthouse_table(self):
        """Dibuja la mesa pequeña en la esquina derecha (siempre visible)."""
        table_x = 730
        table_y = 400
        pygame.draw.rect(self.screen, (92, 68, 52), (table_x, table_y, 100, 12))
        pygame.draw.rect(self.screen, (72, 52, 42), (table_x + 10, table_y + 12, 15, 35))
        pygame.draw.rect(self.screen, (72, 52, 42), (table_x + 75, table_y + 12, 15, 35))

    def _draw_lighthouse_card(self):
        """Dibuja la tarjeta de acceso sobre la mesa (solo si no está en inventario)."""
        # Centrar la tarjeta en la mesa (mesa: 730-830, centro en 780)
        card_x = 755
        card_y = 375
        # Cuerpo de la tarjeta
        pygame.draw.rect(self.screen, (178, 185, 195), (card_x, card_y, 50, 30))
        pygame.draw.rect(self.screen, (145, 152, 162), (card_x, card_y, 50, 30), 2)
        # Banda magnética
        pygame.draw.rect(self.screen, (42, 42, 52), (card_x + 2, card_y + 18, 46, 8))
        # Chip
        pygame.draw.rect(self.screen, (168, 165, 155), (card_x + 5, card_y + 3, 12, 10))
        pygame.draw.rect(self.screen, (145, 142, 132), (card_x + 5, card_y + 3, 12, 10), 1)

    def _draw_label(self, text, position):
        """Dibuja una etiqueta."""
        self._draw_text(text, position, self.small_font, self.PAPER)

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
