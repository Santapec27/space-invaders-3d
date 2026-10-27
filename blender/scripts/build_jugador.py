"""
blender/scripts/build_jugador.py - Construcción, texturizado, rigging,
animación y exportación modular de la nave del jugador (Mk I a Mk V).
Proyecto: Space Invaders 3D (Parcial 2)
"""

import bpy
import bmesh
import math
import mathutils
import os
import sys
import shutil

directorio_scripts = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender\blender\scripts"
if directorio_scripts not in sys.path:
    sys.path.append(directorio_scripts)

import utils_blender

CONFIG_NIVELES = {
    1: {
        'nombre': "Vanguard",
        'sufijo': "mk1",
        'color_neon': (0.0, 0.90, 1.0, 1.0),      # Cian (#00E5FF)
        'presupuesto_min': 30000,
        'presupuesto_max': 38000,
        'canones': ['C'],
        'alas_tipo': 'delta_compacta',
        'toberas_tipo': 'doble_estandar',
    },
    2: {
        'nombre': "Striker",
        'sufijo': "mk2",
        'color_neon': (0.14, 0.38, 1.0, 1.0),     # Azul eléctrico (#2563EB)
        'presupuesto_min': 38000,
        'presupuesto_max': 48000,
        'canones': ['C', 'L', 'R'],
        'alas_tipo': 'delta_escalonada',
        'toberas_tipo': 'doble_potenciada',
    },
    3: {
        'nombre': "Phantom",
        'sufijo': "mk3",
        'color_neon': (0.0, 0.96, 0.62, 1.0),      # Menta (#00F5A0)
        'presupuesto_min': 48000,
        'presupuesto_max': 58000,
        'canones': ['C', 'L', 'R'],
        'alas_tipo': 'flecha_invertida',
        'toberas_tipo': 'pods_laterales',
    },
    4: {
        'nombre': "Titan",
        'sufijo': "mk4",
        'color_neon': (0.96, 0.62, 0.04, 1.0),     # Ámbar (#F59E0B)
        'presupuesto_min': 58000,
        'presupuesto_max': 68000,
        'canones': ['C', 'L', 'R', 'heavy_dorsal'],
        'alas_tipo': 'blindada_pesada',
        'toberas_tipo': 'cuadruple_cluster',
    },
    5: {
        'nombre': "Apex",
        'sufijo': "mk5",
        'color_neon': (1.0, 0.88, 0.35, 1.0),      # Oro-Blanco (#FCD34D)
        'presupuesto_min': 68000,
        'presupuesto_max': 80000,
        'canones': ['C', 'L', 'R', 'hyper_laser'],
        'alas_tipo': 'cuchillas_flotantes',
        'toberas_tipo': 'quintuple_hiperdrive',
    }
}

def configurar_materiales(nivel):
    """Crea los 5 materiales Principled BSDF para el nivel correspondiente."""
    cfg = CONFIG_NIVELES[nivel]
    suf = cfg['sufijo']
    col_neon = cfg['color_neon']

    # 1. Casco base metálico oscuro (#182030)
    mat_casco = utils_blender.crear_material(
        f"m_jugador_casco_{suf}",
        base_color=(0.012, 0.016, 0.026, 1.0),
        metallic=0.90,
        roughness=0.24
    )

    # 2. Blindaje secundario grafito / gunmetal
    mat_blindaje = utils_blender.crear_material(
        f"m_jugador_blindaje_{suf}",
        base_color=(0.008, 0.011, 0.018, 1.0),
        metallic=0.92,
        roughness=0.32
    )

    # 3. Cristal de la cabina (reflectante oscuro)
    mat_cabina = utils_blender.crear_material(
        f"m_jugador_cabina_{suf}",
        base_color=(0.010, 0.025, 0.040, 1.0),
        metallic=0.25,
        roughness=0.08
    )

    # 4. Interior de toberas / maquinaria
    mat_motor = utils_blender.crear_material(
        f"m_jugador_motor_{suf}",
        base_color=(0.006, 0.008, 0.012, 1.0),
        metallic=0.95,
        roughness=0.20
    )

    # 5. Neón de acento evolutivo por nivel (Emisión 3.5)
    mat_neon = utils_blender.crear_material(
        f"m_jugador_neon_{suf}",
        base_color=col_neon,
        metallic=0.10,
        roughness=0.18,
        emission_color=col_neon,
        emission_strength=3.5
    )

    return {
        'casco': mat_casco,
        'blindaje': mat_blindaje,
        'cabina': mat_cabina,
        'motor': mat_motor,
        'neon': mat_neon
    }

def transferir_geom(bm_src, bm_dst, mat_index=0):
    """Copia la geometría de bm_src a bm_dst y retorna los vértices creados."""
    v_map = {v: bm_dst.verts.new(v.co) for v in bm_src.verts}
    for f in bm_src.faces:
        try:
            nf = bm_dst.faces.new([v_map[v] for v in f.verts])
            nf.material_index = mat_index
        except:
            pass
    return list(v_map.values())

def construir_fuselaje_base(bm, nivel):
    """
    Construye el fuselaje principal común de la nave con acabado high-poly:
    morro chiseled (48 segs), quilla ventral, baldosas térmicas,
    cabina facetada (32 segs) con roll-cage y habitáculo, espina dorsal blindada,
    radiadores ranurados y tomas de aire con álabes de compresor biselados.
    """
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    verts_fuselaje = []

    # Densidad poligonal adaptativa según nivel
    segs_fuse = 36 + (nivel * 2)  # 38 a 46 segmentos radiales
    segs_bevel = 2 if nivel <= 2 else 3

    # 1. Cono de fuselaje principal
    bm_fuse = bmesh.new()
    bmesh.ops.create_cone(
        bm_fuse,
        cap_ends=True,
        cap_tris=False,
        segments=segs_fuse,
        radius1=0.18,
        radius2=0.026, # morro chiseled
        depth=0.86
    )
    bmesh.ops.transform(bm_fuse, matrix=rot_x90, verts=bm_fuse.verts)
    scale_fuse = mathutils.Matrix.Diagonal((1.30, 1.0, 0.58, 1.0))
    trans_fuse = mathutils.Matrix.Translation((0, 0.05, 0.02))
    bmesh.ops.transform(bm_fuse, matrix=trans_fuse @ scale_fuse, verts=bm_fuse.verts)
    bmesh.ops.bevel(bm_fuse, geom=bm_fuse.edges[:], offset=0.008, segments=segs_bevel)
    verts_fuselaje.extend(transferir_geom(bm_fuse, bm, mat_index=0))
    bm_fuse.free()

    # 2. Quilla blindada ventral y placas compuestas inferiores
    bm_quilla = bmesh.new()
    bmesh.ops.create_cube(bm_quilla, size=1.0)
    sc_q = mathutils.Matrix.Diagonal((0.16, 0.68, 0.045, 1.0))
    tr_q = mathutils.Matrix.Translation((0, 0.02, -0.055))
    bmesh.ops.transform(bm_quilla, matrix=tr_q @ sc_q, verts=bm_quilla.verts)
    bmesh.ops.bevel(bm_quilla, geom=bm_quilla.edges[:], offset=0.006, segments=segs_bevel)
    verts_fuselaje.extend(transferir_geom(bm_quilla, bm, mat_index=1))
    bm_quilla.free()

    # Baldosas térmicas en la panza (matriz 2 x N)
    num_tiles = 6 + (nivel * 2)
    for bx in [-0.07, 0.07]:
        for bz_i in range(num_tiles):
            y_tile = -0.25 + (bz_i * (0.42 / float(num_tiles)))
            bm_tile = bmesh.new()
            bmesh.ops.create_cube(bm_tile, size=1.0)
            sc_t = mathutils.Matrix.Diagonal((0.055, 0.030, 0.012, 1.0))
            tr_t = mathutils.Matrix.Translation((bx, y_tile, -0.078))
            bmesh.ops.transform(bm_tile, matrix=tr_t @ sc_t, verts=bm_tile.verts)
            bmesh.ops.bevel(bm_tile, geom=bm_tile.edges[:], offset=0.003, segments=2)
            verts_fuselaje.extend(transferir_geom(bm_tile, bm, mat_index=1))
            bm_tile.free()

    # 3. Cabina acristalada facetada (32 lados)
    bm_cab = bmesh.new()
    bmesh.ops.create_cone(
        bm_cab,
        cap_ends=True,
        cap_tris=False,
        segments=32,
        radius1=0.095,
        radius2=0.024,
        depth=0.42
    )
    bmesh.ops.transform(bm_cab, matrix=rot_x90, verts=bm_cab.verts)
    scale_cab = mathutils.Matrix.Diagonal((0.96, 1.0, 0.62, 1.0))
    trans_cab = mathutils.Matrix.Translation((0, 0.10, 0.090))
    bmesh.ops.transform(bm_cab, matrix=trans_cab @ scale_cab, verts=bm_cab.verts)
    bmesh.ops.bevel(bm_cab, geom=bm_cab.edges[:], offset=0.006, segments=segs_bevel)
    verts_fuselaje.extend(transferir_geom(bm_cab, bm, mat_index=2))
    bm_cab.free()

    # Roll-cage y costillas de soporte de cabina (4 costillas metálicas con bevel)
    for y_rib in [0.01, 0.08, 0.15, 0.22]:
        bm_rib = bmesh.new()
        bmesh.ops.create_cone(
            bm_rib,
            cap_ends=False,
            cap_tris=False,
            segments=28,
            radius1=0.092 - ((y_rib - 0.01) * 0.14),
            radius2=0.092 - ((y_rib - 0.01) * 0.14),
            depth=0.022
        )
        bmesh.ops.transform(bm_rib, matrix=rot_x90, verts=bm_rib.verts)
        scale_rib = mathutils.Matrix.Diagonal((1.02, 1.0, 0.66, 1.0))
        trans_rib = mathutils.Matrix.Translation((0, y_rib, 0.090))
        bmesh.ops.transform(bm_rib, matrix=trans_rib @ scale_rib, verts=bm_rib.verts)
        bmesh.ops.bevel(bm_rib, geom=bm_rib.edges[:], offset=0.002, segments=2)
        verts_fuselaje.extend(transferir_geom(bm_rib, bm, mat_index=1))
        bm_rib.free()

    # Consola interior y HUD holográfico visible bajo el cristal
    bm_hud = bmesh.new()
    bmesh.ops.create_cube(bm_hud, size=1.0)
    sc_hud = mathutils.Matrix.Diagonal((0.08, 0.08, 0.04, 1.0))
    tr_hud = mathutils.Matrix.Translation((0, 0.16, 0.075))
    bmesh.ops.transform(bm_hud, matrix=tr_hud @ sc_hud, verts=bm_hud.verts)
    bmesh.ops.bevel(bm_hud, geom=bm_hud.edges[:], offset=0.003, segments=2)
    verts_fuselaje.extend(transferir_geom(bm_hud, bm, mat_index=4)) # emite luz holográfica
    bm_hud.free()

    # 4. Disipadores térmicos dorsales y cresta blindada
    num_aletas = 16 + (nivel * 4)  # 20 a 36 aletas dorsales
    for i in range(num_aletas):
        y_pos = -0.28 + (i * (0.36 / float(num_aletas)))
        bm_fin = bmesh.new()
        bmesh.ops.create_cube(bm_fin, size=1.0)
        sc = mathutils.Matrix.Diagonal((0.14 - (i * 0.0025), 0.010, 0.030, 1.0))
        tr = mathutils.Matrix.Translation((0, y_pos, 0.068))
        bmesh.ops.transform(bm_fin, matrix=tr @ sc, verts=bm_fin.verts)
        bmesh.ops.bevel(bm_fin, geom=bm_fin.edges[:], offset=0.002, segments=2)
        verts_fuselaje.extend(transferir_geom(bm_fin, bm, mat_index=1))
        bm_fin.free()

    # 5. Tomas de aire laterales con álabe de compresor biselado
    for sx in [-1, 1]:
        bm_toma = bmesh.new()
        bmesh.ops.create_cube(bm_toma, size=1.0)
        scale_toma = mathutils.Matrix.Diagonal((0.062, 0.38, 0.072, 1.0))
        trans_toma = mathutils.Matrix.Translation((sx * 0.160, -0.06, 0.015))
        rot_toma = mathutils.Euler((math.radians(5), 0, math.radians(sx * -6))).to_matrix().to_4x4()
        bmesh.ops.transform(bm_toma, matrix=trans_toma @ rot_toma @ scale_toma, verts=bm_toma.verts)
        bmesh.ops.bevel(bm_toma, geom=bm_toma.edges[:], offset=0.007, segments=segs_bevel)
        verts_fuselaje.extend(transferir_geom(bm_toma, bm, mat_index=1))
        bm_toma.free()

        # Turbina interior con álabes biselados
        num_alabes = 14 + (nivel * 3)
        for a_idx in range(num_alabes):
            rad_a = (a_idx / float(num_alabes)) * math.pi
            bm_al = bmesh.new()
            bmesh.ops.create_cube(bm_al, size=1.0)
            sc_al = mathutils.Matrix.Diagonal((0.006, 0.07, 0.050, 1.0))
            rot_al = mathutils.Euler((0, rad_a, 0)).to_matrix().to_4x4()
            tr_al = mathutils.Matrix.Translation((sx * 0.160, 0.07, 0.015))
            bmesh.ops.transform(bm_al, matrix=tr_al @ rot_al @ sc_al, verts=bm_al.verts)
            bmesh.ops.bevel(bm_al, geom=bm_al.edges[:], offset=0.0015, segments=2)
            verts_fuselaje.extend(transferir_geom(bm_al, bm, mat_index=3))
            bm_al.free()

        # Riel de luz neón sobre la toma
        bm_n = bmesh.new()
        bmesh.ops.create_cube(bm_n, size=1.0)
        scale_n = mathutils.Matrix.Diagonal((0.016, 0.32, 0.014, 1.0))
        trans_n = mathutils.Matrix.Translation((sx * 0.190, -0.06, 0.024))
        bmesh.ops.transform(bm_n, matrix=trans_n @ rot_toma @ scale_n, verts=bm_n.verts)
        bmesh.ops.bevel(bm_n, geom=bm_n.edges[:], offset=0.002, segments=2)
        verts_fuselaje.extend(transferir_geom(bm_n, bm, mat_index=4))
        bm_n.free()

    return verts_fuselaje

def construir_alas_nivel(bm, nivel):
    """
    Construye las alas modulares según el nivel del jugador con alta densidad poligonal.
    """
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    grupos_alas = {'wing_L': [], 'wing_R': []}
    segs_bevel = 3

    cfg = CONFIG_NIVELES[nivel]
    tipo = cfg['alas_tipo']

    for sx, lado in [(-1, 'wing_L'), (1, 'wing_R')]:
        if tipo == 'delta_compacta':
            # Mk I: Placas de ala delta con paneles segmentados y slats
            for p_idx in range(3):
                bm_w = bmesh.new()
                bmesh.ops.create_cube(bm_w, size=1.0)
                scale_w = mathutils.Matrix.Diagonal((0.15, 0.40 - (p_idx * 0.06), 0.030, 1.0))
                rot_w = mathutils.Euler((0, math.radians(sx * 4.0), math.radians(sx * -18.0))).to_matrix().to_4x4()
                trans_w = mathutils.Matrix.Translation((sx * (0.22 + (p_idx * 0.12)), -0.10 - (p_idx * 0.04), 0.01))
                bmesh.ops.transform(bm_w, matrix=trans_w @ rot_w @ scale_w, verts=bm_w.verts)
                bmesh.ops.bevel(bm_w, geom=bm_w.edges[:], offset=0.006, segments=2)
                grupos_alas[lado].extend(transferir_geom(bm_w, bm, mat_index=0 if p_idx % 2 == 0 else 1))
                bm_w.free()

            # Baldosas de armadura superior en el ala (3 baldosas por ala)
            for t_i in range(3):
                bm_t = bmesh.new()
                bmesh.ops.create_cube(bm_t, size=1.0)
                sc_t = mathutils.Matrix.Diagonal((0.08, 0.05, 0.012, 1.0))
                rot_t = mathutils.Euler((0, 0, math.radians(sx * -18.0))).to_matrix().to_4x4()
                tr_t = mathutils.Matrix.Translation((sx * (0.28 + (t_i * 0.07)), -0.06 - (t_i * 0.05), 0.026))
                bmesh.ops.transform(bm_t, matrix=tr_t @ rot_t @ sc_t, verts=bm_t.verts)
                bmesh.ops.bevel(bm_t, geom=bm_t.edges[:], offset=0.002, segments=2)
                grupos_alas[lado].extend(transferir_geom(bm_t, bm, mat_index=1))
                bm_t.free()

            # Alerones de control posteriores (3 segmentos biselados)
            for a_i in range(3):
                bm_al = bmesh.new()
                bmesh.ops.create_cube(bm_al, size=1.0)
                scale_al = mathutils.Matrix.Diagonal((0.075, 0.075, 0.018, 1.0))
                trans_al = mathutils.Matrix.Translation((sx * (0.25 + (a_i * 0.08)), -0.28, 0.01))
                rot_al = mathutils.Euler((math.radians(sx * 4.0), 0, math.radians(sx * -18.0))).to_matrix().to_4x4()
                bmesh.ops.transform(bm_al, matrix=trans_al @ rot_al @ scale_al, verts=bm_al.verts)
                bmesh.ops.bevel(bm_al, geom=bm_al.edges[:], offset=0.003, segments=2)
                grupos_alas[lado].extend(transferir_geom(bm_al, bm, mat_index=1))
                bm_al.free()

            # Neón borde de ataque
            bm_n = bmesh.new()
            bmesh.ops.create_cube(bm_n, size=1.0)
            scale_n = mathutils.Matrix.Diagonal((0.48, 0.018, 0.018, 1.0))
            rot_n = mathutils.Euler((0, 0, math.radians(sx * -18.0))).to_matrix().to_4x4()
            trans_n = mathutils.Matrix.Translation((sx * 0.38, 0.05, 0.01))
            bmesh.ops.transform(bm_n, matrix=trans_n @ rot_n @ scale_n, verts=bm_n.verts)
            bmesh.ops.bevel(bm_n, geom=bm_n.edges[:], offset=0.003, segments=2)
            grupos_alas[lado].extend(transferir_geom(bm_n, bm, mat_index=4))
            bm_n.free()

        elif tipo == 'delta_escalonada':
            # Mk II: 5 secciones escalonadas con canards y winglets dobles
            for w_sec in range(5):
                offset_x = 0.22 + (w_sec * 0.11)
                scale_f = 1.0 - (w_sec * 0.08)
                bm_w = bmesh.new()
                bmesh.ops.create_cube(bm_w, size=1.0)
                scale_w = mathutils.Matrix.Diagonal((0.13, 0.42 * scale_f, 0.032, 1.0))
                rot_w = mathutils.Euler((0, math.radians(sx * 3.0), math.radians(sx * -22.0))).to_matrix().to_4x4()
                trans_w = mathutils.Matrix.Translation((sx * offset_x, -0.12 - (w_sec * 0.045), 0.01))
                bmesh.ops.transform(bm_w, matrix=trans_w @ rot_w @ scale_w, verts=bm_w.verts)
                bmesh.ops.bevel(bm_w, geom=bm_w.edges[:], offset=0.005, segments=segs_bevel)
                grupos_alas[lado].extend(transferir_geom(bm_w, bm, mat_index=0 if w_sec % 2 == 0 else 1))
                bm_w.free()

            # Canards delanteros biselados
            bm_can = bmesh.new()
            bmesh.ops.create_cube(bm_can, size=1.0)
            sc_can = mathutils.Matrix.Diagonal((0.12, 0.14, 0.020, 1.0))
            rot_can = mathutils.Euler((0, 0, math.radians(sx * -30.0))).to_matrix().to_4x4()
            tr_can = mathutils.Matrix.Translation((sx * 0.24, 0.22, 0.03))
            bmesh.ops.transform(bm_can, matrix=tr_can @ rot_can @ sc_can, verts=bm_can.verts)
            bmesh.ops.bevel(bm_can, geom=bm_can.edges[:], offset=0.003, segments=segs_bevel)
            grupos_alas[lado].extend(transferir_geom(bm_can, bm, mat_index=1))
            bm_can.free()

            # Doble aleta vertical (Twin Winglets)
            for f_i in [0, 1]:
                bm_fin = bmesh.new()
                bmesh.ops.create_cube(bm_fin, size=1.0)
                scale_fin = mathutils.Matrix.Diagonal((0.024, 0.20, 0.16, 1.0))
                trans_fin = mathutils.Matrix.Translation((sx * (0.58 + (f_i * 0.07)), -0.22 - (f_i * 0.05), 0.08))
                rot_fin = mathutils.Euler((math.radians(10), math.radians(sx * 8), 0)).to_matrix().to_4x4()
                bmesh.ops.transform(bm_fin, matrix=trans_fin @ rot_fin @ scale_fin, verts=bm_fin.verts)
                bmesh.ops.bevel(bm_fin, geom=bm_fin.edges[:], offset=0.004, segments=segs_bevel)
                grupos_alas[lado].extend(transferir_geom(bm_fin, bm, mat_index=4))
                bm_fin.free()

        elif tipo == 'flecha_invertida':
            # Mk III: Alas en flecha invertida (Forward-swept) con cuchillas menta
            for w_sec in range(5):
                offset_x = 0.22 + (w_sec * 0.11)
                bm_w = bmesh.new()
                bmesh.ops.create_cube(bm_w, size=1.0)
                scale_w = mathutils.Matrix.Diagonal((0.13, 0.38, 0.032, 1.0))
                rot_w = mathutils.Euler((0, math.radians(sx * -4.0), math.radians(sx * 26.0))).to_matrix().to_4x4()
                trans_w = mathutils.Matrix.Translation((sx * offset_x, 0.04 - (w_sec * 0.025), 0.01))
                bmesh.ops.transform(bm_w, matrix=trans_w @ rot_w @ scale_w, verts=bm_w.verts)
                bmesh.ops.bevel(bm_w, geom=bm_w.edges[:], offset=0.005, segments=segs_bevel)
                grupos_alas[lado].extend(transferir_geom(bm_w, bm, mat_index=0 if w_sec % 2 == 0 else 1))
                bm_w.free()

            # Doble cuchilla de energía neón menta en la punta
            for b_i in [0, 1]:
                bm_blade = bmesh.new()
                bmesh.ops.create_cone(
                    bm_blade,
                    cap_ends=True,
                    cap_tris=False,
                    segments=24,
                    radius1=0.028,
                    radius2=0.003,
                    depth=0.34
                )
                bmesh.ops.transform(bm_blade, matrix=rot_x90, verts=bm_blade.verts)
                trans_blade = mathutils.Matrix.Translation((sx * (0.62 + (b_i * 0.06)), 0.16 + (b_i * 0.09), 0.01))
                bmesh.ops.transform(bm_blade, matrix=trans_blade, verts=bm_blade.verts)
                bmesh.ops.bevel(bm_blade, geom=bm_blade.edges[:], offset=0.002, segments=2)
                grupos_alas[lado].extend(transferir_geom(bm_blade, bm, mat_index=4))
                bm_blade.free()

        elif tipo == 'blindada_pesada':
            # Mk IV: Blindaje compuesto multicapa con 6 placas gruesas y estabilizadores
            for i in range(6):
                bm_placa = bmesh.new()
                bmesh.ops.create_cube(bm_placa, size=1.0)
                scale_p = mathutils.Matrix.Diagonal((0.13, 0.40 - (i * 0.026), 0.040, 1.0))
                rot_p = mathutils.Euler((0, 0, math.radians(sx * -16.0))).to_matrix().to_4x4()
                trans_p = mathutils.Matrix.Translation((sx * (0.22 + (i * 0.095)), -0.10 - (i * 0.035), 0.018))
                bmesh.ops.transform(bm_placa, matrix=trans_p @ rot_p @ scale_p, verts=bm_placa.verts)
                bmesh.ops.bevel(bm_placa, geom=bm_placa.edges[:], offset=0.005, segments=3)
                grupos_alas[lado].extend(transferir_geom(bm_placa, bm, mat_index=1 if i % 2 == 1 else 0))
                bm_placa.free()

            # Radiadores y placas de refuerzo ámbar
            for r_i in range(3):
                bm_bar = bmesh.new()
                bmesh.ops.create_cube(bm_bar, size=1.0)
                scale_bar = mathutils.Matrix.Diagonal((0.14, 0.026, 0.022, 1.0))
                trans_bar = mathutils.Matrix.Translation((sx * (0.36 + (r_i * 0.12)), -0.18 - (r_i * 0.04), 0.042))
                bmesh.ops.transform(bm_bar, matrix=trans_bar @ scale_bar, verts=bm_bar.verts)
                bmesh.ops.bevel(bm_bar, geom=bm_bar.edges[:], offset=0.003, segments=3)
                grupos_alas[lado].extend(transferir_geom(bm_bar, bm, mat_index=4))
                bm_bar.free()

        elif tipo == 'cuchillas_flotantes':
            # Mk V: Cuchillas flotantes estilizadas y anillos orbitales levitantes
            for c_i in range(4):
                bm_cuchilla = bmesh.new()
                bmesh.ops.create_cone(
                    bm_cuchilla,
                    cap_ends=True,
                    cap_tris=False,
                    segments=24,
                    radius1=0.040,
                    radius2=0.004,
                    depth=0.55 - (c_i * 0.07)
                )
                bmesh.ops.transform(bm_cuchilla, matrix=rot_x90, verts=bm_cuchilla.verts)
                scale_c = mathutils.Matrix.Diagonal((1.65, 1.0, 0.26, 1.0))
                rot_c = mathutils.Euler((0, math.radians(sx * 6), math.radians(sx * -28))).to_matrix().to_4x4()
                trans_c = mathutils.Matrix.Translation((sx * (0.42 + (c_i * 0.10)), 0.06 - (c_i * 0.03), 0.02))
                bmesh.ops.transform(bm_cuchilla, matrix=trans_c @ rot_c @ scale_c, verts=bm_cuchilla.verts)
                bmesh.ops.bevel(bm_cuchilla, geom=bm_cuchilla.edges[:], offset=0.004, segments=2)
                grupos_alas[lado].extend(transferir_geom(bm_cuchilla, bm, mat_index=0 if c_i % 2 == 0 else 1))
                bm_cuchilla.free()

            # Anillos orbitales levitantes dobles (26 segmentos)
            for h_i in [0, 1]:
                bm_halo = bmesh.new()
                bmesh.ops.create_cone(
                    bm_halo,
                    cap_ends=False,
                    cap_tris=False,
                    segments=26,
                    radius1=0.080 + (h_i * 0.025),
                    radius2=0.080 + (h_i * 0.025),
                    depth=0.018
                )
                bmesh.ops.transform(bm_halo, matrix=rot_x90, verts=bm_halo.verts)
                trans_halo = mathutils.Matrix.Translation((sx * 0.34, -0.06 - (h_i * 0.04), 0.025))
                bmesh.ops.transform(bm_halo, matrix=trans_halo, verts=bm_halo.verts)
                bmesh.ops.bevel(bm_halo, geom=bm_halo.edges[:], offset=0.002, segments=2)
                grupos_alas[lado].extend(transferir_geom(bm_halo, bm, mat_index=4))
                bm_halo.free()

    return grupos_alas

def construir_canones_nivel(bm, nivel):
    """
    Construye los cañones con cañón base (32-36 segs), chaqueta de refrigeración
    ranurada, bobinas de aceleración y boca de fuego compensada.
    """
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    grupos_canones = {'canon_C': [], 'canon_L': [], 'canon_R': []}
    segs_bevel = 3
    cfg = CONFIG_NIVELES[nivel]
    lista_c = cfg['canones']

    if 'C' in lista_c:
        # Cañón central railgun pesado
        bm_c = bmesh.new()
        bmesh.ops.create_cone(
            bm_c,
            cap_ends=True,
            cap_tris=False,
            segments=36,
            radius1=0.042,
            radius2=0.032,
            depth=0.40
        )
        bmesh.ops.transform(bm_c, matrix=rot_x90, verts=bm_c.verts)
        trans_c = mathutils.Matrix.Translation((0, 0.44, -0.02))
        bmesh.ops.transform(bm_c, matrix=trans_c, verts=bm_c.verts)
        bmesh.ops.bevel(bm_c, geom=bm_c.edges[:], offset=0.005, segments=segs_bevel)
        grupos_canones['canon_C'].extend(transferir_geom(bm_c, bm, mat_index=1))
        bm_c.free()

        # Chaqueta de disipación y bobinas de aceleración (8 a 14 anillos)
        num_anillos = 8 + (nivel * 2)
        for i_a in range(num_anillos):
            y_a = 0.30 + (i_a * (0.22 / float(num_anillos)))
            bm_an = bmesh.new()
            bmesh.ops.create_cone(
                bm_an,
                cap_ends=False,
                cap_tris=False,
                segments=28,
                radius1=0.046,
                radius2=0.046,
                depth=0.014
            )
            bmesh.ops.transform(bm_an, matrix=rot_x90, verts=bm_an.verts)
            trans_an = mathutils.Matrix.Translation((0, y_a, -0.02))
            bmesh.ops.transform(bm_an, matrix=trans_an, verts=bm_an.verts)
            bmesh.ops.bevel(bm_an, geom=bm_an.edges[:], offset=0.002, segments=2)
            grupos_canones['canon_C'].extend(transferir_geom(bm_an, bm, mat_index=4))
            bm_an.free()

    if 'L' in lista_c and 'R' in lista_c:
        # Cañones laterales en las alas
        for sx, lado in [(-1, 'canon_L'), (1, 'canon_R')]:
            bm_c = bmesh.new()
            bmesh.ops.create_cone(
                bm_c,
                cap_ends=True,
                cap_tris=False,
                segments=28,
                radius1=0.034,
                radius2=0.025,
                depth=0.36
            )
            bmesh.ops.transform(bm_c, matrix=rot_x90, verts=bm_c.verts)
            trans_c = mathutils.Matrix.Translation((sx * 0.42, 0.20, 0.0))
            bmesh.ops.transform(bm_c, matrix=trans_c, verts=bm_c.verts)
            bmesh.ops.bevel(bm_c, geom=bm_c.edges[:], offset=0.005, segments=segs_bevel)
            grupos_canones[lado].extend(transferir_geom(bm_c, bm, mat_index=1))
            bm_c.free()

            # Muzzle neón y corona
            bm_m = bmesh.new()
            bmesh.ops.create_cone(
                bm_m,
                cap_ends=True,
                cap_tris=False,
                segments=24,
                radius1=0.020,
                radius2=0.020,
                depth=0.050
            )
            bmesh.ops.transform(bm_m, matrix=rot_x90, verts=bm_m.verts)
            trans_m = mathutils.Matrix.Translation((sx * 0.42, 0.36, 0.0))
            bmesh.ops.transform(bm_m, matrix=trans_m, verts=bm_m.verts)
            bmesh.ops.bevel(bm_m, geom=bm_m.edges[:], offset=0.003, segments=2)
            grupos_canones[lado].extend(transferir_geom(bm_m, bm, mat_index=4))
            bm_m.free()

            # Bobinas laterales
            for b_idx in range(4):
                bm_cb = bmesh.new()
                bmesh.ops.create_cone(
                    bm_cb,
                    cap_ends=False,
                    cap_tris=False,
                    segments=24,
                    radius1=0.038,
                    radius2=0.038,
                    depth=0.012
                )
                bmesh.ops.transform(bm_cb, matrix=rot_x90, verts=bm_cb.verts)
                trans_cb = mathutils.Matrix.Translation((sx * 0.42, 0.12 + (b_idx * 0.05), 0.0))
                bmesh.ops.transform(bm_cb, matrix=trans_cb, verts=bm_cb.verts)
                grupos_canones[lado].extend(transferir_geom(bm_cb, bm, mat_index=3))
                bm_cb.free()

    if 'heavy_dorsal' in lista_c:
        # Mk IV: Cañón dorsal pesado de titanio
        bm_hd = bmesh.new()
        bmesh.ops.create_cone(
            bm_hd,
            cap_ends=True,
            cap_tris=False,
            segments=36,
            radius1=0.052,
            radius2=0.040,
            depth=0.48
        )
        bmesh.ops.transform(bm_hd, matrix=rot_x90, verts=bm_hd.verts)
        trans_hd = mathutils.Matrix.Translation((0, 0.28, 0.10))
        bmesh.ops.transform(bm_hd, matrix=trans_hd, verts=bm_hd.verts)
        bmesh.ops.bevel(bm_hd, geom=bm_hd.edges[:], offset=0.005, segments=3)
        grupos_canones['canon_C'].extend(transferir_geom(bm_hd, bm, mat_index=1))
        bm_hd.free()

        # 4 Anillos de refuerzo blindado en el cañón dorsal
        for d_i in range(4):
            bm_cr = bmesh.new()
            bmesh.ops.create_cone(
                bm_cr,
                cap_ends=False,
                cap_tris=False,
                segments=28,
                radius1=0.058,
                radius2=0.058,
                depth=0.022
            )
            bmesh.ops.transform(bm_cr, matrix=rot_x90, verts=bm_cr.verts)
            tr_cr = mathutils.Matrix.Translation((0, 0.16 + (d_i * 0.08), 0.10))
            bmesh.ops.transform(bm_cr, matrix=tr_cr, verts=bm_cr.verts)
            bmesh.ops.bevel(bm_cr, geom=bm_cr.edges[:], offset=0.002, segments=2)
            grupos_canones['canon_C'].extend(transferir_geom(bm_cr, bm, mat_index=4))
            bm_cr.free()

    if 'hyper_laser' in lista_c:
        # Mk V: Núcleo de cristal hiper-láser
        bm_hl = bmesh.new()
        bmesh.ops.create_cone(
            bm_hl,
            cap_ends=True,
            cap_tris=False,
            segments=36,
            radius1=0.048,
            radius2=0.012,
            depth=0.52
        )
        bmesh.ops.transform(bm_hl, matrix=rot_x90, verts=bm_hl.verts)
        trans_hl = mathutils.Matrix.Translation((0, 0.32, 0.08))
        bmesh.ops.transform(bm_hl, matrix=trans_hl, verts=bm_hl.verts)
        bmesh.ops.bevel(bm_hl, geom=bm_hl.edges[:], offset=0.005, segments=segs_bevel)
        grupos_canones['canon_C'].extend(transferir_geom(bm_hl, bm, mat_index=4))
        bm_hl.free()

    return grupos_canones

def construir_tobera_completa(bm, pos_x, pos_y, pos_z, r1=0.058, r2=0.075, depth=0.18, nivel=1):
    """
    Construye una tobera vectorial de alta fidelidad:
    campana de tobera biselada, pétalos vectoriales orientables,
    estator interior y anillos de confinamiento de plasma.
    """
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    verts_tob = []

    segs_campana = 24 if nivel <= 2 else 28
    segs_bevel = 2

    # 1. Campana principal
    bm_c = bmesh.new()
    bmesh.ops.create_cone(
        bm_c,
        cap_ends=True,
        cap_tris=False,
        segments=segs_campana,
        radius1=r1,
        radius2=r2,
        depth=depth
    )
    bmesh.ops.transform(bm_c, matrix=rot_x90, verts=bm_c.verts)
    trans_c = mathutils.Matrix.Translation((pos_x, pos_y, pos_z))
    bmesh.ops.transform(bm_c, matrix=trans_c, verts=bm_c.verts)
    bmesh.ops.bevel(bm_c, geom=bm_c.edges[:], offset=0.005, segments=segs_bevel)
    verts_tob.extend(transferir_geom(bm_c, bm, mat_index=3))
    bm_c.free()

    # 2. Pétalos vectoriales (12 a 14 pétalos articulados)
    num_petalos = 10 + nivel
    for p_i in range(num_petalos):
        ang = (p_i / float(num_petalos)) * 2.0 * math.pi
        px = pos_x + math.cos(ang) * (r2 * 0.95)
        pz = pos_z + math.sin(ang) * (r2 * 0.95)
        bm_p = bmesh.new()
        bmesh.ops.create_cube(bm_p, size=1.0)
        sc_p = mathutils.Matrix.Diagonal((0.012, 0.040, 0.006, 1.0))
        rot_p = mathutils.Euler((0, 0, ang)).to_matrix().to_4x4()
        tr_p = mathutils.Matrix.Translation((px, pos_y - (depth * 0.45), pz))
        bmesh.ops.transform(bm_p, matrix=tr_p @ rot_p @ sc_p, verts=bm_p.verts)
        bmesh.ops.bevel(bm_p, geom=bm_p.edges[:], offset=0.0015, segments=2)
        verts_tob.extend(transferir_geom(bm_p, bm, mat_index=1))
        bm_p.free()

    # 3. Estator de turbina interior
    num_alabes = 10
    for a_i in range(num_alabes):
        ang_a = (a_i / float(num_alabes)) * math.pi
        bm_al = bmesh.new()
        bmesh.ops.create_cube(bm_al, size=1.0)
        sc_al = mathutils.Matrix.Diagonal((0.004, 0.050, r1 * 1.5, 1.0))
        rot_al = mathutils.Euler((0, ang_a, 0)).to_matrix().to_4x4()
        tr_al = mathutils.Matrix.Translation((pos_x, pos_y + (depth * 0.20), pos_z))
        bmesh.ops.transform(bm_al, matrix=tr_al @ rot_al @ sc_al, verts=bm_al.verts)
        bmesh.ops.bevel(bm_al, geom=bm_al.edges[:], offset=0.001, segments=2)
        verts_tob.extend(transferir_geom(bm_al, bm, mat_index=3))
        bm_al.free()

    # 4. Anillos de plasma neón (20 segmentos)
    for y_ring in [pos_y - (depth * 0.40), pos_y - (depth * 0.55)]:
        bm_ring = bmesh.new()
        bmesh.ops.create_cone(
            bm_ring,
            cap_ends=False,
            cap_tris=False,
            segments=20,
            radius1=r2 * 0.88,
            radius2=r2 * 0.88,
            depth=0.015
        )
        bmesh.ops.transform(bm_ring, matrix=rot_x90, verts=bm_ring.verts)
        tr_ring = mathutils.Matrix.Translation((pos_x, y_ring, pos_z))
        bmesh.ops.transform(bm_ring, matrix=tr_ring, verts=bm_ring.verts)
        bmesh.ops.bevel(bm_ring, geom=bm_ring.edges[:], offset=0.002, segments=2)
        verts_tob.extend(transferir_geom(bm_ring, bm, mat_index=4))
        bm_ring.free()

    return verts_tob

def construir_motores_nivel(bm, nivel):
    """
    Construye las toberas según el nivel con alta resolución poligonal.
    """
    grupos_motor = []
    cfg = CONFIG_NIVELES[nivel]
    tipo = cfg['toberas_tipo']

    if tipo == 'doble_estandar':
        for sx in [-1, 1]:
            verts_t = construir_tobera_completa(bm, sx * 0.09, -0.36, 0.015, r1=0.056, r2=0.072, depth=0.17, nivel=nivel)
            grupos_motor.extend(verts_t)

    elif tipo == 'doble_potenciada':
        for sx in [-1, 1]:
            verts_t = construir_tobera_completa(bm, sx * 0.10, -0.38, 0.015, r1=0.068, r2=0.088, depth=0.21, nivel=nivel)
            grupos_motor.extend(verts_t)

    elif tipo == 'pods_laterales':
        rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
        for sx in [-1, 1]:
            # Carenado de pod lateral con bevel 3
            bm_pod = bmesh.new()
            bmesh.ops.create_cone(
                bm_pod,
                cap_ends=True,
                cap_tris=False,
                segments=32,
                radius1=0.084,
                radius2=0.068,
                depth=0.48
            )
            bmesh.ops.transform(bm_pod, matrix=rot_x90, verts=bm_pod.verts)
            trans_pod = mathutils.Matrix.Translation((sx * 0.25, -0.22, 0.02))
            bmesh.ops.transform(bm_pod, matrix=trans_pod, verts=bm_pod.verts)
            bmesh.ops.bevel(bm_pod, geom=bm_pod.edges[:], offset=0.006, segments=3)
            grupos_motor.extend(transferir_geom(bm_pod, bm, mat_index=1))
            bm_pod.free()

            verts_t = construir_tobera_completa(bm, sx * 0.25, -0.46, 0.02, r1=0.062, r2=0.080, depth=0.17, nivel=nivel)
            grupos_motor.extend(verts_t)

    elif tipo == 'cuadruple_cluster':
        pos_cluster = [
            (-0.11, 0.045), (0.11, 0.045),
            (-0.11, -0.025), (0.11, -0.025)
        ]
        for px, pz in pos_cluster:
            verts_t = construir_tobera_completa(bm, px, -0.38, pz, r1=0.052, r2=0.066, depth=0.18, nivel=nivel)
            grupos_motor.extend(verts_t)

    elif tipo == 'quintuple_hiperdrive':
        pos_quin = [
            (0.0, 0.02),
            (-0.14, 0.02), (0.14, 0.02),
            (0.0, 0.09), (0.0, -0.05)
        ]
        for px, pz in pos_quin:
            verts_t = construir_tobera_completa(bm, px, -0.38, pz, r1=0.048, r2=0.062, depth=0.17, nivel=nivel)
            grupos_motor.extend(verts_t)

    return grupos_motor

def crear_armature_y_rigging(obj_mesh, col, grupos_indices, nivel):
    """
    Crea el Armature con nodo root estacionario en (0,0,0) y huesos móviles.
    """
    cfg = CONFIG_NIVELES[nivel]
    suf = cfg['sufijo']

    arm_data = bpy.data.armatures.new(f"Armature_jugador_{suf}")
    arm_obj = bpy.data.objects.new(f"nave_{suf}", arm_data)
    col.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    # 1. Hueso root ESTACIONARIO en (0,0,0) - REGLA CRÍTICA
    b_root = arm_data.edit_bones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    # 2. Hueso body
    b_body = arm_data.edit_bones.new("body")
    b_body.head = (0, 0, 0.02)
    b_body.tail = (0, 0.20, 0.02)
    b_body.parent = b_root

    # 3. Huesos alas
    b_wl = arm_data.edit_bones.new("wing_L")
    b_wl.head = (-0.18, -0.10, 0.01)
    b_wl.tail = (-0.48, -0.15, 0.01)
    b_wl.parent = b_body

    b_wr = arm_data.edit_bones.new("wing_R")
    b_wr.head = (0.18, -0.10, 0.01)
    b_wr.tail = (0.48, -0.15, 0.01)
    b_wr.parent = b_body

    # 4. Huesos cañones
    b_cc = arm_data.edit_bones.new("canon_C")
    b_cc.head = (0, 0.32, -0.02)
    b_cc.tail = (0, 0.52, -0.02)
    b_cc.parent = b_body

    b_cl = arm_data.edit_bones.new("canon_L")
    b_cl.head = (-0.38, 0.14, 0.0)
    b_cl.tail = (-0.38, 0.32, 0.0)
    b_cl.parent = b_wl

    b_cr = arm_data.edit_bones.new("canon_R")
    b_cr.head = (0.38, 0.14, 0.0)
    b_cr.tail = (0.38, 0.32, 0.0)
    b_cr.parent = b_wr

    # 5. Hueso motor
    b_thr = arm_data.edit_bones.new("thruster")
    b_thr.head = (0, -0.32, 0.01)
    b_thr.tail = (0, -0.45, 0.01)
    b_thr.parent = b_body

    bpy.ops.object.mode_set(mode='OBJECT')

    mod_arm = obj_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod_arm.object = arm_obj
    obj_mesh.parent = arm_obj

    for nombre_hueso, v_indices in grupos_indices.items():
        if v_indices and nombre_hueso in arm_data.bones:
            vg = obj_mesh.vertex_groups.new(name=nombre_hueso)
            vg.add(v_indices, 1.0, 'REPLACE')

    return arm_obj

def crear_animaciones_jugador(arm_obj, nivel):
    """
    Genera las 6 acciones NLA exactas requeridas para la nave del jugador:
    1. Idle-loop (45 frames / 1.5 s)
    2. Fire (8 frames / ~0.26 s)
    3. Hit (8 frames / ~0.26 s)
    4. Spawn (30 frames / 1.0 s)
    5. Victory (60 frames / 2.0 s)
    6. Death (24 frames / 0.8 s)
    REGLA CRÍTICA: NO animar el hueso root.
    """
    arm_obj.animation_data_create()

    def preparar_accion(nombre):
        act = bpy.data.actions.get(nombre)
        if act:
            bpy.data.actions.remove(act)
        return bpy.data.actions.new(name=nombre)

    pose_bones = arm_obj.pose.bones
    for pb in pose_bones:
        pb.rotation_mode = 'XYZ'

    # 1. IDLE-LOOP (45 frames / 1.5 s, 30 FPS - Bucle perfecto)
    act_idle = preparar_accion("Idle-loop")
    arm_obj.animation_data.action = act_idle

    for f in [1, 12, 23, 34, 45]:
        t = (f - 1) / 44.0 * 2.0 * math.pi

        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, 0.0, math.sin(t) * 0.012)
            pb_body.rotation_euler = (math.sin(t) * math.radians(1.2), 0.0, math.cos(t) * math.radians(0.8))
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for lado_s, prefix in [(-1.0, "wing_L"), (1.0, "wing_R")]:
            pb_w = pose_bones.get(prefix)
            if pb_w:
                pb_w.rotation_euler = (0.0, math.sin(t) * math.radians(lado_s * 1.5), 0.0)
                pb_w.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_thr = pose_bones.get("thruster")
        if pb_thr:
            p_scale = 1.0 + math.sin(t) * 0.05
            pb_thr.scale = (p_scale, 1.0, p_scale)
            pb_thr.keyframe_insert(data_path="scale", frame=f)

    track_idle = arm_obj.animation_data.nla_tracks.new()
    track_idle.name = "Idle-loop"
    track_idle.strips.new("Idle-loop", 1, act_idle)

    # 2. FIRE (8 frames / ~0.26 s, 30 FPS)
    act_fire = preparar_accion("Fire")
    arm_obj.animation_data.action = act_fire

    puntos_fire = [
        (1,  0.00,  0.0, 1.0),
        (3, -0.04,  2.0, 1.25),
        (5, -0.02,  0.8, 1.10),
        (8,  0.00,  0.0, 1.0)
    ]

    for f, c_rec, b_pitch, thr_sc in puntos_fire:
        for prefix in ["canon_C", "canon_L", "canon_R"]:
            pb_c = pose_bones.get(prefix)
            if pb_c:
                pb_c.location = (0.0, c_rec, 0.0)
                pb_c.keyframe_insert(data_path="location", frame=f)

        pb_b = pose_bones.get("body")
        if pb_b:
            pb_b.rotation_euler = (math.radians(b_pitch), 0.0, 0.0)
            pb_b.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_thr = pose_bones.get("thruster")
        if pb_thr:
            pb_thr.scale = (thr_sc, 1.0, thr_sc)
            pb_thr.keyframe_insert(data_path="scale", frame=f)

    track_fire = arm_obj.animation_data.nla_tracks.new()
    track_fire.name = "Fire"
    track_fire.strips.new("Fire", 1, act_fire)

    # 3. HIT (8 frames / ~0.26 s, 30 FPS)
    act_hit = preparar_accion("Hit")
    arm_obj.animation_data.action = act_hit

    puntos_hit = [
        (1,  0.00,  0.00,  0.0,  0.0),
        (2, -0.025, 0.015, 3.5, -4.0),
        (4,  0.010,-0.008,-1.8,  2.0),
        (6, -0.004, 0.003, 0.6, -0.8),
        (8,  0.00,  0.00,  0.0,  0.0)
    ]

    for f, yl, zl, pitch, roll in puntos_hit:
        pb_b = pose_bones.get("body")
        if pb_b:
            pb_b.location = (0.0, yl, zl)
            pb_b.rotation_euler = (math.radians(pitch), math.radians(roll), 0.0)
            pb_b.keyframe_insert(data_path="location", frame=f)
            pb_b.keyframe_insert(data_path="rotation_euler", frame=f)

    track_hit = arm_obj.animation_data.nla_tracks.new()
    track_hit.name = "Hit"
    track_hit.strips.new("Hit", 1, act_hit)

    # 4. SPAWN (30 frames / 1.0 s, 30 FPS)
    act_spawn = preparar_accion("Spawn")
    arm_obj.animation_data.action = act_spawn

    puntos_spawn = [
        (1,  35.0, -0.05, 0.2),
        (12, 20.0, -0.02, 0.6),
        (22, -3.0,  0.01, 1.2),
        (30,  0.0,  0.00, 1.0)
    ]

    for f, w_ang, c_pos, thr_sc in puntos_spawn:
        for lado_s, prefix in [(-1.0, "wing_L"), (1.0, "wing_R")]:
            pb_w = pose_bones.get(prefix)
            if pb_w:
                pb_w.rotation_euler = (0.0, math.radians(lado_s * w_ang), 0.0)
                pb_w.keyframe_insert(data_path="rotation_euler", frame=f)

        for prefix in ["canon_C", "canon_L", "canon_R"]:
            pb_c = pose_bones.get(prefix)
            if pb_c:
                pb_c.location = (0.0, c_pos, 0.0)
                pb_c.keyframe_insert(data_path="location", frame=f)

        pb_thr = pose_bones.get("thruster")
        if pb_thr:
            pb_thr.scale = (thr_sc, 1.0, thr_sc)
            pb_thr.keyframe_insert(data_path="scale", frame=f)

    track_spawn = arm_obj.animation_data.nla_tracks.new()
    track_spawn.name = "Spawn"
    track_spawn.strips.new("Spawn", 1, act_spawn)

    # 5. VICTORY (60 frames / 2.0 s, 30 FPS)
    act_vic = preparar_accion("Victory")
    arm_obj.animation_data.action = act_vic

    for f in range(1, 61, 5):
        t = (f - 1) / 59.0
        roll = t * 360.0
        pitch = math.sin(t * math.pi) * 8.0
        boost = 1.0 + math.sin(t * math.pi) * 0.4

        pb_b = pose_bones.get("body")
        if pb_b:
            pb_b.rotation_euler = (math.radians(pitch), math.radians(roll), 0.0)
            pb_b.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_thr = pose_bones.get("thruster")
        if pb_thr:
            pb_thr.scale = (boost, 1.0, boost)
            pb_thr.keyframe_insert(data_path="scale", frame=f)

    track_vic = arm_obj.animation_data.nla_tracks.new()
    track_vic.name = "Victory"
    track_vic.strips.new("Victory", 1, act_vic)

    # 6. DEATH (24 frames / 0.8 s, 30 FPS)
    act_death = preparar_accion("Death")
    arm_obj.animation_data.action = act_death

    puntos_death = [
        (1,   0.0,   0.0,  0.0),
        (6,   4.0,  -8.0, -0.01),
        (14, 12.0, -25.0, -0.04),
        (24, 18.0, -45.0, -0.07)
    ]

    for f, b_pt, w_ang, c_drop in puntos_death:
        pb_b = pose_bones.get("body")
        if pb_b:
            pb_b.rotation_euler = (math.radians(b_pt), 0.0, 0.0)
            pb_b.keyframe_insert(data_path="rotation_euler", frame=f)

        for lado_s, prefix in [(-1.0, "wing_L"), (1.0, "wing_R")]:
            pb_w = pose_bones.get(prefix)
            if pb_w:
                pb_w.rotation_euler = (0.0, math.radians(lado_s * w_ang), math.radians(lado_s * 15.0))
                pb_w.keyframe_insert(data_path="rotation_euler", frame=f)

        for prefix in ["canon_C", "canon_L", "canon_R"]:
            pb_c = pose_bones.get(prefix)
            if pb_c:
                pb_c.location = (0.0, c_drop, c_drop * 0.8)
                pb_c.keyframe_insert(data_path="location", frame=f)

    track_death = arm_obj.animation_data.nla_tracks.new()
    track_death.name = "Death"
    track_death.strips.new("Death", 1, act_death)

    arm_obj.animation_data.action = act_idle
    bpy.context.scene.frame_set(1)

def construir_nave(nivel):
    """
    Construye, riggea, anima y exporta la nave del jugador para el nivel indicado (1 a 5).
    """
    cfg = CONFIG_NIVELES[nivel]
    suf = cfg['sufijo']
    nombre = cfg['nombre']
    nombre_src = f"SRC_jugador_{suf}"
    nombre_export = f"EXPORT_jugador_{suf}"

    print("=" * 60)
    print(f"Iniciando construcción de Nave del Jugador Mk {nivel} («{nombre}»)...")
    print("=" * 60)

    # Limpiar acciones huérfanas
    for a in list(bpy.data.actions):
        if a.users == 0:
            bpy.data.actions.remove(a)

    utils_blender.limpiar_coleccion(nombre_src)
    utils_blender.limpiar_coleccion(nombre_export)

    for o in list(bpy.data.objects):
        if o.name.startswith("nave_") or o.name.startswith("Armature_jugador"):
            bpy.data.objects.remove(o, do_unlink=True)

    col_src = utils_blender.obtener_o_crear_coleccion(nombre_src)
    col_export = utils_blender.obtener_o_crear_coleccion(nombre_export)

    mats = configurar_materiales(nivel)

    bm = bmesh.new()

    # Construir componentes modulares
    verts_fuselaje = construir_fuselaje_base(bm, nivel)
    grupos_alas = construir_alas_nivel(bm, nivel)
    grupos_canones = construir_canones_nivel(bm, nivel)
    verts_motores = construir_motores_nivel(bm, nivel)

    bm.verts.index_update()

    grupos_indices = {
        'body': list(set(v.index for v in verts_fuselaje + verts_motores)),
        'wing_L': list(set(v.index for v in grupos_alas['wing_L'])),
        'wing_R': list(set(v.index for v in grupos_alas['wing_R'])),
        'canon_C': list(set(v.index for v in grupos_canones['canon_C'])),
        'canon_L': list(set(v.index for v in grupos_canones['canon_L'])),
        'canon_R': list(set(v.index for v in grupos_canones['canon_R'])),
        'thruster': list(set(v.index for v in verts_motores))
    }

    mesh = bpy.data.meshes.new(f"nave_{suf}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj_mesh = bpy.data.objects.new(f"nave_{suf}_mesh_obj", mesh)
    col_src.objects.link(obj_mesh)

    # Asignar los 5 materiales
    obj_mesh.data.materials.append(mats['casco'])    # 0
    obj_mesh.data.materials.append(mats['blindaje']) # 1
    obj_mesh.data.materials.append(mats['cabina'])   # 2
    obj_mesh.data.materials.append(mats['motor'])    # 3
    obj_mesh.data.materials.append(mats['neon'])     # 4

    # Modificador Weighted Normal (suavizado perfecto de normales de aristas)
    bpy.context.view_layer.objects.active = obj_mesh
    for p in mesh.polygons:
        p.use_smooth = True

    mod_norm = obj_mesh.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True
    try:
        bpy.ops.object.modifier_apply(modifier="WeightedNormal")
    except Exception as e:
        print(f"Notice applying WeightedNormal: {e}")

    # Rigging con Armature
    arm_obj = crear_armature_y_rigging(obj_mesh, col_src, grupos_indices, nivel)

    # 6 Animaciones NLA
    crear_animaciones_jugador(arm_obj, nivel)

    # Centrar pivote del volumen en (0,0,0)
    bpy.context.view_layer.update()
    min_co, max_co, tamano, centro = utils_blender.calcular_aabb([obj_mesh])
    offset_centro = mathutils.Vector((-centro[0], -centro[1], -centro[2]))

    bpy.context.view_layer.objects.active = obj_mesh
    mesh.transform(mathutils.Matrix.Translation(offset_centro))
    mesh.update()

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in arm_obj.data.edit_bones:
        eb.head += offset_centro
        eb.tail += offset_centro
    b_root = arm_obj.data.edit_bones.get("root")
    if b_root:
        b_root.head = (0, 0, 0)
        b_root.tail = (0, 0, 0.05)
    bpy.ops.object.mode_set(mode='OBJECT')

    for o in [obj_mesh, arm_obj]:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        o.select_set(False)

    # Mover a EXPORT
    col_src.objects.unlink(obj_mesh)
    col_src.objects.unlink(arm_obj)
    col_export.objects.link(arm_obj)
    col_export.objects.link(obj_mesh)

    bpy.context.view_layer.update()
    min_final, max_final, tam_final, cen_final = utils_blender.calcular_aabb([obj_mesh])
    total_triangulos = utils_blender.contar_triangulos([obj_mesh])

    print("-" * 60)
    print(f"INFORME GEOMÉTRICO FINAL — NAVE MK {nivel} («{nombre}»):")
    print(f"Total Triángulos Evaluados: {total_triangulos} (Presupuesto: {cfg['presupuesto_min']} - {cfg['presupuesto_max']})")
    print(f"Dimensiones Bounding Box (Godot X x Y x Z): {tam_final[0]:.3f} x {tam_final[2]:.3f} x {tam_final[1]:.3f} m")
    print(f"Centro del Bounding Box: ({cen_final[0]:.3f}, {cen_final[1]:.3f}, {cen_final[2]:.3f})")
    print("-" * 60)

    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", f"nave_{suf}.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # Exportación dual a .glb
    ruta_glb_1 = os.path.join(ws_dir, "assets", "models", "jugador", f"nave_{suf}.glb")
    ruta_glb_2 = os.path.join(ws_dir, "Space invaders", "assets", "models", "jugador", f"nave_{suf}.glb")
    os.makedirs(os.path.dirname(ruta_glb_1), exist_ok=True)
    os.makedirs(os.path.dirname(ruta_glb_2), exist_ok=True)

    utils_blender.exportar_glb(ruta_glb_1, [arm_obj, obj_mesh])
    shutil.copy2(ruta_glb_1, ruta_glb_2)

    return {
        'nivel': nivel,
        'nombre': nombre,
        'sufijo': suf,
        'triangulos': total_triangulos,
        'tam_blender': [tam_final[0], tam_final[1], tam_final[2]],
        'tam_godot': [tam_final[0], tam_final[2], tam_final[1]],
        'centro': [cen_final[0], cen_final[1], cen_final[2]],
        'ruta_glb': ruta_glb_1,
        'ruta_blend': ruta_blend,
        'clips': ["Idle-loop", "Fire", "Hit", "Spawn", "Victory", "Death"]
    }

if __name__ == "__main__":
    construir_nave(1)
