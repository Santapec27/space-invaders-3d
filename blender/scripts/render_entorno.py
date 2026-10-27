"""
blender/scripts/render_entorno.py - Generación de renders de estudio
(Hero, Cenital, Frontal) para el Planeta Orbital de Fondo.
Proyecto: Space Invaders 3D
"""

import bpy
import bmesh
import math
import mathutils
import os
import sys
import shutil
import json

directorio_scripts = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender\blender\scripts"
if directorio_scripts not in sys.path:
    sys.path.append(directorio_scripts)

import build_entorno
import utils_blender

WS_DIR = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
ARTIFACTS_DIR = r"C:\Users\santa\.gemini\antigravity\brain\8f4f2fe9-1d8f-42d4-9ea7-14f535bae226"

def render_entorno_views():
    print("\n" + "=" * 60)
    print("Iniciando construcción y renderizado del Planeta Orbital de Fondo...")
    print("=" * 60)

    # 1. Limpiar objetos de escenas previas
    for o in list(bpy.data.objects):
        if not o.name.startswith("planeta_fondo"):
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Construir Planeta
    stats = build_entorno.construir_planeta()

    # Limpiar luces y cámaras
    for o in list(bpy.context.scene.objects):
        if o.name in ["Cube", "Light", "Camera", "LightKey", "LightFill", "LightRim", "CamRender", "CamHero", "CamStudio"]:
            bpy.data.objects.remove(o, do_unlink=True)

    # 3. Luces de escala astronómica (Estrella lejana + rebote de nebulosa)
    if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
        bg_node = bpy.context.scene.world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs[0].default_value = (0.010, 0.012, 0.022, 1.0) # Fondo espacio profundo

    lk = bpy.data.lights.new("LightKey", 'POINT')
    lk.energy = 420.0
    lk.color = (1.0, 0.98, 0.92) # Luz solar estelar blanca cálida
    ok = bpy.data.objects.new("LightKey", lk)
    bpy.context.scene.collection.objects.link(ok)
    ok.location = (2.8, 3.6, 2.5)

    lf = bpy.data.lights.new("LightFill", 'POINT')
    lf.energy = 160.0
    lf.color = (0.35, 0.65, 0.95) # Nebulosa ambiental cian
    of = bpy.data.objects.new("LightFill", lf)
    bpy.context.scene.collection.objects.link(of)
    of.location = (-3.2, 1.8, 1.4)

    lr = bpy.data.lights.new("LightRim", 'POINT')
    lr.energy = 320.0
    lr.color = (0.30, 0.85, 1.0) # Rim light atmósfera cian intensa
    orr = bpy.data.objects.new("LightRim", lr)
    bpy.context.scene.collection.objects.link(orr)
    orr.location = (-1.2, -3.8, 1.6)

    # Cámara de renderizado
    cd = bpy.data.cameras.new("CamRender")
    cam = bpy.data.objects.new("CamRender", cd)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 768
    bpy.context.scene.render.film_transparent = False

    os.makedirs(os.path.join(WS_DIR, "blender", "renders"), exist_ok=True)
    tmp_render = os.path.join(WS_DIR, "blender", "renders", "temp_render.png")
    bpy.context.scene.render.filepath = tmp_render

    # A) Vista Heroica Oblicua (3/4 - mostrando curvatura, anillos y estación orbital)
    cam.location = (3.2, 3.4, 2.1)
    rot_quat = (mathutils.Vector((0, 0, 0.0)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 50.0
    bpy.context.view_layer.update()

    p_hero = os.path.join(WS_DIR, "blender", "renders", "planeta_fondo_hero.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_hero)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, "planeta_fondo_hero.png"))
    print(f"[RENDER HERO] Guardado en: {p_hero}")

    # B) Vista Cenital (Top-Down polar)
    cam.location = (0.0, 0.0, 4.8)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.data.lens = 42.0
    bpy.context.view_layer.update()

    p_cen = os.path.join(WS_DIR, "blender", "renders", "planeta_fondo_cenital.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_cen)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, "planeta_fondo_cenital.png"))
    print(f"[RENDER CENITAL] Guardado en: {p_cen}")

    # C) Vista Frontal (Ecuatorial)
    cam.location = (0.0, 4.6, 0.8)
    rot_quat = (mathutils.Vector((0, 0, 0.0)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 48.0
    bpy.context.view_layer.update()

    p_front = os.path.join(WS_DIR, "blender", "renders", "planeta_fondo_frontal.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_front)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, "planeta_fondo_frontal.png"))
    print(f"[RENDER FRONTAL] Guardado en: {p_front}")

    # Escribir estadísticas a JSON
    ruta_stats = os.path.join(WS_DIR, "blender", "renders", "entorno_stats.json")
    with open(ruta_stats, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n[OK] Renders y estadísticas de Planeta Orbital generados con éxito.")
    return stats

if __name__ == "__main__":
    render_entorno_views()
