class_name UFO
extends Area3D

signal ufo_hit(score_value: int)

@export var speed: float = 12.0
var direction: float = 1.0

@onready var visual: Node3D = $Visual
@onready var colision: CollisionShape3D = $CollisionShape3D

func _ready() -> void:
	add_to_group("ufo")
	if AudioManager:
		AudioManager.start_ufo()
		
	var anim: AnimationPlayer = find_child("AnimationPlayer", true, false)
	if anim:
		if anim.has_animation("Idle"):
			anim.play("Idle")
		elif anim.has_animation("Idle-loop"):
			anim.play("Idle-loop")

func setup_flight(start_x: float, dir: float) -> void:
	global_position.x = start_x
	direction = dir

func _physics_process(delta: float) -> void:
	global_position.x += direction * speed * delta
	
	if abs(global_position.x) > 30.0:
		if AudioManager:
			AudioManager.stop_ufo()
		queue_free()

func _exit_tree() -> void:
	if AudioManager:
		AudioManager.stop_ufo()

func take_hit_from_player() -> void:
	if colision:
		colision.set_deferred("disabled", true)
		
	if AudioManager:
		AudioManager.play_ufo_killed()
		AudioManager.stop_ufo()
		
	var bonus_options: Array[int] = [100, 200, 300]
	var bonus: int = bonus_options.pick_random()
	ufo_hit.emit(bonus)
	
	_crear_puntaje_flotante(bonus)
	GameFeel.sacudir_camara(0.25, 0.2)
	await GameFeel.hit_stop(0.06)
	
	if not is_inside_tree():
		return
		
	var tween := create_tween().set_parallel(true)
	if visual:
		tween.tween_property(visual, "scale", Vector3.ONE * 0.001, 0.35) \
			.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
		tween.tween_property(visual, "rotation:y", TAU * 2.0, 0.35).as_relative()
	tween.set_parallel(false)
	tween.tween_callback(queue_free)

func _crear_puntaje_flotante(bonus: int) -> void:
	var lbl := Label3D.new()
	lbl.text = "BONUS +%d" % bonus
	lbl.font_size = 36
	lbl.outline_size = 8
	lbl.modulate = Color(1.0, 0.9, 0.0, 1.0)
	lbl.outline_modulate = Color(0, 0, 0, 0.9)
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.global_position = global_position + Vector3(0.0, 1.0, 0.0)
	get_parent().add_child(lbl)
	
	var tw := lbl.create_tween().set_parallel(true)
	tw.tween_property(lbl, "position:y", lbl.position.y + 1.8, 0.6).set_ease(Tween.EASE_OUT)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.6).set_delay(0.2)
	tw.set_parallel(false)
	tw.tween_callback(lbl.queue_free)
