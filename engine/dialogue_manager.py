"""
engine/dialogue_manager.py

Muestra mensajes/diálogos en pantalla, con duración opcional.
"""

import pygame


class DialogueManager:
    def __init__(self, screen, font_size=50, color=(255, 255, 255)):
        self.screen = screen
        self.font = pygame.font.Font(None, font_size)
        self.color = color

        self.active_message = None
        self.message_surfaces = []
        self.message_rect = None
        self.message_timer = 0
        self.message_duration = 0  # 0 => mensaje permanente

    def _wrap_text(self, text, max_width):
        """Divide el texto en líneas que no excedan max_width. Respeta saltos de línea manuales."""
        # Primero dividir por saltos de línea manuales
        manual_lines = text.split('\n')
        final_lines = []
        
        for manual_line in manual_lines:
            words = manual_line.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = (current_line + " " + word).strip() if current_line else word
                if self.font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            final_lines.extend(lines)
        
        return final_lines

    def show_message(self, text, duration_seconds=0, position="center", max_width=700):
        """Muestra un mensaje con word wrapping. Si la duración es 0, es permanente."""
        self.active_message = text

        # Aplicar word wrapping
        lines = self._wrap_text(text, max_width)
        self.message_surfaces = [self.font.render(line, True, self.color) for line in lines]

        screen_rect = self.screen.get_rect()
        total_height = len(self.message_surfaces) * (self.font.get_height() + 5)

        if position == "center":
            base_y = screen_rect.centery - total_height // 2
            self.message_rect = pygame.Rect(
                screen_rect.centerx - max_width // 2,
                base_y,
                max_width,
                total_height
            )
        elif position == "top":
            base_y = 20
            self.message_rect = pygame.Rect(
                screen_rect.centerx - max_width // 2,
                base_y,
                max_width,
                total_height
            )
        else:
            base_y = screen_rect.centery - total_height // 2
            self.message_rect = pygame.Rect(
                screen_rect.centerx - max_width // 2,
                base_y,
                max_width,
                total_height
            )

        self.message_duration = duration_seconds * 1000
        self.message_timer = pygame.time.get_ticks()

    def update(self):
        if self.message_duration > 0:
            if pygame.time.get_ticks() - self.message_timer > self.message_duration:
                self.clear_message()

    def draw(self):
        if self.message_surfaces and self.message_rect:
            y = self.message_rect.y
            for surface in self.message_surfaces:
                x = self.message_rect.centerx - surface.get_width() // 2
                self.screen.blit(surface, (x, y))
                y += self.font.get_height() + 5

    def clear_message(self):
        self.active_message = None
        self.message_surfaces = []
        self.message_duration = 0
