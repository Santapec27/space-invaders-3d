"""
blender/scripts/build_escudo.py - Construcción, texturizado y exportación
de bloques de escudo (sano y agrietado).
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

NOMBRE_SRC = "SRC_escudo"
NOMBRE_EXPORT = "EXPORT_escudo"

def configurar_materiales():
    """Crea los materiales arcade neon verde lima (#B6FF3B) para los escudos."""
    # 0. Metal base oscuro del blindaje (#1B2030)
    mat_metal = utils_blender.crear_material(
        "m_escudo_metal",
        base_color=(0.011, 0.014, 0.028, 1.0),
        metallic=0.88,
        roughness=0.28
    )

    # 1. Neón verde lima intacto (#B6FF3B)
    mat_neon = utils_blender.crear_material(
        "m_escudo_neon",
        base_color=(0.47, 1.0, 0.04, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(0.47, 1.0, 0.04, 1.0),
        emission_strength=3.0
    )

    # 2. Neón de fractura / energía inestable en grietas (#B6FF3B caliente)
    mat_crack = utils_blender.crear_material(
        "m_escudo_crack",
        base_color=(0.55, 0.95, 0.05, 1.0),
        metallic=0.15,
        roughness=0.35,
        emission_color=(0.55, 0.95, 0.05, 1.0),
        emission_strength=2.4
    )

    # 3. Marco interior / sujeción estructural
    mat_interior = utils_blender.crear_material(
        "m_escudo_interior",
        base_color=(0.007, 0.009, 0.016, 1.0),
        metallic=0.92,
        roughness=0.25
    )

    return {
        'metal': mat_metal,
        'neon': mat_neon,
        'crack': mat_crack,
        'interior': mat_interior
    }

def construir_bloque_sano(col, mats):
    """
    Construye el bloque de escudo intacto (0.48 x 0.48 x 0.48 m).
    Presupuesto objetivo: 1,000 - 3,000 triángulos.
    """
    bm = bmesh.new()

    # 1. Cubo principal
    bmesh.ops.create_cube(bm, size=0.48)

    # Las 6 caras iniciales
    caras = bm.faces[:]
    for f in caras:
        f.material_index = 0 # m_escudo_metal

    # Inset 1: Marco exterior hundido
    res1 = bmesh.ops.inset_individual(bm, faces=caras, thickness=0.035, depth=-0.012)
    for f in res1['faces']:
        f.material_index = 3 # interior oscuro

    # Inset 2: Canal de neón perimetral
    res2 = bmesh.ops.inset_individual(bm, faces=caras, thickness=0.020, depth=0.005)
    for f in res2['faces']:
        f.material_index = 1 # neon verde lima

    # Inset 3: Placa central elevada
    res3 = bmesh.ops.inset_individual(bm, faces=caras, thickness=0.025, depth=0.010)
    for f in res3['faces']:
        f.material_index = 0 # metal

    # 2. Pernos cilíndricos en las 4 esquinas de cada una de las 6 caras (24 pernos)
    ejes_principales = [
        (mathutils.Vector((0, 0, 1)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0))),
        (mathutils.Vector((0, 0, -1)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0))),
        (mathutils.Vector((0, 1, 0)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 0, 1))),
        (mathutils.Vector((0, -1, 0)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 0, 1))),
        (mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1))),
        (mathutils.Vector((-1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1))),
    ]

    for normal_vec, u_vec, v_vec in ejes_principales:
        centro_cara = normal_vec * 0.232
        for su in [-1, 1]:
            for sv in [-1, 1]:
                pos_perno = centro_cara + (u_vec * su * 0.14) + (v_vec * sv * 0.14)
                bm_p = bmesh.new()
                bmesh.ops.create_cone(
                    bm_p,
                    cap_ends=True,
                    cap_tris=False,
                    segments=8,
                    radius1=0.012,
                    radius2=0.010,
                    depth=0.014
                )
                rot_p = normal_vec.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                bmesh.ops.transform(bm_p, matrix=mathutils.Matrix.Translation(pos_perno) @ rot_p, verts=bm_p.verts)
                v_map = {v: bm.verts.new(v.co) for v in bm_p.verts}
                for f in bm_p.faces:
                    try:
                        nf = bm.faces.new([v_map[v] for v in f.verts])
                        nf.material_index = 3 # perno oscuro
                    except:
                        pass
                bm_p.free()

    # 3. Cruz neón central en cada una de las 6 caras
    for normal_vec, u_vec, v_vec in ejes_principales:
        centro_cara = normal_vec * 0.236
        rot_f = normal_vec.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        for s_scale in [(0.016, 0.12, 0.008), (0.12, 0.016, 0.008)]:
            bm_b = bmesh.new()
            bmesh.ops.create_cube(bm_b, size=1.0)
            sc = mathutils.Matrix.Diagonal((*s_scale, 1.0))
            bmesh.ops.transform(bm_b, matrix=mathutils.Matrix.Translation(centro_cara) @ rot_f @ sc, verts=bm_b.verts)
            v_map = {v: bm.verts.new(v.co) for v in bm_b.verts}
            for f in bm_b.faces:
                try:
                    nf = bm.faces.new([v_map[v] for v in f.verts])
                    nf.material_index = 1 # neon verde lima
                except:
                    pass
            bm_b.free()

    # 4. Esquineros biselados en los 8 vértices
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                pos_c = mathutils.Vector((sx * 0.222, sy * 0.222, sz * 0.222))
                bm_c = bmesh.new()
                bmesh.ops.create_cube(bm_c, size=0.038)
                bmesh.ops.bevel(bm_c, geom=bm_c.edges[:], offset=0.006, segments=1)
                bmesh.ops.transform(bm_c, matrix=mathutils.Matrix.Translation(pos_c), verts=bm_c.verts)
                v_map = {v: bm.verts.new(v.co) for v in bm_c.verts}
                for f in bm_c.faces:
                    try:
                        nf = bm.faces.new([v_map[v] for v in f.verts])
                        nf.material_index = 3 # interior/soporte
                    except:
                        pass
                bm_c.free()

    mesh_sano = bpy.data.meshes.new("escudo_bloque_sano_mesh")
    obj_sano = bpy.data.objects.new("escudo_bloque_sano", mesh_sano)
    col.objects.link(obj_sano)

    bm.to_mesh(mesh_sano)
    bm.free()

    obj_sano.data.materials.append(mats['metal'])    # 0
    obj_sano.data.materials.append(mats['neon'])     # 1
    obj_sano.data.materials.append(mats['crack'])    # 2
    obj_sano.data.materials.append(mats['interior']) # 3

    mod_norm = obj_sano.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True

    for p in mesh_sano.polygons:
        p.use_smooth = True

    return obj_sano

def construir_bloque_agrietado(col, mats):
    """
    Construye el bloque de escudo agrietado / dañado (0.48 x 0.48 x 0.48 m).
    Presenta fracturas angulares que exponen el núcleo neón inestable.
    Presupuesto objetivo: 1,000 - 3,000 triángulos.
    """
    bm = bmesh.new()

    # 1. Cubo principal
    bmesh.ops.create_cube(bm, size=0.48)

    # Las 6 caras iniciales
    caras = bm.faces[:]
    for f in caras:
        f.material_index = 0

    # Insets coordinados en las caras
    res1 = bmesh.ops.inset_individual(bm, faces=caras, thickness=0.035, depth=-0.012)
    for f in res1['faces']:
        f.material_index = 3

    res2 = bmesh.ops.inset_individual(bm, faces=caras, thickness=0.020, depth=0.005)
    for f in res2['faces']:
        f.material_index = 2 # crack neon

    res3 = bmesh.ops.inset_individual(bm, faces=caras, thickness=0.025, depth=0.010)
    for f in res3['faces']:
        f.material_index = 0 # metal base

    # 2. Grietas poligonales tridimensionales que atraviesan esquinas y caras
    rutas_grietas = [
        # (inicio, fin, grosor_1, grosor_2, segmentos)
        (mathutils.Vector((-0.245, 0.12, 0.08)), mathutils.Vector((0.08, -0.245, 0.14)), 0.026, 0.016, 8),
        (mathutils.Vector((0.05, 0.245, -0.06)), mathutils.Vector((-0.18, 0.04, -0.245)), 0.024, 0.014, 8),
        (mathutils.Vector((-0.12, -0.16, 0.245)), mathutils.Vector((0.245, 0.14, -0.05)), 0.028, 0.018, 8),
        (mathutils.Vector((0.245, 0.08, 0.12)), mathutils.Vector((0.02, 0.245, 0.22)), 0.022, 0.012, 8),
        (mathutils.Vector((-0.06, -0.04, 0.14)), mathutils.Vector((-0.245, -0.18, -0.04)), 0.020, 0.010, 8),
        (mathutils.Vector((0.14, -0.10, -0.245)), mathutils.Vector((0.245, -0.20, 0.06)), 0.022, 0.012, 8),
        (mathutils.Vector((-0.18, 0.245, 0.10)), mathutils.Vector((0.15, 0.18, 0.245)), 0.022, 0.012, 8),
        (mathutils.Vector((0.245, -0.14, -0.10)), mathutils.Vector((0.06, -0.245, -0.18)), 0.024, 0.014, 8),
    ]

    for p1, p2, r1, r2, segs in rutas_grietas:
        vec = p2 - p1
        mid = (p1 + p2) / 2.0
        rot = vec.normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()

        bm_f = bmesh.new()
        bmesh.ops.create_cone(
            bm_f,
            cap_ends=True,
            cap_tris=False,
            segments=segs,
            radius1=r1,
            radius2=r2,
            depth=vec.length * 1.05
        )
        bmesh.ops.transform(bm_f, matrix=mathutils.Matrix.Translation(mid) @ rot, verts=bm_f.verts)

        vert_map = {}
        for v in bm_f.verts:
            vert_map[v] = bm.verts.new(v.co)
        for f in bm_f.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 2 # m_escudo_crack
            except:
                pass
        bm_f.free()

    # 3. Desconches / fracturas angulares en 3 esquinas
    esquinas_danadas = [
        (mathutils.Vector((0.21, 0.21, 0.21)), mathutils.Euler((0.35, 0.45, 0.2))),
        (mathutils.Vector((-0.21, 0.21, -0.21)), mathutils.Euler((-0.4, 0.3, -0.25))),
        (mathutils.Vector((-0.21, -0.21, 0.21)), mathutils.Euler((0.25, -0.5, 0.4)))
    ]
    for pos_c, rot_e in esquinas_danadas:
        bm_c = bmesh.new()
        bmesh.ops.create_cone(
            bm_c,
            cap_ends=True,
            cap_tris=False,
            segments=5,
            radius1=0.045,
            radius2=0.015,
            depth=0.06
        )
        rot_mat = rot_e.to_matrix().to_4x4()
        bmesh.ops.transform(bm_c, matrix=mathutils.Matrix.Translation(pos_c) @ rot_mat, verts=bm_c.verts)

        vert_map = {}
        for v in bm_c.verts:
            vert_map[v] = bm.verts.new(v.co)
        for f in bm_c.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3 # interior estructural dañado
            except:
                pass
        bm_c.free()

    # 4. Fragmentos flotantes de plasma cristalizado
    for i, offset_frag in enumerate([
        mathutils.Vector((0.18, 0.15, 0.12)),
        mathutils.Vector((-0.12, 0.18, -0.10)),
        mathutils.Vector((0.08, -0.16, 0.18))
    ]):
        bm_fr = bmesh.new()
        bmesh.ops.create_cube(bm_fr, size=0.028)
        rot_fr = mathutils.Euler((i * 0.7, i * 1.1, i * 0.5)).to_matrix().to_4x4()
        bmesh.ops.transform(bm_fr, matrix=mathutils.Matrix.Translation(offset_frag) @ rot_fr, verts=bm_fr.verts)

        vert_map = {}
        for v in bm_fr.verts:
            vert_map[v] = bm.verts.new(v.co)
        for f in bm_fr.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 2 # crack neon
            except:
                pass
        bm_fr.free()

    # 5. Esquineros intactos restantes (5 de 8)
    esquinas_sanas = [
        (1, 1, -1), (1, -1, 1), (1, -1, -1), (-1, 1, 1), (-1, -1, -1)
    ]
    for sx, sy, sz in esquinas_sanas:
        pos_c = mathutils.Vector((sx * 0.222, sy * 0.222, sz * 0.222))
        bm_c = bmesh.new()
        bmesh.ops.create_cube(bm_c, size=0.038)
        bmesh.ops.bevel(bm_c, geom=bm_c.edges[:], offset=0.006, segments=1)
        bmesh.ops.transform(bm_c, matrix=mathutils.Matrix.Translation(pos_c), verts=bm_c.verts)

        vert_map = {}
        for v in bm_c.verts:
            vert_map[v] = bm.verts.new(v.co)
        for f in bm_c.faces:
            try:
                nf = bm.faces.new([vert_map[v] for v in f.verts])
                nf.material_index = 3
            except:
                pass
        bm_c.free()

    # 6. Pernos de sujeción restantes (en las caras menos dañadas)
    for normal_vec, u_vec, v_vec in [
        (mathutils.Vector((0, 0, 1)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0))),
        (mathutils.Vector((0, 0, -1)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0))),
        (mathutils.Vector((0, -1, 0)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 0, 1))),
    ]:
        centro_cara = normal_vec * 0.232
        for su in [-1, 1]:
            for sv in [-1, 1]:
                pos_perno = centro_cara + (u_vec * su * 0.14) + (v_vec * sv * 0.14)
                bm_p = bmesh.new()
                bmesh.ops.create_cone(
                    bm_p,
                    cap_ends=True,
                    cap_tris=False,
                    segments=8,
                    radius1=0.012,
                    radius2=0.010,
                    depth=0.014
                )
                rot_p = normal_vec.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                bmesh.ops.transform(bm_p, matrix=mathutils.Matrix.Translation(pos_perno) @ rot_p, verts=bm_p.verts)
                v_map = {v: bm.verts.new(v.co) for v in bm_p.verts}
                for f in bm_p.faces:
                    try:
                        nf = bm.faces.new([v_map[v] for v in f.verts])
                        nf.material_index = 3
                    except:
                        pass
                bm_p.free()

    mesh_agrietado = bpy.data.meshes.new("escudo_bloque_agrietado_mesh")
    obj_agrietado = bpy.data.objects.new("escudo_bloque_agrietado", mesh_agrietado)
    col.objects.link(obj_agrietado)

    bm.to_mesh(mesh_agrietado)
    bm.free()

    obj_agrietado.data.materials.append(mats['metal'])    # 0
    obj_agrietado.data.materials.append(mats['neon'])     # 1
    obj_agrietado.data.materials.append(mats['crack'])    # 2
    obj_agrietado.data.materials.append(mats['interior']) # 3

    mod_norm = obj_agrietado.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod_norm.keep_sharp = True

    for p in mesh_agrietado.polygons:
        p.use_smooth = True

    return obj_agrietado

def construir_escudos():
    """Función principal para generar ambos bloques de escudo."""
    print("=" * 60)
    print("Iniciando construcción de Bloques de Escudo (Sano y Agrietado)...")
    print("=" * 60)

    utils_blender.limpiar_coleccion(NOMBRE_SRC)
    utils_blender.limpiar_coleccion(NOMBRE_EXPORT)

    # Limpiar mallas residuales
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)

    col_src = utils_blender.obtener_o_crear_coleccion(NOMBRE_SRC)
    col_export = utils_blender.obtener_o_crear_coleccion(NOMBRE_EXPORT)

    mats = configurar_materiales()

    # Construir variante sana en SRC
    obj_sano = construir_bloque_sano(col_src, mats)
    # Construir variante agrietada en SRC
    obj_agrietado = construir_bloque_agrietado(col_src, mats)

    # Centrar y aplicar transformaciones
    for obj in [obj_sano, obj_agrietado]:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.context.view_layer.update()

    # Mover a EXPORT
    col_src.objects.unlink(obj_sano)
    col_src.objects.unlink(obj_agrietado)
    col_export.objects.link(obj_sano)
    col_export.objects.link(obj_agrietado)

    tris_sano = utils_blender.contar_triangulos([obj_sano])
    tris_agrietado = utils_blender.contar_triangulos([obj_agrietado])

    min_s, max_s, tam_s, cen_s = utils_blender.calcular_aabb([obj_sano])
    min_a, max_a, tam_a, cen_a = utils_blender.calcular_aabb([obj_agrietado])

    print("-" * 60)
    print("INFORME GEOMÉTRICO — ESCUDOS:")
    print(f"Bloque Sano:      {tris_sano} tris (Presupuesto: 1,000 - 3,000) | AABB: {tam_s[0]:.3f} x {tam_s[1]:.3f} x {tam_s[2]:.3f} m")
    print(f"Bloque Agrietado: {tris_agrietado} tris (Presupuesto: 1,000 - 3,000) | AABB: {tam_a[0]:.3f} x {tam_a[1]:.3f} x {tam_a[2]:.3f} m")
    print("-" * 60)

    ws_dir = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
    ruta_blend = os.path.join(ws_dir, "blender", "src", "escudo.blend")
    os.makedirs(os.path.dirname(ruta_blend), exist_ok=True)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
        print(f"[SAVE] Escena guardada en: {ruta_blend}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

    # Exportar GLB combinado
    ruta_glb = os.path.join(ws_dir, "assets", "models", "escudo", "escudo_bloque.glb")
    ruta_glb_godot = os.path.join(ws_dir, "Space invaders", "assets", "models", "escudo", "escudo_bloque.glb")
    os.makedirs(os.path.dirname(ruta_glb), exist_ok=True)
    os.makedirs(os.path.dirname(ruta_glb_godot), exist_ok=True)
    utils_blender.exportar_glb(ruta_glb, [obj_sano, obj_agrietado])
    shutil.copy2(ruta_glb, ruta_glb_godot)

    # Exportar variante sana individual
    ruta_sano = os.path.join(ws_dir, "assets", "models", "escudo", "escudo_bloque_sano.glb")
    ruta_sano_godot = os.path.join(ws_dir, "Space invaders", "assets", "models", "escudo", "escudo_bloque_sano.glb")
    utils_blender.exportar_glb(ruta_sano, [obj_sano])
    shutil.copy2(ruta_sano, ruta_sano_godot)

    # Exportar variante agrietada individual
    ruta_agri = os.path.join(ws_dir, "assets", "models", "escudo", "escudo_bloque_agrietado.glb")
    ruta_agri_godot = os.path.join(ws_dir, "Space invaders", "assets", "models", "escudo", "escudo_bloque_agrietado.glb")
    utils_blender.exportar_glb(ruta_agri, [obj_agrietado])
    shutil.copy2(ruta_agri, ruta_agri_godot)

    return {
        'tris_sano': tris_sano,
        'tris_agrietado': tris_agrietado,
        'tam_sano': [tam_s[0], tam_s[1], tam_s[2]],
        'tam_agrietado': [tam_a[0], tam_a[1], tam_a[2]],
        'ruta_glb': ruta_glb,
        'ruta_blend': ruta_blend
    }

if __name__ == "__main__":
    construir_escudos()
