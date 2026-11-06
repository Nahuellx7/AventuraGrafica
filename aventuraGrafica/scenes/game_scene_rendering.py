"""GameSceneRendering for the main game scene."""

import pygame

from .game_scene_config import (
    ALTO_VENTANA,
    ANCHO_VENTANA,
    AZUL_OSCURO,
    DORADO,
    DURACION_FRAME_BINOCULARES,
    DURACION_FRAME_CAMINAR,
    DURACION_FRAME_IDLE,
    EstadoJuego,
    INICIO_UI,
    PANEL,
    PAPEL,
)


class GameSceneRenderingMixin:
    """Handles rendering for GameScene."""

    def draw(self, surface):
        """Renderiza el juego delegando a las escenas correspondientes."""
        surface.fill(AZUL_OSCURO)

        # Delegar dibujo a la escena correspondiente
        if self.scene == "aldea":
            self.aldea_scene.draw(
                self.inventory,
                self.barra_tomada,
                self.bunker_desbloqueado,
                self.barril_tomado,
            )
        elif self.scene == "bosque":
            self.bosque_scene.draw()
        elif self.scene == "refugio":
            self.refugio_scene.draw(self.inventory, self.llave_tomada, self.llave_disponible)
        elif self.scene == "herreria":
            self.herreria_scene.draw(self.inventory)
        elif self.scene == "faro":
            self.faro_exterior_scene.draw(self.progreso_luces, self.faro_desbloqueado)
        elif self.scene == "faro_interior":
            self.faro_interior_scene.draw(self.progreso_luces, self.inventory, self.puzle_luces_resuelto)
        elif self.scene == "faro_ventana":
            self.ventana_faro_scene.draw(self.puzle_luces_resuelto)
        elif self.scene == "bunker_interior":
            self.bunker_interior_scene.draw(self.inventory)
        elif self.scene == "luna":
            self.luna_scene.draw()

        # Dibujar elementos comunes del juego
        if self.scene != "luna":
            self._dibujar_jugador(self.player)
        self._dibujar_mensaje(self.message, self.message_timer, self.state.name, self.dialogue)
        self._dibujar_interfaz(("MIRAR", "USAR", "HABLAR", "AGARRAR"), self.verb, self.inventory)

        if self.depurar_puntos:
            for hotspot in self.hotspots[self.scene]:
                pygame.draw.rect(surface, (255, 255, 0), hotspot.rect, 2)

        if self.state == EstadoJuego.DIALOGO:
            self._dibujar_opciones_dialogo(self.dialogue_choices)
        elif self.state == EstadoJuego.TECLADO:
            self._dibujar_teclado(self.entrada_teclado)

        # Dibujar HUD de vidas (corazón)
        self._dibujar_hud_vidas()

        self._dibujar_cursor()

    def _dibujar_jugador(self, player_pos):
        """Dibuja el frame que corresponde al estado actual del jugador."""
        x, y = int(player_pos.x), int(player_pos.y)
        screen = self.game.screen
        pygame.draw.ellipse(screen, (23, 21, 35), (x - 23, y - 7, 46, 12))

        now = pygame.time.get_ticks()
        if self.state in (
            EstadoJuego.MIRANDO_LUNA,
            EstadoJuego.VOLVIENDO_BINOCULARES,
        ):
            frames = self.player_frames["binoculares"]
            elapsed = now - self.binoculares_animation_started
            animation_frame = elapsed // DURACION_FRAME_BINOCULARES
            if self.state == EstadoJuego.VOLVIENDO_BINOCULARES:
                frame_index = max(len(frames) - 1 - animation_frame, 0)
            else:
                frame_index = min(animation_frame, len(frames) - 1)
            image = frames[frame_index] if frames else None
        elif self.state == EstadoJuego.CAMINANDO:
            walk_direction = "walk_left" if self.target.x < self.player.x else "walk"
            frames = self.player_frames[walk_direction] or self.player_frames["walk"]
            if frames:
                frame_index = (now // DURACION_FRAME_CAMINAR) % len(frames)
                if walk_direction == "walk_left":
                    frame_index = len(frames) - 1 - frame_index
                image = frames[frame_index]
            else:
                image = None
        elif (
            self.state in (EstadoJuego.DIALOGO, EstadoJuego.TECLADO, EstadoJuego.INTERACTUANDO)
            or now < self.interact_until
        ):
            frames = self.player_frames["interact"]
            image = frames[0] if frames else None
        else:
            frames = self.player_frames["idle"]
            image = (
                frames[(now // DURACION_FRAME_IDLE) % len(frames)]
                if frames
                else None
            )

        if image is not None:
            screen.blit(image, image.get_rect(midbottom=(x, y)))
            return

        pygame.draw.rect(screen, (53, 43, 42), (x - 14, y - 52, 12, 29))
        pygame.draw.rect(screen, (53, 43, 42), (x + 2, y - 52, 12, 29))
        pygame.draw.rect(screen, (120, 73, 48), (x - 16, y - 28, 15, 26))
        pygame.draw.rect(screen, (120, 73, 48), (x + 1, y - 28, 15, 26))
        pygame.draw.rect(screen, (47, 94, 108), (x - 21, y - 91, 42, 65))
        pygame.draw.rect(screen, (228, 215, 174), (x - 20, y - 76, 40, 8))
        pygame.draw.rect(screen, (228, 215, 174), (x - 19, y - 53, 38, 7))
        pygame.draw.rect(screen, (207, 151, 109), (x - 15, y - 119, 31, 31))
        pygame.draw.rect(screen, (66, 43, 36), (x - 18, y - 125, 36, 12))
        pygame.draw.rect(screen, (235, 191, 117), (x - 22, y - 124, 44, 6))
        pygame.draw.rect(screen, (38, 35, 39), (x - 7, y - 108, 4, 4))
        pygame.draw.rect(screen, (38, 35, 39), (x + 3, y - 108, 4, 4))
        pygame.draw.rect(screen, (125, 72, 58), (x - 10, y - 94, 18, 4))

    def _dibujar_mensaje(self, message, message_timer, state, dialogue):
        """Dibuja mensajes temporales en pantalla con word wrapping dinámico."""
        if message and pygame.time.get_ticks() < message_timer:
            # Word wrapping para el mensaje
            panel_width = 660
            max_lines = 3  # Permitir hasta 3 líneas
            lines = []
            line = ""
            for word in message.split():
                candidate = (line + " " + word).strip()
                if line and self.font.size(candidate)[0] > panel_width - 24:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            if line:
                lines.append(line)
            lines = lines[:max_lines]

            # Calcular altura del panel dinámicamente
            panel_height = 58 + (len(lines) - 1) * 24
            panel = pygame.Rect(150, 14, panel_width, panel_height)

            # Panel con mayor contraste para mejor legibilidad del texto
            pygame.draw.rect(self.game.screen, (12, 15, 28), panel, border_radius=4)
            pygame.draw.rect(self.game.screen, DORADO, panel, 2, border_radius=4)

            # Centrar verticalmente el texto dentro del panel
            total_height = len(lines) * 24
            start_y = panel.centery - total_height // 2 + 8
            for index, line in enumerate(lines):
                # Texto más brillante y con mayor contraste, centrado vertical y horizontalmente
                self._draw_text(line, (panel.centerx, start_y + index * 24),
                                self.font, (255, 255, 255), centered=True)
        elif state == "DIALOGUE" and dialogue.active_message:
            dialogue.draw()

    def _dibujar_interfaz(self, verbs, verb, inventory):
        """Dibuja la interfaz de usuario (verbos e inventario)."""
        pygame.draw.rect(self.game.screen, (23, 22, 32), (0, INICIO_UI, ANCHO_VENTANA, ALTO_VENTANA - INICIO_UI))
        pygame.draw.line(self.game.screen, DORADO, (0, INICIO_UI), (ANCHO_VENTANA, INICIO_UI), 3)
        pygame.draw.rect(self.game.screen, PANEL, (12, INICIO_UI + 10, 430, 128))
        pygame.draw.rect(self.game.screen, DORADO, (12, INICIO_UI + 10, 430, 128), 2)
        self._draw_text("ACCIONES", (27, INICIO_UI + 25), self.small_font, DORADO)
        button_width, button_height = 92, 40
        for index, v in enumerate(verbs):
            rect = pygame.Rect(22 + index * (button_width + 14), INICIO_UI + 47, button_width, button_height)
            active = verb == v
            pygame.draw.rect(self.game.screen, (111, 78, 47) if active else (58, 52, 54), rect)
            pygame.draw.rect(self.game.screen, DORADO if active else (114, 102, 86), rect, 2)
            self._draw_text(v, rect.center, self.font, PAPEL, centered=True)
        self._draw_text("1-4", (412, INICIO_UI + 112), self.small_font, (161, 151, 134), centered=True)
        pygame.draw.rect(self.game.screen, PANEL, (457, INICIO_UI + 10, 490, 128))
        pygame.draw.rect(self.game.screen, DORADO, (457, INICIO_UI + 10, 490, 128), 2)
        self._draw_text("INVENTARIO", (472, INICIO_UI + 25), self.small_font, DORADO)
        if inventory.selected is not None:
            self._draw_text("Usando: " + inventory.selected.name,
                            (931, INICIO_UI + 25), self.small_font, PAPEL, right=True)
        slot, gap = 78, 12
        for index in range(inventory.capacity):
            rect = pygame.Rect(483 + index * (slot + gap), INICIO_UI + 47, slot, 76)
            pygame.draw.rect(self.game.screen, (55, 49, 48), rect)
            pygame.draw.rect(self.game.screen, DORADO if (
                index < len(inventory.items) and
                inventory.items[index] is inventory.selected
            ) else (117, 100, 75), rect, 2)
            if index < len(inventory.items):
                item = inventory.items[index]
                self._draw_item_icon(item.name, rect.centerx, rect.centery)

    def _dibujar_opciones_dialogo(self, dialogue_choices):
        """Dibuja las opciones de diálogo con word wrapping."""
        # Calcular altura dinámica según número de opciones y longitud de texto
        panel_width = 420
        option_height = 32
        padding = 20

        # Procesar cada opción para calcular el número de líneas
        option_lines = []
        for label, _ in dialogue_choices:
            # Word wrapping para cada opción
            words = label.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = (current_line + " " + word).strip() if current_line else word
                if self.font.size(test_line)[0] <= panel_width - 50:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            option_lines.append(lines)

        # Calcular altura total del panel
        total_lines = sum(len(lines) for lines in option_lines)
        panel_height = 50 + total_lines * option_height
        panel_y = max(100, (ALTO_VENTANA - panel_height) // 2)  # Centrado verticalmente

        panel = pygame.Rect(280, panel_y, panel_width, panel_height)

        # Overlay solo alrededor del panel (no pantalla completa)
        overlay_width = panel.width + 40
        overlay_height = panel.height + 40
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay.fill((5, 7, 17, 120))
        self.game.screen.blit(overlay, (panel.x - 20, panel.y - 20))

        pygame.draw.rect(self.game.screen, (34, 30, 37), panel, border_radius=6)
        pygame.draw.rect(self.game.screen, DORADO, panel, 3, border_radius=6)

        # Dibujar cada opción con sus líneas
        current_y = panel_y + 20
        for index, (label, _) in enumerate(dialogue_choices):
            lines = option_lines[index]
            # Dibujar botón de fondo para la primera línea
            rect = pygame.Rect(295, current_y, panel_width - 30, len(lines) * option_height)
            pygame.draw.rect(self.game.screen, (72, 55, 43), rect, border_radius=3)

            # Dibujar cada línea de texto
            for line_index, line in enumerate(lines):
                self._draw_text("› " + line if line_index == 0 else "  " + line,
                               (rect.x + 12, current_y + line_index * option_height + option_height // 2 - 6),
                               self.font, PAPEL)
            current_y += len(lines) * option_height

    def _dibujar_teclado(self, input_text):
        """Dibuja el teclado numérico para la caja fuerte."""
        # Overlay oscuro
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((5, 7, 17, 150))
        self.game.screen.blit(overlay, (0, 0))

        # Panel del teclado centrado
        button_size = 55
        gap = 10
        padding_left = 30
        padding_right = 25
        padding_top = 50
        padding_bottom = 30

        # Calcular dimensiones con márgenes asimétricos
        panel_width = 4 * (button_size + gap) - gap + padding_left + padding_right
        buttons_height = 4 * (button_size + gap) - gap
        panel_height = padding_top + padding_bottom + 25 + 45 + 10 + buttons_height

        # Centrar el panel en la pantalla
        keypad_x = (ANCHO_VENTANA - panel_width) // 2
        keypad_y = (ALTO_VENTANA - panel_height) // 2

        # Panel de fondo con padding asimétrico
        panel = pygame.Rect(keypad_x, keypad_y, panel_width, panel_height)
        pygame.draw.rect(self.game.screen, (34, 30, 37), panel, border_radius=10)
        pygame.draw.rect(self.game.screen, DORADO, panel, 4, border_radius=10)

        # Título del panel - con padding superior y fuente más grande
        self._draw_text("CÓDIGO DE ACCESO", (keypad_x + panel_width // 2, keypad_y + padding_top - 2),
                       self.large_font, DORADO, centered=True)

        # Display del código ingresado - un solo rectángulo con guiones bajos separados
        display_rect = pygame.Rect(keypad_x + padding_left, keypad_y + padding_top + 25, panel_width - padding_left - padding_right, 45)
        pygame.draw.rect(self.game.screen, (20, 18, 25), display_rect, border_radius=5)
        pygame.draw.rect(self.game.screen, (107, 180, 129), display_rect, 3, border_radius=5)

        # Dibujar cada dígito/guión individualmente con espaciado
        display_font = pygame.font.Font(None, 42)
        total_digits = 4
        digit_spacing = 35
        total_width = (total_digits - 1) * digit_spacing
        start_x = keypad_x + panel_width // 2 - total_width // 2
        digit_y = keypad_y + padding_top + 25 + 45 // 2

        for i in range(total_digits):
            if i < len(input_text):
                char = input_text[i]
                char_color = (255, 255, 255)
            else:
                char = "_"
                char_color = (150, 150, 150)
            x = start_x + i * digit_spacing
            self._draw_text(char, (x, digit_y), display_font, char_color, centered=True)

        # Botones de números 1-9
        btn_start_y = keypad_y + padding_top + 80
        for row in range(3):
            for col in range(3):
                num = row * 3 + col + 1
                btn_x = keypad_x + padding_left + col * (button_size + gap)
                btn_y = btn_start_y + row * (button_size + gap)
                rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
                pygame.draw.rect(self.game.screen, (72, 55, 43), rect, border_radius=6)
                pygame.draw.rect(self.game.screen, (98, 82, 65), rect, 3, border_radius=6)
                self._draw_text(str(num), (btn_x + button_size // 2, btn_y + button_size // 2),
                               self.large_font, PAPEL, centered=True)

        # Botón 0
        btn_x = keypad_x + padding_left + (button_size + gap)
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        pygame.draw.rect(self.game.screen, (72, 55, 43), rect, border_radius=6)
        pygame.draw.rect(self.game.screen, (98, 82, 65), rect, 3, border_radius=6)
        self._draw_text("0", (btn_x + button_size // 2, btn_y + button_size // 2),
                       self.large_font, PAPEL, centered=True)

        # Botón Borrar (X)
        btn_x = keypad_x + padding_left
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        pygame.draw.rect(self.game.screen, (145, 55, 55), rect, border_radius=6)
        pygame.draw.rect(self.game.screen, (175, 75, 75), rect, 3, border_radius=6)
        self._draw_text("X", (btn_x + button_size // 2, btn_y + button_size // 2),
                       self.large_font, PAPEL, centered=True)

        # Botón Enter/Aceptar (OK)
        btn_x = keypad_x + padding_left + 2 * (button_size + gap)
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        pygame.draw.rect(self.game.screen, (55, 145, 95), rect, border_radius=6)
        pygame.draw.rect(self.game.screen, (75, 175, 115), rect, 3, border_radius=6)
        self._draw_text("OK", (btn_x + button_size // 2, btn_y + button_size // 2),
                       self.large_font, PAPEL, centered=True)

        # Botón Cancelar (C)
        btn_x = keypad_x + padding_left + 3 * (button_size + gap)
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        pygame.draw.rect(self.game.screen, (145, 95, 55), rect, border_radius=6)
        pygame.draw.rect(self.game.screen, (175, 115, 75), rect, 3, border_radius=6)
        self._draw_text("C", (btn_x + button_size // 2, btn_y + button_size // 2),
                       self.large_font, PAPEL, centered=True)

    def _draw_item_icon(self, name, x, y):
        """Dibuja el icono de un item en el inventario."""
        if name == "Barra de hierro":
            pygame.draw.rect(self.game.screen, (145, 145, 155), (x - 5, y - 22, 10, 44))
            pygame.draw.rect(self.game.screen, (178, 178, 188), (x - 5, y - 22, 10, 44), 2)
            pygame.draw.circle(self.game.screen, (168, 145, 125), (x, y), 4)
        elif name == "Barril":
            pygame.draw.ellipse(self.game.screen, (76, 47, 36), (x - 20, y - 18, 40, 36))
            pygame.draw.rect(self.game.screen, (112, 65, 43), (x - 17, y - 15, 34, 30))
            pygame.draw.line(self.game.screen, (190, 135, 72), (x - 10, y - 14), (x - 10, y + 14), 3)
            pygame.draw.line(self.game.screen, (190, 135, 72), (x + 10, y - 14), (x + 10, y + 14), 3)
            pygame.draw.arc(self.game.screen, (188, 139, 79), (x - 18, y - 12, 36, 20), 0, 3.14, 2)
        elif name == "Binoculares":
            pygame.draw.circle(self.game.screen, (83, 91, 82), (x - 11, y), 11)
            pygame.draw.circle(self.game.screen, (83, 91, 82), (x + 11, y), 11)
            pygame.draw.circle(self.game.screen, (154, 174, 158), (x - 11, y), 7, 2)
            pygame.draw.circle(self.game.screen, (154, 174, 158), (x + 11, y), 7, 2)
            pygame.draw.rect(self.game.screen, (83, 91, 82), (x - 5, y - 4, 10, 8))
        elif name == "Llave vieja":
            offset_x = x - 4
            pygame.draw.circle(self.game.screen, (168, 145, 118), (offset_x - 8, y), 12)
            pygame.draw.circle(self.game.screen, (145, 125, 98), (offset_x - 8, y), 12, 2)
            pygame.draw.circle(self.game.screen, (130, 110, 85), (offset_x - 8, y), 5, 2)
            pygame.draw.rect(self.game.screen, (168, 145, 118), (offset_x + 4, y - 3, 22, 6))
            pygame.draw.rect(self.game.screen, (145, 125, 98), (offset_x + 4, y - 3, 22, 6), 2)
            pygame.draw.rect(self.game.screen, (168, 145, 118), (offset_x + 26, y - 2, 6, 10))
            pygame.draw.rect(self.game.screen, (145, 125, 98), (offset_x + 26, y - 2, 6, 10), 2)
            pygame.draw.line(self.game.screen, (185, 165, 135), (offset_x + 26, y - 2), (offset_x + 26, y + 8), 1)
        elif name == "Llave maestra":
            offset_x = x - 4
            pygame.draw.circle(self.game.screen, (218, 185, 118), (offset_x - 8, y), 12)
            pygame.draw.circle(self.game.screen, (198, 165, 98), (offset_x - 8, y), 12, 2)
            pygame.draw.circle(self.game.screen, (175, 145, 85), (offset_x - 8, y), 5, 2)
            pygame.draw.rect(self.game.screen, (218, 185, 118), (offset_x + 4, y - 3, 22, 6))
            pygame.draw.rect(self.game.screen, (198, 165, 98), (offset_x + 4, y - 3, 22, 6), 2)
            pygame.draw.rect(self.game.screen, (218, 185, 118), (offset_x + 26, y - 2, 6, 10))
            pygame.draw.rect(self.game.screen, (198, 165, 98), (offset_x + 26, y - 2, 6, 10), 2)
            pygame.draw.line(self.game.screen, (235, 205, 135), (offset_x + 26, y - 2), (offset_x + 26, y + 8), 1)
            pygame.draw.circle(self.game.screen, (248, 212, 138), (offset_x - 8, y), 4)
            pygame.draw.circle(self.game.screen, (230, 195, 120), (offset_x - 8, y), 4, 1)
        elif name == "Tarjeta de acceso":
            pygame.draw.rect(self.game.screen, (178, 185, 195), (x - 20, y - 12, 40, 24))
            pygame.draw.rect(self.game.screen, (145, 152, 162), (x - 20, y - 12, 40, 24), 2)
            pygame.draw.rect(self.game.screen, (42, 42, 52), (x - 18, y + 2, 36, 8))
            pygame.draw.rect(self.game.screen, (168, 165, 155), (x - 15, y - 9, 10, 8))
            pygame.draw.rect(self.game.screen, (145, 142, 132), (x - 15, y - 9, 10, 8), 1)
        else:
            pygame.draw.rect(self.game.screen, (168, 157, 126), (x - 8, y - 24, 16, 48))
            pygame.draw.circle(self.game.screen, (230, 192, 108), (x, y - 24), 10)
            pygame.draw.rect(self.game.screen, (230, 192, 108), (x + 8, y + 10, 18, 6))

    def _draw_text(self, text, position, font, color, centered=False, right=False):
        """Dibuja texto."""
        image = font.render(text, True, color)
        if centered:
            rect = image.get_rect(center=position)
        elif right:
            rect = image.get_rect(midright=position)
        else:
            rect = image.get_rect(topleft=position)
        self.game.screen.blit(image, rect)

    def _dibujar_cursor(self):
        """Dibuja el cursor personalizado en la posición actual del mouse."""
        mouse_pos = pygame.mouse.get_pos()
        if self.cursor_image is not None:
            self.game.screen.blit(self.cursor_image, mouse_pos)
        else:
            # Cursor de respaldo si la imagen no carga
            x, y = mouse_pos
            pygame.draw.polygon(self.game.screen, (255, 255, 255), [(x, y), (x, y+15), (x+10, y+10)])
            pygame.draw.polygon(self.game.screen, (0, 0, 0), [(x, y), (x, y+15), (x+10, y+10)], 1)

    def _dibujar_hud_vidas(self):
        """Dibuja el HUD de vidas en la esquina superior derecha."""
        if self.heart_image is not None:
            margin = 24

            lives_text = self.small_font.render("VIDAS:", True, (255, 255, 255))
            text_width = lives_text.get_width()
            heart_width = 24
            separation = 8

            total_width = text_width + separation + heart_width
            x = ANCHO_VENTANA - total_width - margin
            y = 12

            self.game.screen.blit(lives_text, (x, y))

            heart_x = x + text_width + separation
            heart_y = y - 6
            self.game.screen.blit(self.heart_image, (heart_x, heart_y))
