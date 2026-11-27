@tool
extends Node3D

const Cast = preload("res://cast.gd")
const Equipment = preload("res://equipment.gd")
const Plant = preload("res://market/pottedPlant.glb")
const SPECTRUM = [preload("res://plots/clean-spectrum.png"), preload("res://plots/noisy-spectrum.png")]
const SPECTROGRAM = [preload("res://plots/clean-spectrogram.png"), preload("res://plots/noisy-spectrogram.png")]
const LOGO_SIGNAL = [preload("res://plots/clean-signal.png"), preload("res://plots/noisy-signal.png")]
const DAY_SPECTRUM = [preload("res://plots/clean-spectrum-day.png"), preload("res://plots/noisy-spectrum-day.png")]
const DAY_SPECTROGRAM = [preload("res://plots/clean-spectrogram-day.png"), preload("res://plots/noisy-spectrogram-day.png")]
const DAY_LOGO_SIGNAL = [preload("res://plots/clean-signal-day.png"), preload("res://plots/noisy-signal-day.png")]
const WALNUT := Color("#553222")
const OAK := Color("#b97438")
const BRASS := Color("#e7ad47")
const INK := Color("#092a2b")
const CYAN := Color("#83ead5")
const GOLD := Color("#f3b942")
const RED := Color("#db6f50")
const IVORY := Color("#fff0cd")
const SHELL := Color("#c4d1cc")
const SHELL_LIP := Color("#d7e1dc")
const FLOOR := 0.18
const FRONT_DEPTH := 0.68
const DIVIDER_FRONT := 2.06 + FRONT_DEPTH
const CHAMBER_EXTENSION := 0.64
const WINDOW_SILL := 1.19
const WINDOW_HEAD := 2.91
const CONTROL_WALL_LEFT := -4.485
const DIVIDER_CONTROL_FACE := -0.075
const DASHBOARD_WIDTH := 2.70
const FELT_SEAMS := Color("#a6afad")
const TILE_GRADIENT := [Color("#d5a7aa"), Color("#dbb6a2"), Color("#dfcf9f"),
	Color("#bacba0"), Color("#a7cabf"), Color("#a6b9d1"), Color("#baaed0")]
const LOGO_YAW := -0.35
const LOGO_PITCH := 0.28
const LOGO_SIZE := 12.39
const LOGO_TARGET := Vector3(CHAMBER_EXTENSION * 0.5, 0.91, FRONT_DEPTH * 0.5)

var camera: Camera3D
var lighting: WorldEnvironment
var daylight: DirectionalLight3D
var fill_light: DirectionalLight3D
var practicals: Node3D
var clean_screen: MeshInstance3D
var noisy_screen: MeshInstance3D
var title: Label
var tagline: Label
var hint: Label
var picture_frame: Node2D
var materials := {}
var finishes := {}
var yaw := LOGO_YAW
var pitch := LOGO_PITCH
var night := false
var signal_view := LOGO_SIGNAL
var orbiting := false

func _ready() -> void:
	if not has_node("Studio"):
		_build()
	else:
		_bind_studio()
	_frame_camera()
	_update_look()
	if not Engine.is_editor_hint():
		_read_arguments()

func _build() -> void:
	var model := _group(self, "Studio")
	var geometry := _group(model, "Architecture")
	var furniture := _group(model, "Equipment")
	var characters := _group(model, "Cast")
	_architecture(geometry)
	Equipment.build(furniture, Vector2(-1.99, DIVIDER_FRONT))
	_iceberg_poster(furniture)
	_chamber_coffee_table(furniture)
	Cast.build(characters)
	_greenery(model)
	_signal_displays(model)
	_score_and_cables(model)
	_build_view()

func _bind_studio() -> void:
	camera = $LogoCamera
	lighting = $WorldEnvironment
	daylight = $Daylight
	fill_light = $FillLight
	practicals = $Practicals
	clean_screen = $Studio/SignalDisplays/CleanSignal/Plot
	noisy_screen = $Studio/SignalDisplays/ChamberSignal/Plot
	title = $Brand/Title
	tagline = $Brand/Tagline
	hint = $Brand/Hint
	picture_frame = $Brand/PictureFrame

func _architecture(parent: Node3D) -> void:
	_finish(_box(parent, "WalnutPlinth", Vector3(CHAMBER_EXTENSION * 0.5, 0, FRONT_DEPTH * 0.5), Vector3(9.40 + CHAMBER_EXTENSION, 0.30, 4.42 + FRONT_DEPTH), WALNUT), "wood")
	_desk_floor(parent)
	_finish(_box(parent, "ChamberCarpet", Vector3(2.26 + CHAMBER_EXTENSION * 0.5, 0.153, FRONT_DEPTH * 0.5), Vector3(4.42 + CHAMBER_EXTENSION, 0.054, 4.12 + FRONT_DEPTH), Color("#85263f")), "felt")
	_box(parent, "ControlRearWall", Vector3(-2.27, 2.04, -2.06), Vector3(4.43, 3.72, 0.14), SHELL)
	_box(parent, "ChamberRearWall", Vector3(2.27 + CHAMBER_EXTENSION * 0.5, 2.04, -2.06), Vector3(4.43 + CHAMBER_EXTENSION, 3.72, 0.14), SHELL)
	_box(parent, "ChamberSideWall", Vector3(4.49 + CHAMBER_EXTENSION, 2.04, -0.03 + FRONT_DEPTH * 0.5), Vector3(0.12, 3.72, 4.18 + FRONT_DEPTH), SHELL)
	_box(parent, "ChamberRightSkirting", Vector3(4.42 + CHAMBER_EXTENSION, 0.26, -0.02 + FRONT_DEPTH * 0.5), Vector3(0.04, 0.15, 4.10 + FRONT_DEPTH), SHELL_LIP)
	for row in range(7):
		var base := 0.19 + row * 0.56
		var height := minf(0.56, 3.89 - base)
		var y := base + height * 0.5
		for column in range(9):
			var tile_color := _tile_tint(column, row)
			var width := CHAMBER_EXTENSION if column == 8 else 0.542
			var point := Vector3(0.072 + column * 0.542 + width * 0.5, y, -1.94)
			_box(parent, "AcousticTileBacking", point, Vector3(width, height, 0.11), FELT_SEAMS)
			_acoustic_relief(parent, "AcousticTile", point + Vector3(0, 0, 0.055), Vector2(width - 0.042, height - 0.042), tile_color, false)
		for column in range(8):
			var tile_color := _tile_tint(column + 9, row)
			var width := FRONT_DEPTH if column == 7 else 0.57
			var point := Vector3(4.407 + CHAMBER_EXTENSION, y, -1.965 + column * 0.57 + width * 0.5)
			_box(parent, "SideAcousticTileBacking", point, Vector3(0.065, height, width), FELT_SEAMS)
			_acoustic_relief(parent, "SideAcousticTile", point + Vector3(-0.0325, 0, 0), Vector2(width - 0.02, height - 0.042), tile_color, true)
	var partition := _group(parent, "SharedPartition")
	var opening_center := (WINDOW_SILL + WINDOW_HEAD) * 0.5
	var opening_height := WINDOW_HEAD - WINDOW_SILL
	_box(partition, "SillToFloor", Vector3(0, (FLOOR + WINDOW_SILL) * 0.5, FRONT_DEPTH * 0.5), Vector3(0.15, WINDOW_SILL - FLOOR, 4.12 + FRONT_DEPTH), SHELL)
	_box(partition, "LintelToCeiling", Vector3(0, 3.40, FRONT_DEPTH * 0.5), Vector3(0.15, 0.96, 4.12 + FRONT_DEPTH), SHELL)
	for z in [-1.97, 1.97 + FRONT_DEPTH]:
		_box(partition, "WindowJamb", Vector3(0, opening_center, z), Vector3(0.15, opening_height + 0.06, 0.18), SHELL)
	for y in [WINDOW_SILL, WINDOW_HEAD]:
		_box(partition, "WindowRail", Vector3(0, y, FRONT_DEPTH * 0.5), Vector3(0.18, 0.07, 3.80 + FRONT_DEPTH), SHELL_LIP)
	var glass := _box(partition, "ClearObservationGlass", Vector3(0, opening_center, FRONT_DEPTH * 0.5), Vector3(0.014, opening_height - 0.07, 3.78 + FRONT_DEPTH), Color(0.92, 0.98, 0.97, 0.055))
	var glass_material := glass.material_override as StandardMaterial3D
	glass_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glass_material.roughness = 0.15
	glass_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	glass.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_box(parent, "RearWallCap", Vector3(CHAMBER_EXTENSION * 0.5, 3.922, -2.03), Vector3(9.08 + CHAMBER_EXTENSION, 0.082, 0.24), SHELL_LIP)
	_box(parent, "SideWallCap", Vector3(4.49 + CHAMBER_EXTENSION, 3.922, 0.115 + FRONT_DEPTH * 0.5), Vector3(0.18, 0.082, 4.05 + FRONT_DEPTH), SHELL_LIP)
	_box(partition, "DividerWallCap", Vector3(0, 3.91, 0.05 + FRONT_DEPTH * 0.5), Vector3(0.18, 0.06, 4.06 + FRONT_DEPTH), SHELL_LIP)
	_shed_roof(parent)
	_guardrail(parent)

func _shed_roof(parent: Node3D) -> void:
	var roof := _group(parent, "BackThirdShedRoof")
	roof.position = Vector3(0, 4.31, -1.375)
	roof.rotation.x = 0.12
	_box(roof, "ShedRoofSlab", Vector3.RIGHT * CHAMBER_EXTENSION * 0.5, Vector3(9.12 + CHAMBER_EXTENSION, 0.09, 1.37), SHELL_LIP)
	_box(roof, "FrontRoofFascia", Vector3(CHAMBER_EXTENSION * 0.5, -0.035, 0.67), Vector3(9.12 + CHAMBER_EXTENSION, 0.061, 0.03), SHELL)
	for x in [-4.42, 0.0, 4.48 + CHAMBER_EXTENSION]:
		_box(parent, "ShedRoofSupport", Vector3(x, 4.155, -2.04), Vector3(0.09, 0.42, 0.10), SHELL)
	for x in [-3.24, -1.25, 1.25 + CHAMBER_EXTENSION * 0.25, 3.24 + CHAMBER_EXTENSION * 0.75]:
		var panel := _group(roof, "FlushSolarPanel")
		panel.position.x = x
		_box(panel, "PhotovoltaicGlazing", Vector3(0, 0.052, 0), Vector3(1.73, 0.018, 1.10), Color("#243641"))
		for row in range(2):
			for column in range(4):
				var center := Vector3((column - 1.5) * 0.412, 0.063, (row - 0.5) * 0.52)
				_box(panel, "ThinFilmSolarCell", center, Vector3(0.389, 0.006, 0.498), Color("#385364"))

func _rounded_outline(size: Vector2, radius: float) -> Array[Vector2]:
	var outline: Array[Vector2] = []
	for corner in range(4):
		var center := Vector2(1 if corner == 0 or corner == 3 else -1, 1 if corner < 2 else -1) * (size * 0.5 - Vector2.ONE * radius)
		for step in range(9):
			var angle := (corner * 8 + step) * PI / 16.0
			outline.append(center + Vector2(cos(angle), sin(angle)) * radius)
	return outline

func _tile_tint(column: int, row: int) -> Color:
	var span := (column + row * 0.36) / 17.16 * (TILE_GRADIENT.size() - 1)
	var index := mini(floori(span), TILE_GRADIENT.size() - 2)
	return TILE_GRADIENT[index].lerp(TILE_GRADIENT[index + 1], span - index).darkened(0.023 * ((row * 5 + column) % 3))

func _acoustic_relief(parent: Node3D, node_name: String, at: Vector3, size: Vector2, tint: Color, side: bool) -> void:
	var face := SurfaceTool.new()
	face.begin(Mesh.PRIMITIVE_TRIANGLES)
	var outer := _rounded_outline(size, 0.10)
	var inner := _rounded_outline(size - Vector2.ONE * 0.05, 0.075)
	for index in range(outer.size()):
		var next := (index + 1) % outer.size()
		for vertex: Vector2 in [Vector2.ZERO, inner[next], inner[index]]:
			face.set_normal(Vector3.FORWARD * -1.0)
			face.set_uv(vertex / size + Vector2(0.5, 0.5))
			face.add_vertex(Vector3(vertex.x, vertex.y, 0.025))
		for pair: Vector2i in [Vector2i(index, 0), Vector2i(index, 1), Vector2i(next, 0), Vector2i(next, 0), Vector2i(index, 1), Vector2i(next, 1)]:
			var vertex := outer[pair.x] if pair.y == 0 else inner[pair.x]
			var radial := (outer[pair.x] - inner[pair.x]).normalized()
			face.set_normal(Vector3(radial.x, radial.y, 1).normalized())
			face.set_uv(vertex / size + Vector2(0.5, 0.5))
			face.add_vertex(Vector3(vertex.x, vertex.y, 0.025 * pair.y))
	var item := _mesh(parent, node_name, face.commit(), at, tint)
	if side:
		item.rotation.y = -PI / 2.0
	_finish(item, "felt")

func _guardrail(parent: Node3D) -> void:
	var rail := _group(parent, "OpenEdgeGuardrail")
	var joint := SphereMesh.new()
	joint.radius = 0.048
	joint.height = 0.096
	for z in [-1.55, 0.10, 1.75]:
		_rod(rail, "FloorFlange", Vector3(-3.45, FLOOR, z), Vector3(-3.45, 0.206, z), 0.075, BRASS)
		_rod(rail, "GuardrailPost", Vector3(-3.45, 0.205, z), Vector3(-3.45, 0.91, z), 0.030, BRASS)
		_mesh(rail, "PostFinial", joint, Vector3(-3.45, 0.91, z), BRASS)
	_rod(rail, "StraightHandrail", Vector3(-3.45, 0.91, -1.55), Vector3(-3.45, 0.91, 1.75), 0.035, BRASS)
	var satin_brass := StandardMaterial3D.new()
	satin_brass.albedo_color = Color("#c78a44")
	satin_brass.metallic = 0.32
	satin_brass.roughness = 0.32
	for part: MeshInstance3D in rail.get_children():
		part.material_override = satin_brass

func _desk_floor(parent: Node3D) -> void:
	for row in range(12 + roundi(FRONT_DEPTH / 0.34)):
		var z := -1.884 + row * 0.34
		var color := OAK.lightened(0.02 * float(row % 4))
		var join := -3.20 + 0.44 * float(row % 4)
		_finish(_box(parent, "ControlFloorPlank", Vector3((join - 4.47) / 2, 0.153, z), Vector3(join + 4.465, 0.054, 0.334), color), "wood")
		_finish(_box(parent, "ControlFloorPlank", Vector3((join - 0.04) / 2, 0.153, z), Vector3(-join - 0.045, 0.054, 0.334), color.lightened(0.04)), "wood")

func _greenery(parent: Node3D) -> void:
	var garden := _group(parent, "SolarpunkPlanting")
	_finish(_box(garden, "CedarPlanterBed", Vector3(-4.02, FLOOR + 0.053, 0.24), Vector3(0.89, 0.106, 3.34), WALNUT), "wood")
	_box(garden, "PlanterSoil", Vector3(-4.02, FLOOR + 0.110, 0.24), Vector3(0.81, 0.015, 3.24), Color("#504036"))
	var outer := [[-1.12, 2], [-0.61, 2], [0.02, 2], [0.78, 1], [1.18, 0], [1.62, 2]]
	var inner := [[-0.91, 2], [-0.02, 1], [0.38, 2], [0.94, 0], [1.43, 1]]
	for item in outer:
		_broadleaf(garden, Vector3(-4.21, FLOOR + 0.11, item[0]), item[1])
	for item in inner:
		_broadleaf(garden, Vector3(-3.84, FLOOR + 0.11, item[0]), item[1])
	var prop := Plant.instantiate() as Node3D
	prop.name = "KenneyPottedPlant"
	# Bake the imported meshes so edited pot and leaf materials are preserved.
	prop.scene_file_path = ""
	garden.add_child(prop, true)
	prop.position = Vector3(-4.10, FLOOR + 0.11, 1.83)
	_tint_plant(prop)
	_wall_planter(garden, Vector3(-3.88, 3.47, -1.78), 0.0, Vector3(1.05, 1.0, 1.12), 0.37)
	_wall_planter(garden, Vector3(-1.83, 3.53, -1.78), 0.0, Vector3(1.43, 0.85, 1.1), 0.08)
	_wall_planter(garden, Vector3(4.24 + CHAMBER_EXTENSION, 2.55, -0.25), -PI / 2.0, Vector3(1.34, 0.88, 1.12), 0.11)
	_wall_planter(garden, Vector3(4.24 + CHAMBER_EXTENSION, 2.45, 1.05), -PI / 2.0, Vector3(1.16, 1.0, 1.10), 0.34)
	var water := _group(garden, "RainwaterSystem")
	var pipe := Color("#ad8050")
	_line(water, "Gutter", [Vector3(-2.55, 4.169, -0.70), Vector3(-4.42, 4.16, -0.70),
		Vector3(-4.42, 4.12, -0.77), Vector3(-4.42, 3.82, -1.91)], 0.024, pipe, true)
	_rod(water, "Downpipe", Vector3(-4.42, 3.82, -1.91), Vector3(-4.42, 0.79, -1.91), 0.027, pipe)
	_rod(water, "TankInlet", Vector3(-4.42, 0.79, -1.91), Vector3(-4.18, 0.79, -1.72), 0.027, pipe)
	var tank := CylinderMesh.new()
	tank.top_radius = 0.18
	tank.bottom_radius = 0.18
	tank.height = 0.58
	tank.radial_segments = 12
	_mesh(water, "RainBarrel", tank, Vector3(-4.18, FLOOR + 0.29, -1.72), Color("#357e78"))
	_rod(water, "BarrelLid", Vector3(-4.18, 0.77, -1.72), Vector3(-4.18, 0.79, -1.72), 0.19, WALNUT)
	_rod(water, "Outlet", Vector3(-4.30, 0.31, -1.60), Vector3(-4.37, 0.31, -1.47), 0.022, INK)
	_rod(water, "DripLine", Vector3(-4.37, 0.31, -1.47), Vector3(-4.37, 0.31, 1.74), 0.018, INK)

func _wall_planter(parent: Node3D, at: Vector3, direction: float, proportions: Vector3, trail: float) -> void:
	var planter := _group(parent, "LivingWallPod")
	planter.position = at
	planter.rotation.y = direction
	planter.scale = proportions
	var oval := SphereMesh.new()
	oval.radius = 0.5
	oval.height = 1.0
	oval.radial_segments = 24
	oval.rings = 12
	var shell := _mesh(planter, "WhiteOvalPod", oval, Vector3.ZERO, SHELL_LIP)
	shell.scale = Vector3(0.94, 0.22, 0.42)
	var soil := _mesh(planter, "PlantingSurface", oval, Vector3(0, 0.077, 0.018), Color("#38583b"))
	soil.scale = Vector3(0.79, 0.040, 0.31)
	var leaf := SphereMesh.new()
	leaf.radius = 0.5
	leaf.height = 1.0
	leaf.radial_segments = 10
	leaf.rings = 6
	var greens := [Color("#397238"), Color("#549636"), Color("#73aa46"), Color("#92b852")]
	for index in range(18):
		var x := lerpf(-0.37, 0.37, float(index % 9) / 8.0)
		var front := index >= 9
		var y := (0.13 if front else 0.23) + 0.12 * sin(index * 2.4) ** 2
		var tip := Vector3(x, y, 0.12 if front else -0.012)
		var root := Vector3(x * 0.78, 0.091, 0.075 if front else 0.0)
		_rod(planter, "LivingStem", root, tip, 0.012, Color("#3f7834"))
		var blade := _mesh(planter, "LivingLeaf", leaf, tip, greens[(index * 3 + int(at.y * 100)) % greens.size()])
		blade.scale = Vector3(0.133 + 0.015 * float(index % 3), 0.178 + 0.029 * float(index % 4), 0.081)
		blade.rotation = Vector3(0.20 * sin(index * 2.4), -0.32 * cos(index * 2.4), 0.62 * sin(index * 1.6))
	for side in [-1.0, 1.0]:
		var previous := Vector3(side * 0.30, 0.10, 0.112)
		for index in range(1, 6):
			var t := float(index) / 5.0
			var point := Vector3(side * (0.31 + 0.12 * t + 0.027 * sin(index * 1.75)),
				0.10 - t * (trail + 0.055 * side), 0.14 + 0.038 * sin(PI * t))
			_rod(planter, "Vine", previous, point, 0.010, greens[0])
			var blade := _mesh(planter, "VineLeaf", leaf, point, greens[(index + 1) % greens.size()])
			blade.scale = Vector3(0.096, 0.13, 0.055)
			blade.rotation.z = 0.75 * sin(index * 2.65 + side)
			previous = point

func _broadleaf(parent: Node3D, at: Vector3, kind: int) -> void:
	var bush := _group(parent, "HedgeBush")
	bush.position = at
	var leaf := SphereMesh.new()
	leaf.radius = 0.5
	leaf.height = 1.0
	leaf.radial_segments = 7
	leaf.rings = 4
	var height: float = 3.0 * ([0.98, 0.73, 0.45][kind] + 0.09 * sin(at.z * 4.1)) + [0.37, 0.17, 0.15][kind]
	var base_color: Color = [Color("#487d32"), Color("#66a643"), Color("#285b36")][kind]
	for index in range(39):
		var heading := index * 2.39996 + at.z * 2.1
		var spread := (0.035 + 0.035 * float(index % 3)) if kind == 0 else (0.05 + 0.036 * float(index % 3))
		var tip := Vector3(cos(heading) * spread, height * (0.12 + 0.74 * float(index % 13) / 12.0), sin(heading) * spread)
		_rod(bush, "Branch", Vector3(0, 0.04, 0), tip, 0.008, Color("#55743b"))
		var blade := _mesh(bush, "LeafCluster", leaf, tip, base_color.lightened(0.025 * float(index % 4)))
		if kind == 0:
			blade.scale = Vector3(0.075, 0.32, 0.065)
		elif kind == 1:
			blade.scale = Vector3(0.10, 0.15, 0.075)
		else:
			blade.scale = Vector3(0.19, 0.13, 0.15)
		blade.rotation = Vector3(0.25 * sin(heading), heading, 0.35 * cos(heading))
	if kind == 1:
		var petal := SphereMesh.new()
		petal.radius = 0.026
		petal.height = 0.052
		petal.radial_segments = 6
		petal.rings = 3
		for index in range(4):
			var angle := index * 2.39996 + at.z
			var center := Vector3(cos(angle) * 0.10, height * (0.78 + 0.08 * float(index)), sin(angle) * 0.10)
			_rod(bush, "FlowerStem", Vector3(0, height * 0.45, 0), center, 0.007, Color("#628a43"))
			var blossom := _group(bush, "Blossom")
			blossom.position = center
			var color := Color("#ee93ac") if index % 2 == 0 else Color("#f5d478")
			for petal_index in range(5):
				var heading := TAU * petal_index / 5.0
				_mesh(blossom, "Petal", petal, Vector3(cos(heading), 0, sin(heading)) * 0.034, color)
			_mesh(blossom, "FlowerCenter", petal, Vector3.UP * 0.014, Color("#fff0bd"))

func _tint_plant(node: Node) -> void:
	if node is MeshInstance3D:
		var material := StandardMaterial3D.new()
		material.albedo_color = Color("#437b36") if "plant" == String(node.name).to_lower() else Color("#966048")
		material.roughness = 0.88
		node.material_override = material
	for child in node.get_children():
		_tint_plant(child)

func _signal_displays(parent: Node3D) -> void:
	var displays := _group(parent, "SignalDisplays")
	clean_screen = _display(displays, "CleanSignal", Vector3(-0.084, 3.38, 0.02 + FRONT_DEPTH * 0.5), -PI / 2, Vector2(3.45 + FRONT_DEPTH * 0.74, 0.82), LOGO_SIGNAL[0])
	noisy_screen = _display(displays, "ChamberSignal", Vector3(4.30 + CHAMBER_EXTENSION, 3.42, 0.08), -PI / 2.0, Vector2(3.62, 0.82), LOGO_SIGNAL[1])
	_box(displays, "ChamberDisplayWallMount", Vector3(4.365 + CHAMBER_EXTENSION, 3.42, 0.08), Vector3(0.10, 0.55, 2.65), FELT_SEAMS)
	var route := _group(displays, "AudioReturnTowardControl")
	_line(route, "AudioReturn", [
		Vector3(4.27 + CHAMBER_EXTENSION, 3.71, -1.73), Vector3(4.27 + CHAMBER_EXTENSION, 3.75, -1.77),
		Vector3(4.20 + CHAMBER_EXTENSION, 3.75, -1.80), Vector3(-0.13, 3.75, -1.80),
		Vector3(-0.13, 3.75, -1.62), Vector3(-0.13, 3.74, -1.62)
	], 0.028, CYAN, true)
	_arrow(route, Vector3(1.88, 3.75, -1.761), Vector3.LEFT, CYAN, 0.13)
	_dashboard(displays)

func _display(parent: Node3D, node_name: String, at: Vector3, direction: float, size: Vector2, texture: Texture2D) -> MeshInstance3D:
	var panel := _group(parent, node_name)
	panel.position = at
	panel.rotation.y = direction
	_box(panel, "TimberBezel", Vector3.ZERO, Vector3(size.x + 0.085, size.y + 0.086, 0.06), WALNUT)
	var plane := QuadMesh.new()
	plane.size = size
	var screen := _mesh(panel, "Plot", plane, Vector3(0, 0, 0.033), Color.WHITE)
	screen.material_override = _screen_material(texture)
	screen.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return screen

func _dashboard(parent: Node3D) -> void:
	var dash := _group(parent, "ControlDashboard")
	dash.position = Vector3(DIVIDER_CONTROL_FACE - DASHBOARD_WIDTH * 0.5, (WINDOW_SILL + WINDOW_HEAD) * 0.5, -1.96)
	dash.scale.y = (WINDOW_HEAD - WINDOW_SILL) / 1.64
	_box(dash, "Frame", Vector3.ZERO, Vector3(DASHBOARD_WIDTH, 1.64, 0.09), WALNUT)
	_box(dash, "PetrolGlass", Vector3(0, 0, 0.052), Vector3(2.58, 1.52, 0.02), INK)
	_box(dash, "HorizontalGrid", Vector3(0, -0.02, 0.065), Vector3(2.53, 0.017, 0.01), CYAN.darkened(0.66))
	_box(dash, "VerticalGrid", Vector3(0.35, 0, 0.065), Vector3(0.013, 1.48, 0.01), CYAN.darkened(0.66))
	var levels := [0.09, 0.16, 0.26, 0.36, 0.44, 0.34, 0.28, 0.23, 0.18, 0.10, 0.07]
	for index in range(levels.size()):
		var h: float = levels[index]
		_box(dash, "Histogram", Vector3(-1.10 + index * 0.127, 0.09 + h * 0.5, 0.072), Vector3(0.089, h, 0.015), CYAN)
	for channel in range(2):
		for segment in range(9):
			var color := Color("#81d653") if segment < 5 else GOLD
			if segment == 8:
				color = color.darkened(0.53)
			_box(dash, "StereoMeter", Vector3(0.67 + channel * 0.34, 0.10 + segment * 0.062, 0.073), Vector3(0.22, 0.047, 0.015), color)
	var trend: Array[Vector3] = []
	for index in range(12):
		var height := -0.61 + 0.034 * index + sin(index * 1.40) * 0.038
		trend.append(Vector3(-1.16 + 0.124 * index, height, 0.080))
	_line(dash, "TrendChart", trend, 0.013, CYAN)
	for i in range(3):
		_box(dash, "StatusRule", Vector3(0.84, -0.275 - i * 0.178, 0.070), Vector3(0.80, 0.009, 0.01), CYAN.darkened(0.64))
	_label3d(dash, "SampleRate", "48 kHz", Vector3(0.83, -0.635, 0.081), 42, IVORY, 0.0027)
	_label3d(dash, "SignalLevel", "–23 dB", Vector3(0.83, -0.456, 0.081), 42, CYAN, 0.0027)
	_label3d(dash, "MonitorStatus", "READY", Vector3(0.83, -0.276, 0.081), 36, GOLD, 0.0027)

func _chamber_coffee_table(parent: Node3D) -> void:
	var table := _group(parent, "ChamberCoffeeTable")
	table.position = Vector3(2.43, FLOOR, 1.47)
	_freeform_tabletop(table)
	for foot: Vector3 in [Vector3(-1.00, 0, 0.04), Vector3(0.98, 0, -0.03), Vector3(0.18, 0, 0.32)]:
		_rod(table, "SplayedTableLeg", foot + Vector3.UP * 0.015, foot * 0.78 + Vector3.UP * 0.31, 0.033, WALNUT)
	var pot := CylinderMesh.new()
	pot.top_radius = 0.145
	pot.bottom_radius = 0.103
	pot.height = 0.148
	pot.radial_segments = 12
	_mesh(table, "OffWhitePlantPot", pot, Vector3.UP * 0.433, Color("#eeeade"))
	_rod(table, "PlantSoil", Vector3.UP * 0.505, Vector3.UP * 0.514, 0.134, Color("#574432"))
	var foliage := _group(table, "SmallPottedBush")
	foliage.position.y = 0.51
	foliage.scale = Vector3(0.86, 0.25, 0.86)
	_broadleaf(foliage, Vector3(-0.07, 0, 0.04), 2)
	_broadleaf(foliage, Vector3(0.08, -0.13, -0.05), 2)

func _freeform_tabletop(parent: Node3D) -> void:
	var outline := PackedVector2Array([
		Vector2(244, 67), Vector2(281, 92), Vector2(320, 158), Vector2(368, 160),
		Vector2(412, 170), Vector2(412, 201), Vector2(377, 241), Vector2(352, 320),
		Vector2(313, 370), Vector2(272, 372), Vector2(234, 348), Vector2(197, 379),
		Vector2(161, 403), Vector2(139, 389), Vector2(141, 352), Vector2(165, 306),
		Vector2(161, 269), Vector2(135, 254), Vector2(99, 257), Vector2(85, 237),
		Vector2(115, 204), Vector2(166, 179), Vector2(187, 145), Vector2(193, 107),
		Vector2(211, 77),
	])
	for index in range(outline.size()):
		outline[index] = (outline[index] - Vector2(248, 238)) * Vector2(0.00925, 0.00281)
	var curve := Curve2D.new()
	curve.bake_interval = 0.039
	for index in range(outline.size() + 1):
		var current := index % outline.size()
		var previous := posmod(current - 1, outline.size())
		var next := (current + 1) % outline.size()
		var tangent := (outline[next] - outline[previous]) / 6.0
		curve.add_point(outline[current], -tangent, tangent)
	var edge := curve.get_baked_points()
	edge.resize(edge.size() - 1)
	var triangles := Geometry2D.triangulate_polygon(edge)
	assert(not triangles.is_empty(), "Tabletop outline must triangulate.")

	var shape := SurfaceTool.new()
	shape.begin(Mesh.PRIMITIVE_TRIANGLES)
	for index in range(0, triangles.size(), 3):
		for corner in [0, 1, 2]:
			var point := edge[triangles[index + corner]]
			shape.set_normal(Vector3.UP)
			shape.set_uv(point)
			shape.add_vertex(Vector3(point.x, 0.36, point.y))
		for corner in [0, 2, 1]:
			var point := edge[triangles[index + corner]]
			shape.set_normal(Vector3.DOWN)
			shape.set_uv(point)
			shape.add_vertex(Vector3(point.x, 0.29, point.y))
	for index in range(edge.size()):
		var a := edge[index]
		var b := edge[(index + 1) % edge.size()]
		var tangent := b - a
		var outward := Vector3(tangent.y, 0, -tangent.x).normalized()
		var low_a := Vector3(a.x, 0.29, a.y)
		var low_b := Vector3(b.x, 0.29, b.y)
		var high_a := low_a + Vector3.UP * 0.07
		var high_b := low_b + Vector3.UP * 0.07
		for point: Vector3 in [low_a, high_b, high_a, low_a, low_b, high_b]:
			shape.set_normal(outward)
			shape.set_uv(Vector2(point.x, point.z))
			shape.add_vertex(point)
	_finish(_mesh(parent, "Lobed maple tabletop", shape.commit(), Vector3.ZERO, OAK), "wood")

func _iceberg_poster(parent: Node3D) -> void:
	var poster := _group(parent, "IcebergPoster")
	var dash_left := DIVIDER_CONTROL_FACE - DASHBOARD_WIDTH
	poster.position = Vector3((CONTROL_WALL_LEFT + dash_left) * 0.5, (WINDOW_SILL + WINDOW_HEAD) * 0.5, -1.96)
	_box(poster, "WalnutPosterFrame", Vector3.ZERO, Vector3(0.73, 1.03, 0.066), WALNUT)
	_box(poster, "Sky", Vector3(0, 0.225, 0.037), Vector3(0.65, 0.49, 0.01), Color("#7cbdc5"))
	_box(poster, "DeepWater", Vector3(0, -0.24, 0.037), Vector3(0.65, 0.45, 0.01), Color("#125060"))
	_poster_facet(poster, "SnowLeft", [Vector2(-0.25, -0.01), Vector2(-0.17, 0.095), Vector2(-0.04, 0.025)], Color("#d8f2e8"))
	_poster_facet(poster, "SnowRidge", [Vector2(-0.17, 0.095), Vector2(-0.12, 0.08), Vector2(-0.04, 0.025)], Color("#bfe4e2"))
	_poster_facet(poster, "SnowPeak", [Vector2(-0.12, 0.08), Vector2(-0.055, 0.23), Vector2(-0.04, 0.025)], Color("#f2f8ed"))
	_poster_facet(poster, "SnowNotch", [Vector2(-0.055, 0.23), Vector2(-0.005, 0.17), Vector2(-0.04, 0.025)], Color("#b7e0df"))
	_poster_facet(poster, "SnowSummit", [Vector2(-0.005, 0.17), Vector2(0.045, 0.30), Vector2(-0.04, 0.025)], Color("#f4f9f0"))
	_poster_facet(poster, "SnowFace", [Vector2(0.045, 0.30), Vector2(0.105, 0.14), Vector2(-0.04, 0.025)], Color("#b9e0e0"))
	_poster_facet(poster, "SnowRightRidge", [Vector2(0.105, 0.14), Vector2(0.15, 0.15), Vector2(-0.04, 0.025)], Color("#e6f5ef"))
	_poster_facet(poster, "SnowRight", [Vector2(0.15, 0.15), Vector2(0.25, -0.01), Vector2(-0.04, 0.025)], Color("#93cad2"))
	_poster_facet(poster, "SnowBase", [Vector2(0.25, -0.01), Vector2(-0.25, -0.01), Vector2(-0.04, 0.025)], Color("#d4eeea"))
	_poster_facet(poster, "IceTop", [Vector2(-0.25, -0.01), Vector2(0.25, -0.01), Vector2(-0.025, -0.20)], Color("#a3e0dc"))
	_poster_facet(poster, "IceRightShoulder", [Vector2(0.25, -0.01), Vector2(0.29, -0.12), Vector2(-0.025, -0.20)], Color("#59c2ca"))
	_poster_facet(poster, "IceRight", [Vector2(0.29, -0.12), Vector2(0.23, -0.22), Vector2(-0.025, -0.20)], Color("#3ba7b7"))
	_poster_facet(poster, "IceRightDeep", [Vector2(0.23, -0.22), Vector2(0.16, -0.32), Vector2(-0.025, -0.20)], Color("#287e98"))
	_poster_facet(poster, "IceTipRight", [Vector2(0.16, -0.32), Vector2(0.06, -0.43), Vector2(-0.025, -0.20)], Color("#59bdc5"))
	_poster_facet(poster, "IceTipLeft", [Vector2(0.06, -0.43), Vector2(-0.08, -0.40), Vector2(-0.025, -0.20)], Color("#84d2d2"))
	_poster_facet(poster, "IceLeftDeep", [Vector2(-0.08, -0.40), Vector2(-0.20, -0.31), Vector2(-0.025, -0.20)], Color("#469ead"))
	_poster_facet(poster, "IceLeft", [Vector2(-0.20, -0.31), Vector2(-0.29, -0.19), Vector2(-0.025, -0.20)], Color("#79c9cc"))
	_poster_facet(poster, "IceLeftShoulder", [Vector2(-0.29, -0.19), Vector2(-0.28, -0.08), Vector2(-0.025, -0.20)], Color("#4eb2bc"))
	_poster_facet(poster, "IceUpperLeft", [Vector2(-0.28, -0.08), Vector2(-0.25, -0.01), Vector2(-0.025, -0.20)], Color("#8bd8d4"))
	_box(poster, "Waterline", Vector3(0, -0.01, 0.049), Vector3(0.65, 0.016, 0.006), Color("#e0ead0"))

func _poster_facet(parent: Node3D, node_name: String, triangle: Array[Vector2], color: Color) -> void:
	var face := SurfaceTool.new()
	face.begin(Mesh.PRIMITIVE_TRIANGLES)
	for point in triangle:
		face.set_normal(Vector3.BACK)
		face.add_vertex(Vector3(point.x, point.y, 0.046))
	var paint := StandardMaterial3D.new()
	paint.albedo_color = color
	paint.cull_mode = BaseMaterial3D.CULL_DISABLED
	_mesh(parent, node_name, face.commit(), Vector3.ZERO, color).material_override = paint

func _score_and_cables(parent: Node3D) -> void:
	var score := _group(parent, "ScoreRouteTowardChamber")
	var score_wall_z := -1.83
	# Offset the rear-wall score for the depth of the piano's front in the logo view.
	var score_x := Equipment.PIANO_X + tan(-LOGO_YAW) * (Equipment.PIANO_FACE_Z - score_wall_z)
	var root := Vector3(score_x, 3.42, score_wall_z)
	var root_size := Vector2(1.62, 0.58)
	_score_page(score, "RootScore", root, root_size)
	for offset in [-0.90, 0.0, 0.90]:
		var x := score_x + float(offset)
		_score_page(score, "PartScore", Vector3(x, 2.66, -1.82), Vector2(0.90, 0.42))
		_line(score, "ScoreBranch", [Vector3(root.x, 3.14, -1.80), Vector3(root.x, 3.00, -1.80),
			Vector3(x, 3.00, -1.80), Vector3(x, 2.86, -1.80)], 0.023, GOLD, true)
	var console_port := Vector3(-0.52, 1.085, DIVIDER_FRONT)
	_rod(score, "ConsoleOutputFlange", console_port, console_port + Vector3(0, 0, 0.038), 0.072, WALNUT)
	_rod(score, "ConsoleOutputFitting", console_port + Vector3(0, 0, 0.038), console_port + Vector3(0, 0, 0.078), 0.052, BRASS)
	_rod(score, "DividerFeedthrough", Vector3(-0.105, 0.98, DIVIDER_FRONT - 0.10), Vector3(-0.065, 0.98, DIVIDER_FRONT - 0.10), 0.057, BRASS)
	_line(score, "ConsoleScoreFeed", [
		console_port + Vector3(0, 0, 0.076), Vector3(-0.48, 1.075, DIVIDER_FRONT + 0.11),
		Vector3(-0.24, 0.99, DIVIDER_FRONT + 0.11), Vector3(-0.15, 0.98, DIVIDER_FRONT + 0.04),
		Vector3(-0.15, 0.98, DIVIDER_FRONT - 0.10), Vector3(0, 0.98, DIVIDER_FRONT - 0.10),
		Vector3(0, 0.88, -1.74), Vector3(0.06, 0.88, -1.80),
		Vector3(0.21, 0.88, -1.80)], 0.035, GOLD, true)
	_line(score, "RearWallScorePipe", [
		Vector3(0.21, 0.88, -1.80), Vector3(1.40, 0.88, -1.80),
		Vector3(1.49, 0.91, -1.80), Vector3(1.53, 1.00, -1.80),
		Vector3(1.53, 3.29, -1.80), Vector3(1.57, 3.38, -1.80),
		Vector3(1.66, 3.42, -1.80), Vector3(root.x - root_size.x * 0.5 + 0.01, 3.42, -1.80)], 0.035, GOLD, true)
	for height in [1.27, 2.24]:
		_box(score, "PipeWallMount", Vector3(1.53, height, -1.858), Vector3(0.13, 0.067, 0.029), WALNUT)
		_rod(score, "PipeCollar", Vector3(1.53, height - 0.023, -1.80), Vector3(1.53, height + 0.023, -1.80), 0.050, BRASS)
	_arrow(score, Vector3(2.05, 3.42, -1.756), Vector3.RIGHT, GOLD, 0.12)
	var cables := _group(parent, "AudioCables")
	var cable := Color("#252627")
	for z in [0.43, 0.62]:
		_box(cables, "DividerSocketPlate", Vector3(0.086, 0.32, z), Vector3(0.021, 0.12, 0.15), WALNUT.lightened(0.16))
		_rod(cables, "CablePlug", Vector3(0.085, 0.32, z), Vector3(0.19, 0.32, z), 0.036, cable)
	_line(cables, "MicrophoneCable", [
		Vector3(0.19, 0.32, 0.43), Vector3(0.29, 0.20, 0.33), Vector3(0.48, 0.20, 0.06),
		Vector3(Cast.MIC_POSITION.x, 0.20, -0.55), Cast.MIC_JACK], 0.023, cable, true)
	var piano_jack := Equipment.PIANO_JACK
	_line(cables, "PianoCable", [
		Vector3(0.19, 0.32, 0.62), Vector3(0.34, 0.20, 0.52), Vector3(0.71, 0.2, 0.26),
		Vector3(1.09, 0.2, -0.03), Vector3(piano_jack.x - 0.43, 0.2, -0.40),
		Vector3(piano_jack.x - 0.12, 0.2, -1.13), piano_jack], 0.023, cable, true)

func _score_page(parent: Node3D, node_name: String, at: Vector3, size: Vector2) -> void:
	var page := _group(parent, node_name)
	page.position = at
	_box(page, "Paper", Vector3.ZERO, Vector3(size.x, size.y, 0.040), IVORY)
	for i in range(5):
		var y := (i - 2) * size.y * 0.12
		_box(page, "StaffLine", Vector3(0, y, 0.023), Vector3(size.x * 0.81, 0.008, 0.006), WALNUT)
	var note := SphereMesh.new()
	note.radius = size.y * 0.093
	note.height = note.radius * 2.0
	note.radial_segments = 8
	note.rings = 4
	var stem := size.y * 0.27
	for i in range(4):
		var x := (-0.31 + 0.19 * i) * size.x
		var y := (i % 3 - 1) * size.y * 0.10
		_mesh(page, "NoteHead", note, Vector3(x, y, 0.027), INK).scale = Vector3(1.35, 0.63, 0.19)
		_box(page, "NoteStem", Vector3(x + note.radius, y + stem * 0.5, 0.030), Vector3(0.01, stem, 0.010), INK)

func _build_view() -> void:
	camera = Camera3D.new()
	camera.name = "LogoCamera"
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.current = true
	add_child(camera)
	lighting = WorldEnvironment.new()
	lighting.name = "WorldEnvironment"
	lighting.environment = Environment.new()
	lighting.environment.background_mode = Environment.BG_COLOR
	lighting.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	add_child(lighting)
	daylight = DirectionalLight3D.new()
	daylight.name = "Daylight"
	daylight.rotation_degrees = Vector3(-53, -31, 0)
	daylight.shadow_enabled = true
	add_child(daylight)
	fill_light = DirectionalLight3D.new()
	fill_light.name = "FillLight"
	fill_light.rotation_degrees = Vector3(-36, 148, 0)
	add_child(fill_light)
	practicals = _group(self, "Practicals")
	for x in [-3.35, -1.16, 1.12, 3.45]:
		var lamp := OmniLight3D.new()
		lamp.position = Vector3(x, 3.66, -1.32)
		lamp.omni_range = 4.1
		lamp.omni_attenuation = 1.3
		lamp.light_color = Color("#ffcf9a")
		practicals.add_child(lamp, true)
		_box(practicals, "Fixture", Vector3(x, 3.87, -1.88), Vector3(0.23, 0.022, 0.075), BRASS)
	var branding := CanvasLayer.new()
	branding.name = "Brand"
	add_child(branding)
	_picture_frame(branding)
	var type := SystemFont.new()
	type.font_names = ["Avenir Next", "DejaVu Sans", "Arial"]
	type.font_weight = 800
	title = _caption(branding, "Title", "Anechoic", 142, 0.768, 0.903, type)
	tagline = _caption(branding, "Tagline", "Iceberg with guardrails", 42, 0.899, 0.963, type)
	hint = _caption(branding, "Hint", "Drag to inspect   ·   Home resets   ·   D / N lighting   ·   1 / 2 / 3 audio display", 16, 0.97, 0.998, type)

func _picture_frame(branding: CanvasLayer) -> void:
	picture_frame = Node2D.new()
	picture_frame.name = "PictureFrame"
	branding.add_child(picture_frame)
	var outside := Rect2(28, 80, 1024, 742)
	_frame_ring(outside, 3.0, ["#4d2d1e", "#4a281b", "#3c2119", "#42271d"])
	_frame_ring(outside.grow(-3.0), 12.0, ["#9c5c3c", "#79442e", "#713d2a", "#895137"])
	_frame_ring(outside.grow(-15.0), 5.0, ["#5f3828", "#6e402a", "#8e5639", "#5f3828"])

func _frame_ring(rect: Rect2, width: float, shades: Array) -> void:
	var inset := rect.grow(-width)
	var out_points := [rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)]
	var in_points := [inset.position, Vector2(inset.end.x, inset.position.y), inset.end, Vector2(inset.position.x, inset.end.y)]
	for side in range(4):
		var next := (side + 1) % 4
		var miter := Polygon2D.new()
		miter.name = "MiteredWalnut"
		miter.polygon = PackedVector2Array([out_points[side], out_points[next], in_points[next], in_points[side]])
		miter.color = Color(shades[side])
		picture_frame.add_child(miter, true)

func _caption(parent: CanvasLayer, node_name: String, words: String, size: int, top: float, bottom: float, type: Font) -> Label:
	var label := Label.new()
	label.name = node_name
	parent.add_child(label)
	label.anchor_right = 1.0
	label.anchor_top = top
	label.anchor_bottom = bottom
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.text = words
	label.add_theme_font_override("font", type)
	label.add_theme_font_size_override("font_size", size)
	return label

func _frame_camera() -> void:
	var distance := 16.0
	camera.position = LOGO_TARGET + Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * distance
	camera.look_at(LOGO_TARGET)
	camera.size = LOGO_SIZE

func _update_look() -> void:
	var environment := lighting.environment
	environment.background_color = Color("#082a31") if night else Color("#fbefd9")
	environment.ambient_light_color = Color("#a4bef2") if night else Color("#fff5e6")
	environment.ambient_light_energy = 0.53 if night else 0.42
	daylight.light_color = Color("#b7d4ff") if night else Color("#fff2d7")
	daylight.light_energy = 0.30 if night else 0.66
	fill_light.light_color = Color("#a0ddd5")
	fill_light.light_energy = 0.23 if night else 0.19
	for child in practicals.get_children():
		if child is OmniLight3D:
			child.light_energy = 1.40 if night else 0.16
	var text_color := IVORY if night else Color("#123b28")
	for label in [title, tagline, hint]:
		label.add_theme_color_override("font_color", text_color)
	_update_screen_colors()
	Equipment.set_console_theme(get_node("Studio/Equipment/Shared analog mixing console"), night)
	_update_plots()

func _update_screen_colors() -> void:
	var dashboard := $Studio/SignalDisplays/ControlDashboard
	_apply_screen_palette(dashboard, {
		INK.to_html(false): Color("#f0f4eb"),
		CYAN.darkened(0.66).to_html(false): Color("#afc8c0"),
		CYAN.darkened(0.64).to_html(false): Color("#bccfc4"),
		CYAN.to_html(false): Color("#086b65"),
		Color("#81d653").to_html(false): Color("#308448"),
		GOLD.to_html(false): Color("#895116"),
		GOLD.darkened(0.53).to_html(false): Color("#c3b497"),
		IVORY.to_html(false): Color("#264543"),
	})
	var code_panel := get_node("Studio/Equipment/Upright code piano/Integrated upper front code panel")
	_apply_screen_palette(code_panel, {
		"0b2024": Color("#f2f4ec"),
		"f1ead6": Color("#213a3e"),
		"8df5d6": Color("#106259"),
		"ffbb9f": Color("#963d2b"),
	})

func _apply_screen_palette(panel: Node, palette: Dictionary) -> void:
	for child in panel.get_children():
		var material: StandardMaterial3D
		var current: Color
		if child is MeshInstance3D:
			material = child.material_override as StandardMaterial3D
			current = material.albedo_color
		elif child is Label3D:
			current = child.modulate
		else:
			continue
		var dark: Color = child.get_meta("night_screen_color", current)
		var key := dark.to_html(false)
		if not palette.has(key):
			continue
		var tint: Color = dark if night else palette[key]
		if not child.has_meta("night_screen_color"):
			child.set_meta("night_screen_color", dark)
			if material:
				child.set_meta("night_screen_emission", material.emission_enabled)
				material = material.duplicate() as StandardMaterial3D
				child.material_override = material
		if material:
			material.albedo_color = tint
			material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL if night else BaseMaterial3D.SHADING_MODE_UNSHADED
			material.emission_enabled = night and child.get_meta("night_screen_emission", false)
		else:
			child.modulate = tint

func _update_plots() -> void:
	var textures := signal_view
	if not night:
		if signal_view == SPECTRUM:
			textures = DAY_SPECTRUM
		elif signal_view == SPECTROGRAM:
			textures = DAY_SPECTROGRAM
		else:
			textures = DAY_LOGO_SIGNAL
	(clean_screen.material_override as StandardMaterial3D).albedo_texture = textures[0]
	(noisy_screen.material_override as StandardMaterial3D).albedo_texture = textures[1]

func _read_arguments() -> void:
	var arguments := OS.get_cmdline_user_args()
	night = arguments.has("--night")
	if arguments.has("--spectrogram"):
		signal_view = SPECTROGRAM
	elif arguments.has("--spectrum"):
		signal_view = SPECTRUM
	_update_look()
	if arguments.has("--render"):
		hint.hide()
		if arguments.has("--art-only"):
			$Brand.hide()
			camera.v_offset = 1.15
		_render_logo(arguments)

func _render_logo(arguments: PackedStringArray) -> void:
	for i in range(4):
		await get_tree().process_frame
	var index := arguments.find("--render")
	var output := arguments[index + 1] if index + 1 < arguments.size() else "user://anechoic.png"
	var result := get_viewport().get_texture().get_image().save_png(output)
	if result != OK:
		push_error("Logo render failed: %s" % error_string(result))
	get_tree().quit(result)

func _unhandled_input(event: InputEvent) -> void:
	if Engine.is_editor_hint():
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		orbiting = event.pressed
	elif event is InputEventMouseMotion and orbiting:
		yaw -= event.relative.x * 0.006
		pitch = clampf(pitch + event.relative.y * 0.006, -0.15, 1.20)
		picture_frame.hide()
		_frame_camera()
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_HOME:
				yaw = LOGO_YAW
				pitch = LOGO_PITCH
				picture_frame.show()
				_frame_camera()
			KEY_D, KEY_N:
				night = event.keycode == KEY_N
				_update_look()
			KEY_1, KEY_2, KEY_3:
				var views := [SPECTRUM, SPECTROGRAM, LOGO_SIGNAL]
				signal_view = views[event.keycode - KEY_1]
				_update_plots()

func _group(parent: Node3D, node_name: String) -> Node3D:
	var node := Node3D.new()
	node.name = node_name
	parent.add_child(node, true)
	return node

func _box(parent: Node3D, node_name: String, at: Vector3, size: Vector3, color: Color) -> MeshInstance3D:
	var box := BoxMesh.new()
	box.size = size
	return _mesh(parent, node_name, box, at, color)

func _mesh(parent: Node3D, node_name: String, mesh: Mesh, at: Vector3, color: Color) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.name = node_name
	instance.mesh = mesh
	instance.position = at
	if not materials.has(color):
		var material := StandardMaterial3D.new()
		material.albedo_color = color
		material.roughness = 0.72
		materials[color] = material
	instance.material_override = materials[color]
	parent.add_child(instance, true)
	return instance

func _screen_material(texture: Texture2D) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_texture = texture
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	return material

func _finish(item: MeshInstance3D, pattern: String) -> void:
	var base := item.material_override as StandardMaterial3D
	var key := "%s-%s" % [pattern, base.albedo_color.to_html()]
	if not finishes.has(key):
		if not finishes.has(pattern):
			var grain := FastNoiseLite.new()
			grain.seed = 108
			grain.frequency = 0.22 if pattern == "felt" else 0.095
			var texture := NoiseTexture2D.new()
			texture.noise = grain
			texture.width = 128
			texture.height = 128
			texture.seamless = true
			var levels := Gradient.new()
			levels.colors = PackedColorArray([Color("#b5b5b5"), Color.WHITE])
			texture.color_ramp = levels
			finishes[pattern] = texture
		var material := base.duplicate() as StandardMaterial3D
		material.albedo_texture = finishes[pattern]
		material.uv1_scale = Vector3(1, 8, 1) if pattern == "wood" else Vector3(3, 3, 3)
		material.roughness = 0.64 if pattern == "wood" else 0.94
		finishes[key] = material
	item.material_override = finishes[key]

func _rod(parent: Node3D, node_name: String, a: Vector3, b: Vector3, radius: float, color: Color) -> void:
	var delta := b - a
	if delta.length_squared() < 0.000001:
		return
	var rod := CylinderMesh.new()
	rod.top_radius = radius
	rod.bottom_radius = radius
	rod.height = delta.length()
	rod.radial_segments = 8
	var item := _mesh(parent, node_name, rod, (a + b) / 2, color)
	item.quaternion = Quaternion(Vector3.UP, delta.normalized())

func _line(parent: Node3D, node_name: String, points: Array, radius: float, color: Color, rounded := false) -> void:
	for i in range(1, points.size()):
		_rod(parent, node_name, points[i - 1], points[i], radius, color)
		if rounded and i < points.size() - 1:
			var join := SphereMesh.new()
			join.radius = radius
			join.height = radius * 2.0
			join.radial_segments = 8
			join.rings = 3
			_mesh(parent, "CableBend", join, points[i], color)

func _arrow(parent: Node3D, point: Vector3, direction: Vector3, color: Color, size: float) -> void:
	var base := point - direction * size
	_rod(parent, "ArrowHead", base + Vector3.UP * size * 0.65, point, size * 0.17, color)
	_rod(parent, "ArrowHead", base - Vector3.UP * size * 0.65, point, size * 0.17, color)

func _label3d(parent: Node3D, node_name: String, words: String, at: Vector3, size: int, color: Color, pixel: float) -> void:
	var label := Label3D.new()
	label.name = node_name
	label.position = at
	label.text = words
	label.font_size = size
	label.pixel_size = pixel
	label.outline_size = 0
	label.modulate = color
	parent.add_child(label, true)
