"""Escena del menú principal de la aventura gráfica."""

import os
import pygame
from engine.ui import Scene, Button
from engine.shared_assets import MUSIC_VOLUME, music_path


class MenuScene(Scene):
    """Menú principal con título y botón para comenzar."""

    def __init__(self, game):
        super().__init__(game)

        # Fuentes
        self.font_title = pygame.font.Font(None, 78)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_hint = pygame.font.Font(None, 26)

        # Cargar fondo del menú
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            background_path = os.path.join(root_dir, "assets", "sprites", "menu.png")
            background = pygame.image.load(background_path).convert()
            self.background_image = pygame.transform.smoothscale(background, game.screen.get_size())
        except pygame.error:
            self.background_image = None

        # Cargar cursor personalizado
        try:
            cursor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except:
            self.cursor_image = None

        # Verificar si hay un juego en curso
        self.game_started = hasattr(game, 'game_scene') and game.game_scene is not None

        self.volume_slider_rect = pygame.Rect(330, 390, 300, 65)
        self.dragging_volume = False
        self.show_volume = False
        self.boton_volver = None

        # Crear botones iniciales
        self._crear_botones()

        # Animación
        self.t = 0.0

    def _crear_botones(self):
        """Crea los botones según el estado del juego."""
        if self.game_started:
            self.boton_reanudar = Button(
                330, 320, 300, 60, "Reanudar", self.reanudar_juego,
                font_size=36, color=(90, 150, 220), hover_color=(110, 170, 240)
            )
            self.boton_opciones = Button(
                330, 395, 300, 60, "Opciones", self.opciones,
                font_size=36, color=(150, 150, 150), hover_color=(170, 170, 170)
            )
            self.boton_reiniciar = Button(
                330, 470, 300, 60, "Reiniciar", self.reiniciar_juego,
                font_size=36, color=(220, 160, 60), hover_color=(240, 180, 80)
            )
            self.boton_salir = Button(
                330, 545, 300, 60, "Salir", self.salir,
                font_size=36, color=(220, 90, 90), hover_color=(240, 110, 110)
            )
        else:
            self.boton_comenzar = Button(
                330, 340, 300, 60, "Empezar", self.comenzar_juego,
                font_size=36, color=(90, 150, 220), hover_color=(110, 170, 240)
            )
            self.boton_salir = Button(
                330, 420, 300, 60, "Salir", self.salir,
                font_size=36, color=(220, 90, 90), hover_color=(240, 110, 110)
            )

    def on_enter(self):
        """Se ejecuta al entrar al menú."""
        self.t = 0.0
        # Actualizar estado del juego
        self.game_started = hasattr(self.game, 'game_scene') and self.game.game_scene is not None
        # Recrear botones según el estado
        self._crear_botones()
        # Desactivar cursor nativo (usaremos cursor personalizado)
        pygame.mouse.set_visible(False)
        # Cargar y reproducir música del menú solo si no hay juego en pausa
        if not self.game_started and hasattr(self.game, 'audio') and self.game.audio.enabled:
            try:
                self.game.audio.load_music(music_path("menu_principal", "mp3"))
                self.game.audio.play_music(loops=-1, volume=self.game.audio.music_volume)
            except Exception as e:
                pass

    def on_exit(self):
        """Se ejecuta al salir del menú."""
        pass

    def comenzar_juego(self):
        """Inicia el juego cambiando a la escena 'game'."""
        # Detener música del menú
        if hasattr(self.game, 'audio') and self.game.audio.enabled:
            try:
                self.game.audio.stop_music()
            except:
                pass

        # Reproducir sonido de click si existe
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass

        # Crear nueva escena del juego (borrar la anterior si existe)
        self.game.game_scene = None
        self.game.change_scene("game")

    def reanudar_juego(self):
        """Reanuda el juego existente."""
        # Reproducir sonido de click si existe
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass

        # Cambiar a la escena del juego existente
        self.game.change_scene("game")

    def opciones(self):
        """Muestra el control de volumen."""
        # Reproducir sonido de click si existe
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass
        self.show_volume = not self.show_volume
        if self.show_volume:
            self.boton_volver = Button(330, 470, 300, 60, "Volver", self.opciones, font_size=36, color=(150, 150, 150), hover_color=(170, 170, 170))
        else:
            self.boton_volver = None



    def _set_volume_from_mouse(self, mouse_x):
        """Ajusta el volumen según la posición horizontal del slider."""
        track_start = self.volume_slider_rect.left + 20
        track_end = self.volume_slider_rect.right - 20
        # Calcular volumen basado en la posición del mouse
        volume = (mouse_x - track_start) / (track_end - track_start)
        # El slider va de 0-100%
        volume = max(0.0, min(1.0, volume))
        # Guardar el volumen del slider (0-1) directamente en music_volume
        self.game.audio.music_volume = volume
        # Aplicar el factor de 0.20 al volumen real del mixer
        if self.game.audio.enabled:
            pygame.mixer.music.set_volume(volume * 0.20)

    def reiniciar_juego(self):
        """Reinicia el juego desde el principio."""
        # Detener música del menú
        if hasattr(self.game, 'audio') and self.game.audio.enabled:
            try:
                self.game.audio.stop_music()
            except:
                pass

        # Reproducir sonido de click si existe
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass

        # Crear nueva escena del juego
        self.game.game_scene = None
        self.game.change_scene("game")

    def salir(self):
        """Sale del juego."""
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass
        self.game.running = False

    def handle_events(self, events):
        """Maneja eventos del menú."""
        for event in events:
            if self.game_started:
                if self.show_volume:
                    if self.boton_volver:
                        self.boton_volver.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.volume_slider_rect.collidepoint(event.pos):
                            self.dragging_volume = True
                            self._set_volume_from_mouse(event.pos[0])
                            # Capturar el cursor dentro del área del slider
                            pygame.event.set_grab(True)
                    elif event.type == pygame.MOUSEMOTION and self.dragging_volume:
                        self._set_volume_from_mouse(event.pos[0])
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.dragging_volume = False
                        # Liberar el cursor
                        pygame.event.set_grab(False)
                else:
                    self.boton_reanudar.handle_event(event)
                    self.boton_opciones.handle_event(event)
                    self.boton_reiniciar.handle_event(event)
                    self.boton_salir.handle_event(event)
            else:
                self.boton_comenzar.handle_event(event)
                self.boton_salir.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_started:
                        self.reanudar_juego()
                    else:
                        self.salir()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.game_started:
                        self.reanudar_juego()
                    else:
                        self.comenzar_juego()

    def update(self):
        """Actualiza animaciones."""
        self.t += 1.0 / self.game.fps

    def draw(self, surface):
        """Dibuja el menú principal."""
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((25, 30, 50))
        
        # Título principal
        title_surf = self.font_title.render("LA ISLA", True, (255, 235, 150))
        surface.blit(title_surf, title_surf.get_rect(centerx=surface.get_width() // 2, y=110))

        title_surf2 = self.font_title.render("OLVIDADA", True, (255, 235, 150))
        surface.blit(title_surf2, title_surf2.get_rect(centerx=surface.get_width() // 2, y=180))

        # Subtítulo
        subtitle_surf = self.font_subtitle.render("Una aventura gráfica point-and-click", True, (240, 240, 255))
        surface.blit(subtitle_surf, subtitle_surf.get_rect(centerx=surface.get_width() // 2, y=250))
        
        # Dibujar botones
        if self.game_started:
            if self.show_volume:
                display_volume = min(100, round(self.game.audio.music_volume * 100))
                volume_text = self.font_hint.render(
                    f"Volumen de música: {display_volume}%",
                    True, (255, 255, 255)
                )
                surface.blit(volume_text, volume_text.get_rect(center=(surface.get_width() // 2, 404)))

                track_start = self.volume_slider_rect.left + 20
                track_end = self.volume_slider_rect.right - 20
                track_y = 435
                knob_x = track_start + round((track_end - track_start) * min(1.0, self.game.audio.music_volume))
                pygame.draw.line(surface, (35, 40, 55), (track_start, track_y), (track_end, track_y), 10)
                pygame.draw.line(surface, (100, 175, 235), (track_start, track_y), (knob_x, track_y), 6)
                pygame.draw.circle(surface, (245, 245, 250), (knob_x, track_y), 11)
                pygame.draw.circle(surface, (35, 40, 55), (knob_x, track_y), 11, 2)

                if self.boton_volver:
                    self.boton_volver.draw(surface)
            else:
                self.boton_reanudar.draw(surface)
                self.boton_opciones.draw(surface)
                self.boton_reiniciar.draw(surface)
                self.boton_salir.draw(surface)
        else:
            self.boton_comenzar.draw(surface)
            self.boton_salir.draw(surface)
        
        # Texto de hint
        # Solo mostrar en el menú principal inicial, nunca en pausa
        if not self.game_started:
            hint_text = "Presiona ENTER o haz clic para comenzar"
            hint_surf = self.font_hint.render(hint_text, True, (220, 220, 240))
            surface.blit(hint_surf, hint_surf.get_rect(centerx=surface.get_width() // 2, y=510))
        
        # Dibujar cursor personalizado al final
        mouse_pos = pygame.mouse.get_pos()
        if self.cursor_image:
            # Ajustar offset para que la punta del cursor coincida con el punto de clic
            surface.blit(self.cursor_image, (mouse_pos[0] - 8, mouse_pos[1] - 5))
        else:
            # Cursor de respaldo
            x, y = mouse_pos
            pygame.draw.polygon(surface, (255, 255, 255), [(x, y), (x, y+15), (x+10, y+10)])
            pygame.draw.polygon(surface, (0, 0, 0), [(x, y), (x, y+15), (x+10, y+10)], 1)
