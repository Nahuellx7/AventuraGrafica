"""Escena principal del juego point-and-click - Orquestador."""

import math
import os
from enum import Enum, auto
import pygame

from engine.ui import Scene
from engine.dialogue_manager import DialogueManager
from engine.inventory import Inventory, Item
from engine.hotspot import Hotspot
from engine.shared_assets import sfx_path
from engine.audio import AudioManager

# Importar escenas individuales
from .isla import IslaScene
from .refugio import RefugioScene
from .herreria import HerreriaScene
from .faro_exterior import FaroExteriorScene
from .faro_interior import FaroInteriorScene
from .ventana_faro import VentanaFaroScene
from .bunker_interior import BunkerInteriorScene
from .puzzles import PuzzleManager


# Constantes de pantalla
ANCHO_VENTANA = 960
ALTO_VENTANA = 640
ALTURA_JUEGO = 490
INICIO_UI = ALTURA_JUEGO

# Colores del juego 
AZUL_OSCURO = (20, 19, 35) # Fondo de pantalla
PANEL = (37, 31, 43)       # Paneles de interfaz
DORADO = (230, 184, 104)   # Elementos destacados 
PAPEL = (241, 220, 169)    # Texto normal y documentos


class EstadoJuego(Enum):
    """Estados en los que puede estar el juego durante la ejecución."""
    INACTIVO = auto()        # Jugador esperando input
    CAMINANDO = auto()       # Personaje moviéndose
    INTERACTUANDO = auto()   # Interactuando con objeto/hotspot
    DIALOGO = auto()         # En conversación con NPC
    TECLADO = auto()         # Usando teclado numérico (puzle)
    GANADO = auto()          # Juego completado


class GameScene(Scene):
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

        # Cargar cursor personalizado con transparencia (convert_alpha)
        try:
            cursor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sprites", "pointer_b.png")
            self.cursor_image = pygame.image.load(cursor_path).convert_alpha()
        except Exception as e:
            self.cursor_image = None

        # Cargar icono de corazón para HUD de vidas
        try:
            heart_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sprites", "corazon.png")
            self.heart_image = pygame.image.load(heart_path).convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image, (24, 24))
            self.heart_image = self.heart_image.convert_alpha()
        except Exception as e:
            self.heart_image = None

        # Estado del juego
        self.scene = "isla"
        self.verb = "MIRAR"
        self.state = EstadoJuego.INACTIVO
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

        # Inicializar mundo
        self._configurar_mundo()
        self._cambiar_escena("isla", starting_position=(480, 420))
        self._say("La noche cae sobre La Isla Olvidada. El faro lleva años apagado.")

    def on_enter(self):
        """Inicialización al entrar a la escena."""
        pygame.mouse.set_visible(False)

    def on_exit(self):
        """Limpieza al salir de la escena."""
        self._actualizar_audio_pasos(False)

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
            "refugio": self.refugio_scene.get_walkable(),
            "herreria": self.herreria_scene.get_walkable(),
            "faro": self.faro_exterior_scene.get_walkable(),
            "faro_interior": self.faro_interior_scene.get_walkable(),
            "faro_ventana": self.ventana_faro_scene.get_walkable(),
            "bunker_interior": self.bunker_interior_scene.get_walkable(),
        }

        self.hotspots = {
            "isla": self.isla_scene.get_hotspots(),
            "refugio": self.refugio_scene.get_hotspots(self.llave_disponible),
            "herreria": self.herreria_scene.get_hotspots(),
            "faro": self.faro_exterior_scene.get_hotspots(),
            "faro_interior": self.faro_interior_scene.get_hotspots(),
            "faro_ventana": self.ventana_faro_scene.get_hotspots(),
            "bunker_interior": self.bunker_interior_scene.get_hotspots(),
        }

    def _cambiar_escena(self, scene, starting_position=None):
        """Cambia de escena."""
        self._actualizar_audio_pasos(False)
        self.scene = scene
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

    def _iniciar_interaccion(self, hotspot):
        """Inicia una interacción con un hotspot."""
        if self.state in (EstadoJuego.DIALOGO, EstadoJuego.GANADO):
            return
        self.pending_hotspot = hotspot
        self.pending_item = self.inventory.selected if self.verb == "USAR" else None
        self.target = self._punto_caminable_mas_cercano(hotspot.rect.center)
        self.state = EstadoJuego.CAMINANDO
        if self.player.distance_to(self.target) < 13:
            self._llegar_al_hotspot()

    def _llegar_al_hotspot(self):
        """Lógica al llegar al hotspot."""
        hotspot = self.pending_hotspot
        self.pending_hotspot = None
        self.state = EstadoJuego.INTERACTUANDO
        if hotspot is not None:
            # Solo las luces y botones del faro se activan directamente (puzle)
            if hotspot.name in PuzzleManager.HOTSPOTS_LUCES_FARO:
                self._activar_hotspot(hotspot.name)
            else:
                # Para todos los demás hotspots, usar el sistema normal de interacción con verbo
                self._interact(hotspot.name, self.verb, self.pending_item)
        if self.state == EstadoJuego.INTERACTUANDO:
            self.state = EstadoJuego.INACTIVO

    def _look(self, name):
        """Acción de mirar."""
        descriptions = {
            "Puerta del refugio": "Un refugio acogedor para náufragos. La puerta está abierta.",
            "Compuerta del bunker": "La entrada del bunker está bloqueada",
            "Barril": "Un viejo barril de madera, oxidado por el tiempo.",
            "Barra de hierro": "Una barra de hierro oxidada apoyada contra el barril.",
            "Camino al faro": "El sendero sube por el acantilado hacia el viejo faro.",
            "Cartel del puerto": "La Isla Olvidada: «Donde la niebla guarda lo que el mar olvida».",
            "Puerta de la herreria": "Una herrería ruidosa. Huele a hierro caliente.",
            "Salir a la isla": "La salida conduce a la isla.",
            "Bruno": "Bruno, antiguo farero, descansa en el refugio.",
            "Llave vieja": "Una llave antigua y oxidada, pero todavía funcional.",
            "Nota de las luces": "La nota dice: «Sol, Luna, Estrella».",
            "Mesa": "Un mapa húmedo del acantilado cubre la mesa.",
            "Volver al puerto": "El cartel indica el camino de regreso a la isla.",
            "Puerta del faro": "La puerta está abierta. Puedo entrar al faro." if self.faro_desbloqueado else "La cerradura espera una llave maestra.",
            "Bajar": "Bajar por la escalera al exterior del faro.",
            "Luz de la luna": "Un disco de vidrio azul con una luna grabada.",
            "Luz de la estrella": "Un disco de vidrio violeta con una estrella grabada.",
            "Luz del sol": "Un disco de vidrio dorado con un sol grabado.",
            "Botón de la luna": "Un control pequeño debajo de la luz de la luna.",
            "Botón de la estrella": "Un control pequeño debajo de la luz de la estrella.",
            "Botón del sol": "Un control pequeño debajo de la luz del sol.",
            "Interruptor de encendido": "Una palanca grande para activar el faro cuando las luces estén alineadas.",
            "Herrero": "El herrero trabaja con metal en su taller.",
            "Cielo nocturno": "El cielo estrellado revela un patrón: 4-7-2-9." if self.puzle_luces_resuelto else "Las estrellas brillan en la noche. Necesito resolver el puzle de luces para ver el patrón.",
            "Volver": "Volver a la sala del faro.",
            "Panel numérico": "Un panel para ingresar un código de 4 dígitos.",
            "Cámara secreta": "Una cámara oculta que guarda el tesoro de oro.",
            "Caja fuerte": "Una caja fuerte con cerradura numérica que protege el tesoro.",
            "Palanca secreta": "Una palanca oxidada que abre la cámara secreta.",
            "Tarjeta de acceso": "Una tarjeta de acceso para el mecanismo del búnker.",
        }
        if name == "Cuerda" and self.scene == "refugio" and not self.llave_disponible:
            self._say("No veo nada interesante ahí.")
        else:
            self._say(descriptions.get(name, "No encuentro nada especial."))

    def _take(self, name):
        """Acción de coger."""
        if name == "Barra de hierro" and self.scene == "isla":
            if self.inventory.has("Barra de hierro"):
                self._say("Ya tengo la barra de hierro.")
            else:
                self.inventory.add(Item("Barra de hierro", description="Una barra de hierro oxidada pero resistente."))
                self.barra_tomada = True
                self._say("Agarro la barra de hierro.")
        elif name == "Llave vieja" and self.scene == "refugio":
            if not self.llave_disponible:
                self._say("No veo nada interesante ahí.")
                return
            if self.inventory.has("Llave vieja"):
                self._say("Ya tengo la llave vieja.")
            else:
                self.inventory.add(Item("Llave vieja", description="Una llave antigua y oxidada."))
                self.llave_tomada = True
                self._say("Guardo la llave vieja en el inventario.")
        elif name == "Tarjeta de acceso" and self.scene == "faro_interior":
            if self.inventory.has("Tarjeta de acceso"):
                self._say("Ya tengo la tarjeta de acceso.")
            else:
                self.inventory.add(Item("Tarjeta de acceso", description="Una tarjeta de acceso para el mecanismo del búnker."))
                self._say("Agarro la tarjeta de acceso.")
        else:
            self._say("Eso no parece algo que pueda llevarme.")

    def _use(self, name, item):
        """Acción de usar."""
        # Puertas y salidas: si no hay item seleccionado, intentar entrar
        if name in ("Puerta del refugio", "Puerta de la herreria", "Camino al faro",
                    "Salir a la isla", "Volver al puerto", "Bajar", "Volver", "Salir del bunker",
                    "Caja fuerte", "Palanca secreta"):
            self._activar_hotspot(name)
            return
        # Puerta del faro: requiere llave maestra
        if name == "Puerta del faro":
            if item is None:
                if self.faro_desbloqueado:
                    self._activar_hotspot(name)
                else:
                    self._say("La puerta del faro está cerrada. La cerradura espera una llave.")
                return
            elif item.name == "Llave maestra":
                self.faro_desbloqueado = True
                self.inventory.remove("Llave maestra")
                self._say("La puerta cede con un chirrido y deja entrar al faro.")
                self._activar_hotspot(name)
                return
        # Compuerta del bunker: requiere tarjeta de acceso
        if name == "Compuerta del bunker":
            if item is None:
                if self.bunker_desbloqueado:
                    self._activar_hotspot(name)
                else:
                    self._say("La compuerta está cerrada. Necesito la tarjeta de acceso.")
                return
            elif item.name == "Tarjeta de acceso":
                self.bunker_desbloqueado = True
                self.inventory.remove("Tarjeta de acceso")
                self._say("La compuerta se abre lentamente. Puedo entrar al bunker.")
                return
        # Para otros usos con objetos
        if item is None:
            self._say("Primero selecciona un objeto del inventario.")
            return
        if name.startswith("Luz de") and item.name == "Llave maestra":
            self._say("No necesito una llave aquí; debo activar las luces en orden.")
        else:
            # Agregar artículo según el nombre del objeto
            item_name_lower = item.name.lower()
            if item_name_lower.startswith("llave"):
                item_with_article = "la " + item_name_lower
                location = "por aqui"
            elif item_name_lower.startswith("barra"):
                item_with_article = "la " + item_name_lower
                location = "aca"
            elif item_name_lower.startswith("tarjeta"):
                item_with_article = "la " + item_name_lower
                location = "aca"
            else:
                item_with_article = item_name_lower
                location = "aca"
            self._say("No parece que " + item_with_article + " sirva " + location)

    def _combine_items(self, first, second):
        """Combinación de items."""
        self._say("No puedes combinar objetos manualmente. Tienes que llevárselo al herrero.")

    def _abrir_dialogo_bruno(self):
        """Abre diálogo con Bruno."""
        self.state = EstadoJuego.DIALOGO
        self.current_npc = "bruno"
        self.dialogue_choices = [
            ("¿Qué pasó con esta isla?", "isla"),
            ("¿Recuerdas cómo van las luces del faro?", "orden"),
            ("¿Tienes algo útil que me puedas dar?", "ayuda"),
            ("Me voy.", "salir"),
        ]
        self._say("Bruno: «La niebla vuelve esta noche. ¿Qué quieres saber?»", duration=0)

    def _abrir_dialogo_herrero(self):
        """Abre diálogo con el herrero."""
        self.state = EstadoJuego.DIALOGO
        self.current_npc = "herrero"
        self.dialogue_choices = [
            ("¿Qué tal va el trabajo en el taller?", "trabajo"),
            ("¿Me puedes armar una llave con esto?", "armar_llave"),
            ("Me voy.", "salir"),
        ]
        self._say("Herrero: «¿Qué necesitas?»", duration=0)

    def _elegir_dialogo(self, choice):
        """Procesa la elección de diálogo."""
        if choice == "isla":
            self._say("Bruno: «La niebla llegó y todos huyeron».", duration=3)
        elif choice == "orden":
            self._say("Bruno: «Mi nota dice: Sol, Luna, Estrella, pero el mecanismo tiene sus secretos»", duration=3)
        elif choice == "ayuda":
            if not self.inventory.has("Llave vieja"):
                if not self.llave_disponible:
                    # Primera vez: ofrece la llave
                    self._say("Bruno: «¡Toma! Esta llave vieja podría ser útil. ¡Llévatela!»", duration=3)
                    self.llave_disponible = True
                    self._actualizar_hotspots_refugio()
                else:
                    # Llave disponible pero no tomada: le recuerda dónde está
                    self._say("Bruno: «La llave vieja está ahí sobre la mesa. ¡No la olvides!»", duration=3)
            else:
                # Ya tiene la llave: texto alternativo
                self._say("Bruno: «Ya tienes la llave vieja. Úsala bien, marinero».", duration=3)
        elif choice == "trabajo":
            self._say("Herrero: «Tranquilo, trabajo en la mesada. Siempre hay algo que arreglar».", duration=3)
        elif choice == "armar_llave":
            if self.inventory.has("Llave maestra"):
                # Ya tiene la llave maestra: texto alternativo
                self._say("Herrero: «Ya tienes la llave maestra. ¡Ve a abrir ese faro!»", duration=3)
            elif self.inventory.has("Barra de hierro") and self.inventory.has("Llave vieja"):
                # Tiene ambos materiales: crea la llave maestra
                self.inventory.remove("Barra de hierro")
                self.inventory.remove("Llave vieja")
                self.inventory.add(Item("Llave maestra", description="Una llave maestra forjada por el herrero."))
                self._say("Herrero: «Doblo la barra de hierro y la uno con la llave vieja. Aquí tienes tu llave maestra».", duration=3)
            else:
                # No tiene los materiales: le dice qué falta
                if not self.inventory.has("Barra de hierro") and not self.inventory.has("Llave vieja"):
                    self._say("Herrero: «Necesito la barra de hierro y la llave vieja para armar algo».", duration=3)
                elif not self.inventory.has("Barra de hierro"):
                    self._say("Herrero: «Tengo la llave vieja, pero me falta la barra de hierro».", duration=3)
                elif not self.inventory.has("Llave vieja"):
                    self._say("Herrero: «Tengo la barra de hierro, pero me falta la llave vieja».", duration=3)
        elif choice == "volver":
            if self.current_npc == "bruno":
                self._abrir_dialogo_bruno()
            elif self.current_npc == "herrero":
                self._abrir_dialogo_herrero()
        elif choice == "salir":
            self.state = EstadoJuego.INACTIVO
            self.dialogue.clear_message()
            self.current_npc = None
            return
        if choice in ("isla", "orden", "ayuda", "trabajo", "armar_llave"):
            self.dialogue_choices = [
                ("Volver a preguntar", "volver"),
                ("Terminar conversación", "salir"),
            ]

    def _activar_hotspot(self, name):
        """Activa un hotspot (cambio de escena, uso de objeto, etc.)."""
        # Puertas y salidas: cambio de escena directo
        if self.scene == "isla" and name == "Puerta del refugio":
            self.audio.play_sound("abrir_puerta")
            self._cambiar_escena("refugio", starting_position=(160, 430))
        elif self.scene == "isla" and name == "Puerta de la herreria":
            self.audio.play_sound("abrir_puerta")
            self._cambiar_escena("herreria", starting_position=(480, 430))
        elif self.scene == "isla" and name == "Camino al faro":
            self._cambiar_escena("faro", starting_position=(170, 435))
            self._say("El sendero asciende hasta la vieja torre.")
        elif self.scene == "isla" and name == "Compuerta del bunker":
            if self.bunker_desbloqueado:
                self._cambiar_escena("bunker_interior", starting_position=(480, 420))
                self._say("Desciendo por la escalera al interior del bunker.")
            else:
                self._say("La compuerta está cerrada. Necesito la tarjeta de acceso.")
        elif self.scene == "refugio" and name == "Salir a la isla":
            self.audio.play_sound("cerrar_puerta")
            self._cambiar_escena("isla", starting_position=(230, 420))
        elif self.scene == "herreria" and name == "Salir a la isla":
            self.audio.play_sound("cerrar_puerta")
            self._cambiar_escena("isla", starting_position=(830, 425))
        elif self.scene == "faro" and name == "Volver al puerto":
            self._cambiar_escena("isla", starting_position=(830, 425))
        elif self.scene == "faro" and name == "Puerta del faro":
            if not self.faro_desbloqueado:
                self._say("La puerta del faro está cerrada. La cerradura espera una llave.")
            else:
                self.audio.play_sound("abrir_puerta")
                self._cambiar_escena("faro_interior", starting_position=(480, 420))
                if not self.puzle_luces_resuelto:
                    self._say("Dentro, las tres luces esperan el orden correcto.")
        elif self.scene == "faro_interior" and name == "Bajar":
            self.audio.play_sound("cerrar_puerta")
            self._cambiar_escena("faro", starting_position=(420, 400))
        elif self.scene == "faro_interior" and name == "Cielo nocturno":
            if self.puzle_luces_resuelto:
                self._cambiar_escena("faro_ventana", starting_position=(480, 420))
                self._say("Veo el patrón de estrellas claramente.")
            else:
                self._say("Las estrellas brillan en la noche. Necesito resolver el puzle de luces para ver el patrón.")
        elif self.scene == "faro_ventana" and name == "Volver":
            self._cambiar_escena("faro_interior", starting_position=(480, 420))
        elif self.scene == "bunker_interior" and name == "Salir del bunker":
            self._cambiar_escena("isla", starting_position=(480, 420))
        # Puertas que requieren objeto específico (se usan con verbo USAR)
        elif self.scene == "faro" and name == "Puerta del faro":
            # Este caso se maneja en _interact con verbo USAR
            pass
        # Puzles y mecanismos interactivos
        elif self.scene == "faro_interior" and name.startswith("Luz de"):
            nuevo_progreso = PuzzleManager.activar_luz(name, self.progreso_luces, self._say, self._trigger_game_over)
            if nuevo_progreso is not None:
                self.progreso_luces = nuevo_progreso
                if self.progreso_luces == len(PuzzleManager.ORDEN_LUCES):
                    self.puzle_luces_resuelto = True
        elif self.scene == "faro_interior" and name.startswith("Botón de"):
            luces_mapping = {
                "Botón de la luna": "Luz de la luna",
                "Botón de la estrella": "Luz de la estrella",
                "Botón del sol": "Luz del sol",
            }
            nuevo_progreso = PuzzleManager.activar_luz(luces_mapping[name], self.progreso_luces, self._say, self._trigger_game_over)
            if nuevo_progreso is not None:
                self.progreso_luces = nuevo_progreso
                if self.progreso_luces == len(PuzzleManager.ORDEN_LUCES):
                    self.puzle_luces_resuelto = True
        elif self.scene == "faro_interior" and name == "Interruptor de encendido":
            if self.progreso_luces == len(PuzzleManager.ORDEN_LUCES):
                self._say("El interruptor activa el faro. Hay una herramienta en la esquina.")
            else:
                self._say("El interruptor no responde. Primero debo ordenar las tres luces.")
        elif self.scene == "bunker_interior" and name == "Caja fuerte":
            self.state = EstadoJuego.TECLADO
            self.entrada_teclado = ""
            self._say("Ingresa el código de 4 dígitos:", duration=0)
        elif self.scene == "bunker_interior" and name == "Palanca secreta":
            if not self.caja_fuerte_abierta:
                self._say("Necesito abrir la caja fuerte primero.")
            else:
                self.dialogue.clear_message()
                # Limpiar la referencia al game_scene para que el menú no muestre opciones de reanudar
                self.game.game_scene = None
                # Cambiar directamente a escena de victoria
                self.game.change_scene("victory")

    def _interact(self, name, verb, item):
        """Interacción genérica con un hotspot."""
        if verb == "MIRAR":
            self._look(name)
        elif verb == "COGER":
            self._take(name)
        elif verb == "USAR":
            if name in ("Puerta del refugio", "Puerta de la herreria", "Camino al faro",
                        "Salir a la isla", "Volver al puerto", "Bajar", "Volver", "Salir del bunker",
                        "Puerta del faro", "Compuerta del bunker"):
                self._use(name, item)
            else:
                self._use(name, item)
        elif verb == "HABLAR":
            if name == "Bruno" and self.scene == "refugio":
                self._abrir_dialogo_bruno()
            elif name == "Herrero" and self.scene == "herreria":
                self._abrir_dialogo_herrero()
            else:
                self._say("No hay nadie aquí con quien hablar.")

    def handle_events(self, events):
        """Maneja eventos del juego."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == EstadoJuego.DIALOGO:
                        self.state = EstadoJuego.INACTIVO
                        self.dialogue.clear_message()
                        self.current_npc = None
                    else:
                        self.game.change_scene("menu")
                elif event.key == pygame.K_F1:
                    self.depurar_puntos = not self.depurar_puntos
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.verb = ("MIRAR", "USAR", "HABLAR", "COGER")[event.key - pygame.K_1]
                elif event.key == pygame.K_r and self.state == EstadoJuego.GANADO:
                    # Reiniciar juego
                    self.__init__(self.game)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._manejar_click(event.pos)
            elif event.type == pygame.USEREVENT:
                # Timer para cambiar a victoria
                pygame.time.set_timer(pygame.USEREVENT, 0)
                self.game.change_scene("victory")

    def _manejar_click(self, position):
        """Maneja clics del mouse."""
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
        for index, verb in enumerate(("MIRAR", "USAR", "HABLAR", "COGER")):
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

    def update(self):
        """Actualiza la lógica del juego."""
        self.dialogue.update()
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

    def draw(self, surface):
        """Renderiza el juego delegando a las escenas correspondientes."""
        surface.fill(AZUL_OSCURO)

        # Delegar dibujo a la escena correspondiente
        if self.scene == "isla":
            self.isla_scene.draw(self.inventory, self.barra_tomada, self.bunker_desbloqueado)
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

        # Dibujar elementos comunes del juego
        self._dibujar_jugador(self.player)
        self._dibujar_mensaje(self.message, self.message_timer, self.state.name, self.dialogue)
        self._dibujar_interfaz(("MIRAR", "USAR", "HABLAR", "COGER"), self.verb, self.inventory)

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

    # ============ MÉTODOS DE DIBUJO COMUNES ============

    def _dibujar_jugador(self, player_pos):
        """Dibuja el personaje del jugador."""
        x, y = int(player_pos.x), int(player_pos.y)
        pygame.draw.ellipse(self.game.screen, (23, 21, 35), (x - 23, y - 7, 46, 12))
        pygame.draw.rect(self.game.screen, (53, 43, 42), (x - 14, y - 52, 12, 29))
        pygame.draw.rect(self.game.screen, (53, 43, 42), (x + 2, y - 52, 12, 29))
        pygame.draw.rect(self.game.screen, (120, 73, 48), (x - 16, y - 28, 15, 26))
        pygame.draw.rect(self.game.screen, (120, 73, 48), (x + 1, y - 28, 15, 26))
        pygame.draw.rect(self.game.screen, (47, 94, 108), (x - 21, y - 91, 42, 65))
        pygame.draw.rect(self.game.screen, (228, 215, 174), (x - 20, y - 76, 40, 8))
        pygame.draw.rect(self.game.screen, (228, 215, 174), (x - 19, y - 53, 38, 7))
        pygame.draw.rect(self.game.screen, (207, 151, 109), (x - 15, y - 119, 31, 31))
        pygame.draw.rect(self.game.screen, (66, 43, 36), (x - 18, y - 125, 36, 12))
        pygame.draw.rect(self.game.screen, (235, 191, 117), (x - 22, y - 124, 44, 6))
        pygame.draw.rect(self.game.screen, (38, 35, 39), (x - 7, y - 108, 4, 4))
        pygame.draw.rect(self.game.screen, (38, 35, 39), (x + 3, y - 108, 4, 4))
        pygame.draw.rect(self.game.screen, (125, 72, 58), (x - 10, y - 94, 18, 4))

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
