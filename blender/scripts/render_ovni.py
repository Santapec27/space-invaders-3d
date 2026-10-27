"""
blender/scripts/render_ovni.py - Generación de renders de estudio
(Hero, Cenital, Frontal) para el OVNI Bonus.
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

import build_ovni
import utils_blender

WS_DIR = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
ARTIFACTS_DIR = r"C:\Users\santa\.gemini\antigravity\brain\8f4f2fe9-1d8f-42d4-9ea7-14f535bae226"

def render_ovni_views():
    print("\n" + "=" * 60)
    print("Iniciando construcción y renderizado de OVNI Bonus...")
    print("=" * 60)

    # 1. Limpiar completamente objetos de escenas previas
    for o in list(bpy.data.objects):
        if not o.name.startswith("ovni_bonus"):
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Construir OVNI
    stats = build_ovni.construir_ovni()

    # Limpiar luces y cámaras
    for o in list(bpy.context.scene.objects):
        if o.name in ["Cube", "Light", "Camera", "LightKey", "LightFill", "LightRim", "CamRender", "CamHero", "CamStudio"]:
            bpy.data.objects.remove(o, do_unlink=True)

    # 3. Luces de estudio calibradas para materiales Arcade Neon amarillo
    if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
        bg_node = bpy.context.scene.world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs[0].default_value = (0.015, 0.018, 0.028, 1.0) # Fondo espacio profundo elegante

    lk = bpy.data.lights.new("LightKey", 'POINT')
    lk.energy = 180.0
    ok = bpy.data.objects.new("LightKey", lk)
    bpy.context.scene.collection.objects.link(ok)
    ok.location = (2.0, 1.6, 2.2)

    lf = bpy.data.lights.new("LightFill", 'POINT')
    lf.energy = 85.0
    of = bpy.data.objects.new("LightFill", lf)
    bpy.context.scene.collection.objects.link(of)
    of.location = (-1.8, 1.2, 1.4)

    lr = bpy.data.lights.new("LightRim", 'POINT')
    lr.energy = 200.0
    lr.color = (1.0, 0.85, 0.3) # Tinte dorado cálido
    orr = bpy.data.objects.new("LightRim", lr)
    bpy.context.scene.collection.objects.link(orr)
    orr.location = (0.0, -2.2, 1.8)

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

    # A) Vista Heroica Frontal-Oblicua (3/4)
    cam.location = (1.3, 1.5, 0.85)
    rot_quat = (mathutils.Vector((0, 0, 0.0)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 55.0
    bpy.context.view_layer.update()

    p_hero = os.path.join(WS_DIR, "blender", "renders", "ovni_bonus_hero.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_hero)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, "ovni_bonus_hero.png"))
    print(f"[RENDER HERO] Guardado en: {p_hero}")

    # B) Vista Cenital (Top-Down)
    cam.location = (0.0, 0.0, 2.4)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.data.lens = 45.0
    bpy.context.view_layer.update()

    p_cen = os.path.join(WS_DIR, "blender", "renders", "ovni_bonus_cenital.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_cen)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, "ovni_bonus_cenital.png"))
    print(f"[RENDER CENITAL] Guardado en: {p_cen}")

    # C) Vista Frontal (Front Eye-Level)
    cam.location = (0.0, 2.2, 0.35)
    rot_quat = (mathutils.Vector((0, 0, 0.0)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 55.0
    bpy.context.view_layer.update()

    p_front = os.path.join(WS_DIR, "blender", "renders", "ovni_bonus_frontal.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_front)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, "ovni_bonus_frontal.png"))
    print(f"[RENDER FRONTAL] Guardado en: {p_front}")

    # Escribir informe stats a archivo JSON
    ruta_stats = os.path.join(WS_DIR, "blender", "renders", "ovni_stats.json")
    with open(ruta_stats, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n[OK] Renders y estadísticas de OVNI Bonus generados con éxito.")
    return stats

if __name__ == "__main__":
    render_ovni_views()
