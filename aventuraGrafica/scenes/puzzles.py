"""Lógica de acertijos del juego: puzle del faro y código del búnker."""


class PuzzleManager:
    """Gestiona la lógica de los acertijos del juego."""

    # Configuración del puzle del faro
    ORDEN_LUCES = ("sol", "luna", "estrella")
    DIRECT_EXIT_HOTSPOTS = {
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
    def activar_lente(name, progreso_luces, say_callback):
        """
        Activa una lente del puzle del faro.
        
        Args:
            name: Nombre de la lente activada
            progreso_luces: Progreso actual del puzle
            say_callback: Función para mostrar mensajes
            
        Returns:
            Nuevo progreso del puzle
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
            progreso_luces = 0
            say_callback("El orden es incorrecto. Debes empezar de nuevo.")

        return progreso_luces

    @staticmethod
    def verificar_codigo_bunker(codigo_ingresado):
        """
        Verifica si el código ingresado es correcto.
        
        Args:
            codigo_ingresado: Código de 4 dígitos ingresado
            
        Returns:
            True si el código es correcto, False en caso contrario
        """
        return codigo_ingresado == PuzzleManager.CODIGO_BUNKER
