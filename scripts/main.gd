class_name MainGame
extends Node3D

enum GameState { MENU, PLAYING, GAME_OVER, VICTORY }

var state: GameState = GameState.MENU
var score: int = 0
var high_score: int = 0
var current_wave: int = 1

var player_instance: Node3D = null
var fleet_instance: Node3D = null
var ufo_timer: float = 0.0
var next_ufo_time: float = 20.0

# Variables para sacudida armónica de la cámara (GameFeel)
var _cam_base_pos: Vector3
var _cam_shake_intensity: float = 0.0
var _cam_shake_timer: float = 0.0

@onready var hud: CanvasLayer = $HUD
@onready var player_scene: PackedScene = preload("res://scenes/player.tscn")
@onready var fleet_scene: PackedScene = preload("res://scenes/invader_fleet.tscn")
@onready var bunker_scene: PackedScene = preload("res://scenes/bunker.tscn")
@onready var ufo_scene: PackedScene = preload("res://scenes/ufo.tscn")
@onready var camera: Camera3D = $Camera3D
@onready var planeta_fondo: Node3D = $PlanetaFondo
@onready var planet_illumination: OmniLight3D = get_node_or_null("PlanetIllumination")

var _planeta_base_pos: Vector3 = Vector3(0.0, 0.5, -34.0)
var planeta_anim: AnimationPlayer = null

func _ready() -> void:
	if camera:
		_cam_base_pos = camera.position
		
	GameFeel.camara_sacudida.connect(_on_camara_sacudida)
	
	# Inicializar posición base y activar la animación integrada de Blender del planeta
	if planeta_fondo:
		_planeta_base_pos = planeta_fondo.position
		planeta_anim = planeta_fondo.find_child("AnimationPlayer", true, false)
		if planeta_anim:
			var clip_name := "Idle-loop"
			if not planeta_anim.has_animation(clip_name) and planeta_anim.has_animation("Idle"):
				clip_name = "Idle"
			if planeta_anim.has_animation(clip_name):
				var anim_obj := planeta_anim.get_animation(clip_name)
				if anim_obj:
					anim_obj.loop_mode = Animation.LOOP_LINEAR
				planeta_anim.play(clip_name)
				planeta_anim.speed_scale = 0.8
	
	load_high_score()
	hud.call("update_high_score", high_score)
	hud.call("update_score", 0)
	hud.call("show_start_menu")
	
	if hud.has_signal("start_game_pressed"):
		hud.connect("start_game_pressed", start_new_game)
	if hud.has_signal("restart_game_pressed"):
		hud.connect("restart_game_pressed", start_new_game)
	if hud.has_signal("menu_pressed"):
		hud.connect("menu_pressed", _on_menu_pressed)
	
	_setup_bunkers_estaticos()

func _process(delta: float) -> void:
	# Movimiento orbital completo y vivo acorde a la animación del planeta
	if planeta_fondo:
		# 1. Rotación axial continua majestuosa
		planeta_fondo.rotate_y(delta * 0.03)
		
		# 2. Flotación senoidal armónica en X e Y (deriva orbital profunda)
		var t: float = Time.get_ticks_msec() / 1000.0
		var float_y: float = sin(t * 0.35) * 0.5
		var float_x: float = cos(t * 0.22) * 0.4
		
		# 3. Micro-paralaje reactivo respecto a la nave del jugador
		var parallax_x: float = 0.0
		if player_instance and is_instance_valid(player_instance):
			parallax_x = -player_instance.position.x * 0.07
			
		planeta_fondo.position.y = _planeta_base_pos.y + float_y
		planeta_fondo.position.x = lerpf(planeta_fondo.position.x, _planeta_base_pos.x + float_x + parallax_x, delta * 3.5)
		
		# 4. Modulación atmosférica sutil de la luz del planeta
		if planet_illumination:
			planet_illumination.light_energy = 2.4 + sin(t * 0.55) * 0.35
		
	# Sacudida suave decreciente de la cámara
	if _cam_shake_timer > 0.0:
		_cam_shake_timer -= delta
		var offset := Vector3(
			randf_range(-_cam_shake_intensity, _cam_shake_intensity),
			randf_range(-_cam_shake_intensity, _cam_shake_intensity),
			randf_range(-_cam_shake_intensity, _cam_shake_intensity) * 0.4
		)
		camera.position = _cam_base_pos + offset
		_cam_shake_intensity = lerpf(_cam_shake_intensity, 0.0, delta * 12.0)
	else:
		camera.position = _cam_base_pos
		
	if GameManager.estado != GameManager.Estado.JUGANDO:
		return
		
	ufo_timer += delta
	if ufo_timer >= next_ufo_time:
		ufo_timer = 0.0
		next_ufo_time = randf_range(16.0, 26.0)
		_spawn_ufo()

func _on_camara_sacudida(intensidad: float, duracion: float) -> void:
	_cam_shake_intensity = max(_cam_shake_intensity, intensidad)
	_cam_shake_timer = duracion

## Criterio Secuencia de Entrada (20% Rúbrica Parcial 2):
## Orden estricto: Marcianos ➔ Escudos ➔ Jugador.
## Input permanece bloqueado hasta el último callback de entrar_en_escena().
func start_new_game() -> void:
	state = GameState.PLAYING
	score = 0
	current_wave = 1
	GameManager.puntaje = 0
	GameManager.vidas = 3
	GameManager.nivel_actual = 1
	
	hud.call("update_score", score)
	hud.call("update_wave", current_wave)
	hud.call("update_high_score", high_score)
	
	_iniciar_secuencia_nivel(current_wave)

func _iniciar_secuencia_nivel(wave: int) -> void:
	GameManager.bloquear_input()
	GameManager.cambiar_estado(GameManager.Estado.INTRO)
	
	_clear_existing_entities()
	
	# 1. Marcianos: spawn por filas rítmico en bloque
	_spawn_fleet_instance()
	await fleet_instance.spawn_por_filas()
	
	# 2. Escudos: bloques emergen del suelo en oleada
	await _setup_bunkers_animados()
	
	# 3. Jugador: caída elástica que en su ÚLTIMO callback llama GameManager.desbloquear_input()
	_spawn_player_instance()
	player_instance.entrar_en_escena()

func _on_menu_pressed() -> void:
	state = GameState.MENU
	GameManager.cambiar_estado(GameManager.Estado.MENU)
	GameManager.bloquear_input()
	_clear_existing_entities()
	if player_instance and is_instance_valid(player_instance):
		player_instance.queue_free()
	if fleet_instance and is_instance_valid(fleet_instance):
		fleet_instance.queue_free()
	hud.call("update_high_score", high_score)
	hud.call("show_start_menu")

func _spawn_player_instance() -> void:
	if player_instance and is_instance_valid(player_instance):
		player_instance.queue_free()
		
	var player: Area3D = player_scene.instantiate() as Area3D
	add_child(player)
	player.global_position = Vector3(0.0, 0.0, 16.0)
	player.visible = false
	
	if player.has_signal("player_hit"):
		player.connect("player_hit", _on_player_hit)
	if player.has_signal("player_destroyed"):
		player.connect("player_destroyed", _on_player_destroyed)
		
	player_instance = player
	if player.has_method("update_model_for_wave"):
		player.call("update_model_for_wave", current_wave)
		
	hud.call("update_lives", GameManager.vidas)

func _spawn_fleet_instance() -> void:
	if fleet_instance and is_instance_valid(fleet_instance):
		fleet_instance.queue_free()
		
	var fleet: Node3D = fleet_scene.instantiate() as Node3D
	add_child(fleet)
	
	var wave_offset: float = float(current_wave - 1) * 0.8
	var start_z: float = clamp(-14.0 + wave_offset, -14.0, -8.0)
	
	fleet.instanciar_flota(Vector3(-12.0, 0.0, start_z))
	
	if fleet.has_signal("fleet_cleared"):
		fleet.connect("fleet_cleared", _on_fleet_cleared)
	if fleet.has_signal("invaders_reached_player"):
		fleet.connect("invaders_reached_player", _on_invaders_reached_player)
	if fleet.has_signal("score_added"):
		fleet.connect("score_added", _on_score_added)
		
	fleet_instance = fleet

func _setup_bunkers_estaticos() -> void:
	for b in get_tree().get_nodes_in_group("bunker"):
		b.queue_free()
		
	var positions: Array[float] = [-12.0, -4.0, 4.0, 12.0]
	for x in positions:
		var bunker: Node3D = bunker_scene.instantiate() as Node3D
		add_child(bunker)
		bunker.global_position = Vector3(x, 0.0, 10.0)

func _setup_bunkers_animados() -> void:
	for b in get_tree().get_nodes_in_group("bunker"):
		b.queue_free()
		
	var bunkers: Array[Node3D] = []
	var positions: Array[float] = [-12.0, -4.0, 4.0, 12.0]
	for x in positions:
		var bunker: Node3D = bunker_scene.instantiate() as Node3D
		add_child(bunker)
		bunker.global_position = Vector3(x, 0.0, 10.0)
		bunkers.append(bunker)
		
	for b in bunkers:
		if b.has_method("spawn_escudos"):
			b.call("spawn_escudos")
			
	await get_tree().create_timer(0.45).timeout

func _spawn_ufo() -> void:
	var ufo: Area3D = ufo_scene.instantiate() as Area3D
	add_child(ufo)
	var from_left: bool = randf() > 0.5
	var start_x: float = -25.0 if from_left else 25.0
	var dir: float = 1.0 if from_left else -1.0
	ufo.global_position = Vector3(start_x, 0.0, -22.0)
	if ufo.has_method("setup_flight"):
		ufo.call("setup_flight", start_x, dir)
	if ufo.has_signal("ufo_hit"):
		ufo.connect("ufo_hit", _on_score_added)

func _on_score_added(points: int) -> void:
	score += points
	GameManager.sumar_puntaje(points)
	hud.call("update_score", score)
	if score > high_score:
		high_score = score
		hud.call("update_high_score", high_score)
		save_high_score()

func _on_player_hit(lives: int) -> void:
	hud.call("update_lives", lives)

func _on_player_destroyed() -> void:
	_trigger_game_over()

func _on_invaders_reached_player() -> void:
	_trigger_game_over()

func _on_fleet_cleared() -> void:
	if current_wave >= 5:
		_trigger_victory()
		return
		
	current_wave += 1
	GameManager.nivel_actual = current_wave
	hud.call("update_wave", current_wave)
	hud.call("show_wave_cleared", current_wave - 1)
	
	for l in get_tree().get_nodes_in_group("laser"):
		l.queue_free()
		
	var timer := get_tree().create_timer(1.8)
	timer.timeout.connect(_on_wave_next_timer_timeout)

func _on_wave_next_timer_timeout() -> void:
	if state == GameState.PLAYING:
		_iniciar_secuencia_nivel(current_wave)

func _trigger_game_over() -> void:
	state = GameState.GAME_OVER
	GameManager.cambiar_estado(GameManager.Estado.GAME_OVER)
	GameManager.bloquear_input()
	if score > high_score:
		high_score = score
		save_high_score()
	if AudioManager:
		AudioManager.play_game_over()
	hud.call("show_game_over", score, high_score)

func _trigger_victory() -> void:
	state = GameState.VICTORY
	GameManager.cambiar_estado(GameManager.Estado.VICTORIA)
	GameManager.bloquear_input()
	if score > high_score:
		high_score = score
		save_high_score()
	if AudioManager:
		AudioManager.play_wave_cleared()
	hud.call("show_victory", score, high_score)

func _clear_existing_entities() -> void:
	for l in get_tree().get_nodes_in_group("laser"):
		l.queue_free()
	for u in get_tree().get_nodes_in_group("ufo"):
		u.queue_free()

func save_high_score() -> void:
	var file := FileAccess.open("user://highscore.save", FileAccess.WRITE)
	if file:
		file.store_32(high_score)
		file.close()

func load_high_score() -> void:
	if FileAccess.file_exists("user://highscore.save"):
		var file := FileAccess.open("user://highscore.save", FileAccess.READ)
		if file:
			high_score = file.get_32()
			file.close()

## Criterio Teclas de Depuración (F5.9 PLAN_IMPLEMENTACION.md):
## F1-F5: Salto de nivel
## F9: Forzar Victoria
## F10: Forzar Game Over
## F11: Destruir todos los enemigos
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_F1: _debug_saltar_nivel(1)
			KEY_F2: _debug_saltar_nivel(2)
			KEY_F3: _debug_saltar_nivel(3)
			KEY_F4: _debug_saltar_nivel(4)
			KEY_F5: _debug_saltar_nivel(5)
			KEY_F9: _trigger_victory()
			KEY_F10: _trigger_game_over()
			KEY_F11:
				if fleet_instance and fleet_instance.has_method("clear_all_debug"):
					fleet_instance.call("clear_all_debug")

func _debug_saltar_nivel(target_lvl: int) -> void:
	current_wave = target_lvl
	GameManager.nivel_actual = target_lvl
	hud.call("update_wave", current_wave)
	if player_instance and player_instance.has_method("update_model_for_wave"):
		player_instance.call("update_model_for_wave", current_wave)
	_iniciar_secuencia_nivel(current_wave)
