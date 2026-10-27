"""
blender/scripts/build_proyectiles.py - Construcción, texturizado, rigging,
animación y exportación de proyectiles (bala del jugador y bala enemiga).
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

NOMBRE_SRC = "SRC_proyectiles"
NOMBRE_EXPORT = "EXPORT_proyectiles"

def configurar_materiales():
    """Crea los materiales arcade neon para proyectiles."""
    # 0. Plasma cian del jugador (#00E5FF)
    mat_plasma_jugador = utils_blender.crear_material(
        "m_plasma_jugador",
        base_color=(0.0, 0.90, 1.0, 1.0),
        metallic=0.1,
        roughness=0.15,
        emission_color=(0.0, 0.90, 1.0, 1.0),
        emission_strength=4.0
    )

    # 1. Carcasa metálica oscura del proyectil del jugador (#1B2030)
    mat_metal_jugador = utils_blender.crear_material(
        "m_metal_bala_jugador",
        base_color=(0.012, 0.018, 0.032, 1.0),
        metallic=0.92,
        roughness=0.22
    )

    # 2. Plasma marciano rojo-anaranjado (#FF4D2E)
    mat_plasma_enemigo = utils_blender.crear_material(
        "m_plasma_enemigo",
        base_color=(1.0, 0.30, 0.18, 1.0),
        metallic=0.1,
        roughness=0.15,
        emission_color=(1.0, 0.30, 0.18, 1.0),
        emission_strength=4.0
    )

    # 3. Carcasa alienígena oscura
    mat_metal_enemigo = utils_blender.crear_material(
        "m_metal_bala_enemiga",
        base_color=(0.022, 0.012, 0.018, 1.0),
        metallic=0.88,
        roughness=0.25
    )

    # 4. Halo secundario violeta (#A855F7)
    mat_halo_violeta = utils_blender.crear_material(
        "m_halo_violeta",
        base_color=(0.66, 0.33, 0.97, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(0.66, 0.33, 0.97, 1.0),
        emission_strength=3.0
    )

    return {
        'plasma_jugador': mat_plasma_jugador,
        'metal_jugador': mat_metal_jugador,
        'plasma_enemigo': mat_plasma_enemigo,
        'metal_enemigo': mat_metal_enemigo,
        'halo_violeta': mat_halo_violeta
    }

def construir_bala_jugador(col, mats):
    """
    Construye la bala del jugador (ojiva diamante de plasma cian con aletas magnéticas).
    Apunta hacia +Y en Blender (que corresponde a -Z hacia el frente en Godot).
    Presupuesto objetivo: 500 - 2,000 triángulos.
    """
    bm = bmesh.new()
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()

    # 1. Núcleo facetado de plasma cian (20 segmentos)
    bm_core = bmesh.new()
    bmesh.ops.create_cone(
        bm_core,
        cap_ends=True,
        cap_tris=False,
        segments=20,
        radius1=0.038,
        radius2=0.002,
        depth=0.22
    )
    bmesh.ops.transform(bm_core, matrix=rot_x90, verts=bm_core.verts)
    bmesh.ops.transform(bm_core, matrix=mathutils.Matrix.Translation((0, 0.08, 0)), verts=bm_core.verts)

    bm_cola = bmesh.new()
    bmesh.ops.create_cone(
        bm_cola,
        cap_ends=True,
        cap_tris=False,
        segments=20,
        radius1=0.002,
        radius2=0.038,
        depth=0.14
    )
    bmesh.ops.transform(bm_cola, matrix=rot_x90, verts=bm_cola.verts)
    bmesh.ops.transform(bm_cola, matrix=mathutils.Matrix.Translation((0, -0.10, 0)), verts=bm_cola.verts)

    for bm_sub in [bm_core, bm_cola]:
        v_map = {v: bm.verts.new(v.co) for v in bm_sub.verts}
        for f in bm_sub.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 0 # m_plasma_jugador
            except:
                pass
        bm_sub.free()

    # 2. Carcasa magnética acanalada (cilindro biselado de 24 lados)
    bm_anillo = bmesh.new()
    bmesh.ops.create_cone(
        bm_anillo,
        cap_ends=True,
        cap_tris=False,
        segments=24,
        radius1=0.052,
        radius2=0.052,
        depth=0.09
    )
    bmesh.ops.transform(bm_anillo, matrix=rot_x90, verts=bm_anillo.verts)
    bmesh.ops.transform(bm_anillo, matrix=mathutils.Matrix.Translation((0, -0.02, 0)), verts=bm_anillo.verts)

    # Inset en los bordes para crear canales metálicos
    v_map = {v: bm.verts.new(v.co) for v in bm_anillo.verts}
    for f in bm_anillo.faces:
        try:
            nf = bm.faces.new([v_map[v] for v in f.verts])
            nf.material_index = 1 # metal
        except:
            pass
    bm_anillo.free()

    # 3. 4 Aletas estabilizadoras biseladas con ranuras de aceleración
    for ang in [0, 90, 180, 270]:
        rad = math.radians(ang)
        rot_fin = mathutils.Euler((0, rad, 0)).to_matrix().to_4x4()

        bm_aleta = bmesh.new()
        bmesh.ops.create_cube(bm_aleta, size=1.0)
        scale_fin = mathutils.Matrix.Diagonal((0.010, 0.18, 0.055, 1.0))
        trans_fin = mathutils.Matrix.Translation((0, -0.04, 0.060))
        bmesh.ops.transform(bm_aleta, matrix=rot_fin @ trans_fin @ scale_fin, verts=bm_aleta.verts)

        # Bisel en aristas de la aleta
        bmesh.ops.bevel(bm_aleta, geom=bm_aleta.edges[:], offset=0.003, segments=2)

        v_map = {v: bm.verts.new(v.co) for v in bm_aleta.verts}
        for f in bm_aleta.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 1 # metal
            except:
                pass
        bm_aleta.free()

        # Filamento de neón cian en el borde exterior
        bm_edge = bmesh.new()
        bmesh.ops.create_cube(bm_edge, size=1.0)
        scale_edge = mathutils.Matrix.Diagonal((0.014, 0.16, 0.010, 1.0))
        trans_edge = mathutils.Matrix.Translation((0, -0.04, 0.092))
        bmesh.ops.transform(bm_edge, matrix=rot_fin @ trans_edge @ scale_edge, verts=bm_edge.verts)

        v_map = {v: bm.verts.new(v.co) for v in bm_edge.verts}
        for f in bm_edge.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 0 # neon cian
            except:
                pass
        bm_edge.free()

    # 4. Anillos de confinamiento magnético neón frontal y trasero
    for y_pos, r_a in [(0.04, 0.044), (-0.08, 0.042)]:
        bm_ring = bmesh.new()
        bmesh.ops.create_cone(
            bm_ring,
            cap_ends=False,
            cap_tris=False,
            segments=20,
            radius1=r_a,
            radius2=r_a,
            depth=0.018
        )
        bmesh.ops.transform(bm_ring, matrix=rot_x90, verts=bm_ring.verts)
        bmesh.ops.transform(bm_ring, matrix=mathutils.Matrix.Translation((0, y_pos, 0)), verts=bm_ring.verts)

        v_map = {v: bm.verts.new(v.co) for v in bm_ring.verts}
        for f in bm_ring.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 0 # neon cian
            except:
                pass
        bm_ring.free()

    mesh_bala = bpy.data.meshes.new("bala_jugador_mesh")
    obj_bala = bpy.data.objects.new("bala_jugador_mesh_obj", mesh_bala)
    col.objects.link(obj_bala)

    bm.to_mesh(mesh_bala)
    bm.free()

    obj_bala.data.materials.append(mats['plasma_jugador']) # 0
    obj_bala.data.materials.append(mats['metal_jugador'])  # 1

    mod_norm = obj_bala.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True

    for p in mesh_bala.polygons:
        p.use_smooth = True

    # Rigging
    arm_data = bpy.data.armatures.new("Armature_bala_jugador")
    arm_obj = bpy.data.objects.new("bala_jugador", arm_data)
    col.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    b_root = arm_data.edit_bones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    b_spin = arm_data.edit_bones.new("bullet_core")
    b_spin.head = (0, -0.10, 0)
    b_spin.tail = (0, 0.15, 0)
    b_spin.parent = b_root

    bpy.ops.object.mode_set(mode='OBJECT')

    mod_arm = obj_bala.modifiers.new(name="Armature", type='ARMATURE')
    mod_arm.object = arm_obj

    vg = obj_bala.vertex_groups.new(name="bullet_core")
    vg.add(list(range(len(mesh_bala.vertices))), 1.0, 'REPLACE')

    obj_bala.parent = arm_obj

    # Animación Idle-loop
    arm_obj.animation_data_create()
    act = bpy.data.actions.new(name="Idle-loop")
    arm_obj.animation_data.action = act

    arm_obj.pose.bones["bullet_core"].rotation_mode = 'XYZ'
    pbone = arm_obj.pose.bones["bullet_core"]

    # Frame 0
    pbone.rotation_euler = (0, 0, 0)
    pbone.scale = (1.0, 1.0, 1.0)
    pbone.keyframe_insert(data_path='rotation_euler', index=1, frame=0)
    pbone.keyframe_insert(data_path='scale', frame=0)

    # Frame 15: pulsación
    pbone.rotation_euler = (0, math.radians(180), 0)
    pbone.scale = (1.08, 1.0, 1.08)
    pbone.keyframe_insert(data_path='rotation_euler', index=1, frame=15)
    pbone.keyframe_insert(data_path='scale', frame=15)

    # Frame 30: bucle perfecto
    pbone.rotation_euler = (0, math.radians(360), 0)
    pbone.scale = (1.0, 1.0, 1.0)
    pbone.keyframe_insert(data_path='rotation_euler', index=1, frame=30)
    pbone.keyframe_insert(data_path='scale', frame=30)

    track = arm_obj.animation_data.nla_tracks.new()
    track.name = "Idle-loop"
    strip = track.strips.new(name="Idle-loop", start=0, action=act)
    strip.extrapolation = 'HOLD'

    return arm_obj, obj_bala

def construir_bala_enemiga(col, mats):
    """
    Construye la bala enemiga (proyectil de plasma bio-mecánico en espiral, color rojo/violeta).
    Apunta hacia +Y en Blender (hacia el jugador en Godot).
    Presupuesto objetivo: 500 - 2,000 triángulos.
    """
    bm = bmesh.new()
    rot_x90 = mathutils.Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()

    # 1. Núcleo ovoide de plasma rojo-anaranjado (24 segmentos)
    bm_core = bmesh.new()
    bmesh.ops.create_cone(
        bm_core,
        cap_ends=True,
        cap_tris=False,
        segments=24,
        radius1=0.046,
        radius2=0.005,
        depth=0.22
    )
    bmesh.ops.transform(bm_core, matrix=rot_x90, verts=bm_core.verts)
    bmesh.ops.transform(bm_core, matrix=mathutils.Matrix.Translation((0, 0.06, 0)), verts=bm_core.verts)

    bm_tail = bmesh.new()
    bmesh.ops.create_cone(
        bm_tail,
        cap_ends=True,
        cap_tris=False,
        segments=24,
        radius1=0.005,
        radius2=0.046,
        depth=0.18
    )
    bmesh.ops.transform(bm_tail, matrix=rot_x90, verts=bm_tail.verts)
    bmesh.ops.transform(bm_tail, matrix=mathutils.Matrix.Translation((0, -0.10, 0)), verts=bm_tail.verts)

    for bm_sub in [bm_core, bm_tail]:
        v_map = {v: bm.verts.new(v.co) for v in bm_sub.verts}
        for f in bm_sub.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 0 # m_plasma_enemigo
            except:
                pass
        bm_sub.free()

    # 2. 4 Púas / espirales helicoidales periféricas (a 90 grados)
    for i in range(4):
        ang_deg = i * 90
        rot_z = mathutils.Euler((0, math.radians(ang_deg), 0)).to_matrix().to_4x4()

        bm_spica = bmesh.new()
        bmesh.ops.create_cone(
            bm_spica,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=0.018,
            radius2=0.003,
            depth=0.20
        )
        rot_inc = mathutils.Euler((math.radians(72), 0, 0)).to_matrix().to_4x4()
        trans_spica = mathutils.Matrix.Translation((0, 0.02, 0.070))
        bmesh.ops.transform(bm_spica, matrix=rot_z @ trans_spica @ rot_inc, verts=bm_spica.verts)

        v_map = {v: bm.verts.new(v.co) for v in bm_spica.verts}
        for f in bm_spica.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 1 # metal oscuro enemigo
            except:
                pass
        bm_spica.free()

        # Filamento de halo violeta sobre la púa
        bm_fil = bmesh.new()
        bmesh.ops.create_cube(bm_fil, size=1.0)
        scale_fil = mathutils.Matrix.Diagonal((0.010, 0.16, 0.008, 1.0))
        trans_fil = mathutils.Matrix.Translation((0, 0.02, 0.090))
        bmesh.ops.transform(bm_fil, matrix=rot_z @ trans_fil @ rot_inc @ scale_fil, verts=bm_fil.verts)

        v_map = {v: bm.verts.new(v.co) for v in bm_fil.verts}
        for f in bm_fil.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 2 # m_halo_violeta
            except:
                pass
        bm_fil.free()

    # 3. 3 Anillos de energía marciana pulsante (24 segmentos)
    for y_pos, r_anillo in [(0.04, 0.058), (-0.02, 0.054), (-0.08, 0.048)]:
        bm_ring = bmesh.new()
        bmesh.ops.create_cone(
            bm_ring,
            cap_ends=False,
            cap_tris=False,
            segments=24,
            radius1=r_anillo,
            radius2=r_anillo,
            depth=0.022
        )
        bmesh.ops.transform(bm_ring, matrix=rot_x90, verts=bm_ring.verts)
        bmesh.ops.transform(bm_ring, matrix=mathutils.Matrix.Translation((0, y_pos, 0)), verts=bm_ring.verts)

        v_map = {v: bm.verts.new(v.co) for v in bm_ring.verts}
        for f in bm_ring.faces:
            try:
                nf = bm.faces.new([v_map[v] for v in f.verts])
                nf.material_index = 2 # halo violeta
            except:
                pass
        bm_ring.free()

    mesh_bala_e = bpy.data.meshes.new("bala_enemiga_mesh")
    obj_bala_e = bpy.data.objects.new("bala_enemiga_mesh_obj", mesh_bala_e)
    col.objects.link(obj_bala_e)

    bm.to_mesh(mesh_bala_e)
    bm.free()

    obj_bala_e.data.materials.append(mats['plasma_enemigo']) # 0
    obj_bala_e.data.materials.append(mats['metal_enemigo'])  # 1
    obj_bala_e.data.materials.append(mats['halo_violeta'])   # 2

    mod_norm = obj_bala_e.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True

    for p in mesh_bala_e.polygons:
        p.use_smooth = True

    # Rigging
    arm_data = bpy.data.armatures.new("Armature_bala_enemiga")
    arm_obj = bpy.data.objects.new("bala_enemiga", arm_data)
    col.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    b_root = arm_data.edit_bones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.05)

    b_spin = arm_data.edit_bones.new("bullet_core")
    b_spin.head = (0, -0.10, 0)
    b_spin.tail = (0, 0.15, 0)
    b_spin.parent = b_root

    bpy.ops.object.mode_set(mode='OBJECT')

    mod_arm = obj_bala_e.modifiers.new(name="Armature", type='ARMATURE')
    mod_arm.object = arm_obj

    vg = obj_bala_e.vertex_groups.new(name="bullet_core")
    vg.add(list(range(len(mesh_bala_e.vertices))), 1.0, 'REPLACE')

    obj_bala_e.parent = arm_obj

    # Animación Idle-loop
    arm_obj.animation_data_create()
    act = bpy.data.actions.new(name="Idle-loop")
    arm_obj.animation_data.action = act

    pbone = arm_obj.pose.bones["bullet_core"]
    pbone.rotation_mode = 'XYZ'

    # Frame 0
    pbone.rotation_euler = (0, 0, 0)
    pbone.scale = (1.0, 1.0, 1.0)
    pbone.keyframe_insert(data_path='rotation_euler', index=1, frame=0)
    pbone.keyframe_insert(data_path='scale', frame=0)

    # Frame 15: pulsación
    pbone.rotation_euler = (0, math.radians(-180), 0)
    pbone.scale = (1.12, 1.0, 1.12)
    pbone.keyframe_insert(data_path='rotation_euler', index=1, frame=15)
    pbone.keyframe_insert(data_path='scale', frame=15)

    # Frame 30: bucle perfecto
    pbone.rotation_euler = (0, math.radians(-360), 0)
    pbone.scale = (1.0, 1.0, 1.0)
    pbone.keyframe_insert(data_path='rotation_euler', index=1, frame=30)
    pbone.keyframe_insert(data_path='scale', frame=30)

    track = arm_obj.animation_data.nla_tracks.new()
    track.name = "Idle-loop"
    strip = track.strips.new(name="Idle-loop", start=0, action=act)
    strip.extrapolation = 'HOLD'

    return arm_obj, obj_bala_e

def construir_proyectiles():
    """Función principal para generar ambos proyectiles."""
    print("=" * 60)
    print("Iniciando construcción de Proyectiles (Bala Jugador y Bala Enemiga)...")
    print("=" * 60)

    utils_blender.limpiar_coleccion(NOMBRE_SRC)
    utils_blender.limpiar_coleccion(NOMBRE_EXPORT)

    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)

    for o in list(bpy.data.objects):
        if o.type in ['MESH', 'ARMATURE']:
            bpy.data.objects.remove(o, do_unlink=True)

    col_src = utils_blender.obtener_o_crear_coleccion(NOMBRE_SRC)
    col_export = utils_blender.obtener_o_crear_coleccion(NOMBRE_EXPORT)

    mats = configurar_materiales()

    # Construir bala jugador
    arm_jug, mesh_jug = construir_bala_jugador(col_src, mats)

    # Construir bala enemiga
    arm_ene, mesh_ene = construir_bala_enemiga(col_src, mats)

    bpy.context.view_layer.update()

    # Mover a EXPORT
    for obj in [arm_jug, mesh_jug, arm_ene, mesh_ene]:
        col_src.objects.unlink(obj)
        col_export.objects.link(obj)

    tris_jug = utils_blender.contar_triangulos([mesh_jug])
    tris_ene = utils_blender.contar_triangulos([mesh_ene])

    min_j, max_j, tam_j, cen_j = utils_blender.calcular_aabb([mesh_jug])
    min_e, max_e, tam_e, cen_e = utils_blender.calcular_aabb([mesh_ene])

    print("-" * 60)
    print("INFORME GEOMÉTRICO — PROYECTILES:")
    print(f"Bala Jugador: {tris_jug} tris (Presupuesto: 500 - 2,000) | Bounding Box: {tam_j[0]:.3f} x {tam_j[1]:.3f} x {tam_j[2]:.3f} m")
    print(f"Bala Enemiga: {tris_ene} tris (Presupuesto: 500 - 2,000) | Bounding Box: {tam_e[0]:.3f} x {tam_e[1]:.3f} x {tam_e[2]:.3f} m")
    print("-" * 60)

    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "proyectiles.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # Exportar bala del jugador
    ruta_bj = os.path.join(ws_dir, "assets", "models", "proyectiles", "bala_jugador.glb")
    ruta_bj_godot = os.path.join(ws_dir, "Space invaders", "assets", "models", "proyectiles", "bala_jugador.glb")
    os.makedirs(os.path.dirname(ruta_bj), exist_ok=True)
    os.makedirs(os.path.dirname(ruta_bj_godot), exist_ok=True)
    utils_blender.exportar_glb(ruta_bj, [arm_jug, mesh_jug])
    shutil.copy2(ruta_bj, ruta_bj_godot)

    # Exportar bala enemiga
    ruta_be = os.path.join(ws_dir, "assets", "models", "proyectiles", "bala_enemiga.glb")
    ruta_be_godot = os.path.join(ws_dir, "Space invaders", "assets", "models", "proyectiles", "bala_enemiga.glb")
    utils_blender.exportar_glb(ruta_be, [arm_ene, mesh_ene])
    shutil.copy2(ruta_be, ruta_be_godot)

    return {
        'tris_jugador': tris_jug,
        'tris_enemigo': tris_ene,
        'tam_jugador': [tam_j[0], tam_j[1], tam_j[2]],
        'tam_enemigo': [tam_e[0], tam_e[1], tam_e[2]],
        'ruta_bj': ruta_bj,
        'ruta_be': ruta_be,
        'ruta_blend': ruta_blend,
        'clips': ["Idle-loop"]
    }

if __name__ == "__main__":
    construir_proyectiles()
