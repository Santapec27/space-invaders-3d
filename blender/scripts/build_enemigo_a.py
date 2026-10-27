"""
blender/scripts/build_enemigo_a.py - Construcción, texturizado, rigging,
animación y exportación de Enemigo A ("Calamar").
Proyecto: Space Invaders 3D (Parcial 2)
"""

import bpy
import bmesh
import math
import mathutils
import os
import sys

directorio_scripts = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender\blender\scripts"
if directorio_scripts not in sys.path:
    sys.path.append(directorio_scripts)

import utils_blender

NOMBRE_SRC = "SRC_enemigo_a"
NOMBRE_EXPORT = "EXPORT_enemigo_a"

# Metas dimensionales del bounding box en Godot (+Y arriba, -Z frente):
# Ancho X ≈ 1.20 | Alto Y_godot ≈ 0.60 | Profundidad Z_godot ≈ 1.00
# En Blender (con export_yup=True):
# Ancho X ≈ 1.20 | Alto Z_blender ≈ 0.60 | Profundidad Y_blender ≈ 1.00
OBJETIVO_X = 1.20
OBJETIVO_ALTO_Z = 0.60
OBJETIVO_PROF_Y = 1.00

def configurar_materiales():
    """Crea los 4 materiales arcade neon basados en Principled BSDF."""
    # 1. Casco base: Gris azulado oscuro (#1B2030), liso y metálico
    mat_casco = utils_blender.crear_material(
        "m_casco",
        base_color=(0.011, 0.014, 0.028, 1.0),
        metallic=0.85,
        roughness=0.35
    )

    # 2. Acentos emisivos Neón: Violeta (#A855F7)
    mat_neon = utils_blender.crear_material(
        "m_neon",
        base_color=(0.384, 0.088, 0.930, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(0.384, 0.088, 0.930, 1.0),
        emission_strength=2.8
    )

    # 3. Ojo central: Violeta brillante con núcleo blanco-lila (#D8B4FE)
    mat_ojo = utils_blender.crear_material(
        "m_ojo",
        base_color=(0.687, 0.451, 0.985, 1.0),
        metallic=0.0,
        roughness=0.1,
        emission_color=(0.518, 0.246, 0.969, 1.0),
        emission_strength=3.5
    )

    # 4. Detalles mecánicos oscuros (juntas, toberas, marcos)
    mat_detalles = utils_blender.crear_material(
        "m_detalles",
        base_color=(0.007, 0.009, 0.015, 1.0),
        metallic=0.92,
        roughness=0.25
    )

    return {
        'casco': mat_casco,
        'neon': mat_neon,
        'ojo': mat_ojo,
        'detalles': mat_detalles
    }

def construir_cupula_y_cuerpo(bm):
    """Genera la cúpula, ranuras neón y collar inferior en el bmesh principal."""
    # 1. Cúpula superior esférica achatada
    bm_cup = bmesh.new()
    bmesh.ops.create_uvsphere(bm_cup, u_segments=28, v_segments=16, radius=0.35)
    caras_borrar = []
    for v in bm_cup.verts:
        v.co.z = v.co.z * 0.72 + 0.12
        if v.co.z < 0.12:
            caras_borrar.extend(v.link_faces)
    bmesh.ops.delete(bm_cup, geom=list(set(caras_borrar)), context='FACES_ONLY')

    vert_map = {}
    for v in bm_cup.verts:
        vert_map[v] = bm.verts.new(v.co)
    for f in bm_cup.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 0 # m_casco
        except:
            pass
    bm_cup.free()

    # 2. Ranura emisiva neón horizontal
    bm_neon = bmesh.new()
    bmesh.ops.create_cone(
        bm_neon,
        cap_ends=False,
        cap_tris=False,
        segments=28,
        radius1=0.352,
        radius2=0.352,
        depth=0.02
    )
    for v in bm_neon.verts:
        v.co.z += 0.11
    vert_map = {}
    for v in bm_neon.verts:
        vert_map[v] = bm.verts.new(v.co)
    for f in bm_neon.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 1 # m_neon
        except:
            pass
    bm_neon.free()

    # 3. Collar cilíndrico medio
    bm_collar = bmesh.new()
    bmesh.ops.create_cone(
        bm_collar,
        cap_ends=False,
        cap_tris=False,
        segments=28,
        radius1=0.355,
        radius2=0.350,
        depth=0.10
    )
    for v in bm_collar.verts:
        v.co.z += 0.05
    vert_map = {}
    for v in bm_collar.verts:
        vert_map[v] = bm.verts.new(v.co)
    for f in bm_collar.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 0 # m_casco
        except:
            pass
    bm_collar.free()

    # 4. Placa base inferior cónica
    bm_base = bmesh.new()
    bmesh.ops.create_cone(
        bm_base,
        cap_ends=True,
        cap_tris=False,
        segments=28,
        radius1=0.25,
        radius2=0.355,
        depth=0.08
    )
    for v in bm_base.verts:
        v.co.z -= 0.04
    vert_map = {}
    for v in bm_base.verts:
        vert_map[v] = bm.verts.new(v.co)
    for f in bm_base.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 3 # m_detalles
        except:
            pass
    bm_base.free()

def construir_ojo(bm):
    """Genera el gran ojo central frontal (+Y)."""
    rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
    trans_ojo = mathutils.Matrix.Translation((0.0, 0.32, 0.08))

    # 1. Marco exterior biselado
    bm_marco = bmesh.new()
    bmesh.ops.create_cone(
        bm_marco,
        cap_ends=False,
        cap_tris=False,
        segments=24,
        radius1=0.13,
        radius2=0.14,
        depth=0.07
    )
    bmesh.ops.transform(bm_marco, matrix=rot_x, verts=bm_marco.verts)
    vert_map = {}
    for v in bm_marco.verts:
        vert_map[v] = bm.verts.new(trans_ojo @ v.co)
    for f in bm_marco.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 3 # m_detalles
        except:
            pass
    bm_marco.free()

    # 2. Anillo interior de sujeción
    bm_aro = bmesh.new()
    bmesh.ops.create_cone(
        bm_aro,
        cap_ends=False,
        cap_tris=False,
        segments=24,
        radius1=0.105,
        radius2=0.115,
        depth=0.04
    )
    bmesh.ops.transform(bm_aro, matrix=rot_x, verts=bm_aro.verts)
    vert_map = {}
    for v in bm_aro.verts:
        vert_map[v] = bm.verts.new(trans_ojo @ (v.co + mathutils.Vector((0, 0.02, 0))))
    for f in bm_aro.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 0 # m_casco
        except:
            pass
    bm_aro.free()

    # 3. Lente esférica emisiva
    bm_lente = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm_lente,
        u_segments=24,
        v_segments=16,
        radius=0.095
    )
    scale_y = mathutils.Matrix.Scale(0.45, 4, mathutils.Vector((0, 1, 0)))
    bmesh.ops.transform(bm_lente, matrix=scale_y, verts=bm_lente.verts)
    vert_map = {}
    for v in bm_lente.verts:
        vert_map[v] = bm.verts.new(trans_ojo @ (v.co + mathutils.Vector((0, 0.025, 0))))
    for f in bm_lente.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 2 # m_ojo
        except:
            pass
    bm_lente.free()

def construir_propulsores(bm):
    """
    Genera los propulsores laterales de longitud extendida hacia -Y
    para alcanzar un ancho total X ≈ 1.20 y profundidad balanceada.
    """
    rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

    for lado in [-1.0, 1.0]:
        offset = mathutils.Vector((lado * 0.515, -0.16, 0.02))
        rot_z = mathutils.Matrix.Rotation(math.radians(lado * -5.0), 4, 'Z')
        mat_pod = mathutils.Matrix.Translation(offset) @ rot_z

        # Cilindro del pod
        bm_pod = bmesh.new()
        bmesh.ops.create_cone(
            bm_pod,
            cap_ends=True,
            cap_tris=False,
            segments=18,
            radius1=0.075,
            radius2=0.075,
            depth=0.38
        )
        bmesh.ops.transform(bm_pod, matrix=rot_x, verts=bm_pod.verts)
        vert_map = {}
        for v in bm_pod.verts:
            vert_map[v] = bm.verts.new(mat_pod @ v.co)
        for f in bm_pod.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0 # m_casco
            except:
                pass
        bm_pod.free()

        # Tobera trasera (-Y)
        bm_tob = bmesh.new()
        bmesh.ops.create_cone(
            bm_tob,
            cap_ends=False,
            cap_tris=False,
            segments=18,
            radius1=0.082,
            radius2=0.065,
            depth=0.08
        )
        bmesh.ops.transform(bm_tob, matrix=rot_x, verts=bm_tob.verts)
        vert_map = {}
        for v in bm_tob.verts:
            v_co = v.co + mathutils.Vector((0, -0.21, 0))
            vert_map[v] = bm.verts.new(mat_pod @ v_co)
        for f in bm_tob.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # m_detalles
            except:
                pass
        bm_tob.free()

        # Núcleo emisivo neón de la tobera
        bm_llama = bmesh.new()
        bmesh.ops.create_cone(
            bm_llama,
            cap_ends=True,
            cap_tris=False,
            segments=18,
            radius1=0.058,
            radius2=0.058,
            depth=0.02
        )
        bmesh.ops.transform(bm_llama, matrix=rot_x, verts=bm_llama.verts)
        vert_map = {}
        for v in bm_llama.verts:
            v_co = v.co + mathutils.Vector((0, -0.22, 0))
            vert_map[v] = bm.verts.new(mat_pod @ v_co)
        for f in bm_llama.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1 # m_neon
            except:
                pass
        bm_llama.free()

        # Soporte alar
        bm_sop = bmesh.new()
        bmesh.ops.create_cube(bm_sop, size=0.08)
        scale_sop = mathutils.Matrix.Diagonal((2.2, 0.8, 0.25, 1.0))
        bmesh.ops.transform(bm_sop, matrix=scale_sop, verts=bm_sop.verts)
        sop_offset = mathutils.Vector((lado * 0.40, -0.12, 0.02))
        vert_map = {}
        for v in bm_sop.verts:
            vert_map[v] = bm.verts.new(v.co + sop_offset)
        for f in bm_sop.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # m_detalles
            except:
                pass
        bm_sop.free()

def definir_rutas_tentaculos():
    """
    Genera los 6 tentáculos con curvatura hidrodinámica que se extienden
    hacia atrás (-Y) y abajo, manteniendo el alto total Z ≈ 0.60 y profundidad Y ≈ 1.00.
    """
    configs = [
        # Frontal Izquierdo (FL)
        {
            'nombre': "T_FL",
            'base': mathutils.Vector((-0.10, 0.12, -0.06)),
            'curl_y': -0.22, # curva hacia atrás
            'curl_x': -0.08,
            'profundidad_z': -0.16,
        },
        # Frontal Derecho (FR)
        {
            'nombre': "T_FR",
            'base': mathutils.Vector((0.10, 0.12, -0.06)),
            'curl_y': -0.22,
            'curl_x': 0.08,
            'profundidad_z': -0.16,
        },
        # Medio Izquierdo (ML)
        {
            'nombre': "T_ML",
            'base': mathutils.Vector((-0.18, 0.00, -0.06)),
            'curl_y': -0.32,
            'curl_x': -0.16,
            'profundidad_z': -0.17,
        },
        # Medio Derecho (MR)
        {
            'nombre': "T_MR",
            'base': mathutils.Vector((0.18, 0.00, -0.06)),
            'curl_y': -0.32,
            'curl_x': 0.16,
            'profundidad_z': -0.17,
        },
        # Trasero Izquierdo (BL)
        {
            'nombre': "T_BL",
            'base': mathutils.Vector((-0.11, -0.12, -0.06)),
            'curl_y': -0.42, # llega hasta Y ≈ -0.54
            'curl_x': -0.10,
            'profundidad_z': -0.15,
        },
        # Trasero Derecho (BR)
        {
            'nombre': "T_BR",
            'base': mathutils.Vector((0.11, -0.12, -0.06)),
            'curl_y': -0.42,
            'curl_x': 0.10,
            'profundidad_z': -0.15,
        },
    ]

    tentaculos = []
    for cfg in configs:
        b = cfg['base']
        cx = cfg['curl_x']
        cy = cfg['curl_y']
        pz = cfg['profundidad_z']

        p0 = b
        p1 = b + mathutils.Vector((cx * 0.20, cy * 0.18, pz * 0.25))
        p2 = b + mathutils.Vector((cx * 0.50, cy * 0.45, pz * 0.55))
        p3 = b + mathutils.Vector((cx * 0.80, cy * 0.75, pz * 0.80))
        p4 = b + mathutils.Vector((cx * 1.05, cy * 1.05, pz * 1.00))

        puntos = [p0, p1, p2, p3, p4]
        dirs = [(puntos[i+1] - puntos[i]).normalized() for i in range(4)]
        dirs.append(dirs[-1])

        tentaculos.append({
            'nombre': cfg['nombre'],
            'puntos': puntos,
            'direcciones': dirs
        })

    return tentaculos

def construir_tentaculos(bm, defs_tentaculos):
    """Construye los 6 tentáculos mecánicos segmentados."""
    grupos_bm_verts = {}

    for tent in defs_tentaculos:
        nombre_base = tent['nombre']
        puntos = tent['puntos']

        for seg_idx in range(4):
            nombre_hueso = f"{nombre_base}_{seg_idx+1}"
            grupos_bm_verts[nombre_hueso] = []

            p_ini = puntos[seg_idx]
            p_fin = puntos[seg_idx+1]
            vec_dir = (p_fin - p_ini)
            longitud = vec_dir.length
            centro = (p_ini + p_fin) / 2.0

            dir_norm = vec_dir.normalized() if vec_dir.length > 0.0001 else mathutils.Vector((0, 0, -1))
            rot_quat = dir_norm.to_track_quat('Z', 'Y')
            mat_seg = mathutils.Matrix.Translation(centro) @ rot_quat.to_matrix().to_4x4()

            # Eslabón mecánico
            bm_seg = bmesh.new()
            bmesh.ops.create_cube(bm_seg, size=1.0)
            scale_mat = mathutils.Matrix.Diagonal((0.052, 0.042, longitud * 0.90, 1.0))
            bmesh.ops.transform(bm_seg, matrix=scale_mat, verts=bm_seg.verts)

            # Barra neón en la cara exterior
            bm_neon_bar = bmesh.new()
            bmesh.ops.create_cube(bm_neon_bar, size=1.0)
            scale_neon = mathutils.Matrix.Diagonal((0.026, 0.012, longitud * 0.55, 1.0))
            trans_neon = mathutils.Matrix.Translation((0.0, 0.022, 0.0))
            bmesh.ops.transform(bm_neon_bar, matrix=trans_neon @ scale_neon, verts=bm_neon_bar.verts)

            # Insertar eslabón
            vert_map = {}
            for v in bm_seg.verts:
                v_w = mat_seg @ v.co
                nv = bm.verts.new(v_w)
                vert_map[v] = nv
                grupos_bm_verts[nombre_hueso].append(nv)
            for f in bm_seg.faces:
                try:
                    nf = bm.faces.new([vert_map[v] for v in f.verts])
                    nf.material_index = 0 # m_casco
                except:
                    pass
            bm_seg.free()

            # Insertar barra neón
            vert_map = {}
            for v in bm_neon_bar.verts:
                v_w = mat_seg @ v.co
                nv = bm.verts.new(v_w)
                vert_map[v] = nv
                grupos_bm_verts[nombre_hueso].append(nv)
            for f in bm_neon_bar.faces:
                try:
                    nf = bm.faces.new([vert_map[v] for v in f.verts])
                    nf.material_index = 1 # m_neon
                except:
                    pass
            bm_neon_bar.free()

            # Rótula cilíndrica
            bm_rotula = bmesh.new()
            bmesh.ops.create_cone(
                bm_rotula,
                cap_ends=True,
                cap_tris=False,
                segments=12,
                radius1=0.028,
                radius2=0.028,
                depth=0.056
            )
            rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
            trans_rotula = mathutils.Matrix.Translation(p_ini)
            mat_rot = trans_rotula @ rot_quat.to_matrix().to_4x4() @ rot_x
            vert_map = {}
            for v in bm_rotula.verts:
                v_w = mat_rot @ v.co
                nv = bm.verts.new(v_w)
                vert_map[v] = nv
                grupos_bm_verts[nombre_hueso].append(nv)
            for f in bm_rotula.faces:
                try:
                    nf = bm.faces.new([vert_map[v] for v in f.verts])
                    nf.material_index = 3 # m_detalles
                except:
                    pass
            bm_rotula.free()

        # Garra terminal
        nombre_garra = f"{nombre_base}_garra"
        grupos_bm_verts[nombre_garra] = []
        p_tip = puntos[4]
        dir_tip = (puntos[4] - puntos[3]).normalized()
        rot_claw = dir_tip.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_claw_base = mathutils.Matrix.Translation(p_tip) @ rot_claw

        bm_claw_base = bmesh.new()
        bmesh.ops.create_cone(
            bm_claw_base,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.026,
            radius2=0.018,
            depth=0.035
        )
        vert_map = {}
        for v in bm_claw_base.verts:
            v_w = mat_claw_base @ v.co
            nv = bm.verts.new(v_w)
            vert_map[v] = nv
            grupos_bm_verts[nombre_garra].append(nv)
        for f in bm_claw_base.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # m_detalles
            except:
                pass
        bm_claw_base.free()

        for dedo_lado in [-1.0, 1.0]:
            bm_dedo = bmesh.new()
            bmesh.ops.create_cone(
                bm_dedo,
                cap_ends=True,
                cap_tris=False,
                segments=8,
                radius1=0.012,
                radius2=0.003,
                depth=0.045
            )
            rot_dedo = mathutils.Matrix.Rotation(math.radians(dedo_lado * 18.0), 4, 'X')
            trans_dedo = mathutils.Matrix.Translation((dedo_lado * 0.014, 0.0, 0.028))
            mat_dedo = mat_claw_base @ trans_dedo @ rot_dedo
            vert_map = {}
            for v in bm_dedo.verts:
                v_w = mat_dedo @ v.co
                nv = bm.verts.new(v_w)
                vert_map[v] = nv
                grupos_bm_verts[nombre_garra].append(nv)
            for f in bm_dedo.faces:
                try:
                    nf = bm.faces.new([vert_map[v] for v in f.verts])
                    nf.material_index = 0 # m_casco
                except:
                    pass
            bm_dedo.free()

    return grupos_bm_verts

def crear_armature_y_rig(col, defs_tentaculos, obj_mesh, indices_pesos):
    """Crea el Armature mínimo con pesos rígidos 1.0."""
    arm_data = bpy.data.armatures.new("enemigo_a_armature_data")
    arm_obj = bpy.data.objects.new("enemigo_a_armature", arm_data)
    col.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm_data.edit_bones

    # 1. Root en el origen (0, 0, 0)
    b_root = ebones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    # 2. Body en el centro del casco
    b_body = ebones.new("body")
    b_body.head = (0, 0, 0.05)
    b_body.tail = (0, 0, 0.22)
    b_body.parent = b_root

    # 3. Eye
    b_eye = ebones.new("eye")
    b_eye.head = (0, 0.30, 0.08)
    b_eye.tail = (0, 0.38, 0.08)
    b_eye.parent = b_body

    # 4. Huesos de los tentáculos
    for tent in defs_tentaculos:
        nombre_base = tent['nombre']
        puntos = tent['puntos']

        padre = b_body
        for seg_idx in range(4):
            b_name = f"{nombre_base}_{seg_idx+1}"
            b_seg = ebones.new(b_name)
            b_seg.head = puntos[seg_idx]
            b_seg.tail = puntos[seg_idx+1]
            b_seg.parent = padre
            padre = b_seg

        b_garra = ebones.new(f"{nombre_base}_garra")
        b_garra.head = puntos[4]
        dir_tip = (puntos[4] - puntos[3]).normalized()
        b_garra.tail = puntos[4] + dir_tip * 0.045
        b_garra.parent = padre

    bpy.ops.object.mode_set(mode='OBJECT')

    # Modificador Armature
    mod_arm = obj_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod_arm.object = arm_obj
    obj_mesh.parent = arm_obj

    # Asignar Vertex Groups
    vg_body = obj_mesh.vertex_groups.new(name="body")
    vg_eye = obj_mesh.vertex_groups.new(name="eye")

    verts_tentaculos = set()
    for b_name, idx_list in indices_pesos.items():
        vg = obj_mesh.vertex_groups.new(name=b_name)
        verts_tentaculos.update(idx_list)
        if idx_list:
            vg.add(idx_list, 1.0, 'REPLACE')

    v_body_indices = []
    v_eye_indices = []
    for v in obj_mesh.data.vertices:
        if v.index not in verts_tentaculos:
            if v.co.y > 0.25 and v.co.z > 0.01 and abs(v.co.x) < 0.17:
                v_eye_indices.append(v.index)
            else:
                v_body_indices.append(v.index)

    if v_body_indices:
        vg_body.add(v_body_indices, 1.0, 'REPLACE')
    if v_eye_indices:
        vg_eye.add(v_eye_indices, 1.0, 'REPLACE')

    return arm_obj

def crear_animaciones(arm_obj):
    """
    Genera las 4 acciones exactas requeridas a 30 FPS:
    1. Idle-loop (45 frames / 1.5 s, bucle perfecto)
    2. Attack (15 frames / 0.5 s, anticipación y disparo)
    3. Hit (8 frames / 0.26 s, sacudida brusca)
    4. Death (24 frames / 0.8 s, contracción y caída inerte)
    """
    bpy.context.scene.render.fps = 30
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    def preparar_accion(nombre):
        act = bpy.data.actions.get(nombre)
        if act:
            bpy.data.actions.remove(act)
        act = bpy.data.actions.new(name=nombre)
        return act

    pose_bones = arm_obj.pose.bones
    for pb in pose_bones:
        pb.rotation_mode = 'XYZ'

    # 1. IDLE-LOOP (45 frames, 30 FPS, Frame 1 == Frame 45)
    act_idle = preparar_accion("Idle-loop")
    arm_obj.animation_data.action = act_idle

    for f in [1, 12, 23, 34, 45]:
        t = (f - 1) / 44.0 * 2.0 * math.pi

        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, 0.0, math.sin(t) * 0.012)
            pb_body.rotation_euler = (math.sin(t) * math.radians(1.5), 0.0, math.cos(t) * math.radians(0.8))
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_eye = pose_bones.get("eye")
        if pb_eye:
            pb_eye.rotation_euler = (math.sin(t) * math.radians(1.0), 0.0, 0.0)
            pb_eye.keyframe_insert(data_path="rotation_euler", frame=f)

        for idx_t, prefix in enumerate(["T_FL", "T_FR", "T_ML", "T_MR", "T_BL", "T_BR"]):
            fase_tentaculo = idx_t * (math.pi / 3.0)
            for s in range(1, 5):
                pb_s = pose_bones.get(f"{prefix}_{s}")
                if pb_s:
                    fase_seg = fase_tentaculo + s * 0.6
                    ang_x = math.sin(t + fase_seg) * math.radians(4.0 + s * 1.5)
                    ang_y = math.cos(t + fase_seg) * math.radians(2.0 + s * 1.0)
                    pb_s.rotation_euler = (ang_x, ang_y, 0.0)
                    pb_s.keyframe_insert(data_path="rotation_euler", frame=f)

            pb_g = pose_bones.get(f"{prefix}_garra")
            if pb_g:
                ang_g = math.sin(t + fase_tentaculo) * math.radians(3.0)
                pb_g.rotation_euler = (ang_g, 0.0, 0.0)
                pb_g.keyframe_insert(data_path="rotation_euler", frame=f)

    track_idle = arm_obj.animation_data.nla_tracks.new()
    track_idle.name = "Idle-loop"
    track_idle.strips.new("Idle-loop", 1, act_idle)

    # 2. ATTACK (15 frames, 30 FPS)
    act_atk = preparar_accion("Attack")
    arm_obj.animation_data.action = act_atk

    puntos_atk = [
        (1,  0.00,  0.00,  0.0,  0.0),
        (6, -0.04,  0.02,  9.0,  1.8),
        (9,  0.05, -0.01, -4.0, -1.2),
        (12, 0.01,  0.00,  1.0,  0.2),
        (15, 0.00,  0.00,  0.0,  0.0)
    ]

    for f, y_rec, z_lft, pitch, curl in puntos_atk:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, y_rec, z_lft)
            pb_body.rotation_euler = (math.radians(pitch), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_eye = pose_bones.get("eye")
        if pb_eye:
            eye_y = 0.03 if f == 9 else 0.0
            pb_eye.location = (0.0, eye_y, 0.0)
            pb_eye.keyframe_insert(data_path="location", frame=f)

        for prefix in ["T_FL", "T_FR", "T_ML", "T_MR", "T_BL", "T_BR"]:
            for s in range(1, 5):
                pb_s = pose_bones.get(f"{prefix}_{s}")
                if pb_s:
                    pb_s.rotation_euler = (math.radians(curl * (3.0 + s * 2.0)), 0.0, 0.0)
                    pb_s.keyframe_insert(data_path="rotation_euler", frame=f)
            pb_g = pose_bones.get(f"{prefix}_garra")
            if pb_g:
                pb_g.rotation_euler = (math.radians(curl * 5.0), 0.0, 0.0)
                pb_g.keyframe_insert(data_path="rotation_euler", frame=f)

    track_atk = arm_obj.animation_data.nla_tracks.new()
    track_atk.name = "Attack"
    track_atk.strips.new("Attack", 1, act_atk)

    # 3. HIT (8 frames, 30 FPS)
    act_hit = preparar_accion("Hit")
    arm_obj.animation_data.action = act_hit

    puntos_hit = [
        (1,  0.00,  0.00,   0.0,  0.0,  0.0),
        (2, -0.045, 0.025,  8.0, -5.0,  4.0),
        (4,  0.020, -0.010,-3.0,  2.0, -2.0),
        (6, -0.008, 0.005,  1.0, -1.0,  0.5),
        (8,  0.00,  0.00,   0.0,  0.0,  0.0)
    ]

    for f, yl, zl, pt, rl, yw in puntos_hit:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, zl)
            pb_body.rotation_euler = (math.radians(pt), math.radians(rl), math.radians(yw))
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        factor_inercia = 1.0 if f == 2 else (-0.4 if f == 4 else 0.0)
        for prefix in ["T_FL", "T_FR", "T_ML", "T_MR", "T_BL", "T_BR"]:
            for s in range(1, 5):
                pb_s = pose_bones.get(f"{prefix}_{s}")
                if pb_s:
                    pb_s.rotation_euler = (math.radians(factor_inercia * (4.0 + s * 3.0)), 0.0, 0.0)
                    pb_s.keyframe_insert(data_path="rotation_euler", frame=f)

    track_hit = arm_obj.animation_data.nla_tracks.new()
    track_hit.name = "Hit"
    track_hit.strips.new("Hit", 1, act_hit)

    # 4. DEATH (24 frames, 30 FPS)
    act_death = preparar_accion("Death")
    arm_obj.animation_data.action = act_death

    puntos_death = [
        (1,   0.00,  0.00,  0.0,  0.0,  0.0),
        (5,  -0.03,  0.03,  6.0, -8.0, -0.8),
        (12, -0.02, -0.04, 12.0, 18.0,  1.8),
        (18, -0.01, -0.07, 18.0, 24.0,  2.8),
        (24, -0.01, -0.08, 20.0, 25.0,  3.0)
    ]

    for f, yl, zl, pt, rl, curl in puntos_death:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, zl)
            pb_body.rotation_euler = (math.radians(pt), math.radians(rl), 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for prefix in ["T_FL", "T_FR", "T_ML", "T_MR", "T_BL", "T_BR"]:
            for s in range(1, 5):
                pb_s = pose_bones.get(f"{prefix}_{s}")
                if pb_s:
                    pb_s.rotation_euler = (math.radians(curl * (4.0 + s * 3.5)), 0.0, 0.0)
                    pb_s.keyframe_insert(data_path="rotation_euler", frame=f)
            pb_g = pose_bones.get(f"{prefix}_garra")
            if pb_g:
                pb_g.rotation_euler = (math.radians(curl * 6.0), 0.0, 0.0)
                pb_g.keyframe_insert(data_path="rotation_euler", frame=f)

    track_death = arm_obj.animation_data.nla_tracks.new()
    track_death.name = "Death"
    track_death.strips.new("Death", 1, act_death)

    # Pose de reposo por defecto
    arm_obj.animation_data.action = act_idle
    bpy.context.scene.frame_set(1)

def construir_enemigo_a():
    """Función constructora principal idempotente."""
    print("=" * 60)
    print("Iniciando construcción de Enemigo A ('Calamar')...")
    print("=" * 60)

    # 1. Limpiar colecciones previas
    utils_blender.limpiar_coleccion(NOMBRE_SRC)
    utils_blender.limpiar_coleccion(NOMBRE_EXPORT)

    col_src = utils_blender.obtener_o_crear_coleccion(NOMBRE_SRC)
    col_export = utils_blender.obtener_o_crear_coleccion(NOMBRE_EXPORT)

    # 2. Configurar materiales
    mats = configurar_materiales()

    # 3. Construir malla completa en un BMesh unificado
    bm = bmesh.new()
    construir_cupula_y_cuerpo(bm)
    construir_ojo(bm)
    construir_propulsores(bm)

    defs_tentaculos = definir_rutas_tentaculos()
    grupos_bm_verts = construir_tentaculos(bm, defs_tentaculos)

    # Extraer los índices enteros de vértices antes de liberar bm
    bm.verts.index_update()
    indices_pesos = {}
    for nombre_hueso, bm_verts_list in grupos_bm_verts.items():
        indices_pesos[nombre_hueso] = [v.index for v in bm_verts_list]

    # 4. Crear objeto de malla final
    mesh = bpy.data.meshes.new("enemigo_a_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj_mesh = bpy.data.objects.new("enemigo_a", mesh)
    col_src.objects.link(obj_mesh)

    # Asignar los 4 materiales
    obj_mesh.data.materials.append(mats['casco'])    # 0
    obj_mesh.data.materials.append(mats['neon'])     # 1
    obj_mesh.data.materials.append(mats['ojo'])      # 2
    obj_mesh.data.materials.append(mats['detalles']) # 3

    # 5. Modificadores High-Poly: Bevel por ángulo (2 segmentos) + Weighted Normal
    mod_bev = obj_mesh.modifiers.new(name="Bevel", type='BEVEL')
    mod_bev.limit_method = 'ANGLE'
    mod_bev.angle_limit = math.radians(35.0)
    mod_bev.width = 0.008
    mod_bev.segments = 2
    mod_bev.profile = 0.70

    mod_norm = obj_mesh.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True

    # Sombreado suave en todos los polígonos
    bpy.context.view_layer.objects.active = obj_mesh
    for p in mesh.polygons:
        p.use_smooth = True

    # 6. Crear Armature y Rigging
    arm_obj = crear_armature_y_rig(col_src, defs_tentaculos, obj_mesh, indices_pesos)

    # 7. Crear Animaciones NLA
    crear_animaciones(arm_obj)

    # 8. Medir AABB y centrar pivote en el centro exacto del volumen
    bpy.context.view_layer.update()
    min_co, max_co, tamano, centro = utils_blender.calcular_aabb([obj_mesh])
    print(f"[AABB Inicial] Min: {min_co}, Max: {max_co}, Tam: {tamano}, Centro: {centro}")

    offset_centro = mathutils.Vector((-centro[0], -centro[1], -centro[2]))

    # Desplazar la malla en Edit Mode o traslación
    bpy.context.view_layer.objects.active = obj_mesh
    mesh.transform(mathutils.Matrix.Translation(offset_centro))
    mesh.update()

    # Desplazar huesos del armature en Edit Mode
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

    # Aplicar escalas y rotaciones
    for o in [obj_mesh, arm_obj]:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        o.select_set(False)

    # 9. Mover a la colección EXPORT_enemigo_a
    col_src.objects.unlink(obj_mesh)
    col_src.objects.unlink(arm_obj)
    col_export.objects.link(arm_obj)
    col_export.objects.link(obj_mesh)

    # 10. Medir geometría y AABB final evaluado
    bpy.context.view_layer.update()
    min_final, max_final, tam_final, cen_final = utils_blender.calcular_aabb([obj_mesh])
    total_triangulos = utils_blender.contar_triangulos([obj_mesh])

    print("-" * 60)
    print("INFORME GEOMÉTRICO FINAL:")
    print(f"Total Triángulos Evaluados: {total_triangulos} (Presupuesto: 12,000 - 25,000)")
    print(f"Dimensiones Bounding Box (X x Y x Z en Blender): {tam_final[0]:.3f} x {tam_final[1]:.3f} x {tam_final[2]:.3f}")
    print(f"Dimensiones en Godot (Ancho x Alto x Profundidad): {tam_final[0]:.3f} x {tam_final[2]:.3f} x {tam_final[1]:.3f}")
    print(f"Centro del Bounding Box: ({cen_final[0]:.3f}, {cen_final[1]:.3f}, {cen_final[2]:.3f})")
    print("-" * 60)

    # 11. Guardar archivo .blend de trabajo
    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "enemigo_a.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] No se pudo guardar .blend: {e}")

    # 12. Exportar a .glb en ambas ubicaciones
    ruta_glb_1 = os.path.join(ws_dir, "assets", "models", "enemigos", "enemigo_a.glb")
    ruta_glb_2 = os.path.join(ws_dir, "Space invaders", "assets", "models", "enemigos", "enemigo_a.glb")

    utils_blender.exportar_glb(ruta_glb_1, [arm_obj, obj_mesh])
    # Copiar a la segunda ruta de forma directa y rápida
    import shutil
    shutil.copy2(ruta_glb_1, ruta_glb_2)
    print(f"[EXPORT GLB] Copia sincronizada en: {ruta_glb_2}")

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
    construir_enemigo_a()
