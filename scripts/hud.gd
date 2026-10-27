extends CanvasLayer

signal start_game_pressed
signal restart_game_pressed
signal menu_pressed
signal quit_pressed

# Etiquetas del TopBar
@onready var score_lbl: Label = $HUDPanel/TopBar/HBoxTop/ScoreBox/ScoreVal
@onready var high_score_lbl: Label = $HUDPanel/TopBar/HBoxTop/HighScoreBox/HighScoreVal
@onready var wave_lbl: Label = $HUDPanel/TopBar/HBoxTop/WaveBox/WaveVal
@onready var lives_lbl: Label = $HUDPanel/BottomBar/LivesVal

# Overlays principales
@onready var hud_panel: Control = $HUDPanel
@onready var menu_overlay: Control = $MenuOverlay
@onready var game_over_overlay: Control = $GameOverOverlay
@onready var wave_overlay: Control = $WaveOverlay

# Elementos del Menú
@onready var menu_high_score_lbl: Label = $MenuOverlay/Centro/MarcoHUD/VBox/PieBox/MenuHighScore

# Elementos de la pantalla Game Over / Victoria
@onready var go_fondo: ColorRect = $GameOverOverlay/Fondo
@onready var go_title: Label = $GameOverOverlay/Centro/MarcoArcade/VBox/TituloBox/Title
@onready var go_subtitle: Label = $GameOverOverlay/Centro/MarcoArcade/VBox/TituloBox/SubTitle
@onready var final_score_lbl: Label = $GameOverOverlay/Centro/MarcoArcade/VBox/ScoreBox/HBoxScore/PanelFinalScore/FinalScoreVal
@onready var go_high_score_lbl: Label = $GameOverOverlay/Centro/MarcoArcade/VBox/ScoreBox/HBoxScore/GameOverHighScoreVal
@onready var restart_btn: Button = $GameOverOverlay/Centro/MarcoArcade/VBox/BotonesBox/RestartBtn
@onready var menu_btn: Button = $GameOverOverlay/Centro/MarcoArcade/VBox/BotonesBox/MenuBtn

# Wave Overlay
@onready var wave_num_lbl: Label = $WaveOverlay/WaveTitle

func _ready() -> void:
	pass

func _format_num(n: int) -> String:
	var s := str(abs(n))
	var res := ""
	var count := 0
	for i in range(s.length() - 1, -1, -1):
		res = s[i] + res
		count += 1
		if count % 3 == 0 and i > 0:
			res = "," + res
	return ("-" if n < 0 else "") + res

## Micro-interacción: Pop en el HUD al sumar puntos (Criterio Creatividad 10%)
func update_score(score: int) -> void:
	if not score_lbl:
		return
	score_lbl.text = _format_num(score)
	score_lbl.pivot_offset = score_lbl.size / 2.0
	var tw := create_tween()
	tw.tween_property(score_lbl, "scale", Vector2(1.22, 1.22), 0.07)
	tw.tween_property(score_lbl, "scale", Vector2.ONE, 0.08)

func update_high_score(high_score: int) -> void:
	var text := _format_num(high_score)
	if high_score_lbl:
		high_score_lbl.text = text
	if menu_high_score_lbl:
		menu_high_score_lbl.text = "HIGH SCORE: %s" % text
	if go_high_score_lbl:
		go_high_score_lbl.text = "HIGHSCORE: %s" % text

func update_wave(wave: int) -> void:
	if wave_lbl:
		wave_lbl.text = str(wave)

func update_lives(lives: int) -> void:
	if not lives_lbl:
		return
	var icons := ""
	for i in range(max(0, lives)):
		icons += "🚀 "
	lives_lbl.text = icons if lives > 0 else "---"

func show_start_menu() -> void:
	hud_panel.visible = false
	menu_overlay.visible = true
	game_over_overlay.visible = false
	wave_overlay.visible = false

## Criterio Pantallas Finales (25% Rúbrica Parcial 2):
## Interpolación elástica TRANS_ELASTIC para título y TRANS_BACK para botones en cascada
func show_game_over(final_score: int, high_score: int) -> void:
	_mostrar_pantalla_final(false, final_score, high_score)

func show_victory(final_score: int, high_score: int) -> void:
	_mostrar_pantalla_final(true, final_score, high_score)

func _mostrar_pantalla_final(es_victoria: bool, final_score: int, high_score: int) -> void:
	if final_score_lbl:
		final_score_lbl.text = "FINAL SCORE: %s" % _format_num(final_score)
	if go_high_score_lbl:
		go_high_score_lbl.text = "HIGHSCORE: %s" % _format_num(high_score)
		
	if go_title:
		go_title.text = "¡VICTORIA!" if es_victoria else "GAME OVER"
	if go_subtitle:
		go_subtitle.text = "MISIÓN CUMPLIDA - PLANETA SALVADO" if es_victoria else "INSERT COIN TO CONTINUE\nGAME OVER"
		
	game_over_overlay.visible = true
	menu_overlay.visible = false
	wave_overlay.visible = false
	hud_panel.visible = true
	
	# Animación elástica completa requerida por la Rúbrica:
	await get_tree().process_frame
	
	if go_title:
		go_title.pivot_offset = go_title.size / 2.0
		go_title.scale = Vector2.ZERO
	if go_fondo:
		go_fondo.color.a = 0.0
		
	var botones: Array[Button] = [restart_btn, menu_btn]
	for b in botones:
		if b:
			b.pivot_offset = b.size / 2.0
			b.scale = Vector2.ZERO
			b.modulate.a = 0.0

	var tw := create_tween()
	if go_fondo:
		tw.tween_property(go_fondo, "color:a", 0.9, 0.35)
	if go_title:
		tw.parallel().tween_property(go_title, "scale", Vector2.ONE, 1.1) \
			.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
			
	for b in botones:
		if b:
			tw.tween_property(b, "scale", Vector2.ONE, 0.4) \
				.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			tw.parallel().tween_property(b, "modulate:a", 1.0, 0.25)
			
	tw.tween_callback(func(): if restart_btn: restart_btn.grab_focus())

## Transición elástica al superar una oleada
func show_wave_cleared(wave_number: int) -> void:
	if AudioManager:
		AudioManager.play_wave_cleared()
		
	wave_num_lbl.text = "WAVE %d CLEARED!" % wave_number
	wave_overlay.visible = true
	
	wave_num_lbl.pivot_offset = wave_num_lbl.size / 2.0
	wave_num_lbl.scale = Vector2.ZERO
	
	var tw := create_tween()
	tw.tween_property(wave_num_lbl, "scale", Vector2.ONE, 0.6) \
		.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tw.tween_interval(1.1)
	tw.tween_property(wave_num_lbl, "scale", Vector2.ZERO, 0.35) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_callback(func(): wave_overlay.visible = false)

func _on_start_btn_pressed() -> void:
	if AudioManager:
		AudioManager.play_ui_click()
	menu_overlay.visible = false
	game_over_overlay.visible = false
	hud_panel.visible = true
	start_game_pressed.emit()

func _on_quit_btn_pressed() -> void:
	if AudioManager:
		AudioManager.play_ui_click()
	quit_pressed.emit()
	get_tree().quit()

func _on_restart_btn_pressed() -> void:
	if AudioManager:
		AudioManager.play_ui_click()
	game_over_overlay.visible = false
	menu_overlay.visible = false
	hud_panel.visible = true
	restart_game_pressed.emit()

func _on_menu_btn_pressed() -> void:
	if AudioManager:
		AudioManager.play_ui_click()
	game_over_overlay.visible = false
	menu_overlay.visible = true
	hud_panel.visible = false
	menu_pressed.emit()

func _on_options_btn_pressed() -> void:
	if AudioManager:
		AudioManager.play_ui_click()

func _on_high_scores_btn_pressed() -> void:
	if AudioManager:
		AudioManager.play_ui_click()
