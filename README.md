# La Isla Olvidada

Aventura Gráfica - Proyecto desarrollado para la materia Diseño y Desarrollo de Videojuegos 2D.

## Integrantes

- **Nahuel Leguisamon**
- **Mateo Sparano**

## Descripción General

"La Isla Olvidada" es una aventura gráfica point-and-click ambientada en una isla misteriosa donde el jugador debe resolver puzles y explorar locaciones para reactivar un faro abandonado. El juego implementa mecánicas clásicas del género con un sistema de verbos, inventario, diálogos con NPCs y acertijos lógicos.

## Mecánicas Principales

- **Sistema Point-and-Click**: El jugador selecciona acciones mediante teclas o interfaz gráfica.
- **Inventario de Capacidad Limitada**: Sistema de inventario con 5 slots, selección de objetos y combinación de items mediante NPCs.
- **9 Locaciones Interconectadas**: Aldea principal, bosque, refugio, herrería, faro exterior, faro interior, ventana del faro, luna, e interior del búnker.
- **Diálogos con NPCs**: Sistema de diálogo ramificado con Bruno (antiguo farero) y el herrero (forja de llaves).
- **Puzles Lógicos**:
  - **Puzle del Faro**: Activar tres luces en secuencia correcta para revelar el código del búnker.
  - **Puzle del Búnker**: Ingresar código de 4 dígitos en el panel numérico para acceder al tesoro.
- **Transiciones de Escena**: Cambio fluido entre locaciones con conservación del estado del juego.

## Arquitectura

El proyecto sigue una arquitectura modular con separación clara de responsabilidades. La estructura principal se encuentra en el directorio `aventuraGrafica/scenes/`, organizada de manera plana (sin subcarpetas) para facilitar el mantenimiento y la comprensión del código.

### Estructura de Escenas

```
aventuraGrafica/scenes/
├── game_scene.py          # Orquestador principal que coordina todas las escenas
├── game_scene_config.py   # Estados y constantes compartidos por la escena principal
├── game_scene_input.py    # Eventos y controles
├── game_scene_interactions.py # Interacciones, diálogos y transiciones
├── game_scene_rendering.py # Renderizado común de la escena principal
├── puzzles.py             # Lógica de acertijos (PuzzleManager)
├── menu_scene.py          # Menú principal con opciones de juego
├── victory_scene.py       # Pantalla de victoria
├── game_over_scene.py     # Pantalla de game over
├── aldea.py               # Escena de la aldea principal
├── bosque.py              # Escena del bosque
├── refugio.py             # Escena del refugio (NPC Bruno)
├── herreria.py            # Escena de la herrería (NPC Herrero)
├── faro_exterior.py       # Escena exterior del faro
├── faro_interior.py       # Escena interior del faro (puzle de luces)
├── ventana_faro.py        # Escena de la ventana del faro (patrón de estrellas)
├── luna.py                # Escena de la luna
└── bunker_interior.py     # Escena interior del búnker (puzle de código)
```

### Patrones de Diseño

- **Composición**: `GameScene` compone múltiples escenas individuales (`AldeaScene`, `RefugioScene`, etc.).
- **Delegación**: `GameScene` delega el renderizado y la obtención de datos (hotspots, polígonos caminables) a las escenas específicas.
- **Separación de responsabilidades**: la entrada, las interacciones y el renderizado común de `GameScene` se organizan en módulos separados.
- **Single Responsibility Principle**: Cada clase tiene una responsabilidad única (renderizado de una locación, gestión de puzles, orquestación del juego).
- **Constantes Estáticas**: Hotspots y polígonos caminables definidos como atributos de clase para reutilización.

### Componentes Principales

#### GameScene (Orquestador)
Clase principal que coordina todas las escenas del juego. Responsabilidades:
- Inicialización de componentes del juego (inventario, diálogo, cursor).
- Gestión del estado del juego (escena actual, posición del jugador, verbos).
- Coordinación de transiciones entre escenas.
- Delegación de entrada, interacciones y renderizado a sus módulos especializados.

## Controles del Juego

- **Mouse**: Mover cursor, seleccionar hotspots, interactuar con la interfaz.
- **Tecla 1**: Verbo MIRAR
- **Tecla 2**: Verbo USAR
- **Tecla 3**: Verbo HABLAR
- **Tecla 4**: Verbo AGARRAR
- **Tecla ESC**: Abrir menú / Salir de diálogo
- **Tecla F1**: Activar/desactivar modo depuración (visualizar hotspots)

## Guía de Instalación y Ejecución

### Requisitos Previos

- Python 3.8 o superior
- Sistema operativo: Windows, Linux o macOS
- Pip (gestor de paquetes de Python)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Nahuellx7/AventuraGrafica.git
cd AventuraGrafica
```

### Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install pygame
```

### Paso 4: Ejecutar el Juego

Desde la raíz del proyecto:

```bash
python -m aventuraGrafica.main
```

---
