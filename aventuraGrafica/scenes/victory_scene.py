"""Escena de victoria - pantalla épica al completar el juego."""

import os
import pygame
from engine.ui import Scene, Button


class VictoryScene(Scene):
    """Pantalla de victoria full screen con mensaje épico."""

    def __init__(self, game):
        super().__init__(game)
        
        # Fuentes
        self.font_title = pygame.font.Font(None, 82)
        self.font_subtitle = pygame.font.Font(None, 48)
        self.font_message = pygame.font.Font(None, 32)
        self.font_hint = pygame.font.Font(None, 26)
        
        # Cargar cursor personalizado
        try:
            cursor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except:
            self.cursor_image = None
        
        # Botón para volver al menú
        self.boton_menu = Button(
            330, 450, 300, 60, "Volver al Menú", self.volver_menu,
            font_size=36, color=(220, 90, 90), hover_color=(240, 110, 110)
        )
        
        # Animación
        self.t = 0.0
        self.stars = self._generate_stars()

    def _generate_stars(self):
        """Genera estrellas para el fondo."""
        import random
        random.seed(123)
        stars = []
        for _ in range(150):
            x = random.randint(0, 960)
            y = random.randint(0, 640)
            size = random.randint(1, 3)
            brightness = random.randint(230, 255)
            twinkle_speed = random.uniform(0.5, 2.0)
            stars.append({'x': x, 'y': y, 'size': size, 'brightness': brightness, 'speed': twinkle_speed})
        return stars

    def on_enter(self):
        """Se ejecuta al entrar a la escena de victoria."""
        self.t = 0.0
        # Desactivar cursor nativo (usaremos cursor personalizado)
        pygame.mouse.set_visible(False)
        # Reproducir sonido de victoria si existe
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("cheer")
            except:
                pass

    def on_exit(self):
        """Se ejecuta al salir de la escena de victoria."""
        pass

    def volver_menu(self):
        """Vuelve al menú principal."""
        if hasattr(self.game, 'audio'):
            try:
                self.game.audio.play_sound("click")
            except:
                pass
        self.game.change_scene("menu")

    def handle_events(self, events):
        """Maneja eventos de la pantalla de victoria."""
        for event in events:
            self.boton_menu.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.volver_menu()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.volver_menu()

    def update(self):
        """Actualiza animaciones."""
        self.t += 1.0 / self.game.fps

    def draw(self, surface):
        """Dibuja la pantalla de victoria épica."""
        # Fondo con degradado épico más brillante
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

        # Título de victoria
        title_surf = self.font_title.render("¡VICTORIA!", True, (255, 215, 120))
        surface.blit(title_surf, title_surf.get_rect(centerx=surface.get_width() // 2, y=170))

        # Mensaje principal de victoria
        victory_text = "La Isla Olvidada ha sido salvada."
        victory_surf = self.font_message.render(victory_text, True, (255, 235, 180))
        surface.blit(victory_surf, victory_surf.get_rect(centerx=surface.get_width() // 2, y=290))

        # Dibujar botón
        self.boton_menu.draw(surface)

        # Texto de hint - más abajo
        hint_surf = self.font_hint.render("Presiona ESC o haz clic para volver al menú", True, (200, 200, 220))
        surface.blit(hint_surf, hint_surf.get_rect(centerx=surface.get_width() // 2, y=580))

        # Dibujar cursor personalizado al final
        mouse_pos = pygame.mouse.get_pos()
        if self.cursor_image:
            surface.blit(self.cursor_image, mouse_pos)
        else:
            # Cursor de respaldo
            x, y = mouse_pos
            pygame.draw.polygon(surface, (255, 255, 255), [(x, y), (x, y+15), (x+10, y+10)])
            pygame.draw.polygon(surface, (0, 0, 0), [(x, y), (x, y+15), (x+10, y+10)], 1)
