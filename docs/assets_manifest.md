# Manifiesto de Assets 3D (.glb) — Space Invaders 3D
**Modelos High Poly exportados de Blender e integrados en Godot 4.7**

---

## 1. Naves del Jugador (`res://assets/models/jugador/`)

| Modelo | Archivo | Rango de Niveles | Acento Neón | Triángulos aprox. | Animaciones |
|---|---|---|---|---|---|
| **Nave Mk I «Vanguard»** | `nave_mk1.glb` | Niveles 1 – 2 | Cian (`#00E5FF`) | ~32,000 | `Idle-loop`, `Spawn` |
| **Nave Mk II «Striker»** | `nave_mk2.glb` | Niveles 3 – 4 | Azul Eléctrico (`#3D7BFF`) | ~44,000 | `Idle-loop`, `Spawn` |
| **Nave Mk III «Phantom»** | `nave_mk3.glb` | Niveles 5 – 6 | Menta Esmeralda (`#00FFB3`) | ~56,000 | `Idle-loop`, `Spawn` |
| **Nave Mk IV «Titan»** | `nave_mk4.glb` | Niveles 7 – 8 | Ámbar Solar (`#FFB300`) | ~68,000 | `Idle-loop`, `Spawn` |
| **Nave Mk V «Apex»** | `nave_mk5.glb` | Niveles 9 – 10 | Oro Halo (`#FFF1B0`) | ~82,000 | `Idle-loop`, `Spawn` |
| **Rover Terrestre 1** | `rover_1.glb` | Niveles 11 – 12 | Verde Neón | ~28,000 | `Idle-loop` |
| **Rover Terrestre 2** | `rover_2.glb` | Niveles 13 – 14 | Naranja Fuego | ~34,000 | `Idle-loop` |
| **Rover Esférico** | `rover_round.glb` | Niveles 15+ | Violeta Cibernético | ~25,000 | `Idle-loop` |

---

## 2. Invasores Alienígenas (`res://assets/models/enemigos/`)

| Enemigo | Archivo | Posición en Formación | Puntos | Color de Emisión | Triángulos aprox. |
|---|---|---|---|---|---|
| **Enemigo A «Calamar»** | `enemigo_a.glb` | Fila 1 (Superior) | 30 | Magenta / Violeta (`#FF1AD9`) | ~18,500 |
| **Enemigo B «Cangrejo»** | `enemigo_b.glb` | Filas 2 – 3 (Medias) | 20 | Cian / Turquesa (`#00F2FF`) | ~22,000 |
| **Enemigo C «Behemoth»** | `enemigo_c.glb` | Filas 4 – 5 (Bajas) | 10 | Oro / Amarillo (`#FFD700`) | ~24,500 |

---

## 3. Ovni Bonus (`res://assets/models/ovni/`)

| Asset | Archivo | Comportamiento | Puntos | Color de Emisión | Triángulos aprox. |
|---|---|---|---|---|---|
| **Ovni Nodriza** | `ovni_bonus.glb` | Vuelo transversal superior | 100 / 200 / 300 | Amarillo Neón (`#FFE600`) | ~35,000 |

---

## 4. Escudos y Entorno

| Elemento | Archivo | Estado | Propósito |
|---|---|---|---|
| **Bloque Sano** | `escudo_bloque_sano.glb` | Íntegro (2 HP) | Bloque inicial del búnker con borde biselado |
| **Bloque Agrietado** | `escudo_bloque_agrietado.glb` | Dañado (1 HP) | Variante con fracturas y pérdida de integridad |
| **Bala Jugador** | `bala_jugador.glb` | Proyectil | Cápsula alargada con núcleo emisivo cian |
| **Bala Enemiga** | `bala_enemiga.glb` | Proyectil | Cápsula con núcleo emisivo carmesí |
| **Planeta de Fondo** | `planeta_fondo.glb` | Fondo espacial | Esfera con atmósfera y relieve en rotación continua |
