class_name InvaderFleet
extends Node3D

## Señales de estado y flujo
signal formacion_lista
signal fleet_cleared
signal invaders_reached_player
signal score_added(points: int)

@export var rows: int = 5
@export var cols: int = 11
@export var spacing_x: float = 2.4
@export var spacing_z: float = 2.0
@export var max_x_bound: float = 17.0
@export var step_distance: float = 0.8
@export var drop_distance: float = 1.2
@export var player_z_limit: float = 14.5

var invaders: Array[Area3D] = []
var filas_enemigos: Array = [] # Array de Arrays agrupados por fila
var direction: float = 1.0
var should_drop: bool = false
var step_timer: float = 0.0
var current_step_interval: float = 0.7
var max_step_interval: float = 0.75
var min_step_interval: float = 0.06
var total_count: int = 55
var step_counter: int = 0

var shoot_timer: float = 0.0
var shoot_interval: float = 1.6

@onready var invader_scene: PackedScene = preload("res://scenes/invader.tscn")
@onready var laser_scene: PackedScene = preload("res://scenes/laser.tscn")

func _ready() -> void:
	total_count = rows * cols

## Inicializa la flota y deja a los enemigos instanciados y ocultos para la intro
func instanciar_flota(start_pos: Vector3 = Vector3(-12.0, 0.0, -14.0)) -> void:
	for inv in invaders:
		if is_instance_valid(inv):
			inv.queue_free()
	invaders.clear()
	filas_enemigos.clear()
	
	global_position = start_pos
	direction = 1.0
	should_drop = false
	step_counter = 0
	
	for r in range(rows):
		var fila_actual: Array[Area3D] = []
		var type_idx: int = 0
		if r == 0:
			type_idx = 0 # Calamar / Squid
		elif r <= 2:
			type_idx = 1 # Cangrejo / Crab
		else:
			type_idx = 2 # Behemoth / Pulpo
			
		for c in range(cols):
			var inv: Area3D = invader_scene.instantiate() as Area3D
			add_child(inv)
			if inv.has_method("setup_type"):
				inv.call("setup_type", type_idx)
			inv.set("grid_x", c)
			inv.set("grid_y", r)
			inv.position = Vector3(c * spacing_x, 0.0, r * spacing_z)
			inv.visible = false
			if inv.has_method("desactivar_colision"):
				inv.call("desactivar_colision")
				
			if inv.has_signal("invader_destroyed"):
				inv.connect("invader_destroyed", _on_invader_destroyed)
				
			invaders.append(inv)
			fila_actual.append(inv)
			
		filas_enemigos.append(fila_actual)
			
	total_count = invaders.size()
	_update_step_interval()

## Criterio Spawn por Filas (20% Rúbrica Parcial 2)
## Despliega fila por fila completa simultáneamente de la más lejana a la más cercana
func spawn_por_filas() -> void:
	for fila in filas_enemigos:
		if fila.is_empty():
			continue # Evita bloquearse si una fila está vacía
			
		var tw := create_tween().set_parallel(true)
		for inv in fila:
			if not is_instance_valid(inv):
				continue
			var vis: Node3D = inv.get("visual")
			if vis:
				vis.scale = Vector3.ONE * 0.001
				vis.position.y = 4.0
				inv.visible = true
				tw.tween_property(vis, "scale", Vector3.ONE, 0.45) \
					.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
				tw.tween_property(vis, "position:y", 0.0, 0.45) \
					.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
					
		await tw.finished # Callback: la fila actual completó su descenso y rebote
		
		for inv in fila:
			if is_instance_valid(inv) and inv.has_method("reproducir"):
				inv.call("reproducir", "Idle-loop")
				
		await get_tree().create_timer(0.12).timeout # Respiro rítmico entre filas
		
	# Al finalizar todas las filas, se reactivan colisiones para el combate
	activar_todas_las_colisiones()
	formacion_lista.emit()

func activar_todas_las_colisiones() -> void:
	for inv in invaders:
		if is_instance_valid(inv) and inv.has_method("activar_colision"):
			inv.call("activar_colision")

func _process(delta: float) -> void:
	# El enjambre permanece inmóvil si el juego está en intro, menú, o pausa
	if GameManager.estado != GameManager.Estado.JUGANDO:
		return
		
	if invaders.is_empty():
		return
		
	step_timer += delta
	if step_timer >= current_step_interval:
		step_timer = 0.0
		_do_step()
		
	shoot_timer += delta
	if shoot_timer >= shoot_interval:
		shoot_timer = 0.0
		_do_alien_shoot()

func _do_step() -> void:
	step_counter += 1
	if AudioManager:
		AudioManager.play_invader_step(step_counter)
	
	if should_drop:
		direction *= -1.0
		global_position.z += drop_distance
		global_position.x += direction * step_distance
		should_drop = false
	else:
		global_position.x += direction * step_distance
		
		var edge_reached: bool = false
		var reached_bottom: bool = false
		
		for inv in invaders:
			if not is_instance_valid(inv):
				continue
			var global_x: float = inv.global_position.x
			var global_z: float = inv.global_position.z
			
			if (direction > 0.0 and global_x >= max_x_bound) or (direction < 0.0 and global_x <= -max_x_bound):
				edge_reached = true
			if global_z >= player_z_limit:
				reached_bottom = true
				
		if edge_reached:
			should_drop = true
			
		if reached_bottom:
			invaders_reached_player.emit()

func _do_alien_shoot() -> void:
	if invaders.is_empty():
		return
		
	var alive_invaders: Array[Area3D] = []
	for inv in invaders:
		if is_instance_valid(inv) and not inv.get("muerto"):
			alive_invaders.append(inv)
			
	if alive_invaders.is_empty():
		return
		
	var shooter: Area3D = alive_invaders.pick_random()
	
	# Micro-interacción: Telegrafía visual antes de disparar
	if shooter.has_method("telegrafiar_disparo"):
		shooter.call("telegrafiar_disparo")
		
	var laser: Area3D = laser_scene.instantiate() as Area3D
	laser.set("is_player_laser", false)
	get_parent().add_child(laser)
	laser.global_position = shooter.global_position + Vector3(0, 0, 1.0)

func _on_invader_destroyed(invader: Area3D, points: int) -> void:
	score_added.emit(points)
	invaders.erase(invader)
	
	if invaders.is_empty():
		# Regla de rúbrica: Esperar a que el último enemigo termine su salida 3D
		if is_instance_valid(invader) and invader.has_signal("salida_terminada"):
			await invader.salida_terminada
		GameFeel.hit_stop(0.20) # Hit-stop mayor al limpiar la oleada
		fleet_cleared.emit()
	else:
		_update_step_interval()

func _update_step_interval() -> void:
	var count: int = invaders.size()
	var ratio: float = float(count) / float(total_count)
	current_step_interval = lerpf(min_step_interval, max_step_interval, ratio)

## Función de depuración para tecla F11
func clear_all_debug() -> void:
	var list := invaders.duplicate()
	for inv in list:
		if is_instance_valid(inv):
			if inv.has_method("eliminar_enemigo"):
				inv.call("eliminar_enemigo")
			else:
				inv.queue_free()
