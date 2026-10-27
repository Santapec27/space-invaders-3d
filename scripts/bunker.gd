class_name Bunker
extends Node3D

const MODEL_SANO = preload("res://assets/models/escudo/escudo_bloque_sano.glb")
const MODEL_AGRIETADO = preload("res://assets/models/escudo/escudo_bloque_agrietado.glb")

# Clase interna de cada bloque destructible con física y modelos 3D de Blender
class BunkerBlock extends Area3D:
	var hp: int = 2
	var visual: Node3D
	var model_inst: Node3D = null
	var col: CollisionShape3D
	var is_destroyed: bool = false
	
	func _init(pos: Vector3, size: Vector3) -> void:
		position = pos
		add_to_group("bunker_block")
		add_to_group("bloques_escudo")
		
		col = CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = size
		col.shape = box
		add_child(col)
		
		visual = Node3D.new()
		add_child(visual)
		_set_model(MODEL_SANO)

	func damage() -> void:
		if is_destroyed:
			return
			
		hp -= 1
		if hp <= 0:
			is_destroyed = true
			if col:
				col.set_deferred("disabled", true)
			if AudioManager:
				AudioManager.play_invader_killed()
				
			# Micro-interacción: Contracción y vórtice 3D al destruirse el bloque
			var tw := create_tween().set_parallel(true)
			tw.tween_property(visual, "scale", Vector3.ONE * 0.001, 0.22) \
				.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
			tw.tween_property(visual, "rotation:y", TAU, 0.22).as_relative()
			tw.set_parallel(false)
			tw.tween_callback(queue_free)
		else:
			_set_model(MODEL_AGRIETADO)
			# Micro-interacción: Pequeña vibración y flash al cuartearse
			var tween := create_tween()
			tween.tween_property(visual, "position:y", 0.12, 0.04)
			tween.tween_property(visual, "position:y", 0.0, 0.05)

	func _set_model(packed: PackedScene) -> void:
		if model_inst and is_instance_valid(model_inst):
			visual.remove_child(model_inst)
			model_inst.queue_free()
		model_inst = packed.instantiate()
		visual.add_child(model_inst)

@export var columns: int = 6
@export var rows: int = 4
@export var block_size: Vector3 = Vector3(0.5, 0.5, 0.5)

var blocks: Array[BunkerBlock] = []

func _ready() -> void:
	add_to_group("bunker")
	_create_bunker_blocks()

func _create_bunker_blocks() -> void:
	blocks.clear()
	var start_x := - (columns * block_size.x) / 2.0
	for r in range(rows):
		for c in range(columns):
			# Hueco en arco clásico en la base
			if r == rows - 1 and (c == 2 or c == 3):
				continue
			var pos := Vector3(start_x + c * block_size.x, 0.0, r * block_size.z)
			var block := BunkerBlock.new(pos, block_size)
			add_child(block)
			blocks.append(block)

## Criterio Secuencia de Entrada: Escudos emergen del suelo (F5.3)
func spawn_escudos() -> void:
	var tw := create_tween().set_parallel(true)
	var i := 0
	for b in blocks:
		if is_instance_valid(b) and b.visual:
			b.visual.position.y = -1.5
			b.visible = true
			tw.tween_property(b.visual, "position:y", 0.0, 0.35) \
				.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT).set_delay(i * 0.025)
			i += 1
	await tw.finished
