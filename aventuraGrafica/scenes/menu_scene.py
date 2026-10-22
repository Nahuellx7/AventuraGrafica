"""Escena del menú principal de la aventura gráfica."""

import os
import pygame
from engine.ui import Scene, Button
from engine.shared_assets import shared_dir


class MenuScene(Scene):
    """Menú principal con título y botón para comenzar."""

    def __init__(self, game):
        super().__init__(game)

        # Fuentes
        self.font_title = pygame.font.Font(None, 78)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_hint = pygame.font.Font(None, 26)

        try:
            cursor_path = os.path.join(shared_dir(), "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except:
            self.cursor_image = None

        self.game_started = getattr(game, "game_scene", None) is not None
        self.stars = self._generate_stars()
        self.t = 0.0
        self._create_buttons()

    def _generate_stars(self):
        """Genera estrellas para el fondo."""
        import random

        random.seed(42)
        stars = []
        for _ in range(150):
            x = random.randint(0, 960)
            y = random.randint(0, 640)
            size = random.randint(1, 3)
            brightness = random.randint(230, 255)
            twinkle_speed = random.uniform(0.5, 2.0)
            stars.append({'x': x, 'y': y, 'size': size, 'brightness': brightness, 'speed': twinkle_speed})
        return stars

    def _create_buttons(self):
        if self.game_started:
            self.boton_reanudar = Button(
                330, 330, 300, 60, "Reanudar", self.reanudar_juego,
                font_size=36, color=(90, 150, 220), hover_color=(110, 170, 240)
            )
            self.boton_reiniciar = Button(
                330, 410, 300, 60, "Reiniciar", self.reiniciar_juego,
                font_size=36, color=(220, 160, 60), hover_color=(240, 180, 80)
            )
            self.boton_salir = Button(
                330, 490, 300, 60, "Salir", self.salir,
                font_size=36, color=(220, 90, 90), hover_color=(240, 110, 110)
            )
        else:
            self.boton_comenzar = Button(
                330, 350, 300, 60, "Empezar", self.comenzar_juego,
                font_size=36, color=(90, 150, 220), hover_color=(110, 170, 240)
            )
            self.boton_salir = Button(
                330, 430, 300, 60, "Salir", self.salir,
                font_size=36, color=(220, 90, 90), hover_color=(240, 110, 110)
            )

    def on_enter(self):
        self.t = 0.0
        self.game_started = getattr(self.game, "game_scene", None) is not None
        self._create_buttons()
        pygame.mouse.set_visible(False)
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_music(volume=0.3)
            except:
                pass

    def on_exit(self):
        """Se ejecuta al salir del menú."""
        pass

    def comenzar_juego(self):
        """Inicia el juego cambiando a la escena 'game'."""
        self._play_click()
        self.game.game_scene = None
        self.game.change_scene("game")

    def reanudar_juego(self):
        """Reanuda el juego existente."""
        self._play_click()
        self.game.change_scene("game")

    def reiniciar_juego(self):
        """Reinicia el juego desde el principio."""
        self._play_click()
        self.game.game_scene = None
        self.game.change_scene("game")

    def _play_click(self):
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass

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
                self.boton_reanudar.handle_event(event)
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
        # Fondo con degradado épico (azul oscuro a dorado) - más brillante
        for y in range(0, surface.get_height(), 4):
            progress = y / surface.get_height()
            r = int(25 + progress * 120)
            g = int(30 + progress * 100)
            b = int(50 + progress * 80)
            pygame.draw.rect(surface, (r, g, b), (0, y, surface.get_width(), 4))

        # Estrellas titilantes
        for star in self.stars:
            twinkle = int((pygame.math.Vector2(1, 1).length() * 0.5 + 0.5) * 50)
            brightness = min(255, star['brightness'] + twinkle)
            pygame.draw.circle(surface, (brightness, brightness, brightness),
                            (star['x'], star['y']), star['size'])
        
        # Título principal
        title_surf = self.font_title.render("LA ISLA", True, (255, 235, 150))
        surface.blit(title_surf, title_surf.get_rect(centerx=surface.get_width() // 2, y=120))

        title_surf2 = self.font_title.render("OLVIDADA", True, (255, 235, 150))
        surface.blit(title_surf2, title_surf2.get_rect(centerx=surface.get_width() // 2, y=190))

        # Subtítulo
        subtitle_surf = self.font_subtitle.render("Una aventura gráfica point-and-click", True, (240, 240, 255))
        surface.blit(subtitle_surf, subtitle_surf.get_rect(centerx=surface.get_width() // 2, y=260))
        
        # Dibujar botones
        if self.game_started:
            self.boton_reanudar.draw(surface)
            self.boton_reiniciar.draw(surface)
            self.boton_salir.draw(surface)
        else:
            self.boton_comenzar.draw(surface)
            self.boton_salir.draw(surface)
        
        # Texto de hint
        # Solo mostrar en el menú principal inicial, nunca en pausa
        has_game_active = hasattr(self.game, 'game_scene') and self.game.game_scene is not None
        if not has_game_active:
            hint_text = "Presiona ENTER o haz clic para comenzar"
            hint_surf = self.font_hint.render(hint_text, True, (220, 220, 240))
            surface.blit(hint_surf, hint_surf.get_rect(centerx=surface.get_width() // 2, y=520))
        
        # Dibujar cursor personalizado al final
        mouse_pos = pygame.mouse.get_pos()
        if self.cursor_image:
            surface.blit(self.cursor_image, mouse_pos)
        else:
            # Cursor de respaldo
            x, y = mouse_pos
            pygame.draw.polygon(surface, (255, 255, 255), [(x, y), (x, y+15), (x+10, y+10)])
            pygame.draw.polygon(surface, (0, 0, 0), [(x, y), (x, y+15), (x+10, y+10)], 1)
