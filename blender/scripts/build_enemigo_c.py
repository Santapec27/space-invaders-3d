"""
blender/scripts/build_enemigo_c.py - Construcción, texturizado, rigging,
animación y exportación de Enemigo C ("Behemoth").
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

NOMBRE_SRC = "SRC_enemigo_c"
NOMBRE_EXPORT = "EXPORT_enemigo_c"

# Metas dimensionales (en Godot: X ancho ≈ 1.25, Y alto ≈ 0.60, Z profundidad ≈ 1.00)
OBJETIVO_X = 1.25
OBJETIVO_ALTO_Z = 0.60
OBJETIVO_PROF_Y = 1.00

def configurar_materiales():
    """Crea los 4 materiales arcade neon basados en Principled BSDF."""
    # 1. Casco: Gris azulado oscuro (#1B2030), liso y metálico
    mat_casco = utils_blender.crear_material(
        "m_casco_c",
        base_color=(0.011, 0.014, 0.028, 1.0),
        metallic=0.88,
        roughness=0.32
    )

    # 2. Acentos emisivos Neón: Rojo-Naranja (#FF4D2E)
    mat_neon = utils_blender.crear_material(
        "m_neon_rojo",
        base_color=(1.0, 0.057, 0.026, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(1.0, 0.057, 0.026, 1.0),
        emission_strength=3.0
    )

    # 3. Ojos / Núcleos de energía ámbar (#FF8C42)
    mat_ojos = utils_blender.crear_material(
        "m_ojos_behemoth",
        base_color=(1.0, 0.25, 0.05, 1.0),
        metallic=0.0,
        roughness=0.1,
        emission_color=(1.0, 0.20, 0.02, 1.0),
        emission_strength=3.8
    )

    # 4. Detalles mecánicos oscuros (blindaje interior, cañones, toberas)
    mat_detalles = utils_blender.crear_material(
        "m_detalles_c",
        base_color=(0.007, 0.009, 0.015, 1.0),
        metallic=0.94,
        roughness=0.22
    )

    return {
        'casco': mat_casco,
        'neon': mat_neon,
        'ojos': mat_ojos,
        'detalles': mat_detalles
    }

def construir_chasis_acorazado(bm):
    """Construye el casco angular masivo del Behemoth con blindaje pesado escalonado."""
    # 1. Bloque central acorazado (proa en cuña hacia +Y)
    bm_chasis = bmesh.new()
    bmesh.ops.create_cube(bm_chasis, size=1.0)
    # Ancho 0.74, Profundidad 0.70, Alto 0.24
    scale_c = mathutils.Matrix.Diagonal((0.74, 0.70, 0.24, 1.0))
    bmesh.ops.transform(bm_chasis, matrix=scale_c, verts=bm_chasis.verts)

    # Modelar forma de cuña acorazada (frente angulado hacia +Y)
    for v in bm_chasis.verts:
        if v.co.y > 0:
            # Cuña en proa
            v.co.x *= (1.0 - (v.co.y / 0.35) * 0.35)
        if v.co.z > 0:
            v.co.x *= 0.88
            v.co.y *= 0.92

    bmesh.ops.bevel(
        bm_chasis,
        geom=bm_chasis.edges[:],
        offset=0.035,
        segments=2,
        profile=0.7
    )

    vert_map = {}
    for v in bm_chasis.verts:
        vert_map[v] = bm.verts.new(v.co + mathutils.Vector((0, 0.0, 0.06)))
    for f in bm_chasis.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = 0 # m_casco
        except:
            pass
    bm_chasis.free()

    # 2. Placas laterales de blindaje angular (hombros pesados)
    for lado in [-1.0, 1.0]:
        bm_hombro = bmesh.new()
        bmesh.ops.create_cube(bm_hombro, size=1.0)
        scale_h = mathutils.Matrix.Diagonal((0.26, 0.62, 0.20, 1.0))
        bmesh.ops.transform(bm_hombro, matrix=scale_h, verts=bm_hombro.verts)

        for v in bm_hombro.verts:
            if v.co.z > 0:
                v.co.x *= 0.75
            if v.co.y > 0:
                v.co.x *= 0.85

        bmesh.ops.bevel(
            bm_hombro,
            geom=bm_hombro.edges[:],
            offset=0.025,
            segments=2,
            profile=0.7
        )

        offset_h = mathutils.Vector((lado * 0.46, -0.04, 0.08))
        rot_y = mathutils.Matrix.Rotation(math.radians(lado * -6.0), 4, 'Y')
        mat_h = mathutils.Matrix.Translation(offset_h) @ rot_y

        vert_map = {}
        for v in bm_hombro.verts:
            vert_map[v] = bm.verts.new(mat_h @ v.co)
        for f in bm_hombro.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0 # m_casco
            except:
                pass
        bm_hombro.free()

        # Ranuras neón longitudinales en los hombros
        bm_hn = bmesh.new()
        bmesh.ops.create_cube(bm_hn, size=1.0)
        scale_hn = mathutils.Matrix.Diagonal((0.025, 0.52, 0.018, 1.0))
        trans_hn = mathutils.Matrix.Translation((lado * 0.08, 0.0, 0.105))
        bmesh.ops.transform(bm_hn, matrix=trans_hn @ scale_hn, verts=bm_hn.verts)

        vert_map = {}
        for v in bm_hn.verts:
            vert_map[v] = bm.verts.new(mat_h @ v.co)
        for f in bm_hn.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1 # m_neon_rojo
            except:
                pass
        bm_hn.free()

    # 3. Ranuras frontales neón en el chasis
    bm_fn = bmesh.new()
    bmesh.ops.create_cube(bm_fn, size=1.0)
    scale_fn = mathutils.Matrix.Diagonal((0.44, 0.02, 0.016, 1.0))
    bmesh.ops.transform(bm_fn, matrix=scale_fn, verts=bm_fn.verts)

    for z_off in [0.02, 0.12]:
        vert_map = {}
        for v in bm_fn.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((0, 0.32, z_off)))
        for f in bm_fn.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1
            except:
                pass
    bm_fn.free()

    # 4. Cluster de sensores / Ojos cuádruples frontales (+Y)
    rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
    ojos_coords = [
        (-0.15, 0.34, 0.08, 0.045), # Ojo izquierdo superior
        ( 0.15, 0.34, 0.08, 0.045), # Ojo derecho superior
        (-0.06, 0.35, 0.04, 0.038), # Ojo central-izq
        ( 0.06, 0.35, 0.04, 0.038), # Ojo central-der
    ]

    for ox, oy, oz, rad in ojos_coords:
        bm_o = bmesh.new()
        bmesh.ops.create_cone(
            bm_o,
            cap_ends=False,
            cap_tris=False,
            segments=16,
            radius1=rad * 1.15,
            radius2=rad * 1.30,
            depth=0.05
        )
        bmesh.ops.transform(bm_o, matrix=rot_x, verts=bm_o.verts)
        vert_map = {}
        for v in bm_o.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((ox, oy, oz)))
        for f in bm_o.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # m_detalles
            except:
                pass
        bm_o.free()

        bm_l = bmesh.new()
        bmesh.ops.create_uvsphere(bm_l, u_segments=16, v_segments=12, radius=rad)
        vert_map = {}
        for v in bm_l.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((ox, oy + 0.015, oz)))
        for f in bm_l.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 2 # m_ojos_behemoth
            except:
                pass
        bm_l.free()

    # 5. Cuatro toberas traseras masivas (-Y)
    toberas_coords = [
        (-0.24, -0.38, 0.06),
        (-0.08, -0.40, 0.06),
        ( 0.08, -0.40, 0.06),
        ( 0.24, -0.38, 0.06),
    ]

    for tx, ty, tz in toberas_coords:
        bm_tob = bmesh.new()
        bmesh.ops.create_cone(
            bm_tob,
            cap_ends=False,
            cap_tris=False,
            segments=16,
            radius1=0.065,
            radius2=0.050,
            depth=0.09
        )
        bmesh.ops.transform(bm_tob, matrix=rot_x, verts=bm_tob.verts)
        vert_map = {}
        for v in bm_tob.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((tx, ty, tz)))
        for f in bm_tob.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # m_detalles
            except:
                pass
        bm_tob.free()

        # Núcleo llama rojo neón
        bm_ll = bmesh.new()
        bmesh.ops.create_cone(
            bm_ll,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=0.044,
            radius2=0.044,
            depth=0.02
        )
        bmesh.ops.transform(bm_ll, matrix=rot_x, verts=bm_ll.verts)
        vert_map = {}
        for v in bm_ll.verts:
            vert_map[v] = bm.verts.new(v.co + mathutils.Vector((tx, ty - 0.03, tz)))
        for f in bm_ll.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1 # m_neon
            except:
                pass
        bm_ll.free()

def construir_canones_de_hombro(bm):
    """
    Construye dos cañones pesados de plasma sobre los hombros.
    Retorna {nombre_hueso: [bm_verts]}
    """
    grupos_canones = {'canon_L': [], 'canon_R': []}
    rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

    for lado, prefix in [(-1.0, "canon_L"), (1.0, "canon_R")]:
        offset_c = mathutils.Vector((lado * 0.44, 0.12, 0.20))

        # 1. Base del cañón / torreta
        bm_base = bmesh.new()
        bmesh.ops.create_cone(
            bm_base,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=0.065,
            radius2=0.055,
            depth=0.08
        )
        vert_map = {}
        for v in bm_base.verts:
            nv = bm.verts.new(v.co + offset_c)
            vert_map[v] = nv
            grupos_canones[prefix].append(nv)
        for f in bm_base.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_base.free()

        # 2. Cañón estriado (apunta a +Y)
        bm_tubo = bmesh.new()
        bmesh.ops.create_cone(
            bm_tubo,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=0.042,
            radius2=0.042,
            depth=0.32
        )
        bmesh.ops.transform(bm_tubo, matrix=rot_x, verts=bm_tubo.verts)
        vert_map = {}
        for v in bm_tubo.verts:
            nv = bm.verts.new(v.co + offset_c + mathutils.Vector((0, 0.16, 0.02)))
            vert_map[v] = nv
            grupos_canones[prefix].append(nv)
        for f in bm_tubo.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0 # m_casco
            except:
                pass
        bm_tubo.free()

        # 3. Anillos de energía neón rojo en el cañón
        for y_ring in [0.08, 0.18, 0.28]:
            bm_ring = bmesh.new()
            bmesh.ops.create_cone(
                bm_ring,
                cap_ends=False,
                cap_tris=False,
                segments=16,
                radius1=0.048,
                radius2=0.048,
                depth=0.025
            )
            bmesh.ops.transform(bm_ring, matrix=rot_x, verts=bm_ring.verts)
            vert_map = {}
            for v in bm_ring.verts:
                nv = bm.verts.new(v.co + offset_c + mathutils.Vector((0, y_ring, 0.02)))
                vert_map[v] = nv
                grupos_canones[prefix].append(nv)
            for f in bm_ring.faces:
                try:
                    nf = bm.faces.new([vert_map[v] for v in f.verts])
                    nf.material_index = 1 # m_neon
                except:
                    pass
            bm_ring.free()

        # 4. Boca del cañón con núcleo plasma ámbar
        bm_boca = bmesh.new()
        bmesh.ops.create_cone(
            bm_boca,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=0.032,
            radius2=0.032,
            depth=0.015
        )
        bmesh.ops.transform(bm_boca, matrix=rot_x, verts=bm_boca.verts)
        vert_map = {}
        for v in bm_boca.verts:
            nv = bm.verts.new(v.co + offset_c + mathutils.Vector((0, 0.325, 0.02)))
            vert_map[v] = nv
            grupos_canones[prefix].append(nv)
        for f in bm_boca.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 2 # m_ojos
            except:
                pass
        bm_boca.free()

    return grupos_canones

def construir_mandibulas_y_aletas(bm):
    """
    Construye dos colmillos/mandíbulas mecánicas frontales inferiores
    y dos aletas estabilizadoras laterales.
    Retorna {nombre_hueso: [bm_verts]}
    """
    grupos_partes = {
        'mandibula_L': [], 'mandibula_R': [],
        'aleta_L': [], 'aleta_R': []
    }

    # Mandíbulas inferiores (+Y frontal, abajo)
    for lado, prefix in [(-1.0, "mandibula_L"), (1.0, "mandibula_R")]:
        p_base = mathutils.Vector((lado * 0.20, 0.28, -0.06))
        p_tip = mathutils.Vector((lado * 0.12, 0.48, -0.16))
        vec_m = p_tip - p_base
        dir_m = vec_m.normalized()
        rot_m = dir_m.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat_m = mathutils.Matrix.Translation((p_base + p_tip) / 2.0) @ rot_m

        bm_mand = bmesh.new()
        bmesh.ops.create_cone(
            bm_mand,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.048,
            radius2=0.008,
            depth=vec_m.length
        )
        vert_map = {}
        for v in bm_mand.verts:
            nv = bm.verts.new(mat_m @ v.co)
            vert_map[v] = nv
            grupos_partes[prefix].append(nv)
        for f in bm_mand.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # m_detalles
            except:
                pass
        bm_mand.free()

        # Acento neón en la mandíbula
        bm_mn = bmesh.new()
        bmesh.ops.create_cube(bm_mn, size=1.0)
        scale_mn = mathutils.Matrix.Diagonal((0.016, 0.012, vec_m.length * 0.60, 1.0))
        trans_mn = mathutils.Matrix.Translation((lado * 0.02, 0.015, 0.0))
        bmesh.ops.transform(bm_mn, matrix=trans_mn @ scale_mn, verts=bm_mn.verts)
        vert_map = {}
        for v in bm_mn.verts:
            nv = bm.verts.new(mat_m @ v.co)
            vert_map[v] = nv
            grupos_partes[prefix].append(nv)
        for f in bm_mn.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 1 # m_neon
            except:
                pass
        bm_mn.free()

    # Aletas estabilizadoras laterales traseras
    for lado, prefix in [(-1.0, "aleta_L"), (1.0, "aleta_R")]:
        bm_aleta = bmesh.new()
        bmesh.ops.create_cube(bm_aleta, size=1.0)
        scale_al = mathutils.Matrix.Diagonal((0.18, 0.32, 0.025, 1.0))
        bmesh.ops.transform(bm_aleta, matrix=scale_al, verts=bm_aleta.verts)

        for v in bm_aleta.verts:
            if v.co.x * lado > 0:
                v.co.y *= 0.6
                v.co.z *= 0.5

        offset_al = mathutils.Vector((lado * 0.52, -0.22, 0.06))
        rot_y = mathutils.Matrix.Rotation(math.radians(lado * -15.0), 4, 'Y')
        mat_al = mathutils.Matrix.Translation(offset_al) @ rot_y

        vert_map = {}
        for v in bm_aleta.verts:
            nv = bm.verts.new(mat_al @ v.co)
            vert_map[v] = nv
            grupos_partes[prefix].append(nv)
        for f in bm_aleta.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 0 # m_casco
            except:
                pass
        bm_aleta.free()

    return grupos_partes

def crear_armature_y_rig(col, obj_mesh, indices_pesos):
    """
    Crea el Armature de Enemigo C ("Behemoth"):
    - root: en (0, 0, 0), INMÓVIL
    - body: centro del chasis
    - canon_L y canon_R: cañones de plasma de hombro
    - mandibula_L y mandibula_R: colmillos frontales articulados
    - aleta_L y aleta_R: alerones estabilizadores traseros
    """
    arm_data = bpy.data.armatures.new("enemigo_c_armature_data")
    arm_obj = bpy.data.objects.new("enemigo_c_armature", arm_data)
    col.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm_data.edit_bones

    # 1. Root
    b_root = ebones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    # 2. Body
    b_body = ebones.new("body")
    b_body.head = (0, 0, 0.06)
    b_body.tail = (0, 0, 0.24)
    b_body.parent = b_root

    # 3. Cañones de hombro
    for lado, prefix in [(-1.0, "canon_L"), (1.0, "canon_R")]:
        b_can = ebones.new(prefix)
        b_can.head = (lado * 0.44, 0.12, 0.20)
        b_can.tail = (lado * 0.44, 0.44, 0.22)
        b_can.parent = b_body

    # 4. Mandíbulas inferiores
    for lado, prefix in [(-1.0, "mandibula_L"), (1.0, "mandibula_R")]:
        b_man = ebones.new(prefix)
        b_man.head = (lado * 0.20, 0.28, -0.06)
        b_man.tail = (lado * 0.12, 0.48, -0.16)
        b_man.parent = b_body

    # 5. Aletas estabilizadoras
    for lado, prefix in [(-1.0, "aleta_L"), (1.0, "aleta_R")]:
        b_al = ebones.new(prefix)
        b_al.head = (lado * 0.46, -0.22, 0.06)
        b_al.tail = (lado * 0.60, -0.22, 0.06)
        b_al.parent = b_body

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
    """
    Genera las 4 acciones exactas a 30 FPS para Enemigo C:
    1. Idle-loop (45 frames / 1.5 s): bucle perfecto, oscilación pesada y pulso de cañones.
    2. Attack (15 frames / 0.5 s): retroceso de cañones de plasma y descarga con apertura de mandíbula.
    3. Hit (8 frames / 0.26 s): estremecimiento seco de blindaje pesado.
    4. Death (24 frames / 0.8 s): sobrecarga, cañones caen apuntando al suelo y colapso masivo.
    """
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
            pb_body.location = (0.0, 0.0, math.sin(t) * 0.008)
            pb_body.rotation_euler = (math.sin(t) * math.radians(0.8), 0.0, math.cos(t) * math.radians(0.5))
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        # Cañones oscilando sutilmente
        for prefix in ["canon_L", "canon_R"]:
            pb_c = pose_bones.get(prefix)
            if pb_c:
                pb_c.location = (0.0, math.sin(t) * 0.006, 0.0)
                pb_c.keyframe_insert(data_path="location", frame=f)

        # Mandíbulas moviéndose lentamente
        for lado_s, prefix in [(-1.0, "mandibula_L"), (1.0, "mandibula_R")]:
            pb_m = pose_bones.get(prefix)
            if pb_m:
                pb_m.rotation_euler = (0.0, 0.0, math.sin(t) * math.radians(lado_s * 3.0))
                pb_m.keyframe_insert(data_path="rotation_euler", frame=f)

        # Aletas
        for lado_s, prefix in [(-1.0, "aleta_L"), (1.0, "aleta_R")]:
            pb_al = pose_bones.get(prefix)
            if pb_al:
                pb_al.rotation_euler = (0.0, math.sin(t) * math.radians(lado_s * 2.0), 0.0)
                pb_al.keyframe_insert(data_path="rotation_euler", frame=f)

    track_idle = arm_obj.animation_data.nla_tracks.new()
    track_idle.name = "Idle-loop"
    track_idle.strips.new("Idle-loop", 1, act_idle)

    # 2. ATTACK (15 frames, 30 FPS)
    act_atk = preparar_accion("Attack")
    arm_obj.animation_data.action = act_atk

    puntos_atk = [
        # (frame, body_pitch, canon_recoil, mand_open)
        (1,   0.0,   0.00,   0.0),
        (6,   5.0,  -0.05,  15.0), # Carga de energía / retroceso de cañón
        (9,  -2.5,   0.02, -10.0), # Descarga de plasma hacia +Y
        (12,  1.0,  -0.01,   2.0),
        (15,  0.0,   0.00,   0.0)
    ]

    for f, pt, c_rec, m_op in puntos_atk:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.rotation_euler = (math.radians(pt), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for prefix in ["canon_L", "canon_R"]:
            pb_c = pose_bones.get(prefix)
            if pb_c:
                pb_c.location = (0.0, c_rec, 0.0)
                pb_c.keyframe_insert(data_path="location", frame=f)

        for lado_s, prefix in [(-1.0, "mandibula_L"), (1.0, "mandibula_R")]:
            pb_m = pose_bones.get(prefix)
            if pb_m:
                pb_m.rotation_euler = (0.0, 0.0, math.radians(lado_s * m_op))
                pb_m.keyframe_insert(data_path="rotation_euler", frame=f)

    track_atk = arm_obj.animation_data.nla_tracks.new()
    track_atk.name = "Attack"
    track_atk.strips.new("Attack", 1, act_atk)

    # 3. HIT (8 frames, 30 FPS)
    act_hit = preparar_accion("Hit")
    arm_obj.animation_data.action = act_hit

    puntos_hit = [
        (1,  0.00,  0.00,  0.0),
        (2, -0.03,  0.015, 6.0), # Impacto seco en blindaje pesado
        (4,  0.01, -0.006,-2.0),
        (6, -0.004, 0.002, 0.5),
        (8,  0.00,  0.00,  0.0)
    ]

    for f, yl, zl, pt in puntos_hit:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, zl)
            pb_body.rotation_euler = (math.radians(pt), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

    track_hit = arm_obj.animation_data.nla_tracks.new()
    track_hit.name = "Hit"
    track_hit.strips.new("Hit", 1, act_hit)

    # 4. DEATH (24 frames, 30 FPS)
    act_death = preparar_accion("Death")
    arm_obj.animation_data.action = act_death

    puntos_death = [
        (1,   0.00,  0.00,  0.0,   0.0),
        (5,  -0.02,  0.02,  5.0,  10.0), # Sobrecarga
        (12, -0.01, -0.04, 10.0, -25.0), # Cañones caen hacia abajo
        (18, -0.01, -0.07, 14.0, -35.0), # Colapso
        (24, -0.01, -0.08, 15.0, -40.0)  # Inerte
    ]

    for f, yl, zl, pt, c_pitch in puntos_death:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.location = (0.0, yl, zl)
            pb_body.rotation_euler = (math.radians(pt), 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        for prefix in ["canon_L", "canon_R"]:
            pb_c = pose_bones.get(prefix)
            if pb_c:
                pb_c.rotation_euler = (math.radians(c_pitch), 0.0, 0.0)
                pb_c.keyframe_insert(data_path="rotation_euler", frame=f)

    track_death = arm_obj.animation_data.nla_tracks.new()
    track_death.name = "Death"
    track_death.strips.new("Death", 1, act_death)

    arm_obj.animation_data.action = act_idle
    bpy.context.scene.frame_set(1)

def construir_enemigo_c():
    """Función constructora principal idempotente para Enemigo C ('Behemoth')."""
    print("=" * 60)
    print("Iniciando construcción de Enemigo C ('Behemoth')...")
    print("=" * 60)

    # 1. Limpieza de colecciones de Enemigo C y escena
    utils_blender.limpiar_coleccion(NOMBRE_SRC)
    utils_blender.limpiar_coleccion(NOMBRE_EXPORT)

    # Limpiar objetos anteriores para render limpio
    for name in ["enemigo_a", "enemigo_a_armature", "enemigo_b", "enemigo_b_armature"]:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    col_src = utils_blender.obtener_o_crear_coleccion(NOMBRE_SRC)
    col_export = utils_blender.obtener_o_crear_coleccion(NOMBRE_EXPORT)

    # 2. Materiales
    mats = configurar_materiales()

    # 3. Malla unificada
    bm = bmesh.new()
    construir_chasis_acorazado(bm)
    grupos_canones = construir_canones_de_hombro(bm)
    grupos_mandibulas = construir_mandibulas_y_aletas(bm)

    grupos_bm_verts = {}
    grupos_bm_verts.update(grupos_canones)
    grupos_bm_verts.update(grupos_mandibulas)

    bm.verts.index_update()
    indices_pesos = {}
    for nombre_hueso, bm_verts_list in grupos_bm_verts.items():
        indices_pesos[nombre_hueso] = [v.index for v in bm_verts_list]

    # 4. Crear objeto de malla
    mesh = bpy.data.meshes.new("enemigo_c_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj_mesh = bpy.data.objects.new("enemigo_c", mesh)
    col_src.objects.link(obj_mesh)

    obj_mesh.data.materials.append(mats['casco'])
    obj_mesh.data.materials.append(mats['neon'])
    obj_mesh.data.materials.append(mats['ojos'])
    obj_mesh.data.materials.append(mats['detalles'])

    # 5. Modificadores High-Poly (Bevel 4 segmentos + Weighted Normal)
    mod_bev = obj_mesh.modifiers.new(name="Bevel", type='BEVEL')
    mod_bev.limit_method = 'ANGLE'
    mod_bev.angle_limit = math.radians(35.0)
    mod_bev.width = 0.008
    mod_bev.segments = 4
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
    print("INFORME GEOMÉTRICO FINAL — ENEMIGO C:")
    print(f"Total Triángulos Evaluados: {total_triangulos} (Presupuesto: 12,000 - 25,000)")
    print(f"Dimensiones Bounding Box (Godot X x Y x Z): {tam_final[0]:.3f} x {tam_final[2]:.3f} x {tam_final[1]:.3f}")
    print(f"Centro del Bounding Box: ({cen_final[0]:.3f}, {cen_final[1]:.3f}, {cen_final[2]:.3f})")
    print("-" * 60)

    # 11. Guardar .blend
    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "enemigo_c.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # 12. Exportar .glb
    ruta_glb_1 = os.path.join(ws_dir, "assets", "models", "enemigos", "enemigo_c.glb")
    ruta_glb_2 = os.path.join(ws_dir, "Space invaders", "assets", "models", "enemigos", "enemigo_c.glb")

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
    construir_enemigo_c()
