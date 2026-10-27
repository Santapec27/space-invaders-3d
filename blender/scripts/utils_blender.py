"""
utils_blender.py - Utilidades reutilizables para el pipeline Blender -> Godot
Proyecto: Space Invaders 3D
"""

import bpy
import mathutils
import os

def limpiar_coleccion(nombre_coleccion):
    """Elimina todos los objetos de una colección y la colección misma si existe."""
    col = bpy.data.collections.get(nombre_coleccion)
    if col:
        for obj in list(col.objects):
            # Desenlazar de todas las colecciones
            for c in list(obj.users_collection):
                c.objects.unlink(obj)
            # Eliminar datos asociados
            if obj.type == 'MESH' and obj.data:
                mesh = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            elif obj.type == 'ARMATURE' and obj.data:
                arm = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if arm.users == 0:
                    bpy.data.armatures.remove(arm)
            elif obj.type == 'CURVE' and obj.data:
                cu = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if cu.users == 0:
                    bpy.data.curves.remove(cu)
            else:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

def obtener_o_crear_coleccion(nombre_coleccion):
    """Obtiene o crea una colección y la vincula a la escena activa."""
    col = bpy.data.collections.get(nombre_coleccion)
    if not col:
        col = bpy.data.collections.new(nombre_coleccion)
        bpy.context.scene.collection.children.link(col)
    return col

def contar_triangulos(objetos):
    """Triángulos reales tras evaluar modificadores (exactamente lo que se exporta)."""
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

def calcular_aabb(objetos):
    """Calcula el Bounding Box (AABB) global evaluado de una lista de objetos."""
    min_co = [float('inf')] * 3
    max_co = [float('-inf')] * 3
    dg = bpy.context.evaluated_depsgraph_get()

    for o in objetos:
        if o.type != 'MESH':
            continue
        eo = o.evaluated_get(dg)
        for corner in eo.bound_box:
            world_corner = eo.matrix_world @ mathutils.Vector(corner)
            for i in range(3):
                min_co[i] = min(min_co[i], world_corner[i])
                max_co[i] = max(max_co[i], world_corner[i])

    if min_co[0] == float('inf'):
        return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]

    tamano = [max_co[i] - min_co[i] for i in range(3)]
    centro = [(min_co[i] + max_co[i]) / 2.0 for i in range(3)]
    return min_co, max_co, tamano, centro

def crear_material(nombre, base_color=(0.1, 0.1, 0.1, 1.0), metallic=0.0, roughness=0.5,
                   emission_color=(0, 0, 0, 1.0), emission_strength=0.0):
    """Crea o actualiza un material con Principled BSDF compatible con glTF."""
    mat = bpy.data.materials.get(nombre)
    if not mat:
        mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (300, 0)

    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # Configurar entradas BSDF
    if 'Base Color' in node_bsdf.inputs:
        node_bsdf.inputs['Base Color'].default_value = base_color
    if 'Metallic' in node_bsdf.inputs:
        node_bsdf.inputs['Metallic'].default_value = metallic
    if 'Roughness' in node_bsdf.inputs:
        node_bsdf.inputs['Roughness'].default_value = roughness
    if 'Emission Color' in node_bsdf.inputs:
        node_bsdf.inputs['Emission Color'].default_value = emission_color
    elif 'Emission' in node_bsdf.inputs:
        node_bsdf.inputs['Emission'].default_value = emission_color
    if 'Emission Strength' in node_bsdf.inputs:
        node_bsdf.inputs['Emission Strength'].default_value = emission_strength

    return mat

OPCIONES_GLB = dict(
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_animation_mode='ACTIONS',
    export_materials='EXPORT',
    export_skins=True,
    export_def_bones=True,
)

def exportar_glb(ruta_destino, objetos):
    """Exporta los objetos seleccionados a formato .glb aplicando filtros de compatibilidad."""
    os.makedirs(os.path.dirname(os.path.abspath(ruta_destino)), exist_ok=True)
    soportadas = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    kwargs = {k: v for k, v in OPCIONES_GLB.items() if k in soportadas}

    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objetos:
        o.select_set(True)

    if objetos:
        bpy.context.view_layer.objects.active = objetos[0]

    bpy.ops.export_scene.gltf(filepath=ruta_destino, **kwargs)
    print(f"[EXPORT GLB] Archivo exportado exitosamente a: {ruta_destino}")
