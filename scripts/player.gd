class_name Player
extends Area3D

signal player_hit(lives_left: int)
signal player_destroyed

## Modelos de nave para alternar cada 2 niveles (requisito del usuario)
const SHIP_MODELS: Array[PackedScene] = [
	preload("res://assets/models/jugador/nave_mk1.glb"),     # Niveles 1 - 2
	preload("res://assets/models/jugador/nave_mk2.glb"),     # Niveles 3 - 4
	preload("res://assets/models/jugador/nave_mk3.glb"),     # Niveles 5 - 6
	preload("res://assets/models/jugador/nave_mk4.glb"),     # Niveles 7 - 8
	preload("res://assets/models/jugador/nave_mk5.glb"),     # Niveles 9 - 10
	preload("res://assets/models/jugador/rover_1.glb"),      # Niveles 11 - 12
	preload("res://assets/models/jugador/rover_2.glb"),      # Niveles 13 - 14
	preload("res://assets/models/jugador/rover_round.glb")   # Niveles 15+
]

@export var move_speed: float = 16.0
@export var max_x: float = 17.5
@export var fire_rate: float = 0.35
@export var max_lives: int = 3

## Micro-interacciones activables
@export var micro_inclinacion_activa: bool = true
@export var micro_destello_canon_activa: bool = true

var lives: int = 3
var can_shoot: bool = true
var is_alive: bool = true
var is_invulnerable: bool = false
var current_model_idx: int = -1

@onready var laser_scene: PackedScene = preload("res://scenes/laser.tscn")
@onready var cannon_pos: Node3D = $CannonPos
@onready var visual: Node3D = $Visual
@onready var collision_shape: CollisionShape3D = $CollisionShape3D

var muzzle_light: OmniLight3D = null

func _ready() -> void:
	lives = max_lives
	is_alive = true
	add_to_group("player")
	
	# Preparar luz para el destello del cañón (micro-interacción #4)
	muzzle_light = OmniLight3D.new()
	muzzle_light.light_color = Color(0.2, 0.9, 1.0, 1.0)
	muzzle_light.light_energy = 0.0
	muzzle_light.omni_range = 3.5
	cannon_pos.add_child(muzzle_light)
	
	update_model_for_wave(1)

func _process(delta: float) -> void:
	# Criterio Control de Flujo: Input estrictamente bloqueado durante intros y pausas
	if GameManager.input_bloqueado or not is_alive:
		return
		
	var input_dir: float = 0.0
	if Input.is_action_pressed("move_left"):
		input_dir -= 1.0
	if Input.is_action_pressed("move_right"):
		input_dir += 1.0
		
	global_position.x += input_dir * move_speed * delta
	global_position.x = clamp(global_position.x, -max_x, max_x)
	
	# Micro-interacción: Inclinación al moverse (Banking Tilt en eje Z)
	if visual and micro_inclinacion_activa:
		var target_rot_z := -input_dir * 0.28
		visual.rotation.z = lerpf(visual.rotation.z, target_rot_z, delta * 12.0)
	
	if Input.is_action_pressed("shoot") and can_shoot:
		_shoot()

## Criterio Secuencia de Entrada (Spawn por Filas 20%):
## Marcianos -> Escudos -> Jugador.
## El juego permanece bloqueado hasta el ÚLTIMO callback de entrar_en_escena().
func entrar_en_escena() -> void:
	visible = true
	is_alive = true
	can_shoot = true
	is_invulnerable = false
	
	visual.scale = Vector3.ONE * 0.001
	visual.position.y = 6.0
	
	reproducir("Spawn")
	
	var tw := create_tween().set_parallel(true)
	tw.tween_property(visual, "scale", Vector3(1.25, 1.25, 1.25), 0.9) \
		.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(visual, "position:y", 0.0, 0.7) \
		.set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	
	# ÚLTIMO callback de toda la secuencia de inicio:
	tw.set_parallel(false)
	tw.tween_callback(GameManager.desbloquear_input)

## Cambia el modelo de nave cada 2 niveles
func update_model_for_wave(wave: int) -> void:
	var target_idx: int = int((wave - 1) / 2)
	target_idx = clamp(target_idx, 0, SHIP_MODELS.size() - 1)
	
	if target_idx == current_model_idx and visual and visual.has_node("Model"):
		return
		
	current_model_idx = target_idx
	if not visual:
		return
		
	var model_node = visual.get_node_or_null("Model")
	if model_node:
		visual.remove_child(model_node)
		model_node.queue_free()
		
	var packed: PackedScene = SHIP_MODELS[current_model_idx]
	var inst := packed.instantiate()
	inst.name = "Model"
	visual.add_child(inst)
	
	reproducir("Idle-loop")

func reproducir(nombre_clip: String) -> void:
	var anim: AnimationPlayer = visual.find_child("AnimationPlayer", true, false)
	if anim and anim.has_animation(nombre_clip):
		anim.play(nombre_clip)

func _shoot() -> void:
	if not can_shoot or not is_alive or GameManager.input_bloqueado:
		return
	
	can_shoot = false
	
	# Micro-interacción: Destello de cañón (Muzzle Flash)
	if micro_destello_canon_activa and muzzle_light:
		muzzle_light.light_energy = 2.8
		var tw_muzzle := create_tween()
		tw_muzzle.tween_property(muzzle_light, "light_energy", 0.0, 0.08)
		
	# Micro-interacción: Leve impulso de sacudida al disparar
	GameFeel.sacudir_camara(0.06, 0.08)
	
	var laser: Area3D = laser_scene.instantiate() as Area3D
	laser.set("is_player_laser", true)
	get_parent().add_child(laser)
	laser.global_position = cannon_pos.global_position
	
	if AudioManager:
		AudioManager.play_shoot()
	
	var timer := get_tree().create_timer(fire_rate)
	timer.timeout.connect(_on_shoot_cooldown_finished)

func _on_shoot_cooldown_finished() -> void:
	can_shoot = true

## Feedback al jugador al recibir daño (Criterio Eliminación y Feedback 25%)
func take_hit_from_enemy() -> void:
	if not is_alive or is_invulnerable:
		return
		
	lives -= 1
	GameManager.vidas = lives
	
	if AudioManager:
		AudioManager.play_player_hit()
		
	player_hit.emit(lives)
	
	# 1. Hit-Stop marcado (0.12s) + Sacudida fuerte de cámara
	GameFeel.sacudir_camara(0.45, 0.25)
	await GameFeel.hit_stop(0.12)
	
	if lives <= 0:
		is_alive = false
		visible = false
		player_destroyed.emit()
		GameManager.cambiar_estado(GameManager.Estado.GAME_OVER)
	else:
		_reaparecer()

func _reaparecer() -> void:
	is_invulnerable = true
	var tw := create_tween()
	# Parpadeo de invulnerabilidad
	for i in range(5):
		tw.tween_property(visual, "modulate:a", 0.2, 0.1)
		tw.tween_property(visual, "modulate:a", 1.0, 0.1)
	tw.tween_callback(func(): is_invulnerable = false)

func reset(start_x: float = 0.0) -> void:
	global_position.x = start_x
	visible = true
	is_alive = true
	can_shoot = true
	is_invulnerable = false
