"""Escena principal del juego point-and-click - Orquestador."""

import os
import pygame

from engine.ui import Scene
from engine.dialogue_manager import DialogueManager
from engine.inventory import Inventory
from engine.shared_assets import MUSIC_VOLUME, music_path, sfx_path
from engine.audio import AudioManager

# Importar escenas individuales
from .isla import IslaScene
from .refugio import RefugioScene
from .herreria import HerreriaScene
from .faro_exterior import FaroExteriorScene
from .faro_interior import FaroInteriorScene
from .ventana_faro import VentanaFaroScene
from .bunker_interior import BunkerInteriorScene
from .bosque import BosqueScene
from .luna import LunaScene
from .game_scene_config import (
    DURACION_FRAME_BINOCULARES,
    EstadoJuego,
    TAMANO_FRAME_JUGADOR,
    TAMANO_JUGADOR,
)
from .game_scene_input import GameSceneInputMixin
from .game_scene_interactions import GameSceneInteractionMixin
from .game_scene_rendering import GameSceneRenderingMixin

class GameScene(GameSceneInputMixin, GameSceneInteractionMixin, GameSceneRenderingMixin, Scene):
    """Escena principal de la aventura que orquesta todas las escenas."""

    def __init__(self, game):
        super().__init__(game)

        # Inicializar componentes del juego
        pygame.mouse.set_visible(False)
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 34)
        self.dialogue = DialogueManager(self.game.screen, font_size=24, color=(255, 255, 255))
        self.inventory = Inventory(capacity=5)
        self.audio = AudioManager(num_channels=16)
        self.music_track = None

        # Cargar cursor personalizado con transparencia (convert_alpha)
        try:
            cursor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except Exception:
            self.cursor_image = None

        # Cargar icono de corazón para HUD de vidas
        try:
            heart_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sprites", "corazon.png")
            self.heart_image = pygame.image.load(heart_path).convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image, (24, 24))
            self.heart_image = self.heart_image.convert_alpha()
        except Exception:
            self.heart_image = None

        self.player_frames = {
            "idle": self._cargar_frames_jugador("Idle.png"),
            "walk": self._cargar_frames_jugador("Walk.png"),
            "walk_left": self._cargar_frames_jugador("Walk-left.png"),
            "interact": self._cargar_frames_jugador("interact.png"),
            "binoculares": self._cargar_frames_jugador("binoculares.png"),
        }

        # Estado del juego
        self.scene = "isla"
        self.verb = "MIRAR"
        self.state = EstadoJuego.INACTIVO
        self.interact_until = 0
        self.player = pygame.Vector2(480, 420)
        self.target = self.player.copy()
        self.canal_pasos = None
        # Cargar sonidos usando AudioManager
        self.audio.load_sound("pasos", sfx_path("pasos", "mp3"))
        self.audio.load_sound("abrir_puerta", sfx_path("abrir_puerta", "mp3"))
        self.audio.load_sound("cerrar_puerta", sfx_path("cerrar_puerta", "mp3"))
        if self.audio.enabled and "abrir_puerta" in self.audio.sounds:
            self.audio.sounds["abrir_puerta"].set_volume(0.15)
        if self.audio.enabled and "cerrar_puerta" in self.audio.sounds:
            self.audio.sounds["cerrar_puerta"].set_volume(0.15)
        self.pending_hotspot = None
        self.pending_item = None
        self.binoculares_animation_started = 0
        self.luna_return_scene = "faro_ventana"
        self.luna_return_position = self.player.copy()
        self.dialogue_choices = []
        self.current_npc = None
        self.message = "La noche cae sobre La Isla Olvidada. El faro lleva años apagado."
        self.message_timer = 0
        self.depurar_puntos = False
        self.faro_desbloqueado = False
        self.bunker_desbloqueado = False
        self.caja_fuerte_abierta = False
        self.entrada_teclado = ""
        self.progreso_luces = 0
        self.puzle_luces_resuelto = False
        self.barra_tomada = False
        self.barril_tomado = False
        self.herrero_menciono_barril = False
        self.barril_entregado = False
        self.llave_tomada = False
        self.llave_disponible = False

        # Inicializar escenas individuales
        self.isla_scene = IslaScene(self.game.screen)
        self.refugio_scene = RefugioScene(self.game.screen)
        self.herreria_scene = HerreriaScene(self.game.screen)
        self.faro_exterior_scene = FaroExteriorScene(self.game.screen)
        self.faro_interior_scene = FaroInteriorScene(self.game.screen)
        self.ventana_faro_scene = VentanaFaroScene(self.game.screen)
        self.bunker_interior_scene = BunkerInteriorScene(self.game.screen)
        self.bosque_scene = BosqueScene(self.game.screen)
        self.luna_scene = LunaScene(self.game.screen)

        # Inicializar mundo
        self._configurar_mundo()
        self._cambiar_escena("isla", starting_position=(480, 420))
        self._say("La noche cae sobre La Isla Olvidada. El faro lleva años apagado.")

    def on_enter(self):
        """Inicialización al entrar a la escena."""
        pygame.mouse.set_visible(False)
        self._actualizar_musica_escena()

    def on_exit(self):
        """Limpieza al salir de la escena."""
        self._actualizar_audio_pasos(False)

    def _cargar_frames_jugador(self, filename):
        """Carga los frames horizontales de una spritesheet del jugador."""
        asset_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets",
            "sprites",
        )
        path = os.path.join(asset_dir, filename)

        try:
            sheet = pygame.image.load(path).convert_alpha()
            if sheet.get_height() != TAMANO_FRAME_JUGADOR:
                raise ValueError(f"alto inesperado en {filename}: {sheet.get_height()}")
            if sheet.get_width() % TAMANO_FRAME_JUGADOR:
                raise ValueError(f"ancho no divisible por el frame en {filename}")

            frames = []
            for x in range(0, sheet.get_width(), TAMANO_FRAME_JUGADOR):
                frame = sheet.subsurface(
                    (x, 0, TAMANO_FRAME_JUGADOR, TAMANO_FRAME_JUGADOR)
                ).copy()
                frames.append(
                    pygame.transform.scale(frame, (TAMANO_JUGADOR, TAMANO_JUGADOR))
                )
            return frames
        except (pygame.error, OSError, ValueError) as error:
            print(f"No se pudieron cargar los frames de {filename}: {error}")
            return []

    def _mostrar_interaccion(self):
        self.interact_until = pygame.time.get_ticks() + 650

    def _actualizar_audio_pasos(self, caminando):
        """Reproduce pasos solo mientras el jugador se está desplazando."""
        if not self.audio.enabled:
            return

        if caminando and self.canal_pasos is None:
            self.canal_pasos = self.audio.play_sound("pasos", loops=-1)
        elif not caminando and self.canal_pasos is not None:
            self.audio.stop_sound("pasos")
            self.canal_pasos = None

    def _configurar_mundo(self):
        """Configura las zonas caminables y hotspots delegando a las escenas."""
        self.walkable = {
            "isla": self.isla_scene.get_walkable(),
            "bosque": self.bosque_scene.get_walkable(),
            "refugio": self.refugio_scene.get_walkable(),
            "herreria": self.herreria_scene.get_walkable(),
            "faro": self.faro_exterior_scene.get_walkable(),
            "faro_interior": self.faro_interior_scene.get_walkable(),
            "faro_ventana": self.ventana_faro_scene.get_walkable(),
            "bunker_interior": self.bunker_interior_scene.get_walkable(),
            "luna": self.luna_scene.get_walkable(),
        }

        self.hotspots = {
            "isla": self.isla_scene.get_hotspots(),
            "bosque": self.bosque_scene.get_hotspots(),
            "refugio": self.refugio_scene.get_hotspots(self.llave_disponible),
            "herreria": self.herreria_scene.get_hotspots(),
            "faro": self.faro_exterior_scene.get_hotspots(),
            "faro_interior": self.faro_interior_scene.get_hotspots(),
            "faro_ventana": self.ventana_faro_scene.get_hotspots(),
            "bunker_interior": self.bunker_interior_scene.get_hotspots(),
            "luna": self.luna_scene.get_hotspots(),
        }

    def _cambiar_escena(self, scene, starting_position=None):
        """Cambia de escena."""
        self._actualizar_audio_pasos(False)
        if scene != self.scene:
            self._fade_out()
        self.scene = scene
        self._actualizar_musica_escena()
        self.state = EstadoJuego.INACTIVO
        self.pending_hotspot = None
        self.current_npc = None
        self.target = self.player.copy()
        if starting_position is not None:
            self.player.update(starting_position)
            self.target.update(starting_position)
        if scene == "refugio":
            self.llave_disponible = False
            self._actualizar_hotspots_refugio()

    def _fade_out(self):
        """Oscurece la escena actual antes de cambiar de mapa."""
        self.game.fade_out(self.draw)

    def _actualizar_musica_escena(self):
        """Mantiene la misma pista al cambiar entre escenas de una zona."""
        if not self.audio.enabled:
            return
        track_by_scene = {
            "isla": "aldea",
            "refugio": "aldea",
            "herreria": "aldea",
            "bosque": "bosque",
            "faro": "playa",
            "faro_interior": "playa",
            "faro_ventana": "playa",
            "luna": "playa",
        }
        track = track_by_scene.get(self.scene)
        if track == self.music_track and (track is None or pygame.mixer.music.get_busy()):
            return
        if track is None:
            self.audio.stop_music()
        else:
            self.audio.load_music(music_path(track, "mp3"))
            self.audio.play_music(loops=-1, volume=MUSIC_VOLUME)
        self.music_track = track

    def _actualizar_hotspots_refugio(self):
        """Actualiza los hotspots del refugio según el estado de la llave."""
        self.hotspots["refugio"] = self.refugio_scene.get_hotspots(self.llave_disponible)

    def _say(self, text, duration=3.5):
        """Muestra un mensaje temporal."""
        self.message = text
        self.message_timer = pygame.time.get_ticks() + int(duration * 1000)
        self.dialogue.show_message(text, duration_seconds=duration, position="top")

    def _trigger_game_over(self):
        """Dispara la escena de Game Over (sistema de una sola vida)."""
        self.dialogue.clear_message()
        # Limpiar la referencia al game_scene para que el menú no muestre opciones de reanudar
        self.game.game_scene = None
        # Cambiar a la escena de game over
        self.game.change_scene("game_over")

    def _punto_en_poligono(self, point, polygon):
        """Verifica si un punto está dentro de un polígono."""
        x, y = point
        inside = False
        previous = polygon[-1]
        for current in polygon:
            x1, y1 = previous
            x2, y2 = current
            if (y1 > y) != (y2 > y):
                crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if x < crossing_x:
                    inside = not inside
            previous = current
        return inside

    def _punto_caminable_mas_cercano(self, point):
        """Encuentra el punto caminable más cercano."""
        polygon = self.walkable[self.scene]
        if self._punto_en_poligono(point, polygon):
            return pygame.Vector2(point)
        candidate = None
        best_distance = float("inf")
        for index, start in enumerate(polygon):
            end = polygon[(index + 1) % len(polygon)]
            segment = pygame.Vector2(end) - pygame.Vector2(start)
            length_squared = segment.length_squared()
            if length_squared == 0:
                closest = pygame.Vector2(start)
            else:
                fraction = max(0, min(1, (pygame.Vector2(point) - pygame.Vector2(start)).dot(segment)
                                         / length_squared))
                closest = pygame.Vector2(start) + segment * fraction
            distance = closest.distance_squared_to(point)
            if distance < best_distance:
                candidate = closest
                best_distance = distance
        return candidate

    def update(self):
        """Actualiza la lógica del juego."""
        self.dialogue.update()
        if self.state == EstadoJuego.MIRANDO_LUNA:
            animation_duration = (
                len(self.player_frames["binoculares"]) * DURACION_FRAME_BINOCULARES
            )
            if pygame.time.get_ticks() - self.binoculares_animation_started >= animation_duration:
                self.dialogue.clear_message()
                self.message = ""
                self.message_timer = 0
                self._cambiar_escena("luna", starting_position=(480, 420))
            return
        if self.state == EstadoJuego.VOLVIENDO_BINOCULARES:
            animation_duration = (
                len(self.player_frames["binoculares"]) * DURACION_FRAME_BINOCULARES
            )
            if pygame.time.get_ticks() - self.binoculares_animation_started >= animation_duration:
                self.state = EstadoJuego.INACTIVO
            return

        if self.state == EstadoJuego.CAMINANDO:
            offset = self.target - self.player
            distance = offset.length()
            if distance <= 4:
                self._actualizar_audio_pasos(False)
                self.player.update(self.target)
                if self.pending_hotspot is not None:
                    self._llegar_al_hotspot()
                else:
                    self.state = EstadoJuego.INACTIVO
            elif distance > 0:
                self._actualizar_audio_pasos(True)
                self.player += offset.normalize() * min(3.4, distance)
        else:
            self._actualizar_audio_pasos(False)

    # ============ MÉTODOS DE DIBUJO COMUNES ============
