# Plan de implementación — Space Invaders 3D

**Parcial 2 · Animación y Game Feel 3D** · Blender (vía MCP) → Godot 4.7

> **Para:** el agente de desarrollo (Antigravity).
> **Cliente:** el estudiante dueño del proyecto, que debe *sustentar* el trabajo ante el docente: necesita entender cada decisión y cada línea de código.
> **Orden obligatorio:** (1) modelos *high poly* con sus animaciones en Blender → (2) exportar y validar → (3) integrar en Godot y desarrollar el juego.

**Contenido:** 0 Reglas · 1 Contexto y rúbrica · 2 Convenciones · 3 Carpetas · Fase 0 Preparación · Fase 1 Modelado y animación en Blender · Fase 2 Exportación y QA de assets · Fase 3 Integración en Godot · Fase 4 Jugabilidad y niveles · Fase 5 Animación y Game Feel · Fase 6 Creatividad · Fase 7 QA y sustentación · Apéndices A–D

---

## 0. Reglas de trabajo del agente

1. **Lee todo el documento antes de actuar** y avanza **fase por fase**. No se integra nada en Godot hasta cerrar la Fase 1 (única excepción: la prueba de humo de la Fase 0).
2. **Blender, solo con el MCP de Blender** (requisito del curso): modelado, materiales, animación y exportación pasan por él. Cada script que ejecutes por MCP se guarda también en `blender/scripts/` para poder repetirlo.
3. **Godot:** usa el MCP de Godot si está disponible (ejecutar el proyecto, leer errores, crear nodos y escenas). Si no, trabaja "normal": editar `.gd` / `.tres`, crear escenas con el editor o con un script de construcción, y validar por consola. Decide en la Fase 0 y anótalo en la bitácora.
4. **Puntos de control:** al cerrar cada fase (y cada bloque de modelos en la Fase 1) detente, entrega el informe (Apéndice C) con evidencias —capturas, conteo de triángulos, consola— y **espera la aprobación** del estudiante.
5. **No destruyas nada:** no borres ni muevas archivos existentes sin pedir confirmación y no reorganices escenas ni scripts actuales (solo añade). Haz commit al cerrar cada tarea relevante, con mensajes en español.
6. **Código simple, explícito y comentado en español.** Nombres de funciones clave iguales a la guía del docente: `spawn_por_filas`, `hit_stop`, `eliminar_enemigo`. Prefiere soluciones fáciles de explicar sobre patrones sofisticados.
7. **Verifica, no supongas:** tras cada cambio, captura del viewport en Blender; en Godot, ejecuta el proyecto y revisa la consola (sin errores ni advertencias nuevas). Si algo no se pudo verificar, dilo.
8. **Mantén `docs/bitacora.md`:** decisiones, problemas y soluciones (alimenta la sustentación).
9. **Ante una ambigüedad importante** (número de niveles, estilo visual, etc.) usa la opción por defecto de este plan y pregúntalo en el siguiente punto de control; no te bloquees.

---

## 1. Contexto, objetivo y trazabilidad

**Proyecto:** Space Invaders 3D en Godot 4.7. Ya existe un proyecto en marcha; no se parte de cero.

**Objetivo del parcial:** pasar de una mecánica estática a una experiencia orgánica con animación y *game feel* (Tweens y/o AnimationPlayer), y **reemplazar las primitivas por modelos *high poly* creados y animados en Blender**.

**Entregables**
1. Modelos `.glb` (high poly, con animaciones) en `assets/models/`.
2. Juego funcionando con: spawn por filas, bloqueo de input, hit-stop, animación de eliminación, pantallas finales elásticas, micro-interacciones y una nave del jugador distinta en cada nivel.
3. Documentación: `docs/CONVENCIONES.md`, `docs/inventario.md`, `docs/assets_manifest.md`, `docs/bitacora.md`, `docs/SUSTENTACION.md`.

### 1.1 Rúbrica del parcial → dónde se resuelve

| Criterio (peso) | Qué debe verse / explicarse | Se resuelve en |
|---|---|---|
| Spawn por filas (20 %) | Filas completas que aparecen en bloque, una tras otra; orden Marcianos → Escudos → Jugador; juego bloqueado hasta el último callback de entrada | F5.1 – F5.3 |
| Eliminación y feedback (25 %) | Hit-stop funcional + animación de salida 3D (giro/contracción) antes de `queue_free()` | F5.4 – F5.6 |
| Pantallas finales (25 %) | Victoria y Game Over con interpolación elástica y transiciones dinámicas | F5.7 – F5.8 |
| Creatividad (10 %) | Micro-interacciones adicionales que enriquecen la atmósfera | Fase 6 (y los clips de Blender de la Fase 1) |
| Sustentación (20 %) | Control de flujo del input, lógica de callbacks, justificación de parámetros antes de `queue_free()` | Fase 7 + comentarios en el código |

### 1.2 Requisitos heredados de la Tarea 1 (deben seguir funcionando)

- Enjambre enemigo que dispara y **ovni bonus aleatorio** (`OvniSpawner`).
- **Barreras destructibles** hechas de bloques (`Shield` / `ShieldBlock`).
- **UI con puntos** y **3 vidas**.
- Jugador y enjambre **confinados al área visible** (rebote/descenso).
- Estética **"Arcade Neon"**: materiales con Emission, luces y `WorldEnvironment` con Glow.

### 1.3 Entorno

- Windows 11 con PowerShell. El laptop (Ryzen 7 + RTX 3050) es el **equipo de referencia** para medir rendimiento.
- Godot 4.7 (comprobar con `godot --version`; el ejecutable puede no estar en el PATH).
- Blender: versión instalada (consultarla por MCP). Addon de conexión "MCP Connector v2" (por defecto `ws://127.0.0.1:9876`).
- Antigravity con MCP de Blender; MCP de Godot opcional.

---

## 2. Convenciones técnicas

> Propuesta inicial. Se confirma y ajusta en la Fase 0 y se guarda en `docs/CONVENCIONES.md`.

| Tema | Convención |
|---|---|
| Unidades | 1 unidad de Blender = 1 m = 1 unidad de Godot. Escala de escena en Blender = 1.0 |
| Ejes | Exportar con **+Y arriba**. Campo de juego = plano XZ de Godot: jugador abajo (+Z), enemigos arriba (−Z). El **frente** de cada nave apunta a −Z (hacia donde dispara). La orientación real del `.glb` se **comprueba en la prueba de humo** y se corrige en Blender, no con parches en Godot |
| Pivote | Origen en el centro del volumen del modelo (para que el giro `rotation:y` sea sobre su propio centro) |
| Transformaciones | Aplicar escala y rotación (Ctrl+A) antes de exportar, salvo en el Armature |
| Tamaño | *Bounding box* objetivo = AABB de las primitivas actuales (tabla en `docs/inventario.md`). Sin referencia: jugador ≈ 1.6 × 0.6 × 1.4 · enemigo ≈ 1.2 × 0.6 × 1.0 · ovni ≈ 2.2 × 0.7 × 1.2 |
| FPS de animación | 30 |
| Nombres | `snake_case` ASCII, sin espacios ni acentos. Archivos: `nave_mk1.glb`. Objetos: `nave_mk1_casco`. Huesos: `h_canon_izq`. Materiales: `m_casco`, `m_neon`, `m_cristal` |
| Clips | Nombres exactos (ver F1.7). Los cíclicos terminan en `-loop` (Godot los importa con bucle) |
| Colisiones | Siempre formas simples en Godot (caja / esfera / cápsula). Nunca la malla high poly |
| Idioma | Código y comentarios en español; los identificadores ya existentes se respetan tal cual |

**Paleta (acentos emisivos; el casco base es gris azulado oscuro `#1B2030`, metálico)**

| Elemento | Color |
|---|---|
| Jugador Mk I → V | cian `#00E5FF` · azul eléctrico `#3D7BFF` · menta `#00FFB3` · ámbar `#FFB300` · oro-blanco `#FFF1B0` |
| Enemigos A / B / C | violeta `#A855F7` · rosa `#FF2E93` · rojo-naranja `#FF4D2E` |
| Ovni | amarillo `#FFE600` |
| Escudos | verde lima `#B6FF3B` |

---

## 3. Estructura de carpetas

```text
<raíz del proyecto Godot>/
├─ project.godot
├─ PLAN_IMPLEMENTACION.md
├─ blender/                  ← lleva un archivo vacío .gdignore (Godot no la importa)
│  ├─ src/                   ← .blend de trabajo (nave_base.blend, enemigos.blend, …)
│  ├─ scripts/               ← build_<asset>.py · utils_blender.py
│  └─ renders/               ← capturas de control (PNG) de cada hito
├─ docs/                     ← lleva .gdignore · CONVENCIONES · inventario · assets_manifest · bitacora · SUSTENTACION
├─ assets/
│  ├─ models/                ← jugador/ enemigos/ ovni/ escudo/ proyectiles/ entorno/  (*.glb)
│  └─ materials/             ← materiales extraídos (.tres) para ajustar emisión y color
├─ autoload/                 ← game_manager.gd · game_feel.gd
├─ resources/                ← niveles/*.tres (NivelData) · enemigos/*.tres (EnemigoData)
├─ tools/                    ← scripts de validación (validar_modelos.gd)
└─ (escenas y scripts actuales: se quedan donde están; lo nuevo va en carpetas nuevas)
```

---

## Fase 0 — Preparación y prueba de humo

**Objetivo:** entorno verificado, proyecto respaldado y pipeline Blender → Godot probado con un modelo trivial *antes* de invertir horas en modelos high poly.

- [ ] **F0.1 Verificar herramientas.**
  - *MCP de Blender:* lista las herramientas disponibles; pide la información de la escena y una captura del viewport. Si no conecta, **diagnostica antes de seguir**: Blender abierto con el addon en estado *Running* (por defecto `ws://127.0.0.1:9876`), puerto libre y sin bloqueo del firewall de Windows, orden de arranque (primero Blender + addon; luego reiniciar el servidor MCP / Antigravity) y configuración del servidor MCP en el cliente. Registra la causa en la bitácora. Solo con aprobación del estudiante se usa como contingencia `blender -b archivo.blend -P script.py`.
  - *MCP de Godot (opcional):* lista sus herramientas. Si no existe o no conecta, se trabaja "normal" (edición de archivos + consola). Registra la decisión.
  - *Versiones:* `godot --version` y la versión de Blender (por MCP). Ajusta el plan a ellas: el API de acciones/NLA y los nombres de opciones del exportador glTF cambian entre versiones de Blender.
- [ ] **F0.2 Inventario del proyecto (solo lectura)** → `docs/inventario.md`: árbol de escenas y scripts, nodos de la escena principal, señales, Input Map, capas de colisión, posición/FOV de la cámara, límites del campo, tamaño del enjambre (filas × columnas) y el **AABB de las primitivas actuales** de enemigo, jugador, ovni, bloque de escudo y balas (serán el *bounding box* objetivo de cada modelo). Se espera encontrar —**confirmar, no asumir**—: escenas `alien`, `jugador`, `proyectil`, `alien_bullet`, `ShieldBlock`, `Shield`, `ovni`; scripts `alien_fleet.gd`, `alien.gd`, `alien_bullet.gd`, `bala.gd`, `character_body_3d.gd`; una escena principal con `WorldEnvironment`, `DirectionalLight3D`, `Camera3D`, `CanvasLayer` y `OvniSpawner`; y un enjambre de ≈ 20 naves.
- [ ] **F0.3 Respaldo y control de versiones.** Si no hay git: `git init` + `.gitignore` (Godot: `.godot/`; Blender: `*.blend1`, `*.blend2`). Crea la etiqueta/rama `respaldo-primitivas` con la versión actual (la Tarea 1 exigía solo primitivas; la guía del Parcial 2 no restringe el tipo de malla) y trabaja en la rama `parcial2-modelos`. Si la carpeta del proyecto está dentro de OneDrive (p. ej. el Escritorio sincronizado), propón moverla fuera (por ejemplo a la unidad D:) o excluir `.godot/`, `*.blend1` y `*.blend2` de la sincronización: OneDrive puede bloquear archivos de caché e importaciones. Pide confirmación antes de mover nada.
- [ ] **F0.4 Estructura.** Crea las carpetas de la sección 3, incluidos los `.gdignore` de `blender/` y `docs/`.
- [ ] **F0.5 `docs/CONVENCIONES.md`** con la sección 2 ajustada al inventario (tamaños reales, capas de colisión, nombres de acciones del Input Map).
- [ ] **F0.6 Prueba de humo del pipeline.** En Blender (por MCP): cubo con bisel + Armature de 1–2 huesos + dos acciones (`Idle-loop`, `Hit`) + material con emisión cian. Expórtalo a `.glb` con la función de F2.1, impórtalo en Godot en una escena de prueba (`tools/pipeline_test.tscn`) y verifica: escala (1 m), hacia dónde apunta el frente, pivote, nombres de clips, bucle automático de `Idle-loop`, emisión + Glow, y que un Tween sobre un nodo `Visual` padre no choque con el AnimationPlayer. Anota en `CONVENCIONES.md` las opciones de exportación y la corrección de orientación definitivas.

**Aceptación de la Fase 0**
- [ ] MCP de Blender operativo (se recibió una captura del viewport).
- [ ] Decisión "MCP de Godot / normal" registrada.
- [ ] `docs/inventario.md` con tabla de *bounding boxes* objetivo.
- [ ] Respaldo creado y rama de trabajo activa.
- [ ] Carpetas creadas; `CONVENCIONES.md` redactado.
- [ ] Prueba de humo aprobada y opciones de exportación fijadas.
- [ ] Informe de fase entregado. **Detenerse y esperar aprobación.**

---

## Fase 1 — Modelado high poly y animación en Blender (vía MCP)

**Objetivo:** producir en Blender todos los modelos necesarios, con detalle alto y animaciones, listos para exportar. **No se toca Godot hasta cerrar esta fase.**

### F1.1 Método de trabajo

- **Un script idempotente por asset:** `blender/scripts/build_<asset>.py` limpia su colección y reconstruye el modelo desde cero. Así se puede repetir, corregir y explicar. Los `.blend` van en `blender/src/` (se versionan; son pequeños porque los modificadores no se aplican).
- **Ciclo corto:** bloqueo de formas → captura → detalle → captura → materiales → captura → animación → captura. Scripts pequeños; guarda el `.blend` entre pasos (`bpy.ops.wm.save_mainfile()`).
- **Modificadores sin aplicar** (Mirror, Bevel, Subdivision, Array, Boolean): se aplican al exportar.
- **Diseña para la cámara del juego** (cenital/oblicua): la silueta vista desde arriba debe leerse bien a ~100 px de ancho.
- Cada asset vive en dos colecciones: `SRC_<asset>` (trabajo) y `EXPORT_<asset>` (lo que se exporta).

### F1.2 Catálogo de assets

| Bloque | Asset | Archivo (`assets/models/…`) | Triángulos* | Clips |
|---|---|---|---|---|
| 1A | Enemigos A, B, C (fila superior / media / inferior) | `enemigos/enemigo_a.glb` … `enemigo_c.glb` | 12 k – 25 k c/u | `Idle-loop`, `Attack`, `Hit`, `Death` (opcional) |
| 1A | Bloque de escudo: sano + agrietado | `escudo/escudo_bloque.glb` | 1 k – 3 k c/u | — |
| 1A | Bala del jugador / bala enemiga | `proyectiles/bala_jugador.glb`, `bala_enemiga.glb` | 0.5 k – 2 k | `Idle-loop` |
| 1B | **Nave del jugador Mk I → V** (una por nivel) | `jugador/nave_mk1.glb` … `nave_mk5.glb` | 30 k → 80 k (crece con el nivel) | `Idle-loop`, `Fire`, `Hit`, `Spawn`, `Victory`, `Death` |
| 1C | Ovni bonus | `ovni/ovni_bonus.glb` | 20 k – 40 k | `Idle-loop`, `Death` |
| 1C | Decorado de fondo (planeta/estación; opcional) | `entorno/planeta_fondo.glb` | ≤ 50 k | `Idle-loop` (rotación lenta) |

\* Triángulos tras aplicar modificadores. **Presupuesto global: escena completa ≤ ~2.5 M de triángulos en pantalla** (se mide en F4.4).

### F1.3 La nave del jugador cambia en cada nivel

Estrategia: construir un **casco base compartido** (`nave_base.blend`) y añadir **módulos por nivel** (colecciones de alas, cañones, motores). Así las 5 naves se perciben como evolución de la misma y se ahorra tiempo.

| Nivel | Nave | Rasgos | Acento |
|---|---|---|---|
| 1 | Mk I «Vanguard» | Delta compacta, 1 cañón central, cabina de cristal, 2 toberas | cian |
| 2 | Mk II «Striker» | + 2 cañones laterales, aletas, toberas mayores | azul eléctrico |
| 3 | Mk III «Phantom» | Alas en flecha, 2 pods de motor, paneles con luces | menta |
| 4 | Mk IV «Titan» | Blindaje pesado, 4 cañones, estabilizadores | ámbar |
| 5 | Mk V «Apex» | Alas-cuchilla flotantes, halo/anillo orbital, núcleo de energía visible | oro-blanco |

(Nombres y rasgos son una propuesta; el estudiante puede cambiarlos en el punto de control 1B.)

### F1.4 Enemigos y demás assets

- **A «Calamar»** (fila superior, el más pequeño): cúpula + tentáculos (curvas con bisel convertidas a malla) + ojo emisivo. Violeta.
- **B «Cangrejo»** (filas medias): caparazón segmentado, dos pinzas, patas articuladas. Rosa.
- **C «Behemoth»** (fila inferior, el más grande): masa con placas de armadura, varios ojos/antenas. Rojo-naranja.
- Los tres se distinguen por **silueta cenital** y por color de acento.
- **Ovni:** disco con cúpula, anillo giratorio y luces. Amarillo.
- **Bloque de escudo:** bloque con bisel y paneles; variante agrietada (misma silueta, grietas en relieve y emisión baja). Dimensiones = bloque actual.
- **Balas:** cápsula/rombo con halo emisivo. La del jugador se recolorea en Godot con el acento de su nave.

### F1.5 Técnica high poly

- **Hard-surface (naves, ovni, escudo):** blockout → Mirror (X) → Bevel por ángulo/peso → Subdivision Surface (nivel 2–3) → paneles con Inset/Boolean → detalles repetidos con Array (aletas, remaches, cañones, toberas).
- **Orgánico (enemigos):** SubD + Displace con ruido para relieve; tentáculos con curvas + bisel; placas de armadura como piezas separadas.
- **Triángulos con sentido:** sin caras internas ocultas; sombreado suave con corte por ángulo (Smooth by Angle / Weighted Normal según versión de Blender).
- **Niveles de Subdivision y Bevel de viewport = render.** El exportador evalúa el resultado del viewport; verifica siempre con `contar_triangulos` (F2.1).

### F1.6 Materiales

- Solo **Principled BSDF** (color, metallic, roughness, emission). Los nodos procedurales no se exportan.
- Casco oscuro metálico + **acentos neón emisivos** del color del asset (Emission Strength 1–3; el brillo final se ajusta en Godot).
- Cristal/cabina: transparencia con moderación (pocas superficies).
- ≤ 5 materiales por modelo. Sin texturas externas (si se hornea alguna, que viaje embebida en el `.glb`).

### F1.7 Animaciones (nombres exactos)

| Clip | Aplica a | Duración | Descripción |
|---|---|---|---|
| `Idle-loop` | todos | 1–2 s, bucle | Jugador: flotación + pulso de motores · Enemigos: movimiento propio (tentáculos, pinzas, antenas) · Ovni: anillo giratorio + luces · Balas: pulso/giro |
| `Fire` | jugador | 0.2–0.3 s | Retroceso de cañones + destello de tobera |
| `Hit` | jugador, enemigos | 0.2–0.3 s | Sacudida/temblor corto |
| `Attack` | enemigos | 0.4–0.6 s | Anticipación antes de disparar (telegrafía) |
| `Spawn` | jugador | 0.8–1.0 s | Despliegue de la nave nueva (alas se abren, motores se encienden) |
| `Victory` | jugador | 1.5–2.5 s | Maniobra de celebración |
| `Death` | jugador, ovni (enemigos: opcional) | 0.6–1.0 s | Desarme/desintegración de piezas |

- **Armature mínimo:** un hueso por parte móvil; las partes rígidas con peso 1.0 al hueso. **Un Action por clip**, con el nombre exacto; llévalos a pistas NLA y deja la pose de reposo como estado por defecto.
- Clips `-loop`: primer y último fotograma idénticos. Keyframes limpios, 30 fps.
- **Regla de convivencia con los Tweens (importante):** las animaciones de Blender **no animan la transformación del objeto raíz** (posición/escala/rotación global); solo huesos y partes internas. El raíz lo controlan los Tweens en Godot (spawn, eliminación, entrada de la nave).
- Si Blender es 4.4+ (Actions con *slots*) o 5.x, comprueba el API antes de scriptear acciones y NLA.

### F1.8 Registro y control de calidad

Cada asset se anota en `docs/assets_manifest.md` (asset · archivo · triángulos · materiales · clips · bbox · estado). Checklist por asset:

- [ ] Silueta legible desde la cámara de juego (captura cenital + 3/4 en `blender/renders/`).
- [ ] Triángulos dentro del presupuesto (medidos con el depsgraph evaluado).
- [ ] Bbox ≈ objetivo (±10 %), pivote centrado, frente según la prueba de humo, escala/rotación aplicadas.
- [ ] ≤ 5 materiales con nombres de la convención; emisión con el color del acento.
- [ ] Clips con nombres exactos, bucles cerrados, sin animar el raíz.
- [ ] `.blend` guardado + `build_<asset>.py` reproducible.

**Puntos de control:** **1A** enemigos + bloque de escudo + balas · **1B** naves Mk I–V · **1C** ovni + decorado. En cada uno: capturas, tabla de triángulos y lista de clips; esperar aprobación antes del siguiente bloque.

---

## Fase 2 — Exportación y control de calidad de assets

**Objetivo:** `.glb` correctos, medidos y reproducibles.

### F2.1 Exportar a `.glb` (desde Blender, por MCP)

Cada colección `EXPORT_<asset>` se exporta a `assets/models/<categoría>/<archivo>.glb`. Punto de partida para `blender/scripts/utils_blender.py` (verifica nombres y valores contra la versión instalada):

```python
import bpy

def contar_triangulos(objetos):
    """Triángulos reales tras aplicar modificadores (lo que se exporta)."""
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in objetos:
        if o.type != 'MESH':
            continue
        eo = o.evaluated_get(dg)
        me = eo.to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        eo.to_mesh_clear()
    return total

OPCIONES_GLB = dict(
    export_format='GLB', use_selection=True,
    export_apply=True,            # aplica modificadores (Subsurf, Bevel, Array…)
    export_yup=True,
    export_cameras=False, export_lights=False,
    export_animations=True,
    export_animation_mode='ACTIONS',   # un clip por Action (si la versión lo soporta)
    export_materials='EXPORT',
)

def exportar_glb(ruta, objetos):
    # Filtra opciones que no existan en esta versión de Blender.
    soportadas = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    kwargs = {k: v for k, v in OPCIONES_GLB.items() if k in soportadas}
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objetos:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objetos[0]
    bpy.ops.export_scene.gltf(filepath=ruta, **kwargs)
```

- `export_apply` impide exportar *shape keys*: si se usan, aplica los modificadores a mano antes.
- Lee las animaciones desde el Armature: cada Action debe terminar como un clip separado con su nombre.

### F2.2 Informe por asset

Función `informe_asset(coleccion)` que devuelva triángulos, bbox, pivote, materiales y acciones. Compáralo con el presupuesto y el bbox objetivo y anótalo en `assets_manifest.md`.

### F2.3 Validación en Godot

Reimporta (`godot --headless --path . --import`) y comprueba que todo importa sin errores, que cada modelo trae `AnimationPlayer` con los clips esperados, que los `-loop` están en bucle y que orientación y tamaño coinciden. Conviene automatizarlo con `tools/validar_modelos.gd`: instancia cada `.glb` e imprime clips, AABB y modos de bucle.

### F2.4 Ajustes de importación

Advanced Import: Root Type `Node3D` · Meshes: *Generate LODs* y *Create Shadow Meshes* activos · Materials: extraer a `res://assets/materials/` para ajustar `emission_energy_multiplier` y recolorear · Animation: bucle según el sufijo `-loop` (o modo de bucle en el diálogo).

**Aceptación de la Fase 2**
- [ ] 100 % del catálogo importa sin errores ni advertencias.
- [ ] Clips y bucles correctos; bbox a ±10 % del objetivo.
- [ ] `assets_manifest.md` completo. Informe de fase entregado.

---

## Fase 3 — Integración en Godot

**Objetivo:** sustituir las primitivas por los modelos manteniendo el juego funcionando.

### F3.1 Patrón de escena para todos los actores

```text
Enemigo  (el nodo de física actual: Area3D / CharacterBody3D …)  ← script, señales, colisión
├─ CollisionShape3D        ← forma simple (esfera/caja), NO la malla high poly
└─ Visual  (Node3D)        ← PIVOTE: aquí actúan los Tweens (scale, rotation, position)
   └─ Modelo  (instancia del .glb)  ← trae su AnimationPlayer (Idle-loop, Hit, …)
```

**Regla:** los Tweens solo tocan `Visual`; el AnimationPlayer del `.glb` solo toca sus huesos. Así nunca se pisan.

### F3.2 Tareas

- [ ] Importar los `.glb` (`godot --headless --path . --import` o enfocar el editor).
- [ ] `EnemigoData` (Resource): `tipo`, `puntos`, `escena_modelo: PackedScene`, `color_acento`. Un `alien.tscn` + 3 `.tres`, o 3 escenas heredadas (lo que menos rompa lo existente).
- [ ] `alien.tscn`: sustituir el MeshInstance3D primitivo por `Visual/Modelo`; `@onready var visual: Node3D = $Visual`.
- [ ] Jugador: `Visual/Modelo` intercambiable con `set_nave(nivel)` (instancia `nave_mk{n}` y libera la anterior).
- [ ] Ovni, `ShieldBlock` (sano/agrietado) y balas: mismo patrón.
- [ ] Helper `reproducir(nombre)`: busca el AnimationPlayer con `find_child("AnimationPlayer", true, false)` y reproduce solo si existe el clip (`has_animation`).
- [ ] Autoloads `GameManager` y `GameFeel` (Project Settings → Globals → Autoload); `GameFeel` con `process_mode = Always`.
- [ ] Input Map: respeta las acciones existentes y añade las de depuración (F5.9).
- [ ] Documentar las capas de colisión (jugador, enemigos, balas del jugador, balas enemigas, escudos, límites) en `CONVENCIONES.md`.
- [ ] `WorldEnvironment`: ajustar Glow para que los acentos neón brillen sin lavar la imagen; luces de apoyo para el metal.
- [ ] Si un material extraído se comparte, duplicarlo por instancia (`resource_local_to_scene`) donde se anime emisión o color por separado.

**Aceptación de la Fase 3**
- [ ] El juego se comporta igual que antes, pero con los modelos high poly animándose en reposo (`Idle-loop`).
- [ ] Sin errores ni advertencias nuevas en consola; FPS preliminar anotado. Informe de fase entregado.

---

## Fase 4 — Jugabilidad base y niveles

### F4.1 Verificación de la base (corregir solo lo que falle, con el cambio mínimo)

- [ ] Jugador y enjambre confinados al área visible (rebote y descenso del enjambre).
- [ ] El disparo del jugador elimina enemigos y sube el puntaje.
- [ ] Los enemigos disparan (desde la fila inferior de cada columna).
- [ ] 3 vidas: daño, reaparición y derrota al llegar a 0.
- [ ] Barreras destructibles por bloques; ovni aleatorio con bonus.
- [ ] Derrota si el enjambre alcanza la línea del jugador.

### F4.2 Niveles y nave por nivel

```gdscript
class_name NivelData extends Resource
## Datos de un nivel. Se guardan como .tres en res://resources/niveles/

@export var numero := 1
@export var nave_jugador: PackedScene            # nave_mk1 … nave_mk5
@export var filas := 4
@export var columnas := 5
@export var tipos_por_fila: Array[int] = [0, 1, 1, 2]   # índice de EnemigoData por fila
@export var velocidad_formacion := 1.0
@export var intervalo_disparo := 1.6             # segundos entre disparos enemigos
@export var intervalo_ovni := 25.0
```

| Nivel | Nave | Enemigos (aprox.) | Velocidad | Disparo enemigo | Ovni |
|---|---|---|---|---|---|
| 1 | Mk I | 20 (la formación actual) | 1.0× | 1.6 s | ~25 s |
| 2 | Mk II | 24 | 1.15× | 1.4 s | ~22 s |
| 3 | Mk III | 30 | 1.3× | 1.2 s | ~20 s |
| 4 | Mk IV | 35 | 1.5× | 1.0 s | ~18 s |
| 5 | Mk V | 40 | 1.7× | 0.8 s | ~15 s |

Valores iniciales: se ajustan jugando. Si el FPS baja de 60, reduce enemigos antes que triángulos.

### F4.3 Flujo de niveles (desacoplado por señales)

`iniciar_nivel(n)` → intro (Fase 5) → `JUGANDO` → el enjambre emite `nivel_completado` **cuando el último enemigo termina su animación de salida** (no al recibir el disparo) → si `n < 5`: banner + cambio de nave + `iniciar_nivel(n + 1)`; si `n == 5`: `VICTORIA`. El jugador sin vidas o el enjambre en la línea de fondo → `GAME_OVER`.

### F4.4 Puerta de rendimiento (antes de pasar a la Fase 5)

- Medir con la formación completa del nivel 5, escudos, ovni y la nave Mk V: **≥ 60 FPS a 1080p** y **≤ 2.5 M de primitivas** (`Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)`; añade un overlay de depuración con FPS y primitivas).
- Confirma que Godot usa la **GPU dedicada**: el log de arranque indica el dispositivo. Si usa la integrada, forzar "Alto rendimiento" para Godot en Configuración de Windows → Sistema → Pantalla → Gráficos.
- Si no se cumple, en este orden: (1) verificar que los LODs se generaron; (2) reducir sombras (distancia máxima y tamaño del shadow map); (3) decimar enemigos un 30–50 % en Blender y reexportar; (4) `MultiMesh` para los bloques de escudo.

---

## Fase 5 — Animación y Game Feel (núcleo del parcial)

Todo lo de esta fase usa **Tweens** (o `AnimationPlayer` para los clips de Blender) y debe quedar **comentado en español** para la sustentación.

### F5.1 Estados y bloqueo de entrada

```gdscript
# autoload/game_manager.gd  — Autoload "GameManager"
extends Node

enum Estado { MENU, INTRO, JUGANDO, NIVEL_COMPLETADO, VICTORIA, GAME_OVER }

signal estado_cambiado(nuevo_estado)

var estado: Estado = Estado.MENU
var input_bloqueado := true
var nivel_actual := 1

func cambiar_estado(nuevo: Estado) -> void:
	estado = nuevo
	estado_cambiado.emit(nuevo)

func bloquear_input() -> void:
	input_bloqueado = true

# Se llama desde el ÚLTIMO callback de la secuencia de entrada.
func desbloquear_input() -> void:
	input_bloqueado = false
	cambiar_estado(Estado.JUGANDO)
```

Reglas:
- [ ] `mover` y `disparar` del jugador salen de inmediato si `GameManager.input_bloqueado`.
- [ ] Movimiento y disparos del enjambre, `OvniSpawner` y contadores solo corren en `Estado.JUGANDO` (p. ej. `if GameManager.estado != GameManager.Estado.JUGANDO: return` al inicio de `_physics_process`).
- [ ] Los enemigos recién creados no tienen colisión activa hasta el final de la intro (`set_deferred("monitoring", false)` y reactivar al desbloquear).
- [ ] No se encolan pulsaciones: leer el input cada frame y no guardar eventos durante el bloqueo.

### F5.2 Spawn por filas (Marcianos)

Orden de filas: de la más lejana (−Z) a la más cercana al jugador. **Dentro de una fila, todos a la vez** (`set_parallel(true)`); la siguiente fila empieza solo cuando el Tween anterior emite `finished`.

```gdscript
# alien_fleet.gd
signal formacion_lista

# filas_enemigos: Array de Arrays con los enemigos de cada fila (ya instanciados, ocultos).
func spawn_por_filas() -> void:
	for fila in filas_enemigos:
		if fila.is_empty():
			continue                                   # un Tween sin tweeners nunca emite finished
		var tw := create_tween().set_parallel(true)    # toda la fila a la vez
		for e in fila:
			e.visual.scale = Vector3.ONE * 0.001
			e.visual.position.y = 4.0
			e.visible = true
			tw.tween_property(e.visual, "scale", Vector3.ONE, 0.45) \
				.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			tw.tween_property(e.visual, "position:y", 0.0, 0.45) \
				.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		await tw.finished                              # callback: la fila terminó
		for e in fila:
			e.reproducir("Idle-loop")                  # clip de Blender
		await get_tree().create_timer(0.12).timeout    # respiro rítmico entre filas
	formacion_lista.emit()
```

Parámetros iniciales: 0.45 s por fila · 0.12 s entre filas · escala 0→1 con rebote (`TRANS_BACK`) · caída desde y = 4. Alternativa válida: un solo Tween con `set_delay(fila * 0.57)` (queda un único `finished`).

### F5.3 Escudos y jugador (orquestación)

```gdscript
# main.gd (o NivelManager)
func iniciar_nivel(n: int) -> void:
	GameManager.nivel_actual = n
	GameManager.bloquear_input()
	GameManager.cambiar_estado(GameManager.Estado.INTRO)
	jugador.set_nave(n)                        # modelo de la nave del nivel (invisible aún)
	await alien_fleet.spawn_por_filas()        # 1) Marcianos, fila por fila
	await escudos.spawn_escudos()              # 2) Escudos
	jugador.entrar_en_escena()                 # 3) Jugador: su último callback desbloquea el juego
```

```gdscript
# escudos.gd — los bloques emergen del suelo en oleada
func spawn_escudos() -> void:
	var tw := create_tween().set_parallel(true)
	var i := 0
	for bloque in get_tree().get_nodes_in_group("bloques_escudo"):
		bloque.visual.position.y = -1.5
		bloque.visible = true
		tw.tween_property(bloque.visual, "position:y", 0.0, 0.35) \
			.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT).set_delay(i * 0.03)
		i += 1
	await tw.finished
```

```gdscript
# character_body_3d.gd (jugador)
func entrar_en_escena() -> void:
	visual.scale = Vector3.ONE * 0.001
	visual.position.y = 6.0
	reproducir("Spawn")                                  # clip de Blender (si existe)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(visual, "scale", Vector3.ONE, 0.9) \
		.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(visual, "position:y", 0.0, 0.7) \
		.set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	tw.set_parallel(false)
	tw.tween_callback(GameManager.desbloquear_input)     # ÚLTIMO callback de la entrada
```

### F5.4 Hit-stop

```gdscript
# autoload/game_feel.gd — Autoload "GameFeel"
extends Node

var _congelaciones := 0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS     # este nodo sigue vivo mientras el árbol está en pausa

func hit_stop(duracion: float = 0.06) -> void:
	if GameManager.estado != GameManager.Estado.JUGANDO:
		return
	_congelaciones += 1
	get_tree().paused = true
	# Temporizador que corre en pausa (process_always = true) e ignora Engine.time_scale.
	await get_tree().create_timer(duracion, true, false, true).timeout
	_congelaciones -= 1
	if _congelaciones == 0:
		get_tree().paused = false
```

- Duraciones: **0.06 s** al matar un enemigo · **0.12 s** al herir al jugador · **0.15–0.2 s** al matar al último enemigo del nivel.
- El contador `_congelaciones` evita que dos hit-stops superpuestos reanuden el juego antes de tiempo.
- Pausar el árbol equivale a desactivar `set_process` / `set_physics_process` en todos los nodos pausables **y además** congela Tweens, físicas y AnimationPlayers. Para la sustentación, documenta esto y deja anotada la variante literal con `set_process(false)` por grupo, por si el docente la pide.

### F5.5 Eliminación del enemigo

```gdscript
# alien.gd
signal eliminado(puntos: int)
signal salida_terminada

@export var puntos := 10
var muerto := false
@onready var visual: Node3D = $Visual
@onready var colision: CollisionShape3D = $CollisionShape3D

func eliminar_enemigo() -> void:
	if muerto:
		return
	muerto = true
	colision.set_deferred("disabled", true)      # ya no recibe ni hace daño
	eliminado.emit(puntos)                       # el enjambre y la UI actualizan cuenta y puntaje
	await GameFeel.hit_stop(0.06)                # 1) peso del golpe
	if not is_inside_tree():
		return                                   # el nivel se reinició durante la espera
	var tw := create_tween().set_parallel(true)  # 2) salida 3D: contracción + giro
	tw.tween_property(visual, "scale", Vector3.ONE * 0.001, 0.4) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_property(visual, "rotation:y", TAU, 0.4).as_relative()
	tw.set_parallel(false)
	tw.tween_callback(_terminar_salida)          # 3) solo al final se libera el nodo

func _terminar_salida() -> void:
	salida_terminada.emit()
	queue_free()
```

Justificación de parámetros (para la sustentación):
- **0.4 s** (≈ 24 cuadros a 60 fps): suficiente para leerse, corto para no frenar el ritmo.
- **Escala y giro en paralelo**: efecto de "vórtice"; **TAU (360°)** deja al modelo en su orientación original.
- **`TRANS_BACK` + `EASE_IN`**: el enemigo se infla un instante (anticipación) y luego se contrae.
- **Colisión desactivada antes** de animar: no se puede disparar dos veces al mismo enemigo ni daña al jugador mientras agoniza.
- **`queue_free()` como último callback**: el nodo no desaparece a mitad de la animación.
- Se anima `Visual` (no el raíz): evita escalar a cero un cuerpo físico. Si aparecen errores de matriz singular, mantener `0.001` en lugar de `Vector3.ZERO`.
- Extras de la fase: flash blanco con `material_overlay`, partículas del color del acento y puntaje flotante.

### F5.6 Feedback al jugador

- [ ] Al recibir daño: `await GameFeel.hit_stop(0.12)`, sacudida de cámara (~0.25 s, amplitud decreciente), clip `Hit`, parpadeo de invulnerabilidad (~1.5 s con Tween finito) y "pop" en el icono de vidas.
- [ ] Si quedan vidas: clip `Death` corto + `reaparecer()` (misma entrada elástica que `entrar_en_escena()`, más corta; no se repite el spawn de filas).
- [ ] Si no quedan: `GameManager.cambiar_estado(GameManager.Estado.GAME_OVER)`.

### F5.7 Pantallas de Victoria y Game Over (interpolación elástica)

`EndScreen` es un `CanvasLayer` con `process_mode = Always`. Victoria y Game Over comparten escena; cambian textos, colores y extras.

```gdscript
# end_screen.gd
extends CanvasLayer

@onready var fondo: ColorRect = $Fondo
@onready var titulo: Label = $Titulo
@onready var botones := [$BtnReintentar, $BtnMenu]

func mostrar(victoria: bool, puntaje: int) -> void:
	show()
	titulo.text = "¡VICTORIA!" if victoria else "GAME OVER"
	await get_tree().process_frame               # el tamaño del Label ya está calculado
	titulo.pivot_offset = titulo.size / 2.0      # escalar desde el centro
	titulo.scale = Vector2.ZERO
	fondo.color.a = 0.0
	for b in botones:
		b.pivot_offset = b.size / 2.0
		b.scale = Vector2.ZERO
		b.modulate.a = 0.0

	var tw := create_tween()
	tw.tween_property(fondo, "color:a", 0.75, 0.4)                       # fundido del fondo
	tw.tween_property(titulo, "scale", Vector2.ONE, 1.2) \
		.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)         # rebote elástico
	for b in botones:                                                    # botones en cascada
		tw.tween_property(b, "scale", Vector2.ONE, 0.5) \
			.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_property(b, "modulate:a", 1.0, 0.3)
	tw.tween_callback(func(): botones[0].grab_focus())
```

- Añadir: conteo animado del puntaje (`tween_method`), título que cae desde fuera de pantalla con elástico, y diferencias entre pantallas (Victoria: partículas de confeti + clip `Victory` de la nave + cámara que se acerca; Game Over: tinte rojo con Tween en el `WorldEnvironment`, sacudida y enemigos que se congelan).
- **Reintentar:** restablecer `GameManager` (`estado`, `input_bloqueado`, `nivel_actual`), `get_tree().paused = false` y recargar la escena (los Tweens ligados a nodos liberados se cancelan solos).

### F5.8 Transición de nivel y cambio de nave

1. Último enemigo muerto (tras su `salida_terminada`) → `GameFeel.hit_stop(0.2)` + cámara lenta breve opcional.
2. Banner **"NIVEL N"** entra con `TRANS_ELASTIC`, se mantiene ~1 s y sale con `TRANS_BACK`.
3. La nave actual sale con la misma contracción + giro de F5.5; se instancia la siguiente (`set_nave(n + 1)`).
4. `iniciar_nivel(n + 1)`: otra vez Marcianos → Escudos → Jugador, con el clip `Spawn` de la nave nueva.

### F5.9 Teclas de depuración (solo si `OS.is_debug_build()`)

`F1`–`F5` saltan al nivel N · `F9` fuerza Victoria · `F10` fuerza Game Over · `F11` elimina todos los enemigos. Sirven para probar y para la demo.

**Aceptación de la Fase 5 (contra la rúbrica)**
- [ ] **Spawn:** las filas aparecen una a una, cada una en bloque; durante todo el proceso mover/disparar no hace nada; justo tras el último callback el jugador responde.
- [ ] **Hit-stop:** perceptible (~60 ms), no deja el juego pausado, aguanta varias muertes casi simultáneas.
- [ ] **Eliminación:** giro + contracción de ~0.4 s antes de desaparecer; sin errores de nodo liberado.
- [ ] **Pantallas finales:** título con rebote elástico, fondo con fundido, botones en cascada; Reintentar funciona.
- [ ] **Transición de nivel:** banner elástico y nave nueva con su `Spawn`.
- [ ] Todo comentado en español. Informe de fase entregado.

---

## Fase 6 — Creatividad: micro-interacciones

**Objetivo:** enriquecer la atmósfera visual (10 % de la rúbrica) sin romper el flujo. Implementa **al menos 6** de esta lista, en este orden de prioridad (valor / costo). Cada una debe tener un `@export var activa := true` para poder apagarla en la demo y explicarla en la sustentación.

1. **Destello de impacto:** flash blanco en el enemigo golpeado (`material_overlay` duplicado por instancia + Tween del alfa).
2. **Explosión por enemigo:** partículas (`GPUParticles3D` / `CPUParticles3D`) con el color de acento del tipo.
3. **Sacudida de cámara proporcional:** leve al disparar, fuerte al ser herido.
4. **Destello de cañón:** `OmniLight3D` breve + clip `Fire` de la nave.
5. **Telegrafía del disparo enemigo:** clip `Attack` + pulso de emisión antes de disparar.
6. **Inclinación al moverse:** la nave hace *bank* (rotación en Z de `Visual`) y los motores pulsan según la velocidad.
7. **Escudos vivos:** parpadeo al recibir impacto; al destruirse un bloque, la misma contracción + giro de F5.5 y pequeños fragmentos.
8. **Puntaje flotante:** `Label3D` con "+10" que sube y se desvanece.
9. **HUD con "pop":** el contador de puntaje escala al subir; las vidas se rompen al perderse.
10. **Fondo vivo:** campo de estrellas con parallax y/o planeta girando (clip `Idle-loop` de Blender).
11. **Cámara con vida:** leve paralaje con la X del jugador y *dolly-in* durante la intro.
12. **Cámara lenta breve** al destruir al último enemigo del nivel.
13. **Latido del enjambre:** el ritmo (y un pulso de luz) se acelera al quedar pocos enemigos.
14. **Ovni:** entrada con estela y lluvia de puntos al destruirse.
15. *(Opcional)* **Audio:** disparos con `pitch_scale` aleatorio, sin dependencias externas.

**Aceptación de la Fase 6**
- [ ] ≥ 6 micro-interacciones funcionando, cada una activable/desactivable.
- [ ] Ninguna bloquea el flujo ni rompe el hit-stop. FPS ≥ 60. Informe de fase entregado.

---

## Fase 7 — QA, rendimiento y sustentación

### F7.1 Pruebas manuales

- [ ] Intro: filas una a una; mover/disparar durante la intro no hace nada; tras el último callback responde.
- [ ] Reiniciar y repetir 5 veces: sin bloqueos permanentes ni dobles intros.
- [ ] Hit-stop perceptible y nunca deja el juego pausado (matar 3 enemigos casi a la vez).
- [ ] Salida 3D: giro + contracción de ~0.4 s; sin errores "previously freed" en consola.
- [ ] Último enemigo de cada nivel → banner de nivel y nave Mk correcta (I → V).
- [ ] Nivel 5 completado → Victoria elástica; 0 vidas o enjambre en la línea → Game Over elástico; Reintentar y Menú funcionan.
- [ ] Escudos se destruyen por bloques; el ovni aparece y da bonus; 3 vidas operativas.
- [ ] Cada micro-interacción se puede apagar sin romper nada.
- [ ] Teclas de depuración solo en modo debug.
- [ ] Consola limpia (0 errores, 0 advertencias nuevas).

### F7.2 Rendimiento

Perfilar con el depurador de Godot (Monitores / Profiler) en el nivel 5: FPS, primitivas, draw calls y tiempo de física. Documentar los números en `docs/bitacora.md` y las decisiones tomadas si hubo que optimizar (LODs, sombras, decimado).

### F7.3 `docs/SUSTENTACION.md`

Debe contener, en lenguaje simple y con referencias a archivo y función (p. ej. `alien_fleet.gd → spawn_por_filas`):

1. **Control de flujo del input:** diagrama de estados (Mermaid) y explicación de cómo se bloquea el input durante el spawn inicial: bandera `input_bloqueado` + estado `INTRO`, qué sistemas la consultan y por qué solo el **último callback** (`tween_callback(GameManager.desbloquear_input)`) la libera.
2. **Lógica de callbacks:** cómo se detecta el fin de cada animación (`await tween.finished`, `tween_callback`, y `animation_finished` del AnimationPlayer), qué acción dispara a continuación y qué pasa si un Tween se cancela o el nodo se libera (`is_inside_tree()`, `kill()`).
3. **Gestión de la eliminación:** el orden hit-stop → animación → `queue_free()` y la justificación de cada parámetro de F5.5 (duración, escala + giro en paralelo, `TRANS_BACK`/`EASE_IN`, colisión desactivada antes, `queue_free` al final).
4. **Hit-stop:** por qué se pausa el árbol y su equivalencia con `set_process(false)`; variante literal por si se pide.
5. **Decisiones de arte y técnica:** por qué high poly y cómo se controla el costo (presupuesto de triángulos, LODs, colisiones simples), y por qué los Tweens actúan en `Visual` y no en el raíz del `.glb`.
6. **Preguntas probables** con respuesta corta (≥ 8): por qué `await` y no `yield`/temporizadores sueltos, qué pasa si dos enemigos mueren a la vez, por qué no animar la colisión, cómo se evitó que las pulsaciones durante la intro se ejecuten después, etc.
7. **Mapa requisito → archivo y función.**

### F7.4 Guion de demo (3–5 min)

1. Iniciar: mostrar el spawn fila por fila e intentar mover/disparar durante la intro (no responde).
2. La nave aparece con su animación y el control se libera.
3. Matar un enemigo: hit-stop + giro/contracción. Mostrar un escudo recibiendo impacto.
4. Recibir daño: sacudida y reaparición.
5. Completar el nivel: banner elástico y cambio de nave (Mk I → Mk II).
6. Con las teclas de depuración, saltar al nivel 5 y mostrar Victoria y Game Over.
7. Cerrar mostrando un modelo en Blender con su `Idle-loop` y su conteo de triángulos.

### F7.5 Cierre

- [ ] README breve (cómo ejecutar, controles, teclas de depuración).
- [ ] Commit final y etiqueta `parcial2-entrega`.
- [ ] *(Opcional)* exportar un ejecutable de Windows como respaldo para la demo (requiere las plantillas de exportación de Godot).

**Definición de terminado (global):** los cinco criterios de la rúbrica están cubiertos y verificados (§1.1), los requisitos de la Tarea 1 siguen funcionando (§1.2), la escena cumple la puerta de rendimiento (F4.4) y `docs/SUSTENTACION.md` está completo.

---

## Apéndice A — Riesgos y mitigaciones

| Riesgo | Señal | Mitigación |
|---|---|---|
| El MCP de Blender no conecta | Herramientas con error o timeout | Diagnosticar según F0.1; contingencia `blender -b … -P script.py` solo con aprobación del estudiante |
| Blender se congela con un script largo | No responde | Dividir en pasos pequeños; guardar antes; hacer los Boolean sobre mallas ligeras y subdividir después |
| Triángulos por encima del presupuesto | `contar_triangulos` | Bajar niveles de SubD, Decimate planar, simplificar bisel; niveles de viewport = render |
| Las animaciones no aparecen en Godot | AnimationPlayer vacío | Revisar el modo de animación del exportador, que las Actions estén en el Armature/NLA y los nombres; usar Advanced Import |
| Modelo orientado al revés o a otra escala | Prueba de humo | Corregir en Blender (rotar + aplicar), no con parches en Godot |
| Tween y AnimationPlayer se pelean | El modelo "salta" | Tweens solo en `Visual`; Blender nunca anima el raíz |
| Error al usar nodos liberados tras un `await` | "previously freed" | `is_inside_tree()` / `is_instance_valid()` tras cada `await`; cancelar Tweens al reiniciar |
| Escala cero en cuerpos físicos | Matriz singular en consola | Desactivar colisión antes, animar `Visual`, usar `0.001` en vez de `0` |
| OneDrive bloquea `.godot/` o los `.blend` | Archivos en uso, importaciones corruptas | Proyecto fuera de OneDrive o excluir `.godot/`, `*.blend1`, `*.blend2` |
| FPS bajos aunque haya GPU dedicada | Godot eligió la integrada | Forzar GPU de alto rendimiento (F4.4) |
| El hit-stop deja el juego pausado | Congelado tras varios impactos | Contador `_congelaciones` y `process_mode = Always` en `GameFeel` |
| Pulsaciones de la intro se ejecutan después | Disparo "fantasma" | No encolar input; consultar el estado cada frame |

## Apéndice B — Comandos útiles (PowerShell)

Ajusta la ruta del ejecutable si `godot` no está en el PATH y confirma las opciones con `godot --help`.

```powershell
godot --version
godot --headless --path . --import              # reimporta recursos nuevos (.glb) sin abrir el editor
godot --path .                                  # ejecuta el juego
godot --headless --path . --quit-after 300      # prueba de humo: corre 300 iteraciones y sale (revisar consola)
git tag respaldo-primitivas
git switch -c parcial2-modelos
```

## Apéndice C — Plantilla de informe de fase

```text
FASE: <n> — <nombre>
Completado: <tareas y entregables cerrados>
Evidencias: <capturas, tabla de triángulos, salida de consola, FPS>
Desviaciones y decisiones: <resumen; detalle en docs/bitacora.md>
Riesgos abiertos: <lista>
Necesito del estudiante: <aprobación / decisión / dato>
```

## Apéndice D — Prompt de arranque (para pegar en Antigravity)

```text
Lee PLAN_IMPLEMENTACION.md completo. Ejecuta únicamente la Fase 0 y detente con el
informe de fase. No avances a la Fase 1 hasta que yo lo apruebe. Usa el MCP de Blender
para todo el modelado y la animación; en Godot usa su MCP si está disponible.
```
