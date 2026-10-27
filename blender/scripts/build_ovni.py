"""
blender/scripts/build_ovni.py - Construcción, texturizado, rigging,
animación y exportación del Ovni Bonus.
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

CONFIG_OVNI = {
    'nombre': "OVNI Bonus",
    'sufijo': "ovni_bonus",
    'color_neon': (1.0, 0.68, 0.02, 1.0),   # Amarillo / Oro arcade alienígena saturado (#F59E0B / #FACC15)
    'presupuesto_min': 20000,
    'presupuesto_max': 40000,
}

def configurar_materiales():
    """Crea los 5 materiales Principled BSDF para el Ovni Bonus."""
    col_neon = CONFIG_OVNI['color_neon']

    # 1. Casco disco oscuro pulido
    mat_casco = utils_blender.crear_material(
        "m_ovni_casco",
        base_color=(0.008, 0.011, 0.018, 1.0),
        metallic=0.92,
        roughness=0.22
    )

    # 2. Blindaje secundario grafito
    mat_blindaje = utils_blender.crear_material(
        "m_ovni_blindaje",
        base_color=(0.014, 0.018, 0.028, 1.0),
        metallic=0.88,
        roughness=0.35
    )

    # 3. Cúpula acristalada reflectante con tinte sutil
    mat_cupula = utils_blender.crear_material(
        "m_ovni_cupula",
        base_color=(0.020, 0.020, 0.012, 1.0),
        metallic=0.30,
        roughness=0.08
    )

    # 4. Mecanismo interior / turbinas
    mat_mecanismo = utils_blender.crear_material(
        "m_ovni_mecanismo",
        base_color=(0.005, 0.005, 0.008, 1.0),
        metallic=0.95,
        roughness=0.20
    )

    # 5. Neón amarillo / oro alienígena (Emisión 3.5)
    mat_neon = utils_blender.crear_material(
        "m_ovni_neon",
        base_color=col_neon,
        metallic=0.10,
        roughness=0.15,
        emission_color=col_neon,
        emission_strength=3.5
    )

    return {
        'casco': mat_casco,
        'blindaje': mat_blindaje,
        'cupula': mat_cupula,
        'mecanismo': mat_mecanismo,
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

def construir_ovni_malla(bm):
    """
    Construye la nave OVNI Bonus con acabado High Poly:
    - Platillo elíptico aerodinámico (48 segs) con labio perimetral biselado
    - Cúpula acristalada con anillo base y núcleo de energía interior
    - Anillo rotatorio exterior con 12 proyectores de luz neón
    - Emisores gravitatorios inferiores con anillos de plasma
    - Antenas sensoras superiores
    """
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    grupos = {
        'body': [],
        'ring_rot': [],
        'repulsor': [],
        'antenna': []
    }

    # 1. PLATILLO PRINCIPAL (Saucer Core Hull)
    # Cono truncado superior e inferior para formar el platillo lenticular
    bm_saucer = bmesh.new()
    bmesh.ops.create_cone(
        bm_saucer,
        cap_ends=True,
        cap_tris=False,
        segments=64,
        radius1=0.62,
        radius2=0.24,
        depth=0.14
    )
    tr_top = mathutils.Matrix.Translation((0, 0, 0.05))
    bmesh.ops.transform(bm_saucer, matrix=tr_top, verts=bm_saucer.verts)
    bmesh.ops.bevel(bm_saucer, geom=bm_saucer.edges[:], offset=0.008, segments=4)
    grupos['body'].extend(transferir_geom(bm_saucer, bm, mat_index=0))
    bm_saucer.free()

    # Vientre inferior del platillo
    bm_belly = bmesh.new()
    bmesh.ops.create_cone(
        bm_belly,
        cap_ends=True,
        cap_tris=False,
        segments=64,
        radius1=0.62,
        radius2=0.28,
        depth=0.12
    )
    tr_bot = mathutils.Matrix.Translation((0, 0, -0.05))
    bmesh.ops.transform(bm_belly, matrix=tr_bot, verts=bm_belly.verts)
    bmesh.ops.bevel(bm_belly, geom=bm_belly.edges[:], offset=0.008, segments=4)
    grupos['body'].extend(transferir_geom(bm_belly, bm, mat_index=1))
    bm_belly.free()

    # Brida de ecuador y canales neón perimetrales
    bm_flange = bmesh.new()
    bmesh.ops.create_cone(
        bm_flange,
        cap_ends=False,
        cap_tris=False,
        segments=64,
        radius1=0.645,
        radius2=0.645,
        depth=0.032
    )
    bmesh.ops.bevel(bm_flange, geom=bm_flange.edges[:], offset=0.004, segments=3)
    grupos['body'].extend(transferir_geom(bm_flange, bm, mat_index=4))
    bm_flange.free()

    # Anillo de canal neón interior en el casco superior
    bm_groove = bmesh.new()
    bmesh.ops.create_cone(
        bm_groove,
        cap_ends=False,
        cap_tris=False,
        segments=64,
        radius1=0.40,
        radius2=0.40,
        depth=0.015
    )
    tr_groove = mathutils.Matrix.Translation((0, 0, 0.082))
    bmesh.ops.transform(bm_groove, matrix=tr_groove, verts=bm_groove.verts)
    grupos['body'].extend(transferir_geom(bm_groove, bm, mat_index=4))
    bm_groove.free()

    # 24 Placas segmentadas de blindaje en el borde del disco
    for i in range(24):
        ang = (i / 24.0) * 2.0 * math.pi
        px = math.cos(ang) * 0.52
        py = math.sin(ang) * 0.52
        bm_p = bmesh.new()
        bmesh.ops.create_cube(bm_p, size=1.0)
        sc_p = mathutils.Matrix.Diagonal((0.065, 0.095, 0.022, 1.0))
        rot_p = mathutils.Euler((0, 0, ang)).to_matrix().to_4x4()
        tr_p = mathutils.Matrix.Translation((px, py, 0.038))
        bmesh.ops.transform(bm_p, matrix=tr_p @ rot_p @ sc_p, verts=bm_p.verts)
        bmesh.ops.bevel(bm_p, geom=bm_p.edges[:], offset=0.003, segments=2)
        grupos['body'].extend(transferir_geom(bm_p, bm, mat_index=1 if i % 2 == 0 else 0))
        bm_p.free()

    # 8 Aletas de refrigeración y disipadores en el vientre
    for v_i in range(8):
        ang_v = (v_i / 8.0) * 2.0 * math.pi
        vx = math.cos(ang_v) * 0.42
        vy = math.sin(ang_v) * 0.42
        bm_v = bmesh.new()
        bmesh.ops.create_cube(bm_v, size=1.0)
        sc_v = mathutils.Matrix.Diagonal((0.035, 0.12, 0.028, 1.0))
        rot_v = mathutils.Euler((0, 0, ang_v)).to_matrix().to_4x4()
        tr_v = mathutils.Matrix.Translation((vx, vy, -0.06))
        bmesh.ops.transform(bm_v, matrix=tr_v @ rot_v @ sc_v, verts=bm_v.verts)
        bmesh.ops.bevel(bm_v, geom=bm_v.edges[:], offset=0.002, segments=2)
        grupos['body'].extend(transferir_geom(bm_v, bm, mat_index=3))
        bm_v.free()

    # 2. CÚPULA SUPERIOR (Dome & Cockpit)
    # Cúpula acristalada semiesférica suavizada de alta definición (48 x 24)
    bm_dome = bmesh.new()
    bmesh.ops.create_uvsphere(bm_dome, u_segments=48, v_segments=24, radius=0.22)
    # Conservar semiesfera superior z >= -0.01
    verts_del = [v for v in bm_dome.verts if v.co.z < -0.005]
    if verts_del:
        bmesh.ops.delete(bm_dome, geom=verts_del, context='VERTS')
    # Escalar altura de la cúpula para perfil curvado elegante
    sc_dome = mathutils.Matrix.Diagonal((1.0, 1.0, 0.75, 1.0))
    tr_dome = mathutils.Matrix.Translation((0, 0, 0.11))
    bmesh.ops.transform(bm_dome, matrix=tr_dome @ sc_dome, verts=bm_dome.verts)
    bmesh.ops.bevel(bm_dome, geom=bm_dome.edges[:], offset=0.004, segments=2)
    grupos['body'].extend(transferir_geom(bm_dome, bm, mat_index=2))
    bm_dome.free()

    # Collar de sujeción de cúpula
    bm_collar = bmesh.new()
    bmesh.ops.create_cone(
        bm_collar,
        cap_ends=False,
        cap_tris=False,
        segments=48,
        radius1=0.235,
        radius2=0.235,
        depth=0.028
    )
    tr_col = mathutils.Matrix.Translation((0, 0, 0.11))
    bmesh.ops.transform(bm_collar, matrix=tr_col, verts=bm_collar.verts)
    bmesh.ops.bevel(bm_collar, geom=bm_collar.edges[:], offset=0.003, segments=2)
    grupos['body'].extend(transferir_geom(bm_collar, bm, mat_index=1))
    bm_collar.free()

    # Núcleo interior palpitante visible bajo la cúpula
    bm_core = bmesh.new()
    bmesh.ops.create_icosphere(bm_core, subdivisions=3, radius=0.09)
    tr_core = mathutils.Matrix.Translation((0, 0, 0.16))
    bmesh.ops.transform(bm_core, matrix=tr_core, verts=bm_core.verts)
    grupos['body'].extend(transferir_geom(bm_core, bm, mat_index=4)) # Emisión neón amarillo
    bm_core.free()

    # 3. ANTENAS SENSORAS SUPERIORES (3 antenas a 120°)
    for a_i in range(3):
        ang_a = (a_i / 3.0) * 2.0 * math.pi
        ax = math.cos(ang_a) * 0.15
        ay = math.sin(ang_a) * 0.15
        bm_ant = bmesh.new()
        bmesh.ops.create_cone(
            bm_ant,
            cap_ends=True,
            cap_tris=False,
            segments=20,
            radius1=0.016,
            radius2=0.006,
            depth=0.15
        )
        tr_ant = mathutils.Matrix.Translation((ax, ay, 0.28))
        bmesh.ops.transform(bm_ant, matrix=tr_ant, verts=bm_ant.verts)
        bmesh.ops.bevel(bm_ant, geom=bm_ant.edges[:], offset=0.002, segments=2)
        grupos['antenna'].extend(transferir_geom(bm_ant, bm, mat_index=1))
        bm_ant.free()

        # Esfera terminal neón
        bm_tip = bmesh.new()
        bmesh.ops.create_uvsphere(bm_tip, u_segments=16, v_segments=12, radius=0.018)
        tr_tip = mathutils.Matrix.Translation((ax, ay, 0.36))
        bmesh.ops.transform(bm_tip, matrix=tr_tip, verts=bm_tip.verts)
        grupos['antenna'].extend(transferir_geom(bm_tip, bm, mat_index=4))
        bm_tip.free()

    # 4. ANILLO GIRATORIO PERIFÉRICO (Rotating Ring - Hueso ring_rot)
    # Anillo exterior levitante de alta precisión
    bm_ring = bmesh.new()
    bmesh.ops.create_cone(
        bm_ring,
        cap_ends=False,
        cap_tris=False,
        segments=64,
        radius1=0.73,
        radius2=0.73,
        depth=0.034
    )
    bmesh.ops.bevel(bm_ring, geom=bm_ring.edges[:], offset=0.004, segments=2)
    grupos['ring_rot'].extend(transferir_geom(bm_ring, bm, mat_index=1))
    bm_ring.free()

    # 16 Proyectores / Faros de luz giratorios en el anillo
    for l_i in range(16):
        ang_l = (l_i / 16.0) * 2.0 * math.pi
        lx = math.cos(ang_l) * 0.73
        ly = math.sin(ang_l) * 0.73
        bm_lamp = bmesh.new()
        bmesh.ops.create_cube(bm_lamp, size=1.0)
        sc_lamp = mathutils.Matrix.Diagonal((0.036, 0.048, 0.026, 1.0))
        rot_lamp = mathutils.Euler((0, 0, ang_l)).to_matrix().to_4x4()
        tr_lamp = mathutils.Matrix.Translation((lx, ly, 0.0))
        bmesh.ops.transform(bm_lamp, matrix=tr_lamp @ rot_lamp @ sc_lamp, verts=bm_lamp.verts)
        bmesh.ops.bevel(bm_lamp, geom=bm_lamp.edges[:], offset=0.003, segments=2)
        grupos['ring_rot'].extend(transferir_geom(bm_lamp, bm, mat_index=4)) # Luz neón amarilla
        bm_lamp.free()

    # 5. EMISORES GRAVITATORIOS INFERIORES (Repulsor Core - Hueso repulsor)
    # Núcleo ventral principal
    bm_ventral = bmesh.new()
    bmesh.ops.create_cone(
        bm_ventral,
        cap_ends=True,
        cap_tris=False,
        segments=48,
        radius1=0.22,
        radius2=0.15,
        depth=0.09
    )
    tr_ven = mathutils.Matrix.Translation((0, 0, -0.13))
    bmesh.ops.transform(bm_ventral, matrix=tr_ven, verts=bm_ventral.verts)
    bmesh.ops.bevel(bm_ventral, geom=bm_ventral.edges[:], offset=0.004, segments=2)
    grupos['repulsor'].extend(transferir_geom(bm_ventral, bm, mat_index=3))
    bm_ventral.free()

    # 3 Emisores gravitatorios en triángulo a 120°
    for r_i in range(3):
        ang_r = (r_i / 3.0) * 2.0 * math.pi
        rx = math.cos(ang_r) * 0.16
        ry = math.sin(ang_r) * 0.16

        bm_rep = bmesh.new()
        bmesh.ops.create_cone(
            bm_rep,
            cap_ends=True,
            cap_tris=False,
            segments=32,
            radius1=0.07,
            radius2=0.048,
            depth=0.10
        )
        tr_rep = mathutils.Matrix.Translation((rx, ry, -0.16))
        bmesh.ops.transform(bm_rep, matrix=tr_rep, verts=bm_rep.verts)
        bmesh.ops.bevel(bm_rep, geom=bm_rep.edges[:], offset=0.003, segments=2)
        grupos['repulsor'].extend(transferir_geom(bm_rep, bm, mat_index=3))
        bm_rep.free()

        # Doble anillo de plasma gravitatorio
        for dz, rad_p in [(-0.19, 0.056), (-0.22, 0.042)]:
            bm_p = bmesh.new()
            bmesh.ops.create_cone(
                bm_p,
                cap_ends=False,
                cap_tris=False,
                segments=28,
                radius1=rad_p,
                radius2=rad_p,
                depth=0.014
            )
            tr_p = mathutils.Matrix.Translation((rx, ry, dz))
            bmesh.ops.transform(bm_p, matrix=tr_p, verts=bm_p.verts)
            grupos['repulsor'].extend(transferir_geom(bm_p, bm, mat_index=4))
            bm_p.free()

    return grupos

def crear_armature_y_rigging(obj_mesh, col, grupos_indices):
    """
    Crea el Armature del OVNI:
    - root en (0,0,0) ESTACIONARIO (crítico para Tweens de Godot)
    - body (disco central)
    - ring_rot (anillo giratorio)
    - repulsor (tren gravitatorio)
    - antenna (sensores)
    """
    arm_data = bpy.data.armatures.new("Armature_ovni_bonus")
    arm_obj = bpy.data.objects.new("ovni_bonus", arm_data)
    col.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    # 1. Hueso root ESTACIONARIO en (0,0,0)
    b_root = arm_data.edit_bones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    # 2. Hueso body
    b_body = arm_data.edit_bones.new("body")
    b_body.head = (0, 0, 0.0)
    b_body.tail = (0, 0, 0.15)
    b_body.parent = b_root

    # 3. Hueso ring_rot (anillo giratorio sobre el eje Z)
    b_ring = arm_data.edit_bones.new("ring_rot")
    b_ring.head = (0, 0, 0.0)
    b_ring.tail = (0, 0, 0.20)
    b_ring.parent = b_body

    # 4. Hueso repulsor
    b_rep = arm_data.edit_bones.new("repulsor")
    b_rep.head = (0, 0, -0.05)
    b_rep.tail = (0, 0, -0.22)
    b_rep.parent = b_body

    # 5. Hueso antenna
    b_ant = arm_data.edit_bones.new("antenna")
    b_ant.head = (0, 0, 0.20)
    b_ant.tail = (0, 0, 0.40)
    b_ant.parent = b_body

    bpy.ops.object.mode_set(mode='OBJECT')

    # Modificador Armature
    mod_arm = obj_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod_arm.object = arm_obj
    obj_mesh.parent = arm_obj

    # Asignar grupos de vértices
    for nombre_hueso, v_indices in grupos_indices.items():
        if v_indices and nombre_hueso in arm_data.bones:
            vg = obj_mesh.vertex_groups.new(name=nombre_hueso)
            vg.add(v_indices, 1.0, 'REPLACE')

    return arm_obj

def crear_animaciones_ovni(arm_obj):
    """
    Crea las 2 acciones NLA requeridas:
    1. Idle-loop (60 frames / 2.0 s, 30 FPS - rotación 360 continua de ring_rot y pulso repulsor)
    2. Death (24 frames / 0.8 s, 30 FPS - desestabilización, desacople de anillo y sobrecarga)
    REGLA CRÍTICA: root ESTACIONARIO sin keyframes.
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

    # 1. IDLE-LOOP (60 frames / 2.0 s, 30 FPS - Bucle continuo perfecto)
    act_idle = preparar_accion("Idle-loop")
    arm_obj.animation_data.action = act_idle

    for f in range(1, 61, 5):
        t = (f - 1) / 59.0
        ang_rot = t * 360.0  # Giro completo continuo de 360°

        pb_ring = pose_bones.get("ring_rot")
        if pb_ring:
            pb_ring.rotation_euler = (0.0, 0.0, math.radians(ang_rot))
            pb_ring.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_body = pose_bones.get("body")
        if pb_body:
            # Levitación vertical suave en Z
            z_hover = math.sin(t * 2.0 * math.pi) * 0.015
            pitch_bob = math.sin(t * 2.0 * math.pi) * math.radians(1.2)
            pb_body.location = (0.0, 0.0, z_hover)
            pb_body.rotation_euler = (pitch_bob, 0.0, 0.0)
            pb_body.keyframe_insert(data_path="location", frame=f)
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_rep = pose_bones.get("repulsor")
        if pb_rep:
            sc_rep = 1.0 + math.sin(t * 4.0 * math.pi) * 0.08  # Pulsación gravitatoria rápida
            pb_rep.scale = (sc_rep, sc_rep, 1.0)
            pb_rep.keyframe_insert(data_path="scale", frame=f)

        pb_ant = pose_bones.get("antenna")
        if pb_ant:
            ant_flex = math.cos(t * 2.0 * math.pi) * math.radians(1.5)
            pb_ant.rotation_euler = (0.0, ant_flex, 0.0)
            pb_ant.keyframe_insert(data_path="rotation_euler", frame=f)

    track_idle = arm_obj.animation_data.nla_tracks.new()
    track_idle.name = "Idle-loop"
    track_idle.strips.new("Idle-loop", 1, act_idle)

    # 2. DEATH (24 frames / 0.8 s, 30 FPS)
    act_death = preparar_accion("Death")
    arm_obj.animation_data.action = act_death

    puntos_death = [
        # f, body_rot, ring_pitch, ring_z, rep_sc
        (1,  (0.0, 0.0, 0.0),    0.0,   0.00, 1.0),
        (6,  (4.0, -3.0, 10.0), 12.0,  -0.03, 1.25),
        (14,(12.0, 8.0, -25.0), 28.0,  -0.08, 0.60),
        (24,(22.0, -15.0, 45.0),45.0,  -0.16, 0.20)
    ]

    for f, b_rot, r_pitch, r_z, rep_sc in puntos_death:
        pb_body = pose_bones.get("body")
        if pb_body:
            pb_body.rotation_euler = (math.radians(b_rot[0]), math.radians(b_rot[1]), math.radians(b_rot[2]))
            pb_body.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_ring = pose_bones.get("ring_rot")
        if pb_ring:
            pb_ring.location = (0.0, 0.0, r_z)
            pb_ring.rotation_euler = (math.radians(r_pitch), math.radians(r_pitch * 0.5), 0.0)
            pb_ring.keyframe_insert(data_path="location", frame=f)
            pb_ring.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_rep = pose_bones.get("repulsor")
        if pb_rep:
            pb_rep.scale = (rep_sc, rep_sc, rep_sc)
            pb_rep.keyframe_insert(data_path="scale", frame=f)

    track_death = arm_obj.animation_data.nla_tracks.new()
    track_death.name = "Death"
    track_death.strips.new("Death", 1, act_death)

    arm_obj.animation_data.action = act_idle
    bpy.context.scene.frame_set(1)

def construir_ovni():
    """
    Construye, riggea, anima y exporta el Ovni Bonus.
    """
    nombre_src = "SRC_ovni_bonus"
    nombre_export = "EXPORT_ovni_bonus"

    print("=" * 60)
    print("Iniciando construcción de OVNI Bonus...")
    print("=" * 60)

    # Limpiar acciones huérfanas
    for a in list(bpy.data.actions):
        if a.users == 0:
            bpy.data.actions.remove(a)

    utils_blender.limpiar_coleccion(nombre_src)
    utils_blender.limpiar_coleccion(nombre_export)

    for o in list(bpy.data.objects):
        if o.name.startswith("ovni_bonus") or o.name.startswith("Armature_ovni"):
            bpy.data.objects.remove(o, do_unlink=True)

    col_src = utils_blender.obtener_o_crear_coleccion(nombre_src)
    col_export = utils_blender.obtener_o_crear_coleccion(nombre_export)

    mats = configurar_materiales()

    bm = bmesh.new()
    grupos = construir_ovni_malla(bm)
    bm.verts.index_update()

    grupos_indices = {
        'body': list(set(v.index for v in grupos['body'])),
        'ring_rot': list(set(v.index for v in grupos['ring_rot'])),
        'repulsor': list(set(v.index for v in grupos['repulsor'])),
        'antenna': list(set(v.index for v in grupos['antenna']))
    }

    mesh = bpy.data.meshes.new("ovni_bonus_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj_mesh = bpy.data.objects.new("ovni_bonus_mesh_obj", mesh)
    col_src.objects.link(obj_mesh)

    # Asignar materiales
    obj_mesh.data.materials.append(mats['casco'])     # 0
    obj_mesh.data.materials.append(mats['blindaje'])  # 1
    obj_mesh.data.materials.append(mats['cupula'])    # 2
    obj_mesh.data.materials.append(mats['mecanismo']) # 3
    obj_mesh.data.materials.append(mats['neon'])      # 4

    # Normales suaves y Weighted Normal horneado antes de rigging
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
    arm_obj = crear_armature_y_rigging(obj_mesh, col_src, grupos_indices)

    # 2 Animaciones NLA
    crear_animaciones_ovni(arm_obj)

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
    print("INFORME GEOMÉTRICO FINAL — OVNI BONUS:")
    print(f"Total Triángulos Evaluados: {total_triangulos} (Presupuesto: {CONFIG_OVNI['presupuesto_min']} - {CONFIG_OVNI['presupuesto_max']})")
    print(f"Dimensiones Bounding Box (Godot X x Y x Z): {tam_final[0]:.3f} x {tam_final[2]:.3f} x {tam_final[1]:.3f} m")
    print(f"Centro del Bounding Box: ({cen_final[0]:.3f}, {cen_final[1]:.3f}, {cen_final[2]:.3f})")
    print("-" * 60)

    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "ovni_bonus.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # Exportación dual a .glb
    ruta_glb_1 = os.path.join(ws_dir, "assets", "models", "ovni", "ovni_bonus.glb")
    ruta_glb_2 = os.path.join(ws_dir, "Space invaders", "assets", "models", "ovni", "ovni_bonus.glb")
    os.makedirs(os.path.dirname(ruta_glb_1), exist_ok=True)
    os.makedirs(os.path.dirname(ruta_glb_2), exist_ok=True)

    utils_blender.exportar_glb(ruta_glb_1, [arm_obj, obj_mesh])
    shutil.copy2(ruta_glb_1, ruta_glb_2)

    return {
        'nombre': "OVNI Bonus",
        'triangulos': total_triangulos,
        'tam_blender': [tam_final[0], tam_final[1], tam_final[2]],
        'tam_godot': [tam_final[0], tam_final[2], tam_final[1]],
        'centro': [cen_final[0], cen_final[1], cen_final[2]],
        'ruta_glb': ruta_glb_1,
        'ruta_blend': ruta_blend,
        'clips': ["Idle-loop", "Death"]
    }

if __name__ == "__main__":
    construir_ovni()
