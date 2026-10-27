class_name Laser
extends Area3D

@export var speed: float = 35.0
@export var is_player_laser: bool = true

var direction: Vector3 = Vector3(0, 0, -1)
var is_destroyed: bool = false

@onready var light: OmniLight3D = $OmniLight3D
@onready var mesh_instance: MeshInstance3D = $MeshInstance3D

func _ready() -> void:
	is_destroyed = false
	if not is_player_laser:
		direction = Vector3(0, 0, 1)
		_setup_enemy_visuals()
	else:
		_setup_player_visuals()
	
	area_entered.connect(_on_area_entered)
	body_entered.connect(_on_body_entered)

func _physics_process(delta: float) -> void:
	if is_destroyed:
		return
		
	var move_dist: float = speed * delta
	var next_pos: Vector3 = global_position + direction * move_dist
	
	# Raycast check along flight path to guarantee 100% collision hit detection
	var space_state := get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(global_position, next_pos + direction * 0.8)
	query.collide_with_areas = true
	query.collide_with_bodies = true
	query.exclude = [self]
	
	var result := space_state.intersect_ray(query)
	if not result.is_empty():
		var hit_collider: Object = result.get("collider")
		if hit_collider and hit_collider != self:
			if _handle_collision(hit_collider):
				return
				
	global_position = next_pos
	
	if abs(global_position.z) > 40.0 or abs(global_position.x) > 40.0:
		queue_free()

func _setup_player_visuals() -> void:
	if has_node("Visual/PlayerBala"):
		$Visual/PlayerBala.visible = true
	if has_node("Visual/EnemyBala"):
		$Visual/EnemyBala.visible = false
	if light:
		light.light_color = Color(0.0, 1.0, 0.9, 1.0)

func _setup_enemy_visuals() -> void:
	if has_node("Visual/PlayerBala"):
		$Visual/PlayerBala.visible = false
	if has_node("Visual/EnemyBala"):
		$Visual/EnemyBala.visible = true
	if light:
		light.light_color = Color(1.0, 0.2, 0.4, 1.0)

func _on_area_entered(area: Area3D) -> void:
	_handle_collision(area)

func _on_body_entered(body: Node3D) -> void:
	_handle_collision(body)

func _handle_collision(target: Object) -> bool:
	if is_destroyed or target == self:
		return false
		
	if is_player_laser:
		if target.has_method("take_hit_from_player"):
			is_destroyed = true
			target.call("take_hit_from_player")
			queue_free()
			return true
		elif target.is_in_group("bunker_block"):
			is_destroyed = true
			if target.has_method("damage"):
				target.call("damage")
			queue_free()
			return true
	else:
		if target.has_method("take_hit_from_enemy"):
			is_destroyed = true
			target.call("take_hit_from_enemy")
			queue_free()
			return true
		elif target.is_in_group("bunker_block"):
			is_destroyed = true
			if target.has_method("damage"):
				target.call("damage")
			queue_free()
			return true
			
	return false
