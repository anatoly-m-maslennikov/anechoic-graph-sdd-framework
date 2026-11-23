extends RefCounted

const PIANO_X := 2.75
const PIANO_FACE_Z := -0.984
const PIANO_JACK := Vector3(PIANO_X - 0.835, 0.43, -1.22)
const WHITE_KEY_WIDTH := 0.031


static func build(parent: Node3D) -> void:
	_mixer(parent)
	_piano(parent)


static func _mixer(parent: Node3D) -> void:
	var mixer := _node(parent, "Shared analog mixing console")
	var teal := _material("226764", 0.39)
	var deck := _material("254847", 0.53)
	var deep := _material("10282a", 0.52)
	var groove := _material("091719", 0.6)
	var maple := _material("ad7345", 0.41)
	var end_grain := _material("795335", 0.48)
	var bronze := _material("b77a4f", 0.32, 0.5)
	var marker := _material("8baba4", 0.56)
	var ivory := _material("dbdbc0", 0.39)
	var coral := _material("fe886c", 0.4, 0.0, 0.38)
	var green := _material("64e0ae", 0.34, 0.0, 0.62)
	var amber := _material("f6b96e", 0.38, 0.0, 0.55)
	var dim_green := _material("315f53", 0.43)

	for z in [-1.48, 1.49]:
		_box(mixer, "Steel side stand", Vector3(-0.46, 0.58, z), Vector3(0.13, 0.80, 0.13), deep)
		_box(mixer, "Stand foot", Vector3(-0.72, 0.21, z), Vector3(0.87, 0.06, 0.15), deep)
		_box(mixer, "Stand cap", Vector3(-1.12, 0.215, z), Vector3(0.08, 0.07, 0.16), bronze)
	_box(mixer, "Stand cross rail", Vector3(-0.47, 0.48, 0), Vector3(0.10, 0.08, 2.95), deep)

	var surface := _node(mixer, "Sloped control surface")
	surface.position = Vector3(-0.785, 1.12, 0.01)
	surface.rotation.z = 0.116
	_box(surface, "Painted steel chassis", Vector3(0, -0.102, 0), Vector3(1.18, 0.18, 3.36), teal)
	_box(surface, "Control face", Vector3(0.015, -0.017, 0), Vector3(1.06, 0.038, 3.31), deck)
	_box(surface, "Pine wrist rest", Vector3(-0.582, -0.004, 0), Vector3(0.115, 0.075, 3.32), maple)
	_box(surface, "Wrist rest edge", Vector3(-0.638, -0.012, 0), Vector3(0.012, 0.043, 3.32), end_grain)
	_box(surface, "Rear housing", Vector3(0.551, 0.016, 0), Vector3(0.136, 0.103, 3.32), teal)
	_box(surface, "Rear brass seam", Vector3(0.603, 0.069, 0), Vector3(0.014, 0.009, 3.30), bronze)
	for z in [-1.686, 1.686]:
		_box(surface, "Solid pine end cheek", Vector3(-0.005, -0.052, z), Vector3(1.27, 0.192, 0.065), maple)
		_box(surface, "End cheek trim", Vector3(-0.005, 0.044, z), Vector3(1.24, 0.013, 0.060), end_grain)
		for x in [-0.44, 0.42]:
			var bolt := _cylinder(surface, "End cheek fastener", Vector3(x, -0.03, z + signf(z) * 0.033), 0.018, 0.006, bronze)
			bolt.rotation.x = PI / 2

	var knob_colors: Array[StandardMaterial3D] = [teal, bronze, deck]
	for bank: int in [-1, 1]:
		var bank_node := _node(surface, "Assistant channels" if bank < 0 else "Human channels")
		for channel in range(8):
			var z: float = bank * (0.31 + channel * 0.17)
			var strip := _node(bank_node, "Channel %02d" % (channel + 1))
			strip.position.z = z
			_box(strip, "Channel boundary", Vector3(0.014, 0.006, 0.083), Vector3(1.015, 0.006, 0.006), marker)
			_box(strip, "Fader bed", Vector3(-0.286, 0.007, 0), Vector3(0.418, 0.012, 0.111), deep)
			_box(strip, "Fader slot", Vector3(-0.289, 0.013, 0), Vector3(0.375, 0.007, 0.020), groove)
			for tick in range(7):
				var x := -0.453 + tick * 0.054
				_box(strip, "Fader scale tick", Vector3(x, 0.017, 0.040), Vector3(0.007, 0.004, 0.020), marker)
			var slider_x := -0.423 + ((channel * 5 + bank + 12) % 9) * 0.037
			_box(strip, "Fader cap", Vector3(slider_x, 0.033, -0.002), Vector3(0.052, 0.037, 0.093), ivory)
			_box(strip, "Fader index", Vector3(slider_x, 0.053, -0.002), Vector3(0.008, 0.005, 0.075), deep)
			_box(strip, "Mute key surround", Vector3(-0.018, 0.011, 0), Vector3(0.086, 0.021, 0.087), groove)
			var mute_light := coral if channel % 4 == 2 else green
			_box(strip, "Mute key", Vector3(-0.018, 0.028, 0), Vector3(0.058, 0.021, 0.059), mute_light)
			for control in range(3):
				var x := 0.099 + control * 0.126
				_knob(strip, Vector3(x, 0.023, 0), 0.045, knob_colors[control], ivory, (channel - control) * 0.29)
			_box(strip, "Signal LED socket", Vector3(0.463, 0.01, 0), Vector3(0.044, 0.013, 0.09), deep)
			_box(strip, "Signal LED", Vector3(0.465, 0.021, -0.019), Vector3(0.019, 0.01, 0.024), green if channel % 3 != 1 else dim_green)
			_box(strip, "Peak LED", Vector3(0.465, 0.021, 0.019), Vector3(0.019, 0.01, 0.024), amber if channel in [2, 5] else dim_green)

	var master := _node(surface, "Stereo master")
	_box(master, "Master faceplate", Vector3(0.002, 0.007, 0), Vector3(1.03, 0.012, 0.43), deep)
	for side in [-1, 1]:
		var z: float = side * 0.108
		_box(master, "Master fader slot", Vector3(-0.307, 0.018, z), Vector3(0.331, 0.01, 0.027), groove)
		for tick in range(8):
			_box(master, "Master fader tick", Vector3(-0.449 + tick * 0.04, 0.018, z + side * 0.036), Vector3(0.007, 0.005, 0.019), marker)
		_box(master, "Master fader cap", Vector3(-0.286 + side * 0.033, 0.040, z), Vector3(0.061, 0.046, 0.101), bronze)
		_box(master, "Master fader index", Vector3(-0.286 + side * 0.033, 0.065, z), Vector3(0.008, 0.005, 0.083), ivory)
		_box(master, "Master route key", Vector3(-0.078, 0.025, z), Vector3(0.076, 0.025, 0.085), amber)

	_knob(master, Vector3(0.088, 0.031, 0), 0.092, teal, ivory, -0.65)
	_box(master, "Stereo meter glass", Vector3(0.345, 0.031, 0), Vector3(0.24, 0.044, 0.31), groove)
	for side in [-1, 1]:
		for step in range(9):
			var light := green
			if step >= 7:
				light = amber if step == 7 and side == 1 else dim_green
			_box(master, "Stereo meter segment", Vector3(0.257 + step * 0.022, 0.055, side * 0.066), Vector3(0.016, 0.009, 0.096), light)


static func _piano(parent: Node3D) -> void:
	var piano := _node(parent, "Upright code piano")
	piano.position.x = PIANO_X
	var lacquer := _material("246360", 0.27)
	var darker := _material("17433f", 0.39)
	var trim := _material("33857b", 0.37)
	var oak := _material("8e5939", 0.40)
	var bronze := _material("bf935c", 0.31, 0.63)
	var shadow := _material("0f2526", 0.43)
	var white := _material("f0e6cd", 0.31)
	var black := _material("172125", 0.35)
	var felt := _material("934d45", 0.94)

	_box(piano, "Rear case", Vector3(0, 1.25, -1.297), Vector3(1.66, 2.10, 0.57), lacquer)
	_box(piano, "Lid", Vector3(0, 2.33, -1.286), Vector3(1.71, 0.071, 0.62), lacquer)
	_box(piano, "Lid beading", Vector3(0, 2.306, -0.979), Vector3(1.66, 0.024, 0.016), bronze)
	_box(piano, "Lower front case", Vector3(0, 0.536, -0.997), Vector3(1.611, 0.60, 0.094), darker)
	_box(piano, "Soundboard border", Vector3(0, 0.549, -0.944), Vector3(1.405, 0.48, 0.025), lacquer)
	_box(piano, "Soundboard inset", Vector3(0, 0.549, -0.928), Vector3(1.335, 0.399, 0.019), darker)
	for x in [-0.606, 0.606]:
		_box(piano, "Soundboard inlay", Vector3(x, 0.549, -0.914), Vector3(0.007, 0.367, 0.006), bronze)
	_box(piano, "Plinth", Vector3(0, 0.236, -1.273), Vector3(1.68, 0.11, 0.62), oak)
	_box(piano, "Keybed", Vector3(0, 0.907, -0.751), Vector3(1.678, 0.11, 0.493), lacquer)
	_box(piano, "Key slip", Vector3(0, 0.944, -0.503), Vector3(1.67, 0.039, 0.027), darker)
	_box(piano, "Keybed front inlay", Vector3(0, 0.932, -0.488), Vector3(1.63, 0.009, 0.008), bronze)
	_box(piano, "Key rail felt", Vector3(0, 0.983, -0.931), Vector3(1.61, 0.019, 0.037), felt)
	_box(piano, "Hinged fallboard", Vector3(0, 1.053, -0.982), Vector3(1.61, 0.126, 0.098), lacquer)
	_box(piano, "Fallboard hinge", Vector3(0, 1.114, -0.926), Vector3(1.60, 0.012, 0.016), bronze)

	for side in [-1, 1]:
		var x: float = side * 0.784
		_box(piano, "Front keybed support", Vector3(x, 0.524, -0.626), Vector3(0.095, 0.681, 0.113), lacquer)
		_box(piano, "Support foot", Vector3(x, 0.218, -0.630), Vector3(0.122, 0.076, 0.165), oak)
		_box(piano, "Support facing", Vector3(x, 0.546, -0.568), Vector3(0.032, 0.554, 0.011), trim)
		_box(piano, "Upper front stile", Vector3(x, 1.708, -0.984), Vector3(0.091, 1.186, 0.075), lacquer)
		_box(piano, "Upper stile inlay", Vector3(x, 1.708, -0.943), Vector3(0.01, 1.08, 0.01), bronze)

	var keys := _node(piano, "88 piano keys")
	var white_count := 0
	var black_count := 0
	for pitch in range(21, 109):
		if pitch % 12 in [0, 2, 4, 5, 7, 9, 11]:
			var x := (white_count - 25.5) * WHITE_KEY_WIDTH
			_box(keys, "White key %d" % pitch, Vector3(x, 0.973, -0.724), Vector3(0.0287, 0.032, 0.391), white)
			white_count += 1
		else:
			var x := (white_count - 26) * WHITE_KEY_WIDTH
			_box(keys, "Black key %d" % pitch, Vector3(x, 1.001, -0.812), Vector3(0.0185, 0.045, 0.224), black)
			black_count += 1
	assert(white_count == 52 and black_count == 36)

	_box(piano, "Pedal plate", Vector3(0, 0.299, -0.944), Vector3(0.367, 0.127, 0.042), oak)
	for x in [-0.111, 0.111]:
		_box(piano, "Pedal recess", Vector3(x, 0.299, -0.920), Vector3(0.090, 0.080, 0.013), shadow)
		var pedal := _node(piano, "Soft pedal" if x < 0 else "Sustain pedal")
		pedal.position = Vector3(x, 0.28, -0.898)
		var arm := _box(pedal, "Brass pedal arm", Vector3(0, -0.006, 0.104), Vector3(0.051, 0.037, 0.223), bronze)
		arm.rotation.x = 0.10
		var tread := _cylinder(pedal, "Rounded pedal tread", Vector3(0, -0.021, 0.220), 0.048, 0.033, bronze)
		tread.scale.z = 1.46

	var jack_center := PIANO_JACK - piano.position
	var washer := _cylinder(piano, "Audio jack brass washer", jack_center, 0.043, 0.018, bronze)
	washer.rotation.z = PI / 2
	var socket := _cylinder(piano, "Audio jack opening", jack_center + Vector3(-0.010, 0, 0), 0.026, 0.008, shadow)
	socket.rotation.z = PI / 2
	_code_display(piano, bronze, shadow)


static func _code_display(piano: Node3D, bronze: StandardMaterial3D, shadow: StandardMaterial3D) -> void:
	var panel := _node(piano, "Integrated upper front code panel")
	panel.position = Vector3(0, 1.71, PIANO_FACE_Z)
	_box(panel, "Display surround", Vector3.ZERO, Vector3(1.48, 1.15, 0.035), shadow)
	var screen := _material("0b2024", 0.38, 0.0, 0.20)
	_box(panel, "Display glass", Vector3(0, 0, 0.019), Vector3(1.44, 1.11, 0.006), screen)
	for y in [-0.565, 0.565]:
		_box(panel, "Panel brass trim", Vector3(0, y, 0.023), Vector3(1.46, 0.012, 0.008), bronze)
	var syntax: Array[Color] = [Color("f1ead6"), Color("ffbb9f"), Color("8df5d6")]
	var source := [
		[[1, "func "], [2, "wave"], [0, "(t):"]],
		[[1, "  return "], [2, "sin"], [0, "(t)"]],
		[[1, "var "], [0, "hz = "], [2, "440"]],
		[[1, "var "], [0, "g="], [2, "0.8"]],
	]
	var mono := SystemFont.new()
	mono.font_names = PackedStringArray(["Menlo", "DejaVu Sans Mono", "Liberation Mono", "Consolas", "monospace"])
	var y := 0.43
	for line in source:
		var x := -0.69
		for token in line:
			var label := Label3D.new()
			label.name = "Code token"
			label.font = mono
			label.font_size = 30
			label.pixel_size = 0.0041
			label.text = token[1]
			label.modulate = syntax[token[0]]
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
			label.outline_size = 0
			label.position = Vector3(x, y, 0.026)
			panel.add_child(label, true)
			x += mono.get_string_size(label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, label.font_size).x * label.pixel_size
		y -= 0.19


static func _knob(parent: Node3D, position: Vector3, radius: float, body: StandardMaterial3D, index: StandardMaterial3D, angle: float) -> void:
	var knob := _node(parent, "Rotary control")
	knob.position = position
	knob.rotation.y = angle
	_cylinder(knob, "Knob collar", Vector3(0, -0.008, 0), radius * 1.12, 0.02, body)
	_cylinder(knob, "Knob crown", Vector3(0, 0.018, 0), radius, 0.040, body)
	_box(knob, "Pointer", Vector3(radius * 0.60, 0.040, 0), Vector3(radius * 0.60, 0.007, 0.011), index)


static func _node(parent: Node3D, label: String) -> Node3D:
	var node := Node3D.new()
	node.name = label
	parent.add_child(node, true)
	return node


static func _box(parent: Node3D, label: String, position: Vector3, size: Vector3, material: StandardMaterial3D) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return _mesh(parent, label, position, mesh, material)


static func _cylinder(parent: Node3D, label: String, position: Vector3, radius: float, height: float, material: StandardMaterial3D) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.bottom_radius = radius
	mesh.top_radius = radius
	mesh.height = height
	mesh.radial_segments = 16
	mesh.rings = 1
	return _mesh(parent, label, position, mesh, material)


static func _mesh(parent: Node3D, label: String, position: Vector3, mesh: PrimitiveMesh, material: StandardMaterial3D) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.name = label
	instance.position = position
	instance.mesh = mesh
	instance.material_override = material
	parent.add_child(instance, true)
	return instance


static func _material(hex: String, roughness: float, metal: float = 0.0, emission: float = 0.0) -> StandardMaterial3D:
	var color := Color(hex)
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = roughness
	material.metallic = metal
	if emission > 0.0:
		material.emission_enabled = true
		material.emission = color
		material.emission_energy_multiplier = emission
	return material
