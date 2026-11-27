extends SceneTree

const Studio = preload("res://studio.gd")

func _initialize() -> void:
	_bake.call_deferred()

func _bake() -> void:
	var studio := Studio.new()
	studio.name = "AnechoicStudio"
	root.add_child(studio)
	_set_owners(studio, studio)
	var scene := PackedScene.new()
	var result := scene.pack(studio)
	if result == OK:
		result = ResourceSaver.save(scene, "res://studio.tscn")
	if result != OK:
		push_error("Could not save studio scene: %s" % error_string(result))
	else:
		print("Baked the editable studio scene.")
	quit(result)

func _set_owners(parent: Node, studio: Node) -> void:
	for child in parent.get_children():
		child.owner = studio
		if child.scene_file_path.is_empty():
			_set_owners(child, studio)
