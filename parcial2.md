## Actividad Práctica: Animación y Game Feel 3D

Guía de Implementación y Evaluación Técnica

## 1. Introducción

El objetivo de esta sesión es transformar la estática mecánica en una experiencia orgánica. Implementaremos sistemas de animación coordinados que brinden retroalimentación clara al jugador, utilizando tanto Tweens como el AnimationPlayer.

## 2. Requerimientos Técnicos

## A. Metodología de Animación

Tienes libertad creativa para elegir el flujo que mejor se adapte a tu diseño:

- Tweens: Recomendados para lógica dinámica y cambios de escala/color por código.

- AnimationPlayer: Ideal para ciclos complejos o animaciones importadas.

## B. Secuencia de Entrada (Spawn por Filas)

- El Reto: Los marcianos deben aparecer escalonadamente por filas completas. Cada fila se despliega simultáneamente antes de dar paso a la siguiente.

- Orden: Marcianos ➔ Escudos ➔ Jugador. El juego permanece bloqueado hasta el último callback de entrada.

## C. Feedback de Combate

- Impacto (Hit-Stop): Pausa el tiempo de juego (set_process) momentáneamente para dar peso al golpe.

- Eliminación: Los enemigos deben despedirse con una animación de salida 3D (giros o contracción) antes de ser eliminados.

## D. Transiciones de Estado

- Las pantallas de Victoria y Game Over deben usar interpolaciones elásticas para captar la atención del usuario.

## 3. Rúbrica de Evaluación

| Criterio | Indicador de Logro Detallado | Peso |
| --- | --- | --- |
| Spawn por Filas | Secuencia rítmica donde cada fila de marcianos aparece | 20% |
|   | en bloque antes de activar al jugador. |   |
| Eliminación y | Efecto de «Hit-Stop» funcional y animación de salida | 25% |
| Feedback | clara al eliminar enemigos. |   |
| Pantallas Finales | Mensajes de fin de partida con suavizado elástico y | 25% |
|   | transiciones dinámicas. |   |


| Creatividad | Añade micro-interacciones adicionales que enriquecen | 10% |
| --- | --- | --- |
|   | la atmósfera visual. |   |
| Sustentación | Explicación técnica de la lógica de sincronización y | 20% |
|   | control de flujo de animaciones. |   |

## 4. Sustentación (Detalles de Evaluación)

Durante la sustentación, el estudiante deberá demostrar y explicar lo siguiente:

- Control de Flujo: Cómo se bloquea el input del jugador durante el spawn inicial.

- Lógica de Callbacks: Explicar el método utilizado para detectar cuándo termina una animación (Tween o AnimationPlayer) y qué acción lógica dispara a continuación.

- Gestión de la Eliminación: Justificar la elección de los parámetros de animación antes de la llamada a queue_free().

## 5. Laboratorio de Código

Ejemplo: Animación de Eliminación (Tween 3D)

Para lograr una salida orgánica, combina escala y rotación antes del borrado:

```
func eliminar_enemigo():
var tw = create_tween().set_parallel(true)
tw.tween_property(self, "scale", Vector3.ZERO, 0.4)
tw.tween_property(self, "rotation:y", deg_to_rad(360), 0.4)
tw.set_parallel(false)
tw.tween_callback(queue_free)
```

«La diferencia entre un juego que funciona y uno que se siente vivo está en los pequeños detalles que solo la animación puede contar.»
