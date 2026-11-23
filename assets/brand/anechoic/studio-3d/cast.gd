extends RefCounted

const Equipment = preload("res://equipment.gd")
const KOI = preload("res://market/ogon-koi.glb")
const KOI_SCALES = preload("res://market/koi-scales.gdshader")
const FLOOR := 0.18
const MIC_POSITION := Vector3(0.56, FLOOR, -0.89)
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
const SHIRT := Color("#788128")
const HAIR := Color("#994323")

static func build(parent: Node3D) -> void:
	var human_seat := _root(parent, "EngineerChair", Vector3(-1.86, FLOOR, 1.02), PI / 2.0)
	_office_chair(human_seat, 1.0)
	var operator := _root(parent, "Engineer", human_seat.position, human_seat.rotation.y)
	_human(operator)
	_scale_performer(operator, Vector3(0, 0.27, 0.52), 1.15 * 1.20)

	var assistant_seat := _root(parent, "AssistantChair", Vector3(-1.73, FLOOR, -0.94), PI / 2.0)
	_office_chair(assistant_seat, 0.72)
	var assistant := _root(parent, "PenguinEngineer", assistant_seat.position, assistant_seat.rotation.y)
	_penguin(assistant, Vector3(0, 0.72, 0.01), Vector3(0.22, 0.36, 0.18), Vector3(0, 1.079, 0.04), 0.135)
	_penguin_arms(assistant, Vector3(0.18, 0.81, 0.06), Vector3(0.14, 0.755, 0.38))
	_headphones(assistant, Vector3(0, 1.094, 0.04), 0.145, 0.048)
	_penguin_feet(assistant, 0.432, 0.085, 0.16)
	_scale_performer(assistant, Vector3(0, 0.40, 0.29), 1.48)

	var singer := _root(parent, "EmperorPenguinSinger", Vector3(0.39, FLOOR, -1.53), deg_to_rad(17.0))
	_penguin(singer, Vector3(0, 1.03, 0), Vector3(0.31, 0.97, 0.27), Vector3(0, 2.08, 0.055), 0.235, true)
	_penguin_arms(singer, Vector3(0.25, 1.49, -0.015), Vector3(0.29, 0.76, -0.13))
	_penguin_feet(singer, 0.055, 0.13, 0.18)
	singer.scale = Vector3(1.11, 0.84, 1.11)
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

	var stool := _root(parent, "HarpStool", Vector3(1.47, FLOOR, 1.30))
	_rod(stool, "WalnutSeat", Vector3(0, 0.285, 0), Vector3(0, 0.37, 0), 0.25, 0.27, WOOD, 10)
	for index in range(3):
		var angle := TAU * float(index) / 3.0 + PI / 2.0
		var radial := Vector3(cos(angle), 0, sin(angle))
		_rod(stool, "SplayedLeg", radial * 0.23, radial * 0.15 + Vector3.UP * 0.302, 0.033, 0.045, WOOD)
	_seated_koi(stool)
	_harp(_root(parent, "SmallHarp", Vector3(2.38, FLOOR, 1.39)))

static func _seated_koi(stool: Node3D) -> void:
	var fish := KOI.instantiate() as Node3D
	fish.name = "OgonKoi"
	fish.scene_file_path = ""
	fish.position = Vector3(0.066, 0.349, 0.012)
	fish.rotation.y = deg_to_rad(44.0)
	fish.scale = Vector3.ONE * 1.72
	stool.add_child(fish)
	for mesh: MeshInstance3D in fish.find_children("*", "MeshInstance3D", true, false):
		var source := mesh.get_active_material(0) as StandardMaterial3D
		var scales := ShaderMaterial.new()
		scales.shader = KOI_SCALES
		scales.set_shader_parameter("albedo_texture", source.albedo_texture)
		scales.set_shader_parameter("normal_texture", source.normal_texture)
		scales.set_shader_parameter("orm_texture", source.roughness_texture)
		scales.set_shader_parameter("use_normal_texture", true)
		scales.set_shader_parameter("use_orm_texture", true)
		mesh.set_surface_override_material(0, scales)

static func _scale_performer(performer: Node3D, anchor: Vector3, factor: float) -> void:
	performer.position -= performer.basis * anchor * (factor - 1.0)
	performer.scale = Vector3.ONE * factor

static func _office_chair(parent: Node3D, factor: float) -> void:
	parent.scale = Vector3.ONE * factor
	_box(parent, "SeatFrame", Vector3(0, 0.437, 0), Vector3(0.59, 0.115, 0.61), INK)
	_box(parent, "SeatCushion", Vector3(0, 0.529, 0.027), Vector3(0.59, 0.13, 0.56), TEAL)
	var back := _ellipsoid(parent, "BackCushion", Vector3(0, 0.842, -0.265), Vector3(0.31, 0.37, 0.10), TEAL, 8, 4)
	back.rotation.x = deg_to_rad(-12.0)
	_box(parent, "ChairBack", Vector3(0, 0.819, -0.32), Vector3(0.38, 0.56, 0.079), TEAL_LIGHT).rotation.x = deg_to_rad(-12.0)
	_rod(parent, "GasLift", Vector3.UP * 0.104, Vector3.UP * 0.43, 0.055, 0.072, STEEL)
	for index in range(5):
		var angle := TAU * float(index) / 5.0
		var tip := Vector3(cos(angle), 0, sin(angle))
		_rod(parent, "ChairFoot", Vector3.UP * 0.143, tip * 0.335 + Vector3.UP * 0.054, 0.044, 0.035, STEEL)
		_ellipsoid(parent, "Caster", tip * 0.344 + Vector3.UP * 0.053, Vector3(0.054, 0.051, 0.054), INK, 7, 3)
	for side: float in [-1.0, 1.0]:
		_rod(parent, "ArmrestStem", Vector3(side * 0.307, 0.48, -0.11), Vector3(side * 0.326, 0.67, -0.11), 0.025, 0.027, STEEL)
		_box(parent, "Armrest", Vector3(side * 0.326, 0.679, -0.002), Vector3(0.065, 0.043, 0.24), INK)

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
	var torso := _ellipsoid(parent, "OliveShirt", Vector3(0, 0.871, 0.022), Vector3(0.235, 0.302, 0.146), SHIRT, 9, 5)
	torso.rotation.x = deg_to_rad(12.0)
	_rod(parent, "Neck", Vector3(0, 1.062, 0.045), Vector3(0, 1.231, 0.096), 0.076, 0.061, SKIN)
	_box(parent, "Collar", Vector3(0, 1.072, 0.071), Vector3(0.155, 0.06, 0.101), Color("#606c20")).rotation.x = -0.12
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

static func _harp(parent: Node3D) -> void:
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
	for index in range(8):
		var top := curve[index].lerp(curve[index + 1], 0.55)
		var bottom := Vector3(lerpf(-0.275, 0.121, float(index) / 7.0), lerpf(0.65, 0.13, float(index) / 7.0), 0)
		var string_color := Color("#a85035") if index in [1, 5] else Color("#ebe7d9")
		_rod(parent, "HarpString", bottom, Vector3(top.x, top.y - 0.024, 0), 0.006, 0.0045, string_color, 5)
		_rod(parent, "TuningPin", Vector3(top.x, top.y - 0.014, 0.039), Vector3(top.x, top.y - 0.014, 0.056), 0.01, 0.007, BRASS, 6)

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
