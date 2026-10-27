"""
blender/scripts/build_entorno.py - Construcción, texturizado, rigging,
animación y exportación del Decorado de Fondo (Planeta Orbital).
Proyecto: Space Invaders 3D
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

CONFIG_ENTORNO = {
    'nombre': "Planeta Orbital de Fondo",
    'sufijo': "planeta_fondo",
    'color_neon': (0.22, 0.74, 0.97, 1.0),   # Cian celeste espacial (#38BDF8)
    'presupuesto_max': 50000,
}

def configurar_materiales():
    """Crea los 5 materiales Principled BSDF para el Planeta y su entorno orbital."""
    col_neon = CONFIG_ENTORNO['color_neon']

    # 1. Corteza / Océano profundo índigo
    mat_corteza = utils_blender.crear_material(
        "m_planeta_corteza",
        base_color=(0.025, 0.038, 0.075, 1.0),
        metallic=0.55,
        roughness=0.42
    )

    # 2. Placas tectónicas / continentes tecnológicos grafito metálico
    mat_placas = utils_blender.crear_material(
        "m_planeta_placas",
        base_color=(0.050, 0.065, 0.098, 1.0),
        metallic=0.88,
        roughness=0.28
    )

    # 3. Anillos planetarios luminosos de hielo y polvo reflectante
    mat_anillos = utils_blender.crear_material(
        "m_planeta_anillos",
        base_color=(0.16, 0.20, 0.28, 1.0),
        metallic=0.45,
        roughness=0.48
    )

    # 4. Estructura de estación orbital y satélites
    mat_estacion = utils_blender.crear_material(
        "m_planeta_estacion",
        base_color=(0.015, 0.018, 0.028, 1.0),
        metallic=0.96,
        roughness=0.18
    )

    # 5. Neón atmosférico / redes de energía orbitales (Cian celeste, emisión 3.8)
    mat_neon = utils_blender.crear_material(
        "m_planeta_neon",
        base_color=col_neon,
        metallic=0.10,
        roughness=0.20,
        emission_color=col_neon,
        emission_strength=3.8
    )

    return {
        'corteza': mat_corteza,
        'placas': mat_placas,
        'anillos': mat_anillos,
        'estacion': mat_estacion,
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

def construir_planeta_malla(bm):
    """
    Construye el Planeta Orbital con alta fidelidad:
    - Esfera planetaria base (80 x 60 segs)
    - 40 Placas continentales curvadas y trincheras neón emisivas
    - Fisura ecuatorial planetaria con línea de energía neón
    - Doble sistema de anillos planetarios concéntricos inclinados (128 segs)
    - Anillo de estación espacial ecuatorial con 12 estaciones/satélites y paneles solares
    """
    grupos = {
        'planet_core': [],
        'rings': [],
        'station_rot': []
    }

    # 1. ESFERA BASE DEL PLANETA (Corteza oceánica profunda)
    bm_core = bmesh.new()
    bmesh.ops.create_uvsphere(bm_core, u_segments=80, v_segments=60, radius=0.85)
    grupos['planet_core'].extend(transferir_geom(bm_core, bm, mat_index=0))
    bm_core.free()

    # 2. PLACAS CONTINENTALES Y TRINCHERAS NEÓN (Tecno-continentes)
    lat_bands = [-0.60, -0.38, -0.15, 0.12, 0.36, 0.58]
    for lat_idx, lat_z in enumerate(lat_bands):
        num_patches = 8 if abs(lat_z) > 0.45 else 10
        rad_at_z = math.sqrt(max(0.01, 0.85**2 - lat_z**2))
        for p_i in range(num_patches):
            if (lat_idx + p_i) % 3 == 0:
                continue # Alternar para formar continentes fragmentados y archipiélagos
            ang = (p_i / float(num_patches)) * 2.0 * math.pi + (lat_idx * 0.42)
            px = math.cos(ang) * (rad_at_z + 0.018)
            py = math.sin(ang) * (rad_at_z + 0.018)
            pz = lat_z

            bm_plate = bmesh.new()
            bmesh.ops.create_cube(bm_plate, size=1.0)
            sc_plate = mathutils.Matrix.Diagonal((0.16, 0.16, 0.024, 1.0))
            # Orientar el cubo tangente a la superficie esférica
            normal = mathutils.Vector((px, py, pz)).normalized()
            up = mathutils.Vector((0, 0, 1))
            tangent = normal.cross(up).normalized() if abs(normal.z) < 0.95 else mathutils.Vector((1, 0, 0))
            bitangent = normal.cross(tangent).normalized()
            rot_mat = mathutils.Matrix([
                [tangent.x, bitangent.x, normal.x, 0],
                [tangent.y, bitangent.y, normal.y, 0],
                [tangent.z, bitangent.z, normal.z, 0],
                [0, 0, 0, 1]
            ])
            tr_plate = mathutils.Matrix.Translation((px, py, pz))
            bmesh.ops.transform(bm_plate, matrix=tr_plate @ rot_mat @ sc_plate, verts=bm_plate.verts)
            bmesh.ops.bevel(bm_plate, geom=bm_plate.edges[:], offset=0.003, segments=2)
            grupos['planet_core'].extend(transferir_geom(bm_plate, bm, mat_index=1))
            bm_plate.free()

            # Grieta / canal neón de energía en el borde del continente
            if (p_i + lat_idx) % 2 == 1:
                bm_glow = bmesh.new()
                bmesh.ops.create_cube(bm_glow, size=1.0)
                sc_glow = mathutils.Matrix.Diagonal((0.14, 0.022, 0.030, 1.0))
                tr_glow = mathutils.Matrix.Translation((px * 0.995, py * 0.995, pz * 0.995))
                bmesh.ops.transform(bm_glow, matrix=tr_glow @ rot_mat @ sc_glow, verts=bm_glow.verts)
                grupos['planet_core'].extend(transferir_geom(bm_glow, bm, mat_index=4)) # Neón
                bm_glow.free()

    # 3. ANILLOS PLANETARIOS DOBLES (Inclinados a 22° respecto al ecuador)
    rot_ring_tilt = mathutils.Euler((math.radians(22), math.radians(10), 0)).to_matrix().to_4x4()

    # Anillo interior A
    bm_ring_in = bmesh.new()
    bmesh.ops.create_cone(
        bm_ring_in,
        cap_ends=False,
        cap_tris=False,
        segments=128,
        radius1=1.12,
        radius2=1.35,
        depth=0.010
    )
    bmesh.ops.transform(bm_ring_in, matrix=rot_ring_tilt, verts=bm_ring_in.verts)
    bmesh.ops.bevel(bm_ring_in, geom=bm_ring_in.edges[:], offset=0.003, segments=2)
    grupos['rings'].extend(transferir_geom(bm_ring_in, bm, mat_index=2))
    bm_ring_in.free()

    # Anillo exterior B (Separación Cassini)
    bm_ring_out = bmesh.new()
    bmesh.ops.create_cone(
        bm_ring_out,
        cap_ends=False,
        cap_tris=False,
        segments=128,
        radius1=1.42,
        radius2=1.68,
        depth=0.008
    )
    bmesh.ops.transform(bm_ring_out, matrix=rot_ring_tilt, verts=bm_ring_out.verts)
    bmesh.ops.bevel(bm_ring_out, geom=bm_ring_out.edges[:], offset=0.003, segments=2)
    grupos['rings'].extend(transferir_geom(bm_ring_out, bm, mat_index=2))
    bm_ring_out.free()

    # Anillo fino de emisión neón en la división Cassini
    bm_cassini_neon = bmesh.new()
    bmesh.ops.create_cone(
        bm_cassini_neon,
        cap_ends=False,
        cap_tris=False,
        segments=128,
        radius1=1.38,
        radius2=1.388,
        depth=0.006
    )
    bmesh.ops.transform(bm_cassini_neon, matrix=rot_ring_tilt, verts=bm_cassini_neon.verts)
    grupos['rings'].extend(transferir_geom(bm_cassini_neon, bm, mat_index=4))
    bm_cassini_neon.free()

    # 4. ESTACIÓN ESPACIAL ORBITAL ECUATORIAL (Estructura celosía y 12 módulos)
    bm_st_ring = bmesh.new()
    bmesh.ops.create_cone(
        bm_st_ring,
        cap_ends=False,
        cap_tris=False,
        segments=96,
        radius1=1.02,
        radius2=1.02,
        depth=0.035
    )
    bmesh.ops.bevel(bm_st_ring, geom=bm_st_ring.edges[:], offset=0.004, segments=2)
    grupos['station_rot'].extend(transferir_geom(bm_st_ring, bm, mat_index=3))
    bm_st_ring.free()

    # 12 Módulos de estación orbital con balizas neón y radiadores
    for st_i in range(12):
        ang_st = (st_i / 12.0) * 2.0 * math.pi
        sx = math.cos(ang_st) * 1.02
        sy = math.sin(ang_st) * 1.02

        bm_hub = bmesh.new()
        bmesh.ops.create_cube(bm_hub, size=1.0)
        sc_hub = mathutils.Matrix.Diagonal((0.065, 0.08, 0.045, 1.0))
        rot_hub = mathutils.Euler((0, 0, ang_st)).to_matrix().to_4x4()
        tr_hub = mathutils.Matrix.Translation((sx, sy, 0.0))
        bmesh.ops.transform(bm_hub, matrix=tr_hub @ rot_hub @ sc_hub, verts=bm_hub.verts)
        bmesh.ops.bevel(bm_hub, geom=bm_hub.edges[:], offset=0.003, segments=2)
        grupos['station_rot'].extend(transferir_geom(bm_hub, bm, mat_index=3))
        bm_hub.free()

        # Faro de baliza / reactor neón
        bm_beacon = bmesh.new()
        bmesh.ops.create_uvsphere(bm_beacon, u_segments=16, v_segments=12, radius=0.016)
        tr_beacon = mathutils.Matrix.Translation((sx * 1.04, sy * 1.04, 0.025))
        bmesh.ops.transform(bm_beacon, matrix=tr_beacon, verts=bm_beacon.verts)
        grupos['station_rot'].extend(transferir_geom(bm_beacon, bm, mat_index=4)) # Neón cian
        bm_beacon.free()

        # Paneles solares / alas de radiador laterales
        for sign_panel in [-1, 1]:
            bm_panel = bmesh.new()
            bmesh.ops.create_cube(bm_panel, size=1.0)
            sc_panel = mathutils.Matrix.Diagonal((0.010, 0.07, 0.035, 1.0))
            tr_panel = mathutils.Matrix.Translation((sx, sy, sign_panel * 0.055))
            bmesh.ops.transform(bm_panel, matrix=tr_panel @ rot_hub @ sc_panel, verts=bm_panel.verts)
            bmesh.ops.bevel(bm_panel, geom=bm_panel.edges[:], offset=0.002, segments=2)
            grupos['station_rot'].extend(transferir_geom(bm_panel, bm, mat_index=1))
            bm_panel.free()

    return grupos

def crear_armature_y_rigging(obj_mesh, col, grupos_indices):
    """
    Crea el Armature del Planeta Orbital:
    - root en (0,0,0) ESTACIONARIO (crítico para Godot)
    - planet_core (rotación axial lenta)
    - rings (inclinación orbital armónica)
    - station_rot (órbita ecuatorial independiente)
    """
    arm_data = bpy.data.armatures.new("Armature_planeta_fondo")
    arm_obj = bpy.data.objects.new("planeta_fondo", arm_data)
    col.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    # 1. Hueso root ESTACIONARIO en (0,0,0)
    b_root = arm_data.edit_bones.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.10)

    # 2. Hueso planet_core
    b_core = arm_data.edit_bones.new("planet_core")
    b_core.head = (0, 0, 0)
    b_core.tail = (0, 0, 0.85)
    b_core.parent = b_root

    # 3. Hueso rings
    b_rings = arm_data.edit_bones.new("rings")
    b_rings.head = (0, 0, 0)
    b_rings.tail = (0, 0.5, 0.5)
    b_rings.parent = b_root

    # 4. Hueso station_rot
    b_st = arm_data.edit_bones.new("station_rot")
    b_st.head = (0, 0, 0)
    b_st.tail = (0, 0, 0.50)
    b_st.parent = b_root

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

def crear_animacion_planeta(arm_obj):
    """
    Crea la acción NLA requerida:
    - Idle-loop (120 frames / 4.0 s, 30 FPS): rotación celestial majestuosa continua y bucle perfecto.
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

    act_idle = preparar_accion("Idle-loop")
    arm_obj.animation_data.action = act_idle

    # Bucle perfecto de 120 fotogramas
    for f in range(1, 122, 10):
        frame_num = min(f, 120) if f <= 120 else 120
        t = (f - 1) / 120.0

        # Rotación planetaria axial
        pb_core = pose_bones.get("planet_core")
        if pb_core:
            rot_planet = t * 360.0
            pb_core.rotation_euler = (0.0, 0.0, math.radians(rot_planet))
            pb_core.keyframe_insert(data_path="rotation_euler", frame=frame_num)

        # Rotación de estación orbital en contra-rotación armónica
        pb_st = pose_bones.get("station_rot")
        if pb_st:
            rot_st = -t * 360.0 * 1.5 # Gira 1.5 veces en sentido contrario
            pb_st.rotation_euler = (0.0, 0.0, math.radians(rot_st))
            pb_st.keyframe_insert(data_path="rotation_euler", frame=frame_num)

        # Ondulación/precesión sutil de los anillos
        pb_rings = pose_bones.get("rings")
        if pb_rings:
            wobble = math.sin(t * 2.0 * math.pi) * math.radians(0.8)
            pb_rings.rotation_euler = (0.0, 0.0, wobble)
            pb_rings.keyframe_insert(data_path="rotation_euler", frame=frame_num)

    track_idle = arm_obj.animation_data.nla_tracks.new()
    track_idle.name = "Idle-loop"
    track_idle.strips.new("Idle-loop", 1, act_idle)

    arm_obj.animation_data.action = act_idle
    bpy.context.scene.frame_set(1)

def construir_planeta():
    """
    Construye, riggea, anima y exporta el Planeta Orbital de Fondo.
    """
    nombre_src = "SRC_planeta_fondo"
    nombre_export = "EXPORT_planeta_fondo"

    print("=" * 60)
    print("Iniciando construcción de Planeta Orbital de Fondo...")
    print("=" * 60)

    # Limpiar acciones huérfanas
    for a in list(bpy.data.actions):
        if a.users == 0:
            bpy.data.actions.remove(a)

    utils_blender.limpiar_coleccion(nombre_src)
    utils_blender.limpiar_coleccion(nombre_export)

    for o in list(bpy.data.objects):
        if o.name.startswith("planeta_fondo") or o.name.startswith("Armature_planeta"):
            bpy.data.objects.remove(o, do_unlink=True)

    col_src = utils_blender.obtener_o_crear_coleccion(nombre_src)
    col_export = utils_blender.obtener_o_crear_coleccion(nombre_export)

    mats = configurar_materiales()

    bm = bmesh.new()
    grupos = construir_planeta_malla(bm)
    bm.verts.index_update()

    grupos_indices = {
        'planet_core': list(set(v.index for v in grupos['planet_core'])),
        'rings': list(set(v.index for v in grupos['rings'])),
        'station_rot': list(set(v.index for v in grupos['station_rot']))
    }

    mesh = bpy.data.meshes.new("planeta_fondo_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj_mesh = bpy.data.objects.new("planeta_fondo_mesh_obj", mesh)
    col_src.objects.link(obj_mesh)

    # Asignar los 5 materiales Principled BSDF
    obj_mesh.data.materials.append(mats['corteza'])   # 0
    obj_mesh.data.materials.append(mats['placas'])    # 1
    obj_mesh.data.materials.append(mats['anillos'])   # 2
    obj_mesh.data.materials.append(mats['estacion'])  # 3
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

    # Animación NLA Idle-loop
    crear_animacion_planeta(arm_obj)

    # Centrar pivote en (0,0,0)
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
        b_root.tail = (0, 0, 0.10)
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
    print("INFORME GEOMÉTRICO FINAL — PLANETA ORBITAL DE FONDO:")
    print(f"Total Triángulos Evaluados: {total_triangulos} (Presupuesto: <= {CONFIG_ENTORNO['presupuesto_max']})")
    print(f"Dimensiones Bounding Box (Godot X x Y x Z): {tam_final[0]:.3f} x {tam_final[2]:.3f} x {tam_final[1]:.3f} m")
    print(f"Centro del Bounding Box: ({cen_final[0]:.3f}, {cen_final[1]:.3f}, {cen_final[2]:.3f})")
    print("-" * 60)

    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "planeta_fondo.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # Exportación dual a .glb
    ruta_glb_1 = os.path.join(ws_dir, "assets", "models", "entorno", "planeta_fondo.glb")
    ruta_glb_2 = os.path.join(ws_dir, "Space invaders", "assets", "models", "entorno", "planeta_fondo.glb")
    os.makedirs(os.path.dirname(ruta_glb_1), exist_ok=True)
    os.makedirs(os.path.dirname(ruta_glb_2), exist_ok=True)

    utils_blender.exportar_glb(ruta_glb_1, [arm_obj, obj_mesh])
    shutil.copy2(ruta_glb_1, ruta_glb_2)

    return {
        'nombre': "Planeta Orbital de Fondo",
        'triangulos': total_triangulos,
        'tam_blender': [tam_final[0], tam_final[1], tam_final[2]],
        'tam_godot': [tam_final[0], tam_final[2], tam_final[1]],
        'centro': [cen_final[0], cen_final[1], cen_final[2]],
        'ruta_glb': ruta_glb_1,
        'ruta_blend': ruta_blend,
        'clips': ["Idle-loop"]
    }

if __name__ == "__main__":
    construir_planeta()
