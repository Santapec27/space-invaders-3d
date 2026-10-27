# autoload/game_manager.gd
# Gestor global de estado, puntaje, vidas, niveles y control de flujo de entrada.
# Cumple rigurosamente los requerimientos de Parcial 2 y PLAN_IMPLEMENTACION.md
extends Node

enum Estado {
	MENU,
	INTRO,
	JUGANDO,
	NIVEL_COMPLETADO,
	VICTORIA,
	GAME_OVER
}

signal estado_cambiado(nuevo_estado: Estado)
signal puntaje_actualizado(nuevo_puntaje: int)
signal record_actualizado(nuevo_record: int)
signal vidas_actualizadas(nuevas_vidas: int)
signal nivel_iniciado(nivel: int)

var estado: Estado = Estado.MENU
var input_bloqueado: bool = true
var puntaje: int = 0
var record_puntaje: int = 0
var vidas: int = 3
var nivel_actual: int = 1

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	cargar_record()

func cambiar_estado(nuevo: Estado) -> void:
	estado = nuevo
	estado_cambiado.emit(nuevo)

func bloquear_input() -> void:
	input_bloqueado = true

## Se llama desde el ÚLTIMO callback de la secuencia de entrada (entrar_en_escena del jugador)
func desbloquear_input() -> void:
	input_bloqueado = false
	cambiar_estado(Estado.JUGANDO)

func sumar_puntaje(puntos: int) -> void:
	puntaje += puntos
	puntaje_actualizado.emit(puntaje)
	if puntaje > record_puntaje:
		record_puntaje = puntaje
		record_actualizado.emit(record_puntaje)
		guardar_record()

func guardar_record() -> void:
	var f := FileAccess.open("user://highscore.save", FileAccess.WRITE)
	if f:
		f.store_32(record_puntaje)
		f.close()

func cargar_record() -> void:
	if FileAccess.file_exists("user://highscore.save"):
		var f := FileAccess.open("user://highscore.save", FileAccess.READ)
		if f:
			record_puntaje = f.get_32()
			f.close()
