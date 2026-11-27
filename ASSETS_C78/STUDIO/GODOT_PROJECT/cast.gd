extends RefCounted

const Equipment = preload("res://equipment.gd")
const CARP_SCALES = preload("res://market/koi-scales.gdshader")
const FLOOR := 0.18
const MIC_POSITION := Vector3(0.64, FLOOR, -0.89)
const MIC_JACK := MIC_POSITION + Vector3(0, 0.065, 0.10)
const FEATHER := Color("#343944")
const FEATHER_DARK := Color("#252933")
const IVORY := Color("#fff2cf")
const GOLD := Color("#e6a444")
const BRASS := Color("#a96c2c")
const WOOD := Color("#985426")
const LEATHER := Color("#9b243a")
const TEAL := Color("#146f6e")
const TEAL_LIGHT := Color("#258d81")
const STEEL := Color("#4f5457")
const INK := Color("#191e25")
const SKIN := Color("#db9568")
const SHIRT := Color("#386eb3")
const HAIR := Color("#994323")
const FISH := Color("#ec652c")
const FISH_LIGHT := Color("#ffb64f")

static func build(parent: Node3D) -> void:
	var human_seat := _root(parent, "EngineerChair", Vector3(-1.86, FLOOR, 1.51), PI / 2.0)
	_office_chair(human_seat, 1.0, true)
	var operator := _root(parent, "Engineer", human_seat.position, human_seat.rotation.y)
	_human(operator)
	_scale_performer(operator, Vector3(0, 0.27, 0.52), 1.15 * 1.20)

	var assistant_seat := _root(parent, "AssistantChair", Vector3(-1.73, FLOOR, -1.19), PI / 2.0)
	_office_chair(assistant_seat, 0.72)
	var assistant := _root(parent, "ShibaInuEngineer", assistant_seat.position, assistant_seat.rotation.y)
	_shiba_assistant(assistant)
	_scale_performer(assistant, Vector3(0, 0.40, 0.29), 1.48)

	var singer_position := Vector3(0.55, FLOOR, -1.53)
	var to_mic := MIC_POSITION - singer_position
	var singer := _root(parent, "WeddellSealSinger", singer_position, atan2(to_mic.x, to_mic.z))
	_weddell_seal(singer)
	_microphone(parent)

	var bench := _root(parent, "PianoBench", Vector3(Equipment.PIANO_X, FLOOR, -0.15))
	_box(bench, "Apron", Vector3(0, 0.36, 0), Vector3(0.76, 0.12, 0.39), WOOD)
	_box(bench, "UpholsteredSeat", Vector3(0, 0.455, 0), Vector3(0.85, 0.12, 0.42), LEATHER)
	_box(bench, "Piping", Vector3(0, 0.438, 0.213), Vector3(0.81, 0.017, 0.012), Color("#b94b4f"))
	for x: float in [-0.31, 0.31]:
		for z: float in [-0.15, 0.15]:
			_box(bench, "BenchLeg", Vector3(x, 0.17, z), Vector3(0.07, 0.34, 0.07), WOOD)
	var pianist := _root(parent, "PenguinPianist", Vector3(Equipment.PIANO_X, FLOOR, -0.21), PI)
	_penguin(pianist, Vector3(0, 0.76, 0), Vector3(0.255, 0.31, 0.205), Vector3(0, 1.06, 0.045), 0.149)
	_penguin_arms(pianist, Vector3(0.217, 0.85, 0.035), Vector3(0.292, 0.704, 0.392))
	_headphones(pianist, Vector3(0, 1.08, 0.045), 0.156, 0.052)
	_penguin_feet(pianist, 0.554, 0.12, 0.18)
	_scale_performer(pianist, Vector3(0, 0.49, 0.32), 1.53)

	_saxophonist(parent, singer.position)

	var harpist := _root(parent, "HarpistStation", Vector3(4.39, FLOOR, -1.33), deg_to_rad(-161.0))
	var stool := _root(harpist, "HarpStool", Vector3.ZERO)
	_rod(stool, "WalnutSeat", Vector3(0, 0.285, 0), Vector3(0, 0.37, 0), 0.25, 0.27, WOOD, 10)
	for index in range(3):
		var angle := TAU * float(index) / 3.0 + PI / 2.0
		var radial := Vector3(cos(angle), 0, sin(angle))
		_rod(stool, "SplayedLeg", radial * 0.23, radial * 0.15 + Vector3.UP * 0.302, 0.033, 0.045, WOOD)
	var carp := _root(stool, "CarpHarpist", Vector3.ZERO, PI / 2.0)
	_scale_performer(carp, Vector3(0, 0.28, 0.17), 1.50)
	carp.position.y += 0.062
	var body_pivot := Vector3(0, 0.66, 0.015)
	var pose_pitch := deg_to_rad(-47.0)
	var pose := _root(carp, "UprightFish", body_pivot - body_pivot.rotated(Vector3.RIGHT, pose_pitch))
	pose.rotation.x = pose_pitch
	_carp(pose)
	var harp := _root(harpist, "SmallHarp", Vector3(0.75, 0, 0.07))
	var strings := _harp(harp)
	var harp_offset := harp.position - stool.position
	var posed_body := carp.transform * pose.transform
	_playing_fin(stool, "FarPlayingFin", posed_body * Vector3(0.177, 0.669, 0.061), harp_offset + strings[3], -1.0)
	_playing_fin(stool, "NearPlayingFin", posed_body * Vector3(-0.177, 0.669, 0.061), harp_offset + strings[1], 1.0)
	for side: float in [-1.0, 1.0]:
		_pelvic_fin(stool, posed_body * Vector3(side * 0.14, 0.507, -0.107), side)

static func _carp(parent: Node3D) -> void:
	var body := _ellipsoid(parent, "OrangeScales", Vector3(0, 0.66, 0.015), Vector3(0.195, 0.266, 0.373), FISH, 13, 9)
	body.rotation.x = deg_to_rad(-13.0)
	var scales := ShaderMaterial.new()
	scales.shader = CARP_SCALES
	scales.set_shader_parameter("body_color", FISH)
	body.material_override = scales
	_ellipsoid(parent, "SoftOrangeBelly", Vector3(0, 0.566, 0.030), Vector3(0.153, 0.17, 0.307), Color("#f69d61"), 10, 6)
	var head := _root(parent, "CarpHead", Vector3(0, 0.726, 0.283), deg_to_rad(15.0))
	head.rotation.x = deg_to_rad(31.0)
	_ellipsoid(head, "TaperedHead", Vector3(0, -0.012, 0.031), Vector3(0.146, 0.151, 0.165), Color("#ef813e"), 10, 7)
	_ellipsoid(head, "RoundedSnout", Vector3(0, -0.047, 0.146), Vector3(0.094, 0.061, 0.061), FISH_LIGHT, 9, 5)
	_ellipsoid(head, "CarpMouth", Vector3(0, -0.051, 0.200), Vector3(0.047, 0.016, 0.014), Color("#813829"), 8, 4)
	for side: float in [-1.0, 1.0]:
		var eye := Vector3(side * 0.122, 0.026, 0.103)
		_ellipsoid(head, "AmberEye", eye, Vector3(0.032, 0.040, 0.034), Color("#ffdf9b"), 8, 4)
		_ellipsoid(head, "Pupil", eye + Vector3(side * 0.021, 0.001, 0.013), Vector3(0.021, 0.026, 0.022), INK, 8, 4)
		_ellipsoid(head, "EyeGlint", eye + Vector3(side * 0.035, 0.010, 0.027), Vector3.ONE * 0.009, IVORY, 6, 4)
		_rod(head, "MouthBarbel", Vector3(side * 0.059, -0.053, 0.173), Vector3(side * 0.095, -0.091, 0.178), 0.008, 0.004, BRASS)
		_rod(parent, "Gill", Vector3(side * 0.141, 0.827, 0.20), Vector3(side * 0.184, 0.724, 0.189), 0.011, 0.010, BRASS, 5)
		_rod(parent, "Gill", Vector3(side * 0.184, 0.724, 0.189), Vector3(side * 0.169, 0.622, 0.182), 0.010, 0.006, BRASS, 5)
	var dorsal := _ellipsoid(parent, "DorsalFin", Vector3(0, 0.90, -0.109), Vector3(0.029, 0.104, 0.196), Color("#f09337"), 7, 4)
	dorsal.rotation.x = deg_to_rad(17.0)
	_rod(parent, "TailStalk", Vector3(0, 0.617, -0.252), Vector3(0, 0.601, -0.423), 0.097, 0.041, FISH, 7)
	var tail_outline := PackedVector3Array([
		Vector3(0, 0.619, -0.343), Vector3(0, 0.819, -0.492), Vector3(0, 0.859, -0.552),
		Vector3(0, 0.608, -0.470), Vector3(0, 0.394, -0.554), Vector3(0, 0.459, -0.456),
	])
	var tail_center := Vector3(0, 0.607, -0.412)
	var tail := SurfaceTool.new()
	tail.begin(Mesh.PRIMITIVE_TRIANGLES)
	for index in range(tail_outline.size()):
		var a := tail_outline[index] - tail_center
		var b := tail_outline[(index + 1) % tail_outline.size()] - tail_center
		_face(tail, Vector3.RIGHT * 0.028, a, b)
		_face(tail, Vector3.LEFT * 0.028, b, a)
	_place(parent, "ForkedCaudalFin", tail_center, tail.commit(), Color("#f9a333"))
	for tip: Vector3 in [tail_outline[1], tail_outline[2], tail_outline[4], tail_outline[5]]:
		_rod(parent, "TailFinRay", tail_center + Vector3(0.03, 0, 0), tip, 0.007, 0.003, Color("#ca622a"), 5)

static func _weddell_seal(parent: Node3D) -> void:
	var coat := Color("#9dadaf")
	var silver := Color("#c5cfcd")
	var muzzle := Color("#f3eee1")
	var whisker := Color("#4e5f5e")
	var body_center := Vector3(0, 0.758, 0)
	var body_radii := Vector3(0.313, 0.736, 0.285)
	_ellipsoid(parent, "Rounded seal body", body_center, body_radii, coat, 14, 10)
	_ellipsoid(parent, "Silver chest", Vector3(0, 0.934, 0.167), Vector3(0.245, 0.478, 0.162), silver, 12, 8)
	for index in range(18):
		var azimuth := TAU * float(index) / 7.0
		var latitude := -0.34 + 0.89 * float(index % 6) / 5.0
		var radial := _sphere_point(latitude, azimuth)
		var spot := _ellipsoid(parent, "Mottled silver spot", body_center + radial * body_radii,
			Vector3(0.044, 0.010, 0.034) * (0.76 + 0.13 * float(index % 4)), coat.lightened(0.17), 7, 5)
		spot.quaternion = Quaternion(Vector3.UP, (radial / body_radii).normalized())
	_ellipsoid(parent, "Short broad seal neck", Vector3(0, 1.315, 0.041), Vector3(0.227, 0.258, 0.216), coat, 12, 8)
	_ellipsoid(parent, "Weddell seal head", Vector3(0, 1.562, 0.126), Vector3(0.235, 0.237, 0.222), coat.lightened(0.07), 14, 9)
	_ellipsoid(parent, "Singing mouth", Vector3(0, 1.495, 0.335), Vector3(0.105, 0.092, 0.054), Color("#293439"), 11, 7)
	_ellipsoid(parent, "Open jaw", Vector3(0, 1.421, 0.319), Vector3(0.118, 0.051, 0.093), silver, 11, 6)
	_ellipsoid(parent, "Tongue", Vector3(0, 1.454, 0.375), Vector3(0.047, 0.021, 0.021), Color("#aa665c"), 9, 5)
	_ellipsoid(parent, "Dark seal nose", Vector3(0, 1.617, 0.416), Vector3(0.064, 0.039, 0.033), INK, 10, 6)
	for side: float in [-1.0, 1.0]:
		var pad := Vector3(side * 0.060, 1.550, 0.374)
		_ellipsoid(parent, "Pale whisker pad", pad, Vector3(0.093, 0.057, 0.065), muzzle, 11, 7)
		var eye := Vector3(side * 0.135, 1.656, 0.283)
		_ellipsoid(parent, "Dark seal eye", eye, Vector3(0.048, 0.047, 0.033), INK, 10, 6)
		_ellipsoid(parent, "Seal eye glint", eye + Vector3(side * 0.018, 0.016, 0.027), Vector3.ONE * 0.011, Color.WHITE, 7, 5)
		for index in range(4):
			var root := pad + Vector3(side * 0.039, -0.030 + 0.016 * index, 0.049)
			var end := root + Vector3(side * (0.117 + 0.020 * index), -0.058 + 0.037 * index, -0.018)
			var bend := root.lerp(end, 0.52) + Vector3.DOWN * 0.009
			_rod(parent, "Vibrissa", root, bend, 0.0054, 0.0039, whisker, 5)
			_rod(parent, "Vibrissa tip", bend, end, 0.0039, 0.0017, whisker, 5)
		var flipper := _ellipsoid(parent, "Front seal flipper", Vector3(side * 0.271, 0.835, 0.14), Vector3(0.093, 0.284, 0.085), coat.darkened(0.12), 10, 7)
		flipper.rotation.z = side * 0.47
		_ellipsoid(parent, "Rear seal flipper", Vector3(side * 0.155, 0.077, 0.258), Vector3(0.102, 0.071, 0.190), coat.darkened(0.13), 10, 6).rotation.y = side * 0.42

static func _saxophonist(parent: Node3D, singer_position: Vector3) -> void:
	var position := Vector3(4.64, FLOOR, 1.94)
	var to_singer := singer_position - position
	var player := _root(parent, "PolarBearSaxophonist", position, atan2(to_singer.x, to_singer.z))
	_polar_bear(player)
	var instrument := _root(player, "TenorSaxophone", Vector3(0, 0.120, 0.035))
	var brass := Color("#d38b25")
	var bright := Color("#efb641")
	var mouth := Vector3(0, 1.367, 0.452)
	var neck := PackedVector3Array([
		mouth, Vector3(0.070, 1.367, 0.508), Vector3(0.145, 1.306, 0.532),
		Vector3(0.159, 1.197, 0.546), Vector3(0.14, 0.656, 0.546),
		Vector3(0.156, 0.557, 0.546), Vector3(0.222, 0.505, 0.546), Vector3(0.315, 0.497, 0.546),
		Vector3(0.389, 0.547, 0.541), Vector3(0.423, 0.630, 0.531),
	])
	for index in range(neck.size() - 1):
		var radius := 0.021 + 0.005 * index
		_rod(instrument, "SaxophoneTube", neck[index], neck[index + 1], radius, radius + 0.005, brass, 10)
		if index > 0:
			_ellipsoid(instrument, "RoundedTubeBend", neck[index], Vector3.ONE * radius, brass, 9, 5)
	_rod(instrument, "ReedMouthpiece", mouth, neck[1].lerp(mouth, 0.40), 0.023, 0.029, INK, 8)
	var bell_base := neck[-1]
	var bell_lip := Vector3(0.481, 0.820, 0.590)
	var bell_axis := (bell_lip - bell_base).normalized()
	_rod(instrument, "FlaredBell", bell_base, bell_lip, 0.063, 0.139, bright, 16)
	_rod(instrument, "DarkBellOpening", bell_lip, bell_lip + bell_axis * 0.003, 0.117, 0.117, Color("#563619"), 16)
	for index in range(6):
		var key := Vector3(0.154 - 0.004 * index, 1.164 - 0.073 * index, 0.615)
		_rod(instrument, "PearlKey", key - Vector3.BACK * 0.037, key, 0.026, 0.025, IVORY, 8)

static func _polar_bear(parent: Node3D) -> void:
	var coat := Color("#dfe8e3")
	var cream := Color("#f5f3e4")
	var shadow := Color("#aabfbd")
	_ellipsoid(parent, "Heavy white coat", Vector3(0, 0.814, -0.026), Vector3(0.354, 0.653, 0.282), coat, 12, 9)
	_ellipsoid(parent, "Shaded back hip", Vector3(0, 0.494, -0.094), Vector3(0.29, 0.306, 0.246), coat.darkened(0.05), 11, 7)
	_ellipsoid(parent, "Light belly", Vector3(0, 0.813, 0.144), Vector3(0.267, 0.469, 0.167), cream, 10, 6)
	_ellipsoid(parent, "Long neck", Vector3(0, 1.341, 0.012), Vector3(0.235, 0.268, 0.210), coat, 11, 7)
	_ellipsoid(parent, "Polar bear head", Vector3(0, 1.611, 0.072), Vector3(0.216, 0.194, 0.243), coat, 12, 8)
	_ellipsoid(parent, "Long pale muzzle", Vector3(0, 1.554, 0.327), Vector3(0.138, 0.103, 0.168), cream, 11, 7)
	_ellipsoid(parent, "Lower jaw", Vector3(0, 1.482, 0.312), Vector3(0.111, 0.047, 0.156), coat, 10, 6)
	_ellipsoid(parent, "Black nose", Vector3(0, 1.562, 0.474), Vector3(0.079, 0.047, 0.048), INK, 9, 5)
	_ellipsoid(parent, "Mouth on reed", Vector3(0, 1.493, 0.468), Vector3(0.066, 0.017, 0.026), Color("#3d4948"), 8, 5)
	for side: float in [-1.0, 1.0]:
		var ear := Vector3(side * 0.158, 1.761, 0.020)
		_ellipsoid(parent, "Rounded bear ear", ear, Vector3(0.071, 0.085, 0.051), coat, 10, 6)
		_ellipsoid(parent, "Ear shadow", ear + Vector3(0, 0.004, 0.035), Vector3(0.044, 0.054, 0.025), shadow, 8, 5)
		var eye := Vector3(side * 0.151, 1.635, 0.247)
		_ellipsoid(parent, "Dark bear eye", eye, Vector3(0.032, 0.032, 0.021), INK, 8, 5)
		_ellipsoid(parent, "Bear eye reflection", eye + Vector3(side * 0.03, 0.003, 0.012), Vector3.ONE * 0.009, Color("#f5f8f5"), 6, 4)
		var paw := Vector3(side * 0.168, 0.080, 0.167)
		_rod(parent, "Strong hind leg", Vector3(side * 0.173, 0.452, -0.041), Vector3(paw.x, 0.110, 0.073), 0.116, 0.083, coat, 8)
		_ellipsoid(parent, "Broad snow paw", paw, Vector3(0.114, 0.079, 0.176), cream, 10, 6)
		for claw in [-0.046, 0.0, 0.046]:
			_rod(parent, "Paw claw", paw + Vector3(claw, 0, 0.145), paw + Vector3(claw, -0.009, 0.183), 0.011, 0.006, shadow.darkened(0.23), 6)
	var lower_key := Vector3(0.118, 1.012, 0.583)
	var upper_key := Vector3(0.195, 1.205, 0.580)
	for arm in [[Vector3(-0.29, 1.260, 0.064), Vector3(-0.257, 1.048, 0.353), lower_key],
			[Vector3(0.288, 1.265, 0.052), Vector3(0.310, 1.185, 0.337), upper_key]]:
		_rod(parent, "Polar bear upper arm", arm[0], arm[1], 0.126, 0.099, coat, 9)
		_ellipsoid(parent, "Soft elbow", arm[1], Vector3(0.102, 0.105, 0.095), coat, 9, 6)
		_rod(parent, "Polar bear forearm", arm[1], arm[2], 0.099, 0.070, coat, 9)
		_ellipsoid(parent, "Paw on sax keys", arm[2], Vector3(0.086, 0.064, 0.078), cream, 10, 6)

static func _playing_fin(parent: Node3D, label: String, base: Vector3, contact: Vector3, side: float) -> void:
	var center := base.lerp(contact, 0.54) + Vector3(0, -0.022, side * 0.063)
	var rim := PackedVector3Array([
		base, center + Vector3(0.041, 0.077, 0), contact, center + Vector3(-0.047, -0.103, 0)
	])
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for index in range(rim.size()):
		var a := rim[index] - center
		var b := rim[(index + 1) % rim.size()] - center
		_face(surface, Vector3(0, 0, 0.035), a, b)
		_face(surface, Vector3(0, 0, -0.035), b, a)
	_place(parent, label, center, surface.commit(), Color("#ee9835"))
	_rod(parent, label + "Ray", base, center + Vector3(0.049, -0.017, 0.027 * side), 0.006, 0.003, BRASS, 5)

static func _pelvic_fin(parent: Node3D, base: Vector3, side: float) -> void:
	var knee := Vector3(0.216, 0.434, side * 0.330)
	var ankle := Vector3(0.297, 0.117, side * 0.307)
	var ochre := Color("#ed8d34")
	_rod(parent, "RearFinThigh", base, knee, 0.054, 0.047, ochre, 7)
	_ellipsoid(parent, "RearFinKnee", knee, Vector3.ONE * 0.047, ochre, 8, 5)
	_rod(parent, "RearFinShin", knee, ankle, 0.047, 0.037, ochre, 7)
	var rim := PackedVector3Array([
		Vector3(-0.05, 0.04, 0), Vector3(0.108, -0.05, side * 0.112),
		Vector3(0.228, -0.067, side * 0.075), Vector3(0.208, -0.065, side * 0.002),
		Vector3(0.131, -0.045, side * -0.079),
	])
	var fin := SurfaceTool.new()
	fin.begin(Mesh.PRIMITIVE_TRIANGLES)
	for index in range(rim.size()):
		var next := (index + 1) % rim.size()
		_face(fin, Vector3.UP * 0.030, rim[index], rim[next])
		_face(fin, Vector3.DOWN * 0.018, rim[next], rim[index])
	_place(parent, "WebbedRearFin", ankle, fin.commit(), Color("#ffaa37"))
	for point: Vector3 in [rim[1], rim[2], rim[4]]:
		_rod(parent, "RearFinRay", ankle + Vector3.UP * 0.028, ankle + point, 0.006, 0.003, Color("#c86b29"), 5)

static func _scale_performer(performer: Node3D, anchor: Vector3, factor: float) -> void:
	performer.position -= performer.basis * anchor * (factor - 1.0)
	performer.scale = Vector3.ONE * factor

static func _office_chair(parent: Node3D, factor: float, operator_fit := false) -> void:
	parent.scale = Vector3.ONE * factor
	var frame_depth := 0.46 if operator_fit else 0.61
	var frame_z := -0.13 if operator_fit else 0.0
	var cushion_depth := 0.45 if operator_fit else 0.56
	var cushion_z := -0.13 if operator_fit else 0.027
	var cushion_y := 0.520 if operator_fit else 0.529
	var back_adjustment := -0.254 if operator_fit else 0.0
	var back_rake := deg_to_rad(-8.0 if operator_fit else -12.0)
	_box(parent, "SeatFrame", Vector3(0, 0.437, frame_z), Vector3(0.59, 0.115, frame_depth), INK)
	_box(parent, "SeatCushion", Vector3(0, cushion_y, cushion_z), Vector3(0.59, 0.13, cushion_depth), TEAL)
	var back := _ellipsoid(parent, "BackCushion", Vector3(0, 0.842, -0.265 + back_adjustment), Vector3(0.31, 0.37, 0.10), TEAL, 8, 4)
	back.rotation.x = back_rake
	_box(parent, "ChairBack", Vector3(0, 0.819, -0.32 + back_adjustment), Vector3(0.38, 0.56, 0.079), TEAL_LIGHT).rotation.x = back_rake
	if operator_fit:
		for side: float in [-1.0, 1.0]:
			var x := side * 0.132
			_rod(parent, "Backrest bracket", Vector3(x, 0.437, -0.284), Vector3(x, 0.56, -0.461), 0.032, 0.029, STEEL)
			_rod(parent, "Backrest upright", Vector3(x, 0.56, -0.461), Vector3(x, 0.755, -0.550), 0.029, 0.025, STEEL)
	_rod(parent, "GasLift", Vector3.UP * 0.104, Vector3.UP * 0.43, 0.055, 0.072, STEEL)
	var caster_yaw := 0.42 if operator_fit else 0.0
	for index in range(5):
		var angle := caster_yaw + TAU * float(index) / 5.0
		var tip := Vector3(cos(angle), 0, sin(angle))
		_rod(parent, "ChairFoot", Vector3.UP * 0.143, tip * 0.335 + Vector3.UP * 0.054, 0.044, 0.035, STEEL)
		_ellipsoid(parent, "Caster", tip * 0.344 + Vector3.UP * 0.053, Vector3(0.054, 0.051, 0.054), INK, 7, 3)
	for side: float in [-1.0, 1.0]:
		var width := 0.405 if operator_fit else 0.326
		_rod(parent, "ArmrestStem", Vector3(side * 0.307, 0.48, -0.11), Vector3(side * width, 0.67, -0.11), 0.025, 0.027, STEEL)
		_box(parent, "Armrest", Vector3(side * width, 0.679, -0.002), Vector3(0.065, 0.043, 0.24), INK)

static func _human(parent: Node3D) -> void:
	var trousers := Color("#3c4536")
	_ellipsoid(parent, "Trousers", Vector3(0, 0.629, 0.014), Vector3(0.231, 0.125, 0.169), trousers, 8, 4)
	for side: float in [-1.0, 1.0]:
		var hip := Vector3(side * 0.122, 0.655, 0.047)
		var knee := Vector3(side * 0.135, 0.579, 0.315)
		var ankle := Vector3(side * 0.14, 0.159, 0.347)
		_rod(parent, "TrouserThigh", hip, knee, 0.109, 0.085, trousers)
		_rod(parent, "TrouserShin", knee, ankle, 0.083, 0.053, trousers)
		_ellipsoid(parent, "WorkShoe", Vector3(ankle.x, 0.121, 0.407), Vector3(0.069, 0.047, 0.126), INK, 7, 4)
	var torso := _ellipsoid(parent, "BlueShirt", Vector3(0, 0.871, 0.022), Vector3(0.235, 0.302, 0.146), SHIRT, 9, 5)
	torso.rotation.x = deg_to_rad(12.0)
	_rod(parent, "Neck", Vector3(0, 1.062, 0.045), Vector3(0, 1.231, 0.096), 0.076, 0.061, SKIN)
	_box(parent, "Collar", Vector3(0, 1.072, 0.071), Vector3(0.155, 0.06, 0.101), Color("#264e83")).rotation.x = -0.12
	for side: float in [-1.0, 1.0]:
		var shoulder := Vector3(side * 0.192, 1.025, 0.025)
		var sleeve := Vector3(side * 0.223, 0.918, 0.08)
		var elbow := Vector3(side * 0.206, 0.839, 0.15)
		var wrist := Vector3(side * 0.173, 0.75, 0.422 + side * 0.03)
		_rod(parent, "RolledSleeve", shoulder, sleeve, 0.113, 0.082, SHIRT)
		_rod(parent, "UpperArm", sleeve, elbow, 0.066, 0.057, SKIN)
		_ellipsoid(parent, "Elbow", elbow, Vector3(0.057, 0.056, 0.051), SKIN, 7, 4)
		_rod(parent, "Forearm", elbow, wrist, 0.061, 0.039, SKIN)
		_ellipsoid(parent, "Palm", wrist + Vector3(0, -0.002, 0.034), Vector3(0.047, 0.026, 0.047), SKIN, 8, 4)
		var thumb := wrist + Vector3(-side * 0.031, -0.005, 0.028)
		_rod(parent, "Thumb", thumb, thumb + Vector3(-side * 0.022, -0.008, 0.044), 0.014, 0.01, SKIN, 6)
		for finger in range(4):
			var lateral := (float(finger) - 1.5) * 0.020
			var knuckle := wrist + Vector3(lateral, -0.001, 0.062)
			var length := 0.042 - 0.012 * absf(float(finger) - 1.5)
			_rod(parent, "Finger", knuckle, knuckle + Vector3(lateral * 0.25, -0.014, length), 0.010, 0.006, SKIN, 6)
	var head := _root(parent, "Head", Vector3(0, 1.299, 0.107), deg_to_rad(-39.0))
	head.rotation.x = deg_to_rad(7.0)
	_ellipsoid(head, "Face", Vector3.ZERO, Vector3(0.12, 0.169, 0.127), SKIN, 10, 6)
	_ellipsoid(head, "Jaw", Vector3(0, -0.077, 0.037), Vector3(0.102, 0.086, 0.091), SKIN, 9, 4)
	_ellipsoid(head, "Hair", Vector3(0, 0.072, -0.025), Vector3(0.133, 0.125, 0.13), HAIR, 9, 4)
	_ellipsoid(head, "Quiff", Vector3(-0.017, 0.13, 0.041), Vector3(0.125, 0.06, 0.137), HAIR.lightened(0.11), 8, 4).rotation.x = -0.2
	_ellipsoid(head, "Nose", Vector3(0, -0.012, 0.124), Vector3(0.023, 0.039, 0.037), SKIN.lightened(0.07), 6, 4)
	_box(head, "Mouth", Vector3(0, -0.063, 0.129), Vector3(0.047, 0.007, 0.008), Color("#8f4537"))
	for side: float in [-1.0, 1.0]:
		var eye_side := "LeftEye" if side < 0.0 else "RightEye"
		var eye := _root(head, eye_side, Vector3(side * 0.060, 0.028, 0.111), side * 0.35)
		_ellipsoid(eye, "Eye", Vector3.ZERO, Vector3(0.021, 0.009, 0.008), Color("#f7d8ab"), 7, 4)
		_ellipsoid(eye, "Pupil", Vector3(0, -0.001, 0.007), Vector3(0.007, 0.008, 0.004), INK, 6, 4)
		_box(eye, "Brow", Vector3(0, 0.023, 0.002), Vector3(0.051, 0.013, 0.011), HAIR).rotation.z = -side * 0.1
	_headphones(head, Vector3(0, 0.018, -0.022), 0.149, 0.061)

static func _shiba_assistant(parent: Node3D) -> void:
	var coat := Color("#c76b2a")
	var coat_light := Color("#e59a4b")
	var cream := Color("#f5e6c9")
	var inner_ear := Color("#d99b78")
	var dark := Color("#25211e")
	var jacket := Color("#667b7c")
	var jacket_trim := Color("#455e60")
	# Seated body and pale chest; +Z faces the mixer.
	_ellipsoid(parent, "ShibaJacket", Vector3(0, 0.68, 0.015), Vector3(0.205, 0.29, 0.17), jacket, 10, 6)
	_ellipsoid(parent, "ShibaShirt", Vector3(0, 0.73, 0.164), Vector3(0.083, 0.19, 0.035), cream, 9, 6)
	_rod(parent, "ShibaJacketSeam", Vector3(0, 0.57, 0.193), Vector3(0, 0.82, 0.193), 0.006, 0.006, jacket_trim, 5)
	_ellipsoid(parent, "ShibaHead", Vector3(0, 1.015, 0.045), Vector3(0.168, 0.145, 0.15), coat_light, 10, 6)
	for side: float in [-1.0, 1.0]:
		# Three-sided tapered rods make upright, pointed ears.
		_rod(parent, "ShibaEar", Vector3(side * 0.105, 1.105, 0.025), Vector3(side * 0.135, 1.245, 0.012), 0.063, 0.002, coat, 3)
		_rod(parent, "ShibaInnerEar", Vector3(side * 0.105, 1.13, 0.069), Vector3(side * 0.131, 1.216, 0.046), 0.029, 0.001, inner_ear, 3)
		_ellipsoid(parent, "ShibaCheek", Vector3(side * 0.093, 0.985, 0.147), Vector3(0.081, 0.067, 0.055), cream, 8, 5)
		_ellipsoid(parent, "ShibaEye", Vector3(side * 0.071, 1.039, 0.171), Vector3(0.016, 0.012, 0.008), dark, 7, 4)
		# Bent sleeves lead to staggered paws resting on the sloped console.
		var paw_z := 0.48 if side < 0.0 else 0.55
		var paw_y := 0.767 if side < 0.0 else 0.775
		var shoulder := Vector3(side * 0.165, 0.84, 0.075)
		var elbow := Vector3(side * 0.21, 0.72, 0.23)
		var wrist := Vector3(side * 0.145, paw_y, paw_z - 0.055)
		_rod(parent, "ShibaUpperSleeve", shoulder, elbow, 0.056, 0.05, jacket, 8)
		_ellipsoid(parent, "ShibaElbow", elbow, Vector3.ONE * 0.05, jacket, 8, 4)
		_rod(parent, "ShibaLowerSleeve", elbow, wrist, 0.05, 0.041, jacket, 8)
		_ellipsoid(parent, "ShibaCuff", wrist, Vector3(0.045, 0.04, 0.04), jacket_trim, 8, 4)
		_ellipsoid(parent, "ShibaMixerPaw", Vector3(side * 0.145, paw_y, paw_z), Vector3(0.049, 0.032, 0.065), cream, 8, 4)
		var hip := Vector3(side * 0.116, 0.553, 0.033)
		var knee := Vector3(side * 0.149, 0.397, 0.296)
		var ankle := Vector3(side * 0.151, 0.195, 0.346)
		var trousers := coat.darkened(0.25)
		_rod(parent, "Shiba hind thigh", hip, knee, 0.078, 0.062, trousers)
		_ellipsoid(parent, "Shiba knee", knee, Vector3(0.065, 0.074, 0.069), trousers, 9, 5)
		_rod(parent, "Shiba hind shin", knee, ankle, 0.052, 0.034, coat)
		_ellipsoid(parent, "Floor planted Shiba paw", Vector3(ankle.x, 0.169, 0.414), Vector3(0.068, 0.039, 0.111), cream, 9, 6)
	_ellipsoid(parent, "ShibaMuzzle", Vector3(0, 0.982, 0.182), Vector3(0.081, 0.052, 0.068), cream, 9, 5)
	_ellipsoid(parent, "ShibaNose", Vector3(0, 1.002, 0.242), Vector3(0.028, 0.019, 0.016), dark, 7, 4)
	_shiba_tail(parent, coat, coat_light)

static func _shiba_tail(parent: Node3D, coat: Color, tip_color: Color) -> void:
	var points := PackedVector3Array([
		Vector3(-0.104, 0.598, -0.095), Vector3(-0.125, 0.645, -0.194),
		Vector3(-0.123, 0.732, -0.288), Vector3(-0.104, 0.849, -0.360),
		Vector3(-0.077, 0.952, -0.381), Vector3(-0.064, 1.029, -0.340),
		Vector3(-0.062, 1.040, -0.267), Vector3(-0.068, 0.996, -0.218),
	])
	var curve := Curve3D.new()
	curve.bake_interval = 0.029
	for index in range(points.size()):
		var tangent := (points[mini(index + 1, points.size() - 1)] - points[maxi(0, index - 1)]) / 6.0
		curve.add_point(points[index], -tangent, tangent)
	var spine := curve.get_baked_points()
	const SIDES := 9
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	for index in range(spine.size()):
		var t := float(index) / float(spine.size() - 1)
		var tangent := (spine[mini(index + 1, spine.size() - 1)] - spine[maxi(0, index - 1)]).normalized()
		var side_axis := Vector3.RIGHT.slide(tangent).normalized()
		var curl_axis := tangent.cross(side_axis).normalized()
		var radius := lerpf(0.066, 0.006, pow(t, 2.7)) + 0.024 * sin(PI * t)
		for side in range(SIDES):
			var angle := TAU * float(side) / float(SIDES)
			var normal := side_axis * cos(angle) + curl_axis * sin(angle)
			vertices.append(spine[index] + normal * radius)
			normals.append(normal)
			colors.append(coat.lerp(tip_color, 0.32 * smoothstep(0.36, 0.96, t)))
	var mesh := SurfaceTool.new()
	mesh.begin(Mesh.PRIMITIVE_TRIANGLES)
	for ring in range(spine.size() - 1):
		for side in range(SIDES):
			var a := ring * SIDES + side
			var b := ring * SIDES + (side + 1) % SIDES
			for index in [a, a + SIDES, b + SIDES, a, b + SIDES, b]:
				mesh.set_color(colors[index])
				mesh.set_normal(normals[index])
				mesh.add_vertex(vertices[index])
	var tail := _place(parent, "Shiba swept curl", Vector3.ZERO, mesh.commit(), Color.WHITE)
	var fur := tail.material_override as StandardMaterial3D
	fur.vertex_color_use_as_albedo = true
	fur.cull_mode = BaseMaterial3D.CULL_DISABLED


static func _penguin(parent: Node3D, body: Vector3, shape: Vector3, head: Vector3, head_size: float, singing := false) -> void:
	_ellipsoid(parent, "FeatherCoat", body, shape, FEATHER, 10, 7)
	_ellipsoid(
		parent, "CreamBib", body + Vector3(0, 0.025, shape.z * 0.69),
		Vector3(shape.x * 0.77, shape.y * 0.93, shape.z * 0.43), IVORY, 10, 7
	)
	_ellipsoid(parent, "Head", head, Vector3(1.0, 0.87, 1.02) * head_size, FEATHER_DARK, 10, 5)
	_ellipsoid(
		parent, "GoldenThroat", head + Vector3(0, -head_size * 0.61, head_size * 0.61),
		Vector3(0.63, 0.45, 0.59) * head_size, GOLD.lightened(0.24), 9, 4
	)
	for side: float in [-1.0, 1.0]:
		var cheek := head + Vector3(side * 0.75, -0.33, 0.27) * head_size
		_ellipsoid(parent, "EarPatch", cheek, Vector3(0.28, 0.385, 0.43) * head_size, GOLD, 7, 4)
		var eye := head + Vector3(side * 0.52, 0.185, 0.79) * head_size
		if singing:
			var rim := eye + Vector3(0, 0, -head_size * 0.015)
			_ellipsoid(parent, "WarmEyeRim", rim, Vector3(0.128, 0.110, 0.046) * head_size, Color("#ba8f54"), 7, 4)
		_ellipsoid(parent, "Eye", eye, Vector3(0.102, 0.087, 0.045) * head_size, INK, 7, 4)
		_ellipsoid(parent, "Catchlight", eye + Vector3(0, 0.025, 0.037) * head_size, Vector3.ONE * head_size * 0.023, IVORY, 6, 4)
	var upper_beak := head + Vector3(0, 0.025, 0.79) * head_size
	var lower_beak := head + Vector3(0, -0.195, 0.787) * head_size
	var upper_tip := head + Vector3(0, 0.65 if singing else -0.08, 2.05 if singing else 1.92) * head_size
	var lower_tip := head + Vector3(0, 0.12 if singing else -0.125, 2.045 if singing else 1.90) * head_size
	_rod(parent, "UpperBill", upper_beak, upper_tip, head_size * 0.28, 0.007, BRASS, 5)
	_rod(parent, "LowerBill", lower_beak, lower_tip, head_size * 0.21, 0.006, GOLD, 5)

static func _penguin_arms(parent: Node3D, shoulder: Vector3, tip: Vector3) -> void:
	for side: float in [-1.0, 1.0]:
		var from := Vector3(shoulder.x * side, shoulder.y, shoulder.z)
		var to := Vector3(tip.x * side, tip.y, tip.z)
		var flipper := _ellipsoid(
			parent, "Flipper", (from + to) * 0.5,
			Vector3(0.077, from.distance_to(to) * 0.61, 0.053), FEATHER_DARK, 7, 5
		)
		flipper.quaternion = Quaternion(Vector3.UP, (to - from).normalized())

static func _penguin_feet(parent: Node3D, height: float, span: float, reach: float) -> void:
	for side: float in [-1.0, 1.0]:
		var foot := _ellipsoid(parent, "OchreFoot", Vector3(side * span, height, reach), Vector3(0.073, 0.045, 0.118), BRASS, 7, 4)
		foot.rotation.y = side * 0.16

static func _headphones(parent: Node3D, head: Vector3, radius: float, cup: float) -> void:
	var previous := head + Vector3(radius, 0.026, -0.027)
	for step in range(1, 9):
		var angle := PI * float(step) / 8.0
		var point := head + Vector3(cos(angle) * radius, sin(angle) * radius * 1.13 + 0.026, -0.027)
		_rod(parent, "HeadphoneBand", previous, point, 0.016, 0.016, INK, 6)
		previous = point
	for side: float in [-1.0, 1.0]:
		var center := head + Vector3(side * radius, 0.005, -0.031)
		var axis := Vector3.RIGHT * side
		_rod(parent, "EarPad", center - axis * 0.034, center - axis * 0.009, cup, cup * 1.10, INK, 10)
		_rod(parent, "EarCup", center - axis * 0.009, center + axis * 0.019, cup * 0.99, cup * 0.96, GOLD, 10)
		_rod(parent, "EarCupFace", center + axis * 0.019, center + axis * 0.022, cup * 0.79, cup * 0.77, INK, 10)

static func _microphone(parent: Node3D) -> void:
	var mic := _root(parent, "CondenserMicrophone", MIC_POSITION)
	var silver := Color("#f4f6ed")
	_rod(mic, "StandBase", Vector3.ZERO, Vector3.UP * 0.068, 0.143, 0.103, INK, 10)
	_rod(mic, "MicrophoneCableSocket", Vector3(0, 0.065, 0.073), Vector3(0, 0.065, 0.1), 0.024, 0.021, BRASS)
	_rod(mic, "StandStem", Vector3.UP * 0.057, Vector3.UP * 1.20, 0.025, 0.020, STEEL)
	_rod(mic, "HeightCollar", Vector3.UP * 0.87, Vector3.UP * 0.95, 0.03, 0.026, BRASS)
	var capsule := _root(mic, "Capsule", Vector3.UP * 1.17)
	capsule.scale = Vector3.ONE * 1.6
	_rod(capsule, "ThreadedMount", Vector3.ZERO, Vector3.UP * 0.09, 0.023, 0.029, BRASS)
	_rod(capsule, "Body", Vector3.UP * 0.05, Vector3.UP * 0.24, 0.057, 0.053, silver, 10)
	_rod(capsule, "Grille", Vector3.UP * 0.225, Vector3.UP * 0.342, 0.061, 0.055, silver, 12)
	_ellipsoid(capsule, "GrilleCap", Vector3.UP * 0.341, Vector3(0.055, 0.024, 0.055), silver, 12, 4)
	_rod(capsule, "GrilleBand", Vector3.UP * 0.223, Vector3.UP * 0.234, 0.063, 0.063, BRASS, 12)
	for index in range(12):
		var angle := TAU * float(index) / 12.0
		var radial := Vector3(cos(angle), 0, sin(angle))
		_rod(capsule, "GrilleRib", radial * 0.061 + Vector3.UP * 0.232, radial * 0.055 + Vector3.UP * 0.342, 0.006, 0.006, INK, 4)
	for index in range(6):
		var angle := TAU * float(index) / 6.0
		var radial := Vector3(cos(angle), 0, sin(angle))
		_rod(capsule, "ShockMountBrace", radial * 0.105 + Vector3.UP * 0.13, Vector3.UP * 0.04, 0.005, 0.005, silver, 5)
		var next_angle := angle + TAU / 6.0
		var next := Vector3(cos(next_angle), 0, sin(next_angle))
		var ring_height := Vector3.UP * 0.135
		_rod(capsule, "ShockMountRing", radial * 0.104 + ring_height, next * 0.104 + ring_height, 0.006, 0.006, GOLD, 5)

static func _harp(parent: Node3D) -> PackedVector3Array:
	_box(parent, "HarpFoot", Vector3(0.025, 0.055, 0), Vector3(0.52, 0.11, 0.28), WOOD)
	_box(parent, "GoldFootTrim", Vector3(0.025, 0.114, 0), Vector3(0.5, 0.032, 0.286), GOLD)
	_rod(parent, "Soundboard", Vector3(-0.187, 0.105, 0), Vector3(-0.31, 0.865, 0), 0.074, 0.043, WOOD, 8)
	_rod(parent, "SoundboardTrim", Vector3(-0.188, 0.116, 0.059), Vector3(-0.307, 0.855, 0.033), 0.013, 0.012, GOLD, 6)
	_rod(parent, "Pillar", Vector3(0.133, 0.114, 0), Vector3(0.319, 1.115, 0), 0.061, 0.05, GOLD, 8)
	_rod(parent, "PillarInlay", Vector3(0.133, 0.143, 0.052), Vector3(0.313, 1.098, 0.046), 0.008, 0.008, BRASS, 6)
	var curve := PackedVector2Array([
		Vector2(-0.31, 0.865), Vector2(-0.255, 0.922), Vector2(-0.179, 0.897),
		Vector2(-0.095, 0.858), Vector2(-0.009, 0.867), Vector2(0.085, 0.941),
		Vector2(0.186, 1.052), Vector2(0.249, 1.105), Vector2(0.319, 1.115)
	])
	for segment in range(curve.size() - 1):
		var from := curve[segment]
		var to := curve[segment + 1]
		_rod(parent, "CarvedNeck", Vector3(from.x, from.y, 0), Vector3(to.x, to.y, 0), 0.046, 0.046, GOLD, 7)
		_ellipsoid(parent, "NeckJoint", Vector3(to.x, to.y, 0), Vector3.ONE * 0.046, GOLD, 7, 4)
	var pluck_points := PackedVector3Array()
	for index in range(8):
		var top := curve[index].lerp(curve[index + 1], 0.55)
		var bottom := Vector3(lerpf(-0.275, 0.121, float(index) / 7.0), lerpf(0.65, 0.13, float(index) / 7.0), 0)
		var end := Vector3(top.x, top.y - 0.024, 0)
		var string_color := Color("#a85035") if index in [1, 5] else Color("#ebe7d9")
		_rod(parent, "HarpString", bottom, end, 0.006, 0.0045, string_color, 5)
		_rod(parent, "TuningPin", Vector3(top.x, top.y - 0.014, 0.039), Vector3(top.x, top.y - 0.014, 0.056), 0.01, 0.007, BRASS, 6)
		pluck_points.append(bottom.lerp(end, 0.63))
	return pluck_points

static func _root(parent: Node3D, label: String, at: Vector3, yaw := 0.0) -> Node3D:
	var node := Node3D.new()
	node.name = label
	node.position = at
	node.rotation.y = yaw
	parent.add_child(node)
	return node

static func _box(parent: Node3D, label: String, at: Vector3, size: Vector3, color: Color) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return _place(parent, label, at, mesh, color)

static func _rod(parent: Node3D, label: String, from: Vector3, to: Vector3, base: float, tip: float, color: Color, sides := 8) -> MeshInstance3D:
	assert(from.distance_squared_to(to) > 0.0)
	var mesh := CylinderMesh.new()
	mesh.height = from.distance_to(to)
	mesh.bottom_radius = base
	mesh.top_radius = tip
	mesh.radial_segments = sides
	mesh.rings = 0
	var instance := _place(parent, label, (from + to) * 0.5, mesh, color)
	instance.quaternion = Quaternion(Vector3.UP, (to - from).normalized())
	return instance

static func _ellipsoid(parent: Node3D, label: String, at: Vector3, radii: Vector3, color: Color, sides: int, bands: int) -> MeshInstance3D:
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for band in range(bands):
		var below := PI * float(band) / float(bands) - PI * 0.5
		var above := PI * float(band + 1) / float(bands) - PI * 0.5
		for index in range(sides):
			var left := TAU * float(index) / float(sides)
			var right := TAU * float(index + 1) / float(sides)
			var a := _sphere_point(below, left) * radii
			var b := _sphere_point(below, right) * radii
			var c := _sphere_point(above, right) * radii
			var d := _sphere_point(above, left) * radii
			if band > 0:
				_face(surface, a, b, c)
			if band < bands - 1:
				_face(surface, a, c, d)
	return _place(parent, label, at, surface.commit(), color)

static func _sphere_point(latitude: float, longitude: float) -> Vector3:
	return Vector3(cos(latitude) * cos(longitude), sin(latitude), cos(latitude) * sin(longitude))

static func _face(surface: SurfaceTool, a: Vector3, b: Vector3, c: Vector3) -> void:
	var normal := (c - a).cross(b - a).normalized()
	if normal.dot(a + b + c) < 0.0:
		var previous := b
		b = c
		c = previous
		normal = -normal
	for point: Vector3 in [a, b, c]:
		surface.set_normal(normal)
		surface.add_vertex(point)

static func _place(parent: Node3D, label: String, at: Vector3, mesh: Mesh, color: Color) -> MeshInstance3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = 0.78
	var instance := MeshInstance3D.new()
	instance.name = label
	instance.position = at
	instance.mesh = mesh
	instance.material_override = material
	parent.add_child(instance, true)
	return instance
