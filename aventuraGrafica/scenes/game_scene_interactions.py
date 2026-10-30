"""GameSceneInteraction for the main game scene."""

import pygame
from engine.inventory import Item
from .game_scene_config import EstadoJuego
from .puzzles import PuzzleManager


class GameSceneInteractionMixin:
    """Handles interaction for GameScene."""

    def _iniciar_interaccion(self, hotspot):
        """Inicia una interacción con un hotspot."""
        if self.state in (
            EstadoJuego.DIALOGO,
            EstadoJuego.GANADO,
            EstadoJuego.MIRANDO_LUNA,
            EstadoJuego.VOLVIENDO_BINOCULARES,
        ):
            return
        if self.scene == "luna" and hotspot.name == "Volver":
            self._cambiar_escena(
                self.luna_return_scene,
                starting_position=self.luna_return_position,
            )
            self.binoculares_animation_started = pygame.time.get_ticks()
            self.state = EstadoJuego.VOLVIENDO_BINOCULARES
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
                self._mostrar_interaccion()
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
        """Acción de agarrar."""
        if name == "Barril" and self.scene == "isla":
            if not self.herrero_menciono_barril:
                self._say("No sé de quién será ese barril. Mejor no llevármelo.")
            elif self.barril_entregado:
                self._say("Ya le devolví el barril al herrero.")
            elif self.inventory.has("Barril"):
                self._say("Ya llevo el barril. Tengo que devolvérselo al herrero.")
            elif self.inventory.add(Item("Barril", description="El barril perdido del herrero.")):
                self.barril_tomado = True
                self._say("Recojo el barril perdido del herrero.")
            else:
                self._say("No tengo espacio en el inventario para llevar el barril.")
        elif name == "Barra de hierro" and self.scene == "isla":
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
        if name == "Luna" and self.scene in ("faro_ventana", "faro_interior"):
            if item is not None and item.name == "Binoculares":
                self.luna_return_scene = self.scene
                self.luna_return_position = self.player.copy()
                self.binoculares_animation_started = pygame.time.get_ticks()
                self.state = EstadoJuego.MIRANDO_LUNA
                self._say("Miro la luna a través de los binoculares.", duration=1.2)
            elif item is None:
                self._say("Necesito unos binoculares para observar la luna.")
            else:
                self._say("Ese objeto no me ayudará a observar la luna.")
            return

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
        self._mostrar_interaccion()
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
            ("¿Por qué la cara larga?", "cara_larga"),
            ("¿Me puedes armar una llave con esto?", "armar_llave"),
        ]
        if self.inventory.has("Barril") and not self.barril_entregado:
            self.dialogue_choices.append(("Entregarle el barril perdido", "entregar_barril"))
        self.dialogue_choices.append(("Me voy.", "salir"))
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
        elif choice == "cara_larga":
            self.herrero_menciono_barril = True
            self._say("Herrero: «Perdí de vista un barril que tenía que traer al taller. Sin él, no puedo organizar mis cosas».", duration=3)
        elif choice == "entregar_barril":
            if self.inventory.has("Barril") and not self.barril_entregado:
                self.inventory.remove("Barril")
                if self.inventory.add(Item("Binoculares", description="Unos binoculares que el herrero te regala en agradecimiento.")):
                    self.barril_entregado = True
                    self.barril_tomado = True
                    self._say("Herrero: «¡Ese es mi barril! Muchas gracias por traerlo. Toma estos binoculares, te los regalo».", duration=3)
                else:
                    self.inventory.add(Item("Barril", description="El barril perdido del herrero."))
                    self._say("No tengo espacio para aceptar la recompensa.")
            else:
                self._say("Herrero: «Todavía no tienes el barril que perdí».", duration=3)
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
        if choice in ("isla", "orden", "ayuda", "trabajo", "cara_larga", "armar_llave", "entregar_barril"):
            self.dialogue_choices = [("Volver a preguntar", "volver")]
            if self.current_npc == "herrero" and self.inventory.has("Barril") and not self.barril_entregado:
                self.dialogue_choices.append(("Entregarle el barril perdido", "entregar_barril"))
            self.dialogue_choices.append(("Terminar conversación", "salir"))

    def _activar_hotspot(self, name):
        """Activa un hotspot (cambio de escena, uso de objeto, etc.)."""
        # Puertas y salidas: cambio de escena directo
        if self.scene == "isla" and name == "Puerta del refugio":
            self.audio.play_sound("abrir_puerta")
            self._cambiar_escena("refugio", starting_position=(160, 430))
        elif self.scene == "isla" and name == "Puerta de la herreria":
            self.audio.play_sound("abrir_puerta")
            self._cambiar_escena("herreria", starting_position=(160, 430))
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
        if verb in ("AGARRAR", "USAR", "HABLAR"):
            self._mostrar_interaccion()
        if verb == "MIRAR":
            self._look(name)
        elif verb == "AGARRAR":
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
