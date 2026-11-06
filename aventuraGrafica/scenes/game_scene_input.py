"""GameSceneInput for the main game scene."""

import pygame

from .game_scene_config import ALTO_VENTANA, ANCHO_VENTANA, INICIO_UI, EstadoJuego
from .puzzles import PuzzleManager


class GameSceneInputMixin:
    """Handles input for GameScene."""

    def handle_events(self, events):
        """Maneja eventos del juego."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == EstadoJuego.DIALOGO:
                        self.state = EstadoJuego.INACTIVO
                        self.dialogue.clear_message()
                        self.current_npc = None
                    elif self.state == EstadoJuego.TECLADO:
                        self.state = EstadoJuego.INACTIVO
                        self.dialogue.clear_message()
                        self.entrada_teclado = ""
                    else:
                        self.game.change_scene("menu")
                elif event.key == pygame.K_F1:
                    self.depurar_puntos = not self.depurar_puntos
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.verb = ("MIRAR", "USAR", "HABLAR", "AGARRAR")[event.key - pygame.K_1]
                elif event.key == pygame.K_r and self.state == EstadoJuego.GANADO:
                    # Reiniciar juego
                    self.__init__(self.game)
                elif self.state == EstadoJuego.TECLADO and event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    # Borrar último dígito en el keypad
                    if self.entrada_teclado:
                        self.entrada_teclado = self.entrada_teclado[:-1]
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._manejar_click(event.pos)
            elif event.type == pygame.USEREVENT:
                # Timer para cambiar a victoria
                pygame.time.set_timer(pygame.USEREVENT, 0)
                self.game.change_scene("victory")

    def _manejar_click(self, position):
        """Maneja clics del mouse."""
        if self.state in (
            EstadoJuego.MIRANDO_LUNA,
            EstadoJuego.VOLVIENDO_BINOCULARES,
        ):
            return
        if self.state == EstadoJuego.GANADO:
            self.game.change_scene("victory")
            return
        if self.state == EstadoJuego.DIALOGO:
            self._click_dialogo(position)
            return
        if self.state == EstadoJuego.TECLADO:
            self._click_teclado(position)
            return
        if position[1] >= INICIO_UI:
            self._click_ui(position)
            return

        # Verificar si se clickeó en un hotspot
        for hotspot in self.hotspots[self.scene]:
            if hotspot.contains(position):
                # Todas las interacciones (incluyendo puertas/salidas) requieren caminar primero
                self._iniciar_interaccion(hotspot)
                return

        # Si no se clickeó en ningún hotspot, caminar hacia esa posición
        self.pending_hotspot = None
        self.target = self._punto_caminable_mas_cercano(position)
        self.state = EstadoJuego.CAMINANDO

    def _click_ui(self, position):
        """Maneja clics en la UI."""
        x, y = position
        button_width, button_height = 98, 40
        verbs_origin = (18, INICIO_UI + 41)
        for index, verb in enumerate(("MIRAR", "USAR", "HABLAR", "AGARRAR")):
            rect = pygame.Rect(verbs_origin[0] + index * (button_width + 7),
                               verbs_origin[1], button_width, button_height)
            if rect.collidepoint(position):
                self.verb = verb
                return
        slot, gap = 78, 8
        inventory_origin = (475, INICIO_UI + 43)
        for index, item in enumerate(self.inventory.items):
            rect = pygame.Rect(inventory_origin[0] + index * (slot + gap),
                               inventory_origin[1], slot, 76)
            if rect.collidepoint(position):
                selected = self.inventory.selected
                if selected is not None and selected is not item and self.verb == "USAR":
                    self._combine_items(selected, item)
                elif selected is item:
                    self.inventory.select("")
                    self.verb = "MIRAR"
                else:
                    self.inventory.select(item.name)
                    self.verb = "USAR"
                return
        if x < 455 and y > INICIO_UI + 90:
            self.verb = "MIRAR"

    def _click_dialogo(self, position):
        """Maneja clics en opciones de diálogo con word wrapping."""
        panel_width = 420
        option_height = 32

        # Calcular el mismo layout que dibujar_opciones_dialogo
        option_lines = []
        for label, _ in self.dialogue_choices:
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

        total_lines = sum(len(lines) for lines in option_lines)
        panel_height = 50 + total_lines * option_height
        panel_y = max(100, (640 - panel_height) // 2)

        # Calcular áreas de clic
        current_y = panel_y + 20
        for index, (_, choice) in enumerate(self.dialogue_choices):
            lines = option_lines[index]
            rect = pygame.Rect(295, current_y, panel_width - 30, len(lines) * option_height)
            if rect.collidepoint(position):
                self._elegir_dialogo(choice)
                return
            current_y += len(lines) * option_height

    def _click_teclado(self, position):
        """Maneja clics en el teclado numérico."""
        button_size = 55
        gap = 10
        padding_left = 30
        padding_right = 25
        padding_top = 50
        padding_bottom = 30
        click_margin = 5

        panel_width = 4 * (button_size + gap) - gap + padding_left + padding_right
        buttons_height = 4 * (button_size + gap) - gap
        panel_height = padding_top + padding_bottom + 25 + 45 + 10 + buttons_height

        keypad_x = (ANCHO_VENTANA - panel_width) // 2
        keypad_y = (ALTO_VENTANA - panel_height) // 2

        panel_rect = pygame.Rect(keypad_x, keypad_y, panel_width, panel_height)
        if not panel_rect.collidepoint(position):
            return

        btn_start_y = keypad_y + padding_top + 80

        for row in range(3):
            for col in range(3):
                num = row * 3 + col + 1
                btn_x = keypad_x + padding_left + col * (button_size + gap) - click_margin
                btn_y = btn_start_y + row * (button_size + gap) - click_margin
                rect = pygame.Rect(btn_x, btn_y, button_size + click_margin * 2, button_size + click_margin * 2)
                if rect.collidepoint(position):
                    if len(self.entrada_teclado) < 4:
                        self.entrada_teclado += str(num)
                    return

        btn_x = keypad_x + padding_left + (button_size + gap) - click_margin
        btn_y = btn_start_y + 3 * (button_size + gap) - click_margin
        rect = pygame.Rect(btn_x, btn_y, button_size + click_margin * 2, button_size + click_margin * 2)
        if rect.collidepoint(position):
            if len(self.entrada_teclado) < 4:
                self.entrada_teclado += "0"
            return

        btn_x = keypad_x + padding_left
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        if rect.collidepoint(position):
            self.entrada_teclado = self.entrada_teclado[:-1]
            return

        btn_x = keypad_x + padding_left + 2 * (button_size + gap)
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        if rect.collidepoint(position):
            if len(self.entrada_teclado) == 4:
                # Verificar código con callback de Game Over
                if PuzzleManager.verificar_codigo_bunker(self.entrada_teclado, self._trigger_game_over):
                    self.caja_fuerte_abierta = True
                    self.state = EstadoJuego.INACTIVO
                    self.dialogue.clear_message()
                    self._say("¡Código correcto!. Ahora puedes usar la palanca secreta.")
                # Nota: si el código es incorrecto, el callback ya disparó Game Over
            else:
                self._say("Ingresa 4 dígitos.", duration=1)
            return

        btn_x = keypad_x + padding_left + 3 * (button_size + gap)
        btn_y = btn_start_y + 3 * (button_size + gap)
        rect = pygame.Rect(btn_x, btn_y, button_size, button_size)
        if rect.collidepoint(position):
            self.state = EstadoJuego.INACTIVO
            self.dialogue.clear_message()
            self.entrada_teclado = ""
            return
