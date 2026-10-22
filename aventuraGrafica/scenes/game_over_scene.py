"""Escena de Game Over - pantalla de derrota."""

import os
import pygame
from engine.ui import Scene, Button
from engine.shared_assets import shared_dir


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
            cursor_path = os.path.join(shared_dir(), "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except:
            self.cursor_image = None
        
        # Botones
        self.boton_reintentar = Button(
            230, 350, 220, 60, "Reintentar", self.reintentar,
            font_size=36, color=(80, 80, 100), hover_color=(100, 100, 120)
        )
        
        self.boton_menu = Button(
            510, 350, 220, 60, "Menú Principal", self.volver_menu,
            font_size=36, color=(80, 50, 50), hover_color=(100, 70, 70)
        )
        
        # Animación
        self.t = 0.0

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
        """Dibuja la pantalla de game over."""
        # Fondo oscuro con degradado
        for y in range(0, surface.get_height(), 4):
            shade = int(15 + (y / surface.get_height()) * 10)
            pygame.draw.rect(surface, (shade, shade + 5, shade + 10), (0, y, surface.get_width(), 4))
        
        # Dibujar estrellas (más tenues)
        import random
        random.seed(99)
        for _ in range(80):
            x = random.randint(0, surface.get_width())
            y = random.randint(0, surface.get_height() - 150)
            size = random.randint(1, 2)
            brightness = random.randint(80, 120)
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)
        
        # Luna gris (el faro sigue apagado)
        moon_x = surface.get_width() // 2
        moon_y = 120
        pygame.draw.circle(surface, (100, 100, 120), (moon_x, moon_y), 60)
        pygame.draw.circle(surface, (60, 60, 80), (moon_x + 15, moon_y - 10), 50)
        
        # Faro oscuro en el fondo
        faro_x = surface.get_width() - 150
        faro_y = surface.get_height() - 200
        # Torre del faro
        pygame.draw.rect(surface, (50, 45, 40), (faro_x - 20, faro_y, 40, 150))
        pygame.draw.rect(surface, (40, 35, 30), (faro_x - 25, faro_y - 30, 50, 30))
        # Luz del faro (apagada, muy oscura)
        pygame.draw.circle(surface, (40, 40, 50), (faro_x, faro_y - 30), 15)
        
        # Título GAME OVER
        title_surf = self.font_title.render("GAME OVER", True, (180, 60, 60))
        # Efecto de sombra
        shadow_surf = self.font_title.render("GAME OVER", True, (100, 30, 30))
        surface.blit(shadow_surf, shadow_surf.get_rect(centerx=surface.get_width() // 2 + 3, y=80 + 3))
        surface.blit(title_surf, title_surf.get_rect(centerx=surface.get_width() // 2, y=80))
        
        # Mensaje
        message_surf = self.font_message.render("El faro sigue apagado...", True, (150, 150, 170))
        surface.blit(message_surf, message_surf.get_rect(centerx=surface.get_width() // 2, y=180))
        
        message_surf2 = self.font_message.render("La Isla Olvidada permanece en la oscuridad", True, (150, 150, 170))
        surface.blit(message_surf2, message_surf2.get_rect(centerx=surface.get_width() // 2, y=220))
        
        # Panel con instrucciones
        panel_rect = pygame.Rect(180, 260, 600, 70)
        pygame.draw.rect(surface, (40, 45, 55), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 70, 70), panel_rect, 2, border_radius=8)
        
        instruction_text = "Presiona R para reintentar o M para volver al menú"
        instruction_surf = self.font_hint.render(instruction_text, True, (200, 200, 220))
        surface.blit(instruction_surf, instruction_surf.get_rect(centerx=surface.get_width() // 2, y=295))
        
        # Dibujar botones
        self.boton_reintentar.draw(surface)
        self.boton_menu.draw(surface)
        
        # Texto de hint adicional
        hint_surf = self.font_hint.render("O haz clic en los botones", True, (120, 120, 140))
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
