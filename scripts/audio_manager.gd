extends Node

# AudioManager singleton / autoload for retro arcade audio effects
var sfx_shoot: AudioStream = preload("res://assets/audio/shoot.wav")
var sfx_invader_killed: AudioStream = preload("res://assets/audio/invader_killed.wav")
var sfx_player_hit: AudioStream = preload("res://assets/audio/player_hit.wav")
var sfx_steps: Array[AudioStream] = [
	preload("res://assets/audio/invader_step1.wav"),
	preload("res://assets/audio/invader_step2.wav"),
	preload("res://assets/audio/invader_step3.wav"),
	preload("res://assets/audio/invader_step4.wav")
]
var sfx_ufo_flying: AudioStream = preload("res://assets/audio/ufo_flying.wav")
var sfx_ufo_killed: AudioStream = preload("res://assets/audio/ufo_killed.wav")
var sfx_game_over: AudioStream = preload("res://assets/audio/game_over.wav")
var sfx_wave_cleared: AudioStream = preload("res://assets/audio/wave_cleared.wav")
var sfx_ui_click: AudioStream = preload("res://assets/audio/ui_click.wav")

var _pool: Array[AudioStreamPlayer] = []
var _pool_size: int = 8
var _current_player_idx: int = 0

var _ufo_player: AudioStreamPlayer
var _jingle_player: AudioStreamPlayer

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	
	for i in range(_pool_size):
		var player := AudioStreamPlayer.new()
		player.bus = "Master"
		add_child(player)
		_pool.append(player)
		
	_ufo_player = AudioStreamPlayer.new()
	_ufo_player.stream = sfx_ufo_flying
	_ufo_player.bus = "Master"
	add_child(_ufo_player)
	
	_jingle_player = AudioStreamPlayer.new()
	_jingle_player.bus = "Master"
	add_child(_jingle_player)

func _play_sfx(stream: AudioStream, volume_db: float = 0.0, pitch_scale: float = 1.0) -> void:
	if not stream:
		return
	var player := _pool[_current_player_idx]
	_current_player_idx = (_current_player_idx + 1) % _pool_size
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch_scale
	player.play()

func play_shoot() -> void:
	_play_sfx(sfx_shoot, -2.0, randf_range(0.96, 1.04))

func play_invader_killed() -> void:
	_play_sfx(sfx_invader_killed, -1.0, randf_range(0.92, 1.08))

func play_player_hit() -> void:
	_play_sfx(sfx_player_hit, 1.0, 1.0)

func play_invader_step(step_index: int) -> void:
	var idx := posmod(step_index, sfx_steps.size())
	_play_sfx(sfx_steps[idx], 0.0, 1.0)

func start_ufo() -> void:
	if _ufo_player and not _ufo_player.playing:
		_ufo_player.play()

func stop_ufo() -> void:
	if _ufo_player and _ufo_player.playing:
		_ufo_player.stop()

func play_ufo_killed() -> void:
	stop_ufo()
	_play_sfx(sfx_ufo_killed, 1.0, 1.0)

func play_wave_cleared() -> void:
	_jingle_player.stream = sfx_wave_cleared
	_jingle_player.play()

func play_game_over() -> void:
	stop_ufo()
	_jingle_player.stream = sfx_game_over
	_jingle_player.play()

func play_ui_click() -> void:
	_play_sfx(sfx_ui_click, -4.0, 1.0)
