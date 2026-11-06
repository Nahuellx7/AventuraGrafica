"""Escena del bosque al oeste de la aldea."""

import pygame
from engine.hotspot import Hotspot


class BosqueScene:
    """Mapa boscoso con una salida de regreso a la aldea."""

    HOTSPOTS = [Hotspot((857, 300, 66, 76), "Volver a la aldea")]
    WALKABLE = [(0, 470), (95, 420), (220, 395), (365, 405),
                (500, 385), (650, 400), (790, 390), (950, 425), (960, 480)]

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 20)

    def get_hotspots(self):
        return self.HOTSPOTS

    def get_walkable(self):
        return self.WALKABLE

    def draw(self):
        self.screen.fill((17, 31, 39))
        pygame.draw.rect(self.screen, (25, 49, 48), (0, 0, 960, 320))
        pygame.draw.circle(self.screen, (196, 194, 147), (780, 78), 25)
        pygame.draw.circle(self.screen, (25, 49, 48), (791, 69), 23)

        for index in range(24):
            x = (index * 173 + 31) % 1020 - 30
            height = 145 + (index * 47) % 115
            width = 70 + (index * 29) % 60
            color = (27 + index % 8, 57 + index % 12, 49 + index % 10)
            pygame.draw.rect(self.screen, (48, 39, 34),
                             (x + width // 2 - 7, 285 - height // 3, 14, height // 2))
            pygame.draw.polygon(
                self.screen,
                color,
                [(x, 285 - height // 3), (x + width // 2, 285 - height),
                 (x + width, 285 - height // 3)],
            )
            pygame.draw.polygon(
                self.screen,
                (color[0] + 4, color[1] + 8, color[2] + 5),
                [(x + 5, 245 - height // 3), (x + width // 2, 245 - height),
                 (x + width - 5, 245 - height // 3)],
            )

        pygame.draw.polygon(self.screen, (48, 61, 48),
                            [(0, 325), (960, 315), (960, 490), (0, 490)])
        pygame.draw.polygon(self.screen, (105, 91, 65),
                            [(420, 325), (550, 325), (800, 490), (185, 490)])
        pygame.draw.polygon(self.screen, (133, 111, 76),
                            [(457, 335), (515, 335), (690, 490), (300, 490)])

        for index in range(18):
            x = (index * 71 + 17) % 960
            y = 380 + (index * 31) % 105
            pygame.draw.ellipse(self.screen, (58, 76, 48), (x, y, 35, 15))
            pygame.draw.ellipse(self.screen, (84, 99, 57), (x + 8, y + 2, 18, 8))

        pygame.draw.line(self.screen, (89, 75, 52), (910, 280), (910, 420), 8)
        pygame.draw.rect(self.screen, (142, 96, 59), (857, 300, 66, 76))
        pygame.draw.rect(self.screen, (205, 163, 105), (857, 300, 66, 76), 3)
        self._draw_text("ALDEA", (890, 323), (241, 220, 169), centered=True)
        pygame.draw.polygon(self.screen, (142, 96, 59), [(890, 376), (875, 391), (905, 391)])
        self._draw_text("BOSQUE", (24, 18), (241, 220, 169))

    def _draw_text(self, text, position, color, centered=False):
        image = self.font.render(text, True, color)
        rect = image.get_rect(center=position) if centered else image.get_rect(topleft=position)
        self.screen.blit(image, rect)
