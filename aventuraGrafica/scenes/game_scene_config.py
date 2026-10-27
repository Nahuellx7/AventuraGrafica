"""Constantes y estados compartidos por la escena principal."""

from enum import Enum, auto


ANCHO_VENTANA = 960
ALTO_VENTANA = 640
ALTURA_JUEGO = 490
INICIO_UI = ALTURA_JUEGO
TAMANO_FRAME_JUGADOR = 128
TAMANO_JUGADOR = 220
DURACION_FRAME_CAMINAR = 100

AZUL_OSCURO = (20, 19, 35)
PANEL = (37, 31, 43)
DORADO = (230, 184, 104)
PAPEL = (241, 220, 169)


class EstadoJuego(Enum):
    """Estados en los que puede estar el juego durante la ejecución."""

    INACTIVO = auto()
    CAMINANDO = auto()
    INTERACTUANDO = auto()
    DIALOGO = auto()
    TECLADO = auto()
    GANADO = auto()
