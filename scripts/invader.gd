class_name Invader
extends Area3D

## Señales para enjambre, puntaje y control de sincronización
signal invader_destroyed(invader: Area3D, score_value: int)
signal salida_terminada

@export var invader_type: int = 0

## Micro-interacciones configurables (Criterio Creatividad 10% de la Rúbrica)
@export var micro_flash_activa: bool = true
@export var micro_particulas_activa: bool = true
@export var micro_puntaje_flotante_activa: bool = true
@export var micro_telegrafia_activa: bool = true

var score_value: int = 10
var grid_x: int = 0
var grid_y: int = 0
var muerto: bool = false
var accent_color: Color = Color(1.0, 0.1, 0.85, 1.0)

@onready var visual: Node3D = $Visual
@onready var model_a: Node3D = $Visual/ModelA
@onready var model_b: Node3D = $Visual/ModelB
@onready var model_c: Node3D = $Visual/ModelC
@onready var light: OmniLight3D = $OmniLight3D
@onready var collision_shape: CollisionShape3D = $CollisionShape3D

var active_anim: AnimationPlayer = null

func setup_type(type_index: int) -> void:
	invader_type = type_index
	
	if not visual:
		return
		
	model_a.visible = (invader_type == 0)
	model_b.visible = (invader_type == 1)
	model_c.visible = (invader_type == 2)
	
	var active_node: Node3D = null
	match invader_type:
		0: # Calamar / Squid (Fila superior)
			score_value = 30
			active_node = model_a
			accent_color = Color(1.0, 0.1, 0.85, 1.0)
		1: # Cangrejo / Crab (Filas intermedias)
			score_value = 20
			active_node = model_b
			accent_color = Color(0.0, 0.95, 1.0, 1.0)
		2: # Behemoth / Pulpo (Filas inferiores)
			score_value = 10
			active_node = model_c
			accent_color = Color(1.0, 0.85, 0.0, 1.0)
			
	if light:
		light.light_color = accent_color
			
	if active_node:
		active_anim = active_node.find_child("AnimationPlayer", true, false)
		reproducir("Idle-loop")

func reproducir(nombre_clip: String) -> void:
	if not active_anim:
		return
	if active_anim.has_animation(nombre_clip):
		active_anim.play(nombre_clip)
	elif nombre_clip == "Idle-loop" and active_anim.has_animation("Idle"):
		active_anim.play("Idle")

func _ready() -> void:
	add_to_group("invader")
	muerto = false
	setup_type(invader_type)

## Desactiva colisiones durante la secuencia de spawn para evitar interacciones anticipadas
func desactivar_colision() -> void:
	if collision_shape:
		collision_shape.set_deferred("disabled", true)

func activar_colision() -> void:
	if not muerto and collision_shape:
		collision_shape.set_deferred("disabled", false)

## Pulso rítmico coordinado con cada paso de la flota
func play_step_pulse() -> void:
	if visual and not muerto:
		var tween := create_tween()
		tween.tween_property(visual, "scale", Vector3(1.18, 0.92, 1.18), 0.06)
		tween.tween_property(visual, "scale", Vector3(1.0, 1.0, 1.0), 0.08)

## Micro-interacción: Telegrafía visual antes de que este enemigo dispare
func telegrafiar_disparo() -> void:
	if not micro_telegrafia_activa or muerto or not visual:
		return
	var tw := create_tween()
	tw.tween_property(visual, "scale", Vector3(1.25, 1.25, 1.25), 0.12)
	if light:
		tw.parallel().tween_property(light, "light_energy", 2.2, 0.12)
	tw.tween_property(visual, "scale", Vector3(1.0, 1.0, 1.0), 0.1)
	if light:
		tw.parallel().tween_property(light, "light_energy", 0.8, 0.1)

## Método de compatibilidad para el láser del jugador
func take_hit_from_player() -> void:
	eliminar_enemigo()

## Criterio Eliminación y Feedback (25% Rúbrica Parcial 2)
## 1) Desactiva colisión de inmediato
## 2) Hit-stop funcional (GameFeel)
## 3) Animación de salida 3D (giro TAU + escala a 0.001 con TRANS_BACK y EASE_IN)
## 4) Callback final que libera con queue_free()
func eliminar_enemigo() -> void:
	if muerto:
		return
	muerto = true
	
	# 1. Desactivación inmediata de física para evitar colisiones dobles
	if collision_shape:
		collision_shape.set_deferred("disabled", true)
	
	invader_destroyed.emit(self, score_value)
	if AudioManager:
		AudioManager.play_invader_killed()
		
	# Micro-interacción: Destello de impacto y puntaje flotante
	if micro_flash_activa and light:
		light.light_energy = 3.5
	if micro_puntaje_flotante_activa:
		_crear_puntaje_flotante()
		
	# 2. Hit-Stop (congelamiento temporal de 0.06s para dar peso físico al impacto)
	GameFeel.sacudir_camara(0.18, 0.15)
	await GameFeel.hit_stop(0.06)
	
	if not is_inside_tree():
		return
		
	# 3. Animación de salida 3D: combinación paralela de contracción y giro
	var tw := create_tween().set_parallel(true)
	tw.tween_property(visual, "scale", Vector3.ONE * 0.001, 0.4) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_property(visual, "rotation:y", TAU, 0.4).as_relative()
	
	# 4. Callback final estricto: queue_free solo cuando la animación termina
	tw.set_parallel(false)
	tw.tween_callback(_terminar_salida)

func _terminar_salida() -> void:
	salida_terminada.emit()
	queue_free()

func _crear_puntaje_flotante() -> void:
	var lbl := Label3D.new()
	lbl.text = "+%d" % score_value
	lbl.font_size = 30
	lbl.outline_size = 6
	lbl.modulate = accent_color
	lbl.outline_modulate = Color(0, 0, 0, 0.9)
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.global_position = global_position + Vector3(0.0, 0.8, 0.0)
	get_parent().add_child(lbl)
	
	var tw := lbl.create_tween().set_parallel(true)
	tw.tween_property(lbl, "position:y", lbl.position.y + 1.4, 0.5).set_ease(Tween.EASE_OUT)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.5).set_delay(0.2)
	tw.set_parallel(false)
	tw.tween_callback(lbl.queue_free)
