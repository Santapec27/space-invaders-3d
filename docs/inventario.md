# Inventario Técnico del Proyecto — Space Invaders 3D
**Parcial 2 · Animación y Game Feel 3D**

---

## 1. Escenas del Proyecto (`res://scenes/`)

| Escena (`.tscn`) | Nodo Raíz | Script Asociado | Propósito |
|---|---|---|---|
| `main.tscn` | `Node3D` | `scripts/main.gd` | Escena principal que orquesta el juego, cámara, iluminación y flujo de niveles. |
| `hud.tscn` | `CanvasLayer` | `scripts/hud.gd` | Interfaz gráfica Arcade Neón: Menú principal, TopBar, Game Over elástico, avisos de nivel. |
| `player.tscn` | `Area3D` | `scripts/player.gd` | Nave del jugador con soporte multi-modelo intercambiable cada 2 niveles. |
| `invader.tscn` | `Area3D` | `scripts/invader.gd` | Enemigo individual con soporte para tipos A, B y C, animaciones y salida 3D. |
| `invader_fleet.tscn` | `Node3D` | `scripts/invader_fleet.gd` | Enjambre enemigo de 5 filas × 11 columnas con animación secuencial por filas. |
| `bunker.tscn` | `Node3D` | `scripts/bunker.gd` | Estructura defensiva compuesta por bloques destructibles con animación emergente. |
| `ufo.tscn` | `Area3D` | `scripts/ufo.gd` | Nave nodriza bonus con vuelo transversal y recompensa aleatoria de puntos. |
| `laser.tscn` | `Area3D` | `scripts/laser.gd` | Proyectil con raycast de detección de impacto para jugador y enemigos. |

---

## 2. Scripts Autoload (Singletons Globales)

| Nombre | Ruta | Modo de Proceso | Responsabilidad |
|---|---|---|---|
| `GameManager` | `res://autoload/game_manager.gd` | `Always` | Máquina de estados (`MENU`, `INTRO`, `JUGANDO`, `GAME_OVER`, `VICTORIA`), vidas, niveles, bloqueo de input y persistencia de High Score dinámico. |
| `GameFeel` | `res://autoload/game_feel.gd` | `Always` | Hit-Stop con contador de concurrencia y señal global de sacudida de cámara. |
| `AudioManager` | `res://scripts/audio_manager.gd` | `Always` | Sintetizador de audio y reproducción de efectos de sonido retro de 16-bit. |

---

## 3. Configuración de Cámara e Iluminación

- **Cámara 3D**:
  - Posición base: `(0, 24, 22)`
  - Rotación: Pitch `-48°`
  - FOV: `65.0°`
  - Proyección: Perspectiva
  - Sistema de Sacudida: Desplazamiento dinámico en los ejes X, Y, Z amortiguado por función `lerpf`.
- **Iluminación & Entorno**:
  - `DirectionalLight3D`: Luz clave cenital suave `Color(0.85, 0.88, 1.0)`, energía `1.1`.
  - `CenterGlowLight`: `OmniLight3D` violeta ambiental en `(0, 5, 0)`.
  - `PlanetIllumination`: `OmniLight3D` dedicada para iluminar el planeta de fondo en `(0, 8, -18)`.
  - `WorldEnvironment`: Modo Clear Color oscuro `Color(0.012, 0.01, 0.03)`, Glow activo con intensidad `0.55`, Bloom `0.1`, Tonemap ACES.

---

## 4. Parámetros del Enjambre y Campo de Juego

- **Dimensiones de la Formación**: 5 filas × 11 columnas = 55 invasores en formación completa.
- **Espaciado**: X = 2.4 m, Z = 2.0 m.
- **Límites Horizontales**: `X = ±17.0 m`.
- **Límite Inferior Crítico**: `Z = 14.5 m` (desata Game Over inmediato si los marcianos alcanzan la línea del jugador).
- **Cadencia de Paso**: De `0.75 s` al inicio hasta `0.06 s` al quedar el último enemigo.
