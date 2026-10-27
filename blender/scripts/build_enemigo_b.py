"""
blender/scripts/build_enemigo_b.py - Construcción, texturizado, rigging,
animación y exportación de Enemigo B ("Calamar").
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

NOMBRE_SRC = "SRC_enemigo_b"
NOMBRE_EXPORT = "EXPORT_enemigo_b"

# Metas dimensionales (en Godot: X ancho, Y alto, Z profundidad)
OBJETIVO_X = 1.20
OBJETIVO_ALTO_Z = 0.55
OBJETIVO_PROF_Y = 1.00

def configurar_materiales():
    """Crea los 4 materiales arcade neon basados en Principled BSDF."""
    # 1. Casco: Gris azulado oscuro (#1B2030), liso y metálico
    mat_casco = utils_blender.crear_material(
        "m_casco_b",
        base_color=(0.011, 0.014, 0.028, 1.0),
        metallic=0.85,
        roughness=0.35
    )

    # 2. Acentos emisivos Neón: Rosa (#FF2E93)
    mat_neon = utils_blender.crear_material(
        "m_neon_rosa",
        base_color=(1.0, 0.026, 0.292, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(1.0, 0.026, 0.292, 1.0),
        emission_strength=2.8
    )

    # 3. Sensores / Ojos duales rosa brillante (#FFA6D5)
    mat_ojos = utils_blender.crear_material(
        "m_ojos_cangrejo",
        base_color=(1.0, 0.38, 0.65, 1.0),
        metallic=0.0,
        roughness=0.1,
        emission_color=(1.0, 0.20, 0.55, 1.0),
        emission_strength=3.5
    )

    # 4. Detalles mecánicos oscuros (juntas, toberas, dientes de pinzas)
    mat_detalles = utils_blender.crear_material(
        "m_detalles_b",
        base_color=(0.007, 0.009, 0.015, 1.0),
        metallic=0.92,
        roughness=0.25
    )

    return {
        'casco': mat_casco,
        'neon': mat_neon,
        'ojos': mat_ojos,
        'detalles': mat_detalles
    }

def construir_caparazon(bm):
    """Construye el caparazón segmentado con 3 placas de armadura superpuestas."""
    # Placas superpuestas en abanico (anterior, media, posterior)
    placas_cfg = [
        # (offset_y, scale_x, scale_y, scale_z, z_elev)
        ( 0.08, 0.58, 0.28, 0.14, 0.08), # Placa frontal
        (-0.06, 0.68, 0.32, 0.16, 0.09), # Placa central (más ancha)
        (-0.20, 0.56, 0.26, 0.13, 0.07), # Placa trasera
    ]

    for py, sx, sy, sz, ze in placas_cfg:
        bm_p = bmesh.new()
        bmesh.ops.create_cube(bm_p, size=1.0)
        scale_mat = mathutils.Matrix.Diagonal((sx, sy, sz, 1.0))
        bmesh.ops.transform(bm_p, matrix=scale_mat, verts=bm_p.verts)

        for v in bm_p.verts:
            if v.co.z > 0:
                v.co.x *= (1.0 - abs(v.co.y) * 0.35)
                v.co.z *= (1.0 - abs(v.co.x) * 0.25)
            else:
                v.co.x *= 0.88
                v.co.y *= 0.88

        bmesh.ops.bevel(
            bm_p,
            geom=bm_p.edges[:],
            offset=0.03,
            segments=2,
            profile=0.7
        )

        vert_map = {}
        for v in bm_p.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((0, py, ze)))
        for f in bm_p.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0 # m_casco
            except:
                pass
        bm_p.free()

        # Ranura emisiva rosa entre las placas
        bm_n = bmesh.new()
        bmesh.ops.create_cube(bm_n, size=1.0)
        scale_n = mathutils.Matrix.Diagonal((sx * 0.85, 0.018, 0.015, 1.0))
        bmesh.ops.transform(bm_n, matrix=scale_n, verts=bm_n.verts)
        vert_map = {}
        for v in bm_n.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((0, py + sy * 0.45, ze + sz * 0.48)))
        for f in bm_n.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1 # m_neon
            except:
                pass
        bm_n.free()

    # Vientre mecánico
    bm_ventral = bmesh.new()
    bmesh.ops.create_cone(
        bm_ventral,
        cap_ends=True,
        cap_tris=False,
        segments=24,
        radius1=0.26,
        radius2=0.34,
        depth=0.12
    )
    for v in bm_ventral.verts:
        v.co.z -= 0.06
        v.co.y -= 0.05
    vert_map = {}
    for v in bm_ventral.verts:
        vert_map[v] = bm.verts.new(v.co)
    for f in bm_ventral.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 3 # m_detalles
        except:
            pass
    bm_ventral.free()

    # Sensores / Ojos duales frontales (+Y)
    rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
    for ojo_x in [-0.14, 0.14]:
        bm_ojo = bmesh.new()
        bmesh.ops.create_cone(
            bm_ojo,
            cap_ends=False,
            cap_tris=False,
            segments=18,
            radius1=0.048,
            radius2=0.056,
            depth=0.06
        )
        bmesh.ops.transform(bm_ojo, matrix=rot_x, verts=bm_ojo.verts)
        offset_ojo = mathutils.Vector((ojo_x, 0.24, 0.09))
        vert_map = {}
        for v in bm_ojo.verts:
            vert_map[v] = bm.verts.new(v.co + offset_ojo)
        for f in bm_ojo.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_ojo.free()

        bm_lente = bmesh.new()
        bmesh.ops.create_uvsphere(bm_lente, u_segments=18, v_segments=14, radius=0.040)
        vert_map = {}
        for v in bm_lente.verts:
            vert_map[v] = bm.verts.new(v.co + offset_ojo + mathutils.Vector((0, 0.018, 0)))
        for f in bm_lente.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 2 # m_ojos
            except:
                pass
        bm_lente.free()

    # Toberas traseras duales (-Y)
    for tob_x in [-0.19, 0.19]:
        bm_tob = bmesh.new()
        bmesh.ops.create_cone(
            bm_tob,
            cap_ends=False,
            cap_tris=False,
            segments=18,
            radius1=0.062,
            radius2=0.048,
            depth=0.08
        )
        bmesh.ops.transform(bm_tob, matrix=rot_x, verts=bm_tob.verts)
        offset_tob = mathutils.Vector((tob_x, -0.34, 0.05))
        vert_map = {}
        for v in bm_tob.verts:
            vert_map[v] = bm.verts.new(v.co + offset_tob)
        for f in bm_tob.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_tob.free()

        bm_llama = bmesh.new()
        bmesh.ops.create_cone(
            bm_llama,
            cap_ends=True,
            cap_tris=False,
            segments=18,
            radius1=0.042,
            radius2=0.042,
            depth=0.02
        )
        bmesh.ops.transform(bm_llama, matrix=rot_x, verts=bm_llama.verts)
        vert_map = {}
        for v in bm_llama.verts:
            vert_map[v] = bm.verts.new(v.co + offset_tob + mathutils.Vector((0, -0.025, 0)))
        for f in bm_llama.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1
            except:
                pass
        bm_llama.free()

def construir_pinzas(bm):
    """Construye las dos grandes pinzas mecánicas frontales/laterales."""
    grupos_pinzas = {
        'pinza_L_brazo': [], 'pinza_L_garra_sup': [], 'pinza_L_garra_inf': [],
        'pinza_R_brazo': [], 'pinza_R_garra_sup': [], 'pinza_R_garra_inf': []
    }

    for lado, prefix in [(-1.0, "pinza_L"), (1.0, "pinza_R")]:
        p_origen = mathutils.Vector((lado * 0.28, 0.10, 0.02))
        p_codo = mathutils.Vector((lado * 0.46, 0.28, 0.02))
        vec_brazo = p_codo - p_origen
        dir_brazo = vec_brazo.normalized()
        rot_b = dir_brazo.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_brazo = mathutils.Matrix.Translation((p_origen + p_codo) / 2.0) @ rot_b

        # Brazo
        bm_b = bmesh.new()
        bmesh.ops.create_cube(bm_b, size=1.0)
        scale_b = mathutils.Matrix.Diagonal((0.085, 0.065, vec_brazo.length * 0.92, 1.0))
        bmesh.ops.transform(bm_b, matrix=scale_b, verts=bm_b.verts)

        # Barra neón
        bm_b_neon = bmesh.new()
        bmesh.ops.create_cube(bm_b_neon, size=1.0)
        scale_bn = mathutils.Matrix.Diagonal((0.038, 0.016, vec_brazo.length * 0.65, 1.0))
        trans_bn = mathutils.Matrix.Translation((0.0, 0.034, 0.0))
        bmesh.ops.transform(bm_b_neon, matrix=trans_bn @ scale_bn, verts=bm_b_neon.verts)

        vert_map = {}
        for v in bm_b.verts:
            nv = bm.verts.new(mat_brazo @ v.co)
            vert_map[v] = nv
            grupos_pinzas[f"{prefix}_brazo"].append(nv)
        for f in bm_b.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0
            except:
                pass
        bm_b.free()

        vert_map = {}
        for v in bm_b_neon.verts:
            nv = bm.verts.new(mat_brazo @ v.co)
            vert_map[v] = nv
            grupos_pinzas[f"{prefix}_brazo"].append(nv)
        for f in bm_b_neon.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1
            except:
                pass
        bm_b_neon.free()

        # Rótula
        bm_rot = bmesh.new()
        bmesh.ops.create_cone(
            bm_rot,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=0.052,
            radius2=0.052,
            depth=0.085
        )
        vert_map = {}
        for v in bm_rot.verts:
            nv = bm.verts.new(v.co + p_codo)
            vert_map[v] = nv
            grupos_pinzas[f"{prefix}_brazo"].append(nv)
        for f in bm_rot.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_rot.free()

        # Garra Superior
        p_punta_sup = mathutils.Vector((lado * 0.38, 0.50, 0.04))
        vec_gs = p_punta_sup - p_codo
        dir_gs = vec_gs.normalized()
        rot_gs = dir_gs.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_gs = mathutils.Matrix.Translation((p_codo + p_punta_sup) / 2.0) @ rot_gs

        bm_gs = bmesh.new()
        bmesh.ops.create_cone(
            bm_gs,
            cap_ends=True,
            cap_tris=False,
            segments=14,
            radius1=0.046,
            radius2=0.009,
            depth=vec_gs.length
        )
        vert_map = {}
        for v in bm_gs.verts:
            nv = bm.verts.new(mat_gs @ v.co)
            vert_map[v] = nv
            grupos_pinzas[f"{prefix}_garra_sup"].append(nv)
        for f in bm_gs.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0
            except:
                pass
        bm_gs.free()

        # Barra neón en garra superior
        bm_gs_neon = bmesh.new()
        bmesh.ops.create_cube(bm_gs_neon, size=1.0)
        scale_gsn = mathutils.Matrix.Diagonal((0.016, 0.012, vec_gs.length * 0.60, 1.0))
        trans_gsn = mathutils.Matrix.Translation((lado * 0.022, 0.012, 0.0))
        bmesh.ops.transform(bm_gs_neon, matrix=trans_gsn @ scale_gsn, verts=bm_gs_neon.verts)
        vert_map = {}
        for v in bm_gs_neon.verts:
            nv = bm.verts.new(mat_gs @ v.co)
            vert_map[v] = nv
            grupos_pinzas[f"{prefix}_garra_sup"].append(nv)
        for f in bm_gs_neon.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1
            except:
                pass
        bm_gs_neon.free()

        # Garra Inferior
        p_punta_inf = mathutils.Vector((lado * 0.46, 0.48, -0.03))
        vec_gi = p_punta_inf - p_codo
        dir_gi = vec_gi.normalized()
        rot_gi = dir_gi.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_gi = mathutils.Matrix.Translation((p_codo + p_punta_inf) / 2.0) @ rot_gi

        bm_gi = bmesh.new()
        bmesh.ops.create_cone(
            bm_gi,
            cap_ends=True,
            cap_tris=False,
            segments=14,
            radius1=0.042,
            radius2=0.007,
            depth=vec_gi.length
        )
        vert_map = {}
        for v in bm_gi.verts:
            nv = bm.verts.new(mat_gi @ v.co)
            vert_map[v] = nv
            grupos_pinzas[f"{prefix}_garra_inf"].append(nv)
        for f in bm_gi.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_gi.free()

    return grupos_pinzas

def construir_patas(bm):
    """Construye 6 patas articuladas (3 por lado: Delantera, Media, Trasera)."""
    grupos_patas = {}

    configs_patas = [
        # Delanteras
        {
            'nombre': 'pata_FL',
            'base': mathutils.Vector((-0.26, 0.12, -0.04)),
            'rodilla': mathutils.Vector((-0.52, 0.22, 0.08)),
            'punta': mathutils.Vector((-0.58, 0.28, -0.20))
        },
        {
            'nombre': 'pata_FR',
            'base': mathutils.Vector((0.26, 0.12, -0.04)),
            'rodilla': mathutils.Vector((0.52, 0.22, 0.08)),
            'punta': mathutils.Vector((0.58, 0.28, -0.20))
        },
        # Medias (abren hacia los laterales exteriores)
        {
            'nombre': 'pata_ML',
            'base': mathutils.Vector((-0.28, -0.04, -0.04)),
            'rodilla': mathutils.Vector((-0.55, -0.04, 0.09)),
            'punta': mathutils.Vector((-0.60, -0.06, -0.20))
        },
        {
            'nombre': 'pata_MR',
            'base': mathutils.Vector((0.28, -0.04, -0.04)),
            'rodilla': mathutils.Vector((0.55, -0.04, 0.09)),
            'punta': mathutils.Vector((0.60, -0.06, -0.20))
        },
        # Traseras
        {
            'nombre': 'pata_BL',
            'base': mathutils.Vector((-0.25, -0.20, -0.04)),
            'rodilla': mathutils.Vector((-0.52, -0.26, 0.07)),
            'punta': mathutils.Vector((-0.56, -0.32, -0.20))
        },
        {
            'nombre': 'pata_BR',
            'base': mathutils.Vector((0.25, -0.20, -0.04)),
            'rodilla': mathutils.Vector((0.52, -0.26, 0.07)),
            'punta': mathutils.Vector((0.56, -0.32, -0.20))
        },
    ]

    for p_cfg in configs_patas:
        p_nom = p_cfg['nombre']
        grupos_patas[f"{p_nom}_femur"] = []
        grupos_patas[f"{p_nom}_tibia"] = []

        p_base = p_cfg['base']
        p_rod = p_cfg['rodilla']
        p_tip = p_cfg['punta']

        # 1. Fémur
        vec_f = p_rod - p_base
        dir_f = vec_f.normalized()
        rot_f = dir_f.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_f = mathutils.Matrix.Translation((p_base + p_rod) / 2.0) @ rot_f

        bm_f = bmesh.new()
        bmesh.ops.create_cone(
            bm_f,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.040,
            radius2=0.028,
            depth=vec_f.length
        )
        vert_map = {}
        for v in bm_f.verts:
            nv = bm.verts.new(mat_f @ v.co)
            vert_map[v] = nv
            grupos_patas[f"{p_nom}_femur"].append(nv)
        for f in bm_f.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0
            except:
                pass
        bm_f.free()

        # Rótula
        bm_rod = bmesh.new()
        bmesh.ops.create_cone(
            bm_rod,
            cap_ends=True,
            cap_tris=False,
            segments=14,
            radius1=0.034,
            radius2=0.034,
            depth=0.055
        )
        vert_map = {}
        for v in bm_rod.verts:
            nv = bm.verts.new(v.co + p_rod)
            vert_map[v] = nv
            grupos_patas[f"{p_nom}_femur"].append(nv)
        for f in bm_rod.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_rod.free()

        # 2. Tibia
        vec_t = p_tip - p_rod
        dir_t = vec_t.normalized()
        rot_t = dir_t.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_t = mathutils.Matrix.Translation((p_rod + p_tip) / 2.0) @ rot_t

        bm_t = bmesh.new()
        bmesh.ops.create_cone(
            bm_t,
            cap_ends=True,
            cap_tris=False,
            segments=10,
            radius1=0.030,
            radius2=0.005,
            depth=vec_t.length
        )
        vert_map = {}
        for v in bm_t.verts:
            nv = bm.verts.new(mat_t @ v.co)
            vert_map[v] = nv
            grupos_patas[f"{p_nom}_tibia"].append(nv)
        for f in bm_t.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_t.free()

        # Acento neón
        bm_tn = bmesh.new()
        bmesh.ops.create_cube(bm_tn, size=1.0)
        scale_tn = mathutils.Matrix.Diagonal((0.014, 0.009, vec_t.length * 0.55, 1.0))
        trans_tn = mathutils.Matrix.Translation((0.0, 0.016, 0.0))
        bmesh.ops.transform(bm_tn, matrix=trans_tn @ scale_tn, verts=bm_tn.verts)
        vert_map = {}
        for v in bm_tn.verts:
            nv = bm.verts.new(mat_t @ v.co)
            vert_map[v] = nv
            grupos_patas[f"{p_nom}_tibia"].append(nv)
        for f in bm_tn.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1
            except:
                pass
        bm_tn.free()

    return grupos_patas

def crear_armature_y_rig(col, obj_mesh, indices_pesos):
    """Crea el Armature de 33 huesos para Enemigo B."""
    arm_data = bpy.data.armatures.new("enemigo_b_armature_data")
    arm_obj = bpy.data.objects.new("enemigo_b_armature", arm_data)
    col.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm_data.edit_bones

    b_root = ebones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    b_body = ebones.new("body")
    b_body.head = (0, -0.04, 0.04)
    b_body.tail = (0, -0.04, 0.18)
    b_body.parent = b_root

    for lado, prefix in [(-1.0, "pinza_L"), (1.0, "pinza_R")]:
        b_brazo = ebones.new(f"{prefix}_brazo")
        b_brazo.head = (lado * 0.28, 0.10, 0.02)
        b_brazo.tail = (lado * 0.46, 0.28, 0.02)
        b_brazo.parent = b_body

        b_gs = ebones.new(f"{prefix}_garra_sup")
        b_gs.head = (lado * 0.46, 0.28, 0.02)
        b_gs.tail = (lado * 0.38, 0.50, 0.04)
        b_gs.parent = b_brazo

        b_gi = ebones.new(f"{prefix}_garra_inf")
        b_gi.head = (lado * 0.46, 0.28, 0.02)
        b_gi.tail = (lado * 0.46, 0.48, -0.03)
        b_gi.parent = b_brazo

    configs_patas = [
        ('pata_FL', (-0.26, 0.12, -0.04), (-0.52, 0.22, 0.08), (-0.58, 0.28, -0.20)),
        ('pata_FR', (0.26, 0.12, -0.04), (0.52, 0.22, 0.08), (0.58, 0.28, -0.20)),
        ('pata_ML', (-0.28, -0.04, -0.04), (-0.55, -0.04, 0.09), (-0.60, -0.06, -0.20)),
        ('pata_MR', (0.28, -0.04, -0.04), (0.55, -0.04, 0.09), (0.60, -0.06, -0.20)),
        ('pata_BL', (-0.25, -0.20, -0.04), (-0.52, -0.26, 0.07), (-0.56, -0.32, -0.20)),
        ('pata_BR', (0.25, -0.20, -0.04), (0.52, -0.26, 0.07), (0.56, -0.32, -0.20)),
    ]

    for p_nom, p_base, p_rod, p_tip in configs_patas:
        b_fem = ebones.new(f"{p_nom}_femur")
        b_fem.head = p_base
        b_fem.tail = p_rod
        b_fem.parent = b_body

        b_tib = ebones.new(f"{p_nom}_tibia")
        b_tib.head = p_rod
        b_tib.tail = p_tip
        b_tib.parent = b_fem

    bpy.ops.object.mode_set(mode='OBJECT')

    mod_arm = obj_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod_arm.object = arm_obj
    obj_mesh.parent = arm_obj

    vg_body = obj_mesh.vertex_groups.new(name="body")
    verts_asignados = set()

    for b_name, idx_list in indices_pesos.items():
        vg = obj_mesh.vertex_groups.new(name=b_name)
        verts_asignados.update(idx_list)
        if idx_list:
            vg.add(idx_list, 1.0, 'REPLACE')

    v_body_indices = [v.index for v in obj_mesh.data.vertices if v.index not in verts_asignados]
    if v_body_indices:
        vg_body.add(v_body_indices, 1.0, 'REPLACE')

    return arm_obj

def crear_animaciones(arm_obj):
    """Genera las 4 acciones exactas a 30 FPS para Enemigo B."""
    bpy.context.scene.render.fps = 30
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    def preparar_accion(nombre):
        act = bpy.data.actions.get(nombre)
        if act:
            bpy.data.actions.remove(act)
        return bpy.data.actions.new(name=nombre)

    pose_bones = arm_obj.pose.bones
    for pb in pose_bones:
        pb.rotation_mode = 'XYZ'

    # 1. IDLE-LOOP (45 frames, 30 FPS)
    act_idle = preparar_accion("Idle-loop")
    arm_obj.animation_data.action = act_idle

    for f in [1, 12, 23, 34, 45]:
        t = (f - 1) / 44.0 * 2.0 * math.pi

        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, 0.0, math.sin(t) * 0.010)
            pb_body.rotation_euler = (math.sin(t) * math.radians(1.2), 0.0, math.cos(t) * math.radians(0.6))
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for lado_s, prefix in [(-1.0, "pinza_L"), (1.0, "pinza_R")]:
            pb_brazo = pose_bones.get(f"{prefix}_brazo")
            if pb_brazo:
                pb_brazo.rotation_euler = (0.0, 0.0, math.sin(t) * math.radians(lado_s * 2.5))
                pb_brazo.keyframe_insert(data_path="rotation_euler", frame=f)

            pb_gi = pose_bones.get(f"{prefix}_garra_inf")
            if pb_gi:
                pb_gi.rotation_euler = (0.0, 0.0, math.sin(t) * math.radians(lado_s * 6.0))
                pb_gi.keyframe_insert(data_path="rotation_euler", frame=f)

        for p_nom, fase in [
            ('pata_FL', 0.0), ('pata_BR', 0.0), ('pata_MR', math.pi),
            ('pata_FR', math.pi), ('pata_BL', math.pi), ('pata_ML', 0.0)
        ]:
            pb_fem = pose_bones.get(f"{p_nom}_femur")
            if pb_fem:
                pb_fem.rotation_euler = (math.sin(t + fase) * math.radians(3.5), 0.0, 0.0)
                pb_fem.keyframe_insert(data_path="rotation_euler", frame=f)
            pb_tib = pose_bones.get(f"{p_nom}_tibia")
            if pb_tib:
                pb_tib.rotation_euler = (math.cos(t + fase) * math.radians(4.0), 0.0, 0.0)
                pb_tib.keyframe_insert(data_path="rotation_euler", frame=f)

    track_idle = arm_obj.animation_data.nla_tracks.new()
    track_idle.name = "Idle-loop"
    track_idle.strips.new("Idle-loop", 1, act_idle)

    # 2. ATTACK (15 frames, 30 FPS)
    act_atk = preparar_accion("Attack")
    arm_obj.animation_data.action = act_atk

    puntos_atk = [
        (1,   0.00,  0.0,   0.0),
        (6,  -0.03,  7.0,  18.0),
        (9,   0.05, -3.0, -12.0),
        (12,  0.01,  1.0,   2.0),
        (15,  0.00,  0.0,   0.0)
    ]

    for f, yl, pt, popen in puntos_atk:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, 0.0)
            pb_body.rotation_euler = (math.radians(pt), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for lado_s, prefix in [(-1.0, "pinza_L"), (1.0, "pinza_R")]:
            pb_gi = pose_bones.get(f"{prefix}_garra_inf")
            if pb_gi:
                pb_gi.rotation_euler = (0.0, 0.0, math.radians(lado_s * popen))
                pb_gi.keyframe_insert(data_path="rotation_euler", frame=f)

    track_atk = arm_obj.animation_data.nla_tracks.new()
    track_atk.name = "Attack"
    track_atk.strips.new("Attack", 1, act_atk)

    # 3. HIT (8 frames, 30 FPS)
    act_hit = preparar_accion("Hit")
    arm_obj.animation_data.action = act_hit

    puntos_hit = [
        (1,  0.00,  0.00,   0.0,  0.0),
        (2, -0.04,  0.02,   8.0, -12.0),
        (4,  0.015,-0.008, -3.0,   4.0),
        (6, -0.005, 0.003,  1.0,  -1.0),
        (8,  0.00,  0.00,   0.0,   0.0)
    ]

    for f, yl, zl, pt, p_prot in puntos_hit:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, zl)
            pb_body.rotation_euler = (math.radians(pt), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for lado_s, prefix in [(-1.0, "pinza_L"), (1.0, "pinza_R")]:
            pb_brazo = pose_bones.get(f"{prefix}_brazo")
            if pb_brazo:
                pb_brazo.rotation_euler = (0.0, 0.0, math.radians(lado_s * p_prot))
                pb_brazo.keyframe_insert(data_path="rotation_euler", frame=f)

    track_hit = arm_obj.animation_data.nla_tracks.new()
    track_hit.name = "Hit"
    track_hit.strips.new("Hit", 1, act_hit)

    # 4. DEATH (24 frames, 30 FPS)
    act_death = preparar_accion("Death")
    arm_obj.animation_data.action = act_death

    puntos_death = [
        (1,   0.00,  0.00,  0.0,  0.0),
        (5,  -0.02,  0.02,  6.0, 15.0),
        (12, -0.01, -0.04, 12.0, 28.0),
        (18, -0.01, -0.06, 16.0, 32.0),
        (24, -0.01, -0.07, 18.0, 35.0)
    ]

    for f, yl, zl, pt, drop in puntos_death:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, zl)
            pb_body.rotation_euler = (math.radians(pt), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for lado_s, prefix in [(-1.0, "pinza_L"), (1.0, "pinza_R")]:
            pb_gi = pose_bones.get(f"{prefix}_garra_inf")
            if pb_gi:
                pb_gi.rotation_euler = (0.0, 0.0, math.radians(lado_s * drop))
                pb_gi.keyframe_insert(data_path="rotation_euler", frame=f)

    track_death = arm_obj.animation_data.nla_tracks.new()
    track_death.name = "Death"
    track_death.strips.new("Death", 1, act_death)

    arm_obj.animation_data.action = act_idle
    bpy.context.scene.frame_set(1)

def construir_enemigo_b():
    """Función constructora principal idempotente para Enemigo B ('Cangrejo')."""
    print("=" * 60)
    print("Iniciando construcción de Enemigo B ('Cangrejo')...")
    print("=" * 60)

    # 1. Limpiar colecciones
    utils_blender.limpiar_coleccion(NOMBRE_SRC)
    utils_blender.limpiar_coleccion(NOMBRE_EXPORT)

    col_src = utils_blender.obtener_o_crear_coleccion(NOMBRE_SRC)
    col_export = utils_blender.obtener_o_crear_coleccion(NOMBRE_EXPORT)

    # 2. Materiales
    mats = configurar_materiales()

    # 3. Malla unificada
    bm = bmesh.new()
    construir_caparazon(bm)
    grupos_pinzas = construir_pinzas(bm)
    grupos_patas = construir_patas(bm)

    grupos_bm_verts = {}
    grupos_bm_verts.update(grupos_pinzas)
    grupos_bm_verts.update(grupos_patas)

    bm.verts.index_update()
    indices_pesos = {}
    for nombre_hueso, bm_verts_list in grupos_bm_verts.items():
        indices_pesos[nombre_hueso] = [v.index for v in bm_verts_list]

    # 4. Crear objeto de malla
    mesh = bpy.data.meshes.new("enemigo_b_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj_mesh = bpy.data.objects.new("enemigo_b", mesh)
    col_src.objects.link(obj_mesh)

    obj_mesh.data.materials.append(mats['casco'])
    obj_mesh.data.materials.append(mats['neon'])
    obj_mesh.data.materials.append(mats['ojos'])
    obj_mesh.data.materials.append(mats['detalles'])

    # 5. Modificadores High-Poly (Bevel 3 segmentos + Weighted Normal)
    mod_bev = obj_mesh.modifiers.new(name="Bevel", type='BEVEL')
    mod_bev.limit_method = 'ANGLE'
    mod_bev.angle_limit = math.radians(35.0)
    mod_bev.width = 0.007
    mod_bev.segments = 3
    mod_bev.profile = 0.70

    mod_norm = obj_mesh.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True

    bpy.context.view_layer.objects.active = obj_mesh
    for p in mesh.polygons:
        p.use_smooth = True

    # 6. Rigging
    arm_obj = crear_armature_y_rig(col_src, obj_mesh, indices_pesos)

    # 7. Animaciones NLA
    crear_animaciones(arm_obj)

    # 8. Centrar pivote en el centro exacto del volumen
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

    # 9. Mover a EXPORT
    col_src.objects.unlink(obj_mesh)
    col_src.objects.unlink(arm_obj)
    col_export.objects.link(arm_obj)
    col_export.objects.link(obj_mesh)

    # 10. Medición final
    bpy.context.view_layer.update()
    min_final, max_final, tam_final, cen_final = utils_blender.calcular_aabb([obj_mesh])
    total_triangulos = utils_blender.contar_triangulos([obj_mesh])

    print("-" * 60)
    print("INFORME GEOMÉTRICO FINAL — ENEMIGO B:")
    print(f"Total Triángulos Evaluados: {total_triangulos} (Presupuesto: 12,000 - 25,000)")
    print(f"Dimensiones Bounding Box (Godot X x Y x Z): {tam_final[0]:.3f} x {tam_final[2]:.3f} x {tam_final[1]:.3f}")
    print(f"Centro del Bounding Box: ({cen_final[0]:.3f}, {cen_final[1]:.3f}, {cen_final[2]:.3f})")
    print("-" * 60)

    # 11. Guardar .blend
    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "enemigo_b.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # 12. Exportar .glb
    ruta_glb_1 = os.path.join(ws_dir, "assets", "models", "enemigos", "enemigo_b.glb")
    ruta_glb_2 = os.path.join(ws_dir, "Space invaders", "assets", "models", "enemigos", "enemigo_b.glb")

    utils_blender.exportar_glb(ruta_glb_1, [arm_obj, obj_mesh])
    shutil.copy2(ruta_glb_1, ruta_glb_2)

    return {
        'triangulos': total_triangulos,
        'tam_blender': [tam_final[0], tam_final[1], tam_final[2]],
        'tam_godot': [tam_final[0], tam_final[2], tam_final[1]],
        'centro': [cen_final[0], cen_final[1], cen_final[2]],
        'ruta_glb': ruta_glb_1,
        'ruta_blend': ruta_blend,
        'clips': ["Idle-loop", "Attack", "Hit", "Death"]
    }

if __name__ == "__main__":
    construir_enemigo_b()
