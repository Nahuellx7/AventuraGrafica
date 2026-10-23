"""Escena de Game Over - pantalla de derrota."""

import os
import pygame
from engine.ui import Scene, Button


class GameOverScene(Scene):
    """Pantalla de Game Over con opciones de reintentar o volver al menú."""

    def __init__(self, game):
        super().__init__(game)

        # Fuentes
        self.font_title = pygame.font.Font(None, 82)
        self.font_message = pygame.font.Font(None, 36)
        self.font_hint = pygame.font.Font(None, 26)

        # Cargar cursor personalizado
        try:
            cursor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except:
            self.cursor_image = None

        # Botones
        self.boton_reintentar = Button(
            230, 350, 220, 60, "Reintentar", self.reintentar,
            font_size=36, color=(90, 150, 220), hover_color=(110, 170, 240)
        )

        self.boton_menu = Button(
            510, 350, 220, 60, "Menú Principal", self.volver_menu,
            font_size=36, color=(220, 90, 90), hover_color=(240, 110, 110)
        )

        # Animación
        self.t = 0.0
        self.stars = self._generate_stars()

    def _generate_stars(self):
        """Genera estrellas para el fondo."""
        import random
        random.seed(99)
        stars = []
        for _ in range(80):
            x = random.randint(0, 960)
            y = random.randint(0, 640)
            size = random.randint(1, 3)
            brightness = random.randint(80, 120)
            twinkle_speed = random.uniform(0.5, 2.0)
            stars.append({'x': x, 'y': y, 'size': size, 'brightness': brightness, 'speed': twinkle_speed})
        return stars

    def on_enter(self):
        """Se ejecuta al entrar a la escena de game over."""
        self.t = 0.0
        # Desactivar cursor nativo (usaremos cursor personalizado)
        pygame.mouse.set_visible(False)
        # Reproducir sonido de game over si existe
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("wrong")
            except:
                pass

    def on_exit(self):
        """Se ejecuta al salir de la escena de game over."""
        pass

    def reintentar(self):
        """Reinicia el juego desde el principio."""
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass
        # Limpiar la referencia al game_scene para reiniciar completamente
        self.game.game_scene = None
        # Cambiar a la escena del juego (reinicia el estado)
        self.game.change_scene("game")

    def volver_menu(self):
        """Vuelve al menú principal."""
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass
        self.game.change_scene("menu")

    def handle_events(self, events):
        """Maneja eventos de la pantalla de game over."""
        for event in events:
            self.boton_reintentar.handle_event(event)
            self.boton_menu.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.volver_menu()
                elif event.key == pygame.K_r:
                    self.reintentar()
                elif event.key == pygame.K_m:
                    self.volver_menu()

    def update(self):
        """Actualiza animaciones."""
        self.t += 1.0 / self.game.fps

    def draw(self, surface):
        """Dibuja la pantalla de game over con el mismo estilo que el menú y victoria."""
        # Fondo con degradado épico (azul oscuro a dorado) - más oscuro para game over
        for y in range(0, surface.get_height(), 4):
            progress = y / surface.get_height()
            r = int(20 + progress * 80)
            g = int(25 + progress * 60)
            b = int(40 + progress * 50)
            pygame.draw.rect(surface, (r, g, b), (0, y, surface.get_width(), 4))

        # Estrellas titilantes (más tenues)
        for star in self.stars:
            twinkle = int((pygame.math.Vector2(1, 1).length() * 0.5 + 0.5) * 30)
            brightness = min(200, star['brightness'] + twinkle)
            pygame.draw.circle(surface, (brightness, brightness, brightness),
                            (star['x'], star['y']), star['size'])

        # Título GAME OVER
        title_surf = self.font_title.render("GAME OVER", True, (200, 80, 80))
        # Efecto de sombra
        shadow_surf = self.font_title.render("GAME OVER", True, (100, 40, 40))
        surface.blit(shadow_surf, shadow_surf.get_rect(centerx=surface.get_width() // 2 + 3, y=80 + 3))
        surface.blit(title_surf, title_surf.get_rect(centerx=surface.get_width() // 2, y=80))

        # Subtítulo - Única línea de texto
        message_surf = self.font_message.render("La combinación falló y la isla permanecerá en la oscuridad.", True, (180, 160, 140))
        surface.blit(message_surf, message_surf.get_rect(centerx=surface.get_width() // 2, y=200))

        # Dibujar botones
        self.boton_reintentar.draw(surface)
        self.boton_menu.draw(surface)

        # Texto de hint
        hint_surf = self.font_hint.render("Presiona R para reintentar o M para volver al menú", True, (200, 200, 220))
        surface.blit(hint_surf, hint_surf.get_rect(centerx=surface.get_width() // 2, y=450))

        # Dibujar cursor personalizado al final
        mouse_pos = pygame.mouse.get_pos()
        if self.cursor_image:
            surface.blit(self.cursor_image, mouse_pos)
        else:
            # Cursor de respaldo
            x, y = mouse_pos
            pygame.draw.polygon(surface, (255, 255, 255), [(x, y), (x, y+15), (x+10, y+10)])
            pygame.draw.polygon(surface, (0, 0, 0), [(x, y), (x, y+15), (x+10, y+10)], 1)
