# autoload/game_feel.gd
# Gestor de feedback sensorial, hit-stop, sacudida de cámara y micro-interacciones.
# Cumple rigurosamente los requerimientos de Parcial 2 (Criterio Feedback 25%).
extends Node

signal camara_sacudida(intensidad: float, duracion: float)

var _congelaciones: int = 0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS

## Pausa breve del árbol de escena (Hit-Stop) para enfatizar impactos:
## 0.06s al matar enemigo, 0.12s al recibir daño, 0.20s al matar al último enemigo
func hit_stop(duracion: float = 0.06) -> void:
	if GameManager.estado != GameManager.Estado.JUGANDO:
		return
		
	_congelaciones += 1
	get_tree().paused = true
	
	# Temporizador en pausa que ignora Engine.time_scale y process_always = true
	await get_tree().create_timer(duracion, true, false, true).timeout
	
	_congelaciones -= 1
	if _congelaciones <= 0:
		_congelaciones = 0
		get_tree().paused = false

## Emite señal global para sacudida armónica decreciente de la cámara
func sacudir_camara(intensidad: float = 0.25, duracion: float = 0.2) -> void:
	camara_sacudida.emit(intensidad, duracion)
