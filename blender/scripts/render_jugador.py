"""
blender/scripts/render_jugador.py - Generación de renders de estudio
(Hero, Cenital, Frontal, Isométrica) para las naves Mk I a Mk V.
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

import build_jugador

WS_DIR = r"c:\Users\santa\OneDrive\Desktop\space inverder Godot+Blender"
ARTIFACTS_DIR = r"C:\Users\santa\.gemini\antigravity\brain\8f4f2fe9-1d8f-42d4-9ea7-14f535bae226"

def render_ship_views(nivel):
    cfg = build_jugador.CONFIG_NIVELES[nivel]
    suf = cfg['sufijo']
    print(f"\n--- Generando renders para Nave Mk {nivel} ({cfg['nombre']}) ---")

    # 1. Construir nave
    build_jugador.construir_nave(nivel)

    # Limpiar objetos no deseados
    for o in list(bpy.context.scene.objects):
        if o.name in ["Cube", "Light", "Camera", "LightKey", "LightFill", "LightRim", "CamRender", "CamHero", "CamStudio"]:
            bpy.data.objects.remove(o, do_unlink=True)

    # Luces de estudio profesionales
    lk = bpy.data.lights.new("LightKey", 'POINT')
    lk.energy = 260.0
    ok = bpy.data.objects.new("LightKey", lk)
    bpy.context.scene.collection.objects.link(ok)
    ok.location = (2.2, 2.0, 2.4)

    lf = bpy.data.lights.new("LightFill", 'POINT')
    lf.energy = 110.0
    of = bpy.data.objects.new("LightFill", lf)
    bpy.context.scene.collection.objects.link(of)
    of.location = (-2.2, 1.2, 1.4)

    lr = bpy.data.lights.new("LightRim", 'POINT')
    lr.energy = 200.0
    orr = bpy.data.objects.new("LightRim", lr)
    bpy.context.scene.collection.objects.link(orr)
    orr.location = (0.0, -2.5, 1.8)

    # Cámara de renderizado
    cd = bpy.data.cameras.new("CamRender")
    cam = bpy.data.objects.new("CamRender", cd)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 768
    bpy.context.scene.render.film_transparent = False

    tmp_render = os.path.join(WS_DIR, "blender", "renders", "temp_render.png")
    bpy.context.scene.render.filepath = tmp_render

    # 1. Vista Heroica Frontal-Oblicua
    cam.location = (1.1, 1.3, 0.75)
    rot_quat = (mathutils.Vector((0, 0, 0.02)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 60.0
    bpy.context.view_layer.update()

    p_hero = os.path.join(WS_DIR, "blender", "renders", f"nave_{suf}_hero.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_hero)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, f"nave_{suf}_hero.png"))
    print(f"[RENDER HERO] Guardado: {p_hero}")

    # 2. Vista Cenital
    cam.location = (0.0, 0.0, 2.3)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.data.lens = 45.0
    bpy.context.view_layer.update()

    p_cen = os.path.join(WS_DIR, "blender", "renders", f"nave_{suf}_cenital.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_cen)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, f"nave_{suf}_cenital.png"))
    print(f"[RENDER CENITAL] Guardado: {p_cen}")

    # 3. Vista Frontal
    cam.location = (0.0, 2.2, 0.30)
    rot_quat = (mathutils.Vector((0, 0, 0.02)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 55.0
    bpy.context.view_layer.update()

    p_front = os.path.join(WS_DIR, "blender", "renders", f"nave_{suf}_frontal.png")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(tmp_render, p_front)
    shutil.copy2(tmp_render, os.path.join(ARTIFACTS_DIR, f"nave_{suf}_frontal.png"))
    print(f"[RENDER FRONTAL] Guardado: {p_front}")

    # Limpiar luces y cámara temporales
    for obj in [ok, of, orr, cam]:
        bpy.data.objects.remove(obj, do_unlink=True)

    return {
        'hero': p_hero,
        'cenital': p_cen,
        'frontal': p_front
    }

def ejecutar_lote(niveles):
    for n in niveles:
        render_ship_views(n)

if __name__ == "__main__":
    ejecutar_lote([1, 2, 3, 4, 5])
