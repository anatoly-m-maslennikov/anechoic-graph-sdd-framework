extends Node3D

const BACKDROP = preload("res://wind_and_water.gdshader")
const VIEW_SIZE := 6.4
const SIDES := 15
const PATH_STEPS := 180
# Height, horizontal radius, depth radius, and horizontal center.
const PROFILE := [
	Vector4(2.03, 0.045, 0.05, -0.43),
	Vector4(1.62, 0.57, 0.43, -0.31),
	Vector4(1.11, 0.98, 0.73, -0.21),
	Vector4(0.55, 1.37, 0.96, -0.12),
	Vector4(0.00, 1.58, 1.11, -0.03),
	Vector4(-0.56, 1.88, 1.28, 0.05),
	Vector4(-1.18, 2.00, 1.37, 0.06),
	Vector4(-1.83, 1.63, 1.13, -0.08),
	Vector4(-2.40, 0.97, 0.67, -0.32),
	Vector4(-2.85, 0.10, 0.12, -0.74),
]

var rings: Array[PackedVector3Array] = []

func _ready() -> void:
	_build_view()
	_build_ice()
	_build_path()
	_build_title()
	var arguments := OS.get_cmdline_user_args()
	var export_index := arguments.find("--render")
	if export_index >= 0:
		if export_index + 1 >= arguments.size():
			push_error("--render requires an output PNG path.")
			get_tree().quit(1)
		else:
			_save_png(arguments[export_index + 1])

func _build_view() -> void:
	var camera := Camera3D.new()
	camera.name = "ProfileCamera"
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = VIEW_SIZE
	camera.position = Vector3(0, 0, 12)
	add_child(camera)
	camera.look_at(Vector3.ZERO)
	camera.make_current()

	var background := QuadMesh.new()
	background.size = Vector2.ONE * (VIEW_SIZE + 0.02)
	var shader := ShaderMaterial.new()
	shader.shader = BACKDROP
	var panel := MeshInstance3D.new()
	panel.name = "AnalogSkyDigitalWater"
	panel.mesh = background
	panel.material_override = shader
	panel.position.z = -7.0
	add_child(panel)

func _build_ice() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 893
	for profile: Vector4 in PROFILE:
		var ring := PackedVector3Array()
		for side in range(SIDES):
			var angle := TAU * float(side) / SIDES
			var radial := 1.0 + rng.randf_range(-0.09, 0.09)
			var x := profile.w + sin(angle) * profile.y * radial
			var z := cos(angle) * profile.z * radial
			ring.append(Vector3(x, profile.x, z))
		rings.append(ring)

	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for level in range(rings.size() - 1):
		var upper := rings[level]
		var lower := rings[level + 1]
		for side in range(SIDES):
			var next := (side + 1) % SIDES
			_ice_face(surface, upper[side], lower[side], upper[next], rng.randf())
			_ice_face(surface, upper[next], lower[side], lower[next], rng.randf())
	var ice := _mesh("FacetedIceberg", surface, Color.WHITE)
	(ice.material_override as StandardMaterial3D).vertex_color_use_as_albedo = true

func _ice_face(surface: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, variation: float) -> void:
	var middle := (a + b + c) / 3.0
	var normal := (c - a).cross(b - a).normalized()
	if normal.dot(Vector3(middle.x, 0, middle.z)) < 0.0:
		var swap := b
		b = c
		c = swap
		normal = -normal
	var reflection := clampf(normal.dot(Vector3(-0.46, 0.63, 0.63).normalized()) * 0.55 + 0.43, 0, 1)
	var color: Color
	if middle.y >= 0.0:
		color = Color("#79a8ae").lerp(Color("#f5faee"), 0.25 + reflection * 0.65)
	else:
		var blue := Color("#1d6675").lerp(Color("#2a8590"), smoothstep(-2.75, 0.0, middle.y))
		color = blue.lerp(Color("#88c4c2"), reflection * 0.47)
	color = color.lightened((variation - 0.44) * 0.19)
	for point: Vector3 in [a, b, c]:
		surface.set_normal(normal)
		surface.set_color(color)
		surface.add_vertex(point)

func _build_path() -> void:
	var track := SurfaceTool.new()
	var rim := SurfaceTool.new()
	var rails := SurfaceTool.new()
	var posts := SurfaceTool.new()
	for surface: SurfaceTool in [track, rim, rails, posts]:
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var previous := PackedVector3Array()
	var distance_since_post := 1.0
	for index in range(PATH_STEPS + 1):
		var percentage := float(index) / PATH_STEPS
		var y := lerpf(1.94, -2.65, percentage)
		var angle := lerpf(-0.70, TAU * 2.0 + 0.90, percentage)
		var radial := Vector3(sin(angle), 0, cos(angle))
		var wall := _wall_point(y, angle)
		var inner := wall + radial * 0.022
		var outer := wall + radial * 0.255
		var guard := outer + Vector3.UP * 0.215
		var current := PackedVector3Array([inner, outer, guard])
		if index > 0:
			_quad(track, previous[0], previous[1], outer, inner)
			_quad(rim, previous[1], previous[1] + Vector3.DOWN * 0.082, outer + Vector3.DOWN * 0.082, outer)
			_bar(rails, previous[2], guard, 0.028)
			distance_since_post += outer.distance_to(previous[1])
		if distance_since_post >= 0.36 or index == PATH_STEPS:
			_bar(posts, outer, guard, 0.026)
			distance_since_post = 0.0
		previous = current
	_mesh("SpiralWalkway", track, Color("#f0c782"))
	_mesh("WalkwayTimberEdge", rim, Color("#9a5433"))
	_mesh("Guardrail", rails, Color("#f6bb58"))
	_mesh("GuardrailPosts", posts, Color("#c36f43"))

func _wall_point(y: float, angle: float) -> Vector3:
	var step := fposmod(angle / TAU, 1.0) * SIDES
	var side := int(floor(step))
	var next := (side + 1) % SIDES
	var along := step - side
	for level in range(PROFILE.size() - 1):
		var top: float = PROFILE[level].x
		var bottom: float = PROFILE[level + 1].x
		if y <= top and y >= bottom:
			var down := (top - y) / (top - bottom)
			var a := rings[level][side]
			var b := rings[level + 1][side]
			var c := rings[level][next]
			var d := rings[level + 1][next]
			# Match the triangulation of the ice wall.
			if along + down <= 1.0:
				return a + (b - a) * down + (c - a) * along
			return d + (c - d) * (1.0 - down) + (b - d) * (1.0 - along)
	assert(false, "Spiral height must remain within the iceberg profile.")
	return Vector3(0, y, 0)

func _bar(surface: SurfaceTool, start: Vector3, finish: Vector3, radius: float) -> void:
	var direction := (finish - start).normalized()
	var reference := Vector3.RIGHT if absf(direction.dot(Vector3.UP)) > 0.95 else Vector3.UP
	var u := direction.cross(reference).normalized() * radius
	var v := direction.cross(u).normalized() * radius
	var corners := [u + v, u - v, -u - v, -u + v]
	for index in range(corners.size()):
		var a: Vector3 = corners[index]
		var b: Vector3 = corners[(index + 1) % corners.size()]
		_quad(surface, start + a, finish + a, finish + b, start + b)

func _quad(surface: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3) -> void:
	for point: Vector3 in [a, b, c, a, c, d]:
		surface.add_vertex(point)

func _mesh(label: String, surface: SurfaceTool, color: Color) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.name = label
	instance.mesh = surface.commit()
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	instance.material_override = material
	add_child(instance)
	return instance

func _build_title() -> void:
	var overlay := CanvasLayer.new()
	overlay.name = "Wordmark"
	add_child(overlay)

	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Avenir Next", "DejaVu Sans", "sans-serif"])
	font.font_weight = 600
	var title := Label.new()
	title.text = "Anechoic"
	title.anchor_right = 1.0
	title.offset_top = 13.0
	title.offset_bottom = 76.0
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title.add_theme_font_override("font", font)
	title.add_theme_font_size_override("font_size", 46)
	title.add_theme_color_override("font_color", Color("#173d34"))
	overlay.add_child(title)

func _save_png(output: String) -> void:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var result := get_viewport().get_texture().get_image().save_png(output)
	if result != OK:
		push_error("Could not save logo: %s" % error_string(result))
	get_tree().quit(result)
