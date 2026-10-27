# Convenciones Técnicas — Space Invaders 3D
**Parcial 2 · Animación y Game Feel 3D** · Godot 4.7 + Blender

---

## 1. Sistema de Coordenadas y Unidades

| Parámetro | Convención | Detalle técnico |
|---|---|---|
| **Unidades** | 1 unidad = 1 metro | 1 unidad de Blender equivale a 1 unidad métrica de Godot. |
| **Ejes** | +Y hacia arriba | El plano de combate es el plano horizontal XZ. |
| **Orientación** | Frente = −Z | El jugador está en `+Z ≈ 16.0` y dispara hacia `−Z`. Los enemigos bajan desde `−Z` hacia `+Z`. |
| **Pivote** | Centro de masa geométrico | El origen de cada malla se ubica en su centro para permitir rotaciones limpias (`rotation:y`) sin desfasar el eje. |
| **FPS Base** | 60 FPS (Físicas a 60 Hz) | Animaciones de Blender muestreadas a 30 FPS, interpoladas suavemente por Godot. |

---

## 2. Separación de Responsabilidades: Tweens vs AnimationPlayer

Para evitar que los Tweens y el AnimationPlayer colisionen o anulen transformaciones:
1. **AnimationPlayer (.glb)**: Anima exclusivamente partes internas, hélices, tentáculos, pulsos o huesos del modelo 3D. **Nunca modifica la posición, rotación o escala de la raíz de la escena.**
2. **Tweens de Godot**: Modifican exclusivamente el nodo intermedio `Visual` (`Node3D`):
   - Escala (Spawn, eliminación, pop).
   - Rotación global (Giro de 360° en Y durante la muerte, banking tilt en Z).
   - Posición relativa (Descenso desde Y = 4.0 o Y = 6.0).
3. **Nodo Raíz de Física (`Area3D`)**: Mantiene las coordenadas absolutas del actor en el campo de batalla y porta la forma de colisión (`CollisionShape3D`).

---

## 3. Jerarquía Estándar de Nodos (Patrón Visual)

```text
Actor (Area3D)              ← Script lógico, señales, velocidad y posición en el mundo
├─ CollisionShape3D         ← Forma primitiva matemática (BoxShape3D / SphereShape3D)
└─ Visual (Node3D)          ← PIVOTE CONTROLADO POR TWEENS (scale, position.y, rotation.y, rotation.z)
   └─ Model (.glb instanciado) ← AnimationPlayer propio de Blender (Idle-loop, clips)
```

---

## 4. Capas de Colisión (Collision Layers)

| Capa | Nombre | Función |
|---|---|---|
| **1** | `Jugador` | Detecta impacto de balas enemigas y contacto con la flota |
| **2** | `Enemigos` | Detecta impactos de proyectiles del jugador |
| **3** | `Proyectil_Jugador` | Colisiona con enemigos, ovni y bloques de bunker |
| **4** | `Proyectil_Enemigo` | Colisiona con el jugador y bloques de bunker |
| **5** | `Escudos` | Absorbe proyectiles de ambos bandos |
| **6** | `Ovni` | Detecta proyectiles del jugador en la parte superior |

---

## 5. Paleta Neón Arcade y Emisión

| Elemento | Acento Neón | Código HEX | Rol Visual |
|---|---|---|---|
| **Jugador Mk I** | Cian Eléctrico | `#00E5FF` | Nave inicial estándar |
| **Jugador Mk II** | Azul Neón | `#3D7BFF` | Nave nivel 3-4 |
| **Jugador Mk III** | Menta Esmeralda | `#00FFB3` | Nave nivel 5-6 |
| **Jugador Mk IV** | Ámbar Solar | `#FFB300` | Nave pesada nivel 7-8 |
| **Jugador Mk V** | Oro / Blanco Halo | `#FFF1B0` | Nave definitiva nivel 9-10 |
| **Enemigo A (Calamar)** | Magenta / Violeta | `#FF1AD9` | Fila superior (30 pts) |
| **Enemigo B (Cangrejo)** | Cian / Turquesa | `#00F2FF` | Filas intermedias (20 pts) |
| **Enemigo C (Behemoth)** | Oro / Amarillo | `#FFD700` | Filas inferiores (10 pts) |
| **Ovni Bonus** | Amarillo Neón Intenso | `#FFE600` | Objetivo especial (100-300 pts) |
| **Escudos** | Verde Esmeralda | `#00FF99` | Barreras defensivas (2 HP) |

---

## 6. Nombres de Identificadores y Funciones Clave

- `spawn_por_filas()`: Despliegue en bloque por fila de marcianos.
- `spawn_escudos()`: Emergencia escalonada de bloques defensivos desde el suelo.
- `entrar_en_escena()`: Caída elástica de la nave del jugador que desbloquea el juego en su callback final.
- `eliminar_enemigo()`: Secuencia Hit-Stop + Contracción y giro 3D + `queue_free()`.
- `hit_stop(duracion)`: Pausa del árbol de escena con temporizador inmune.
- `desbloquear_input()`: Llamada de apertura de flujo tras finalizar todas las intros.
