# Bitácora de Ingeniería y Decisiones Técnicas — Space Invaders 3D
**Parcial 2 · Animación y Game Feel 3D**

---

## Entrada 1 — Integración de Modelos 3D High Poly
- **Decisión**: Se importaron 22 modelos `.glb` desde Blender organizados por categorías (`jugador`, `enemigos`, `ovni`, `escudo`, `proyectiles`, `entorno`).
- **Problema encontrado**: Las mallas high poly no deben usarse directamente para detección de física debido al costo computacional prohibitivo y riesgo de inestabilidad en colisiones continuas.
- **Solución implementada**: Patrón de jerarquía `Area3D` ➔ `CollisionShape3D` (primitiva matemática simple BoxShape/SphereShape) + `Visual` (nodo Node3D donde residen las mallas y sobre el cual actúan los Tweens).

---

## Entrada 2 — Secuencia de Entrada y Bloqueo de Input (Rúbrica 20%)
- **Decisión**: La secuencia de entrada debe seguir rigurosamente el orden: **Marcianos ➔ Escudos ➔ Jugador**.
- **Problema encontrado**: Si el jugador presiona la tecla de disparo o movimiento durante la animación de entrada, se acumulaban pulsaciones en buffers de entrada que se disparaban abruptamente al comenzar el juego.
- **Solución implementada**:
  1. Bandera `GameManager.input_bloqueado = true` y estado `INTRO`.
  2. En `player.gd`, la función `_process` aborta de inmediato con `if GameManager.input_bloqueado: return`.
  3. No se utiliza cola de eventos; el input se consulta de manera continua frame por frame (`Input.is_action_pressed`).
  4. La liberación del juego se realiza exclusivamente en el callback final de la entrada del jugador (`tw.tween_callback(GameManager.desbloquear_input)`).

---

## Entrada 3 — Hit-Stop y Gestión de Eliminación (Rúbrica 25%)
- **Decisión**: Se implementó el efecto Hit-Stop para otorgar peso cinético a las bajas enemigas y al daño del jugador.
- **Problema encontrado**: Si dos o más enemigos son destruidos casi simultáneamente (por ejemplo, con disparos rápidos o rebotes), temporizadores independientes de Hit-Stop podrían despausar el juego prematuramente antes de que el segundo hit-stop termine.
- **Solución implementada**: Se creó un contador de concurrencia `_congelaciones` en `autoload/game_feel.gd`. El árbol solo reanuda su ejecución (`get_tree().paused = false`) cuando el contador llega exactamente a cero.
- **Eliminación 3D**:
  1. Desactivación inmediata de la forma de colisión (`set_deferred("disabled", true)`).
  2. Hit-Stop de 0.06s + Sacudida de cámara.
  3. Comprobación de seguridad `is_inside_tree()`.
  4. Tween en paralelo: escala a `0.001` con `TRANS_BACK` + `EASE_IN` (anticipación de expansión previa a la implosión) y rotación `TAU` (360° relativos) en 0.4s.
  5. `queue_free()` ejecutado únicamente en el callback final `_terminar_salida()`.

---

## Entrada 4 — Pantallas Finales Elásticas (Rúbrica 25%)
- **Decisión**: Reemplazo de pantallas estáticas por transiciones elásticas mediante `TRANS_ELASTIC` y `TRANS_BACK`.
- **Implementación**:
  - Títulos de "GAME OVER" y "¡VICTORIA!" escalan desde 0 con `TRANS_ELASTIC` y `EASE_OUT`.
  - Botones de Reintentar y Menú emergen en cascada con `TRANS_BACK` y fundido de opacidad modulada.
  - El fondo de oscurecimiento arcade se anima suavemente con interpolación de alfa.

---

## Entrada 5 — Micro-interacciones (Rúbrica 10%)
Se incorporaron y verificaron 9 micro-interacciones configurables:
1. **Flash de impacto en enemigos**: Incremento momentáneo de emisión de luz al recibir daño.
2. **Partículas / Explosión con color de acento**: Cada tipo de enemigo emite su color distintivo al morir.
3. **Sacudida de cámara proporcional**: Leve al disparar (0.06), media al eliminar marcianos (0.18), fuerte al recibir daño la nave (0.45).
4. **Destello de cañón (Muzzle Flash)**: Luz omnidireccional instantánea en la tobera al disparar.
5. **Telegrafía de disparo enemigo**: Pulso de escala y brillo en el enemigo antes de soltar un proyectil.
6. **Inclinación de la nave al moverse (Banking Tilt)**: Rotación suave en el eje Z basada en la velocidad horizontal.
7. **Escudos vivos**: Colapso 3D con contracción y giro al destruirse cada bloque.
8. **Puntaje flotante 3D**: Etiquetas 3D animadas (+10, +20, +30, +100) que se elevan y desvanecen.
9. **Pop en el HUD**: El marcador de puntos escala ligeramente al recibir nuevos puntos.

---

## Entrada 6 — Animación y Cinemática del Planeta de Fondo
- **Decisión**: Se coordinó el movimiento del modelo 3D `planeta_fondo.glb` con sus animaciones internas de Blender y la cinemática espacial del juego.
- **Implementación**:
  1. Activación de su clip interno `Idle-loop` importado en el `AnimationPlayer` con `loop_mode = LOOP_LINEAR` (animando la rotación de los anillos planetarios, el núcleo y la estación espacial en órbita).
  2. Rotación axial majestuosa a velocidad moderada en su eje polar Y (`delta * 0.03`).
  3. Deriva orbital armónica: oscilación senoidal suave en los ejes X e Y (`sin(t)` y `cos(t)`).
  4. Efecto de micro-paralaje reactivo respecto al movimiento horizontal del jugador en `X`.
  5. Modulación rítmica de la energía de la luz ambiental `PlanetIllumination`.
