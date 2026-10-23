"""Lógica de acertijos del juego: puzle del faro y código del búnker."""


class PuzzleManager:
    """Gestiona la lógica de los acertijos del juego."""

    # Configuración del puzle del faro
    ORDEN_LUCES = ("sol", "luna", "estrella")
    HOTSPOTS_LUCES_FARO = {
        "Luz de la luna",
        "Luz de la estrella",
        "Luz del sol",
        "Botón de la luna",
        "Botón de la estrella",
        "Botón del sol"
    }

    # Código correcto del búnker
    CODIGO_BUNKER = "4729"

    @staticmethod
    def activar_luz(name, progreso_luces, say_callback, game_over_callback=None):
        """
        Activa una luz del puzle del faro.

        Args:
            name: Nombre de la luz activada
            progreso_luces: Progreso actual del puzle
            say_callback: Función para mostrar mensajes
            game_over_callback: Función opcional para disparar Game Over (sistema de una sola vida)

        Returns:
            Nuevo progreso del puzle (None si se disparó Game Over)
        """
        if progreso_luces >= len(PuzzleManager.ORDEN_LUCES):
            return progreso_luces

        clicked = {
            "Luz de la luna": "luna",
            "Luz de la estrella": "estrella",
            "Luz del sol": "sol",
        }[name]

        expected = PuzzleManager.ORDEN_LUCES[progreso_luces]

        if clicked == expected:
            progreso_luces += 1
            if progreso_luces == len(PuzzleManager.ORDEN_LUCES):
                say_callback("Las luces se alinean correctamente. ¡El faro está listo! Ahora puedo examinar el cielo con detalle.")
            else:
                remaining = len(PuzzleManager.ORDEN_LUCES) - progreso_luces
                say_callback(f"Correcto. Faltan {remaining} luces por alinear.")
        else:
            # Sistema de una sola vida: fallo en el puzzle dispara Game Over inmediatamente
            if game_over_callback:
                game_over_callback()
                return None  # Indica que se disparó Game Over
            else:
                progreso_luces = 0
                say_callback("El orden es incorrecto. Debes empezar de nuevo.")

        return progreso_luces

    @staticmethod
    def verificar_codigo_bunker(codigo_ingresado, game_over_callback=None):
        """
        Verifica si el código ingresado es correcto.

        Args:
            codigo_ingresado: Código de 4 dígitos ingresado
            game_over_callback: Función opcional para disparar Game Over (sistema de una sola vida)

        Returns:
            True si el código es correcto, False en caso contrario
        """
        es_correcto = codigo_ingresado == PuzzleManager.CODIGO_BUNKER
        # Sistema de una sola vida: código incorrecto dispara Game Over inmediatamente
        if not es_correcto and game_over_callback:
            game_over_callback()
        return es_correcto
