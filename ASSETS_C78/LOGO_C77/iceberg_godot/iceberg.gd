extends Node3D

const BACKDROP = preload("res://wind_and_water.gdshader")
const CUTAWAY = preload("res://ice_cutaway.gdshader")
const VIEW_SIZE := 6.4
const SECTION_RESOLUTION := 500
const SIDES := 15
const ICE_WIDTH := 0.876
const FIGURE_HEAD := Vector3(0.016, 0.35, 0)
const PASSAGE := [
	Vector3(-0.37, 1.79, 0.05),
	Vector3(-0.18, 1.45, 0.17),
	Vector3(0.48, 1.05, 0.31),
	Vector3(0.49, 0.78, 0.27),
	Vector3(-0.62, 0.32, 0.52),
	Vector3(-0.78, 0.00, 0.44),
	Vector3(-0.35, -0.33, 0.57),
	Vector3(0.85, -0.78, 0.35),
	Vector3(1.00, -1.06, 0.29),
	Vector3(0.42, -1.40, 0.61),
	Vector3(-0.78, -1.86, 0.37),
	Vector3(-0.83, -2.12, 0.21),
	Vector3(-0.59, -2.51, 0.14),
]
const PRISM := [
	Color("#6654af"), Color("#3e6abb"), Color("#3baebf"), Color("#8ed8bb"),
	Color("#b3d98e"), Color("#dce27d"), Color("#f9d863"), Color("#f9c848"),
]
# Height, horizontal radius, depth radius, and horizontal center.
const PROFILE := [
	Vector4(1.92, 0.16, 0.12, -0.43),
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
	var ice := _build_ice()
	_build_clear_flow()
	ice.set_shader_parameter("opening_mask", _build_path())
	_build_summit_figure()
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
	var figure_head := _summit() + FIGURE_HEAD
	var wind_origin := Vector2(figure_head.x, -figure_head.y) / VIEW_SIZE + Vector2(0.5, 0.5)
	shader.set_shader_parameter("wind_origin", wind_origin)
	var panel := MeshInstance3D.new()
	panel.name = "AnalogSkyDigitalWater"
	panel.mesh = background
	panel.material_override = shader
	panel.position.z = -7.0
	add_child(panel)

func _build_ice() -> ShaderMaterial:
	var rng := RandomNumberGenerator.new()
	rng.seed = 893
	for profile: Vector4 in PROFILE:
		var ring := PackedVector3Array()
		for side in range(SIDES):
			var angle := TAU * float(side) / SIDES
			var radial := 1.0 + rng.randf_range(-0.09, 0.09)
			var x := (profile.w + sin(angle) * profile.y * radial) * ICE_WIDTH
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
	for side in range(SIDES):
		_ice_face(surface, _summit(), rings[0][side], rings[0][(side + 1) % SIDES], rng.randf())
	var ice := _mesh("FacetedIceberg", surface, Color.WHITE)
	var material := ShaderMaterial.new()
	material.shader = CUTAWAY
	material.set_shader_parameter("view_size", VIEW_SIZE)
	ice.material_override = material
	return material

func _ice_face(surface: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, variation: float) -> void:
	var middle := (a + b + c) / 3.0
	var normal := (c - a).cross(b - a).normalized()
	if normal.dot(Vector3(middle.x, 0, middle.z)) < 0.0:
		var swap := b
		b = c
		c = swap
		normal = -normal
	var reflection := clampf(normal.dot(Vector3(-0.46, 0.63, 0.63).normalized()) * 0.55 + 0.43, 0, 1)
	var band := clampf(inverse_lerp(-2.85, 1.92, middle.y + middle.x * 0.23), 0.0, 1.0)
	band *= PRISM.size() - 1
	var first := mini(int(band), PRISM.size() - 2)
	var color: Color = PRISM[first].lerp(PRISM[first + 1], band - first)
	var light := 0.12 + reflection * 0.46 + (variation - 0.5) * 0.24
	if middle.y < 0.0:
		light -= 0.20
	color = color.lerp(Color("#f6f8ee"), light) if light >= 0.0 else color.darkened(-light)
	for point: Vector3 in [a, b, c]:
		surface.set_normal(normal)
		surface.set_color(color)
		surface.add_vertex(point)

func _build_clear_flow() -> void:
	var flow := SurfaceTool.new()
	flow.begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	for index in range(41):
		var progress := float(index) / 40.0
		var angle := lerpf(-0.91, 0.37, progress)
		var y := 1.08 + sin(progress * TAU) * 0.058
		var half_width := sin(progress * PI) * 0.022
		for edge: float in [y - half_width, y + half_width]:
			flow.add_vertex(_wall_point(edge, angle) + Vector3(0, 0, 0.014))
	_mesh("ClearFlowInsideIce", flow, Color("#fffcdf"))

func _build_path() -> ImageTexture:
	var air := PackedVector3Array()
	var water := PackedVector3Array()
	for index in range(PASSAGE.size() - 1):
		var from: Vector3 = PASSAGE[index]
		var to: Vector3 = PASSAGE[index + 1]
		var before: Vector3 = PASSAGE[maxi(index - 1, 0)]
		var after: Vector3 = PASSAGE[mini(index + 2, PASSAGE.size() - 1)]
		var samples := air if from.y > 0.0 else water
		for step in range(16):
			samples.append(from.cubic_interpolate(to, before, after, float(step) / 16.0))
	air.append(water[0])
	water.append(PASSAGE[-1])
	assert(is_zero_approx(air[-1].y) and air[-1].is_equal_approx(water[0]))
	var above := _build_path_section(air, false)
	var underwater := _build_path_section(water, true)
	_build_oceanarium(underwater)
	var mask := Image.create_empty(SECTION_RESOLUTION, SECTION_RESOLUTION, false, Image.FORMAT_R8)
	_cut_passage(mask, above, 0.24)
	_cut_passage(mask, underwater, 0.32)
	return ImageTexture.create_from_image(mask)

func _build_path_section(samples: PackedVector3Array, submerged: bool) -> Array[PackedVector3Array]:
	var track := SurfaceTool.new()
	var rim := SurfaceTool.new()
	var rails := SurfaceTool.new()
	var posts := SurfaceTool.new()
	for surface: SurfaceTool in [track, rim, rails, posts]:
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var sections: Array[PackedVector3Array] = []
	var distance_since_post := 1.0
	for index in range(samples.size()):
		var point := samples[index]
		var width := minf(0.23, PROFILE[0].x - point.y + 0.04)
		var inner := point - Vector3(0.058, 0, width * 0.5)
		var outer := point + Vector3(0.058, 0, width * 0.5)
		var rail_height := minf(0.16, PROFILE[0].x - point.y - 0.021)
		var guard := outer + Vector3.UP * rail_height
		var current := PackedVector3Array([inner, outer, guard])
		if index > 0:
			var previous := sections.back() as PackedVector3Array
			_quad(track, previous[0], previous[1], outer, inner)
			_quad(rim, previous[1], previous[1] + Vector3.DOWN * 0.042, outer + Vector3.DOWN * 0.042, outer)
			_bar(rails, previous[2], guard, 0.012)
			distance_since_post += outer.distance_to(previous[1])
		if distance_since_post >= 0.29 or index == samples.size() - 1:
			_bar(posts, outer, guard, 0.010)
			distance_since_post = 0.0
		sections.append(current)
	if submerged:
		_mesh("OceanariumWalkway", track, Color("#8cb8bc"))
		_mesh("OceanariumWalkwayEdge", rim, Color("#b9e5da"))
		_mesh("OceanariumGuardrail", rails, Color("#b0d8d3"))
		_mesh("OceanariumGuardrailPosts", posts, Color("#8bafbe"))
	else:
		_mesh("SpiralWalkway", track, Color("#b59f6e"))
		_mesh("WalkwayTimberEdge", rim, Color("#e9be77"))
		_mesh("Guardrail", rails, Color("#f6dc97"))
		_mesh("GuardrailPosts", posts, Color("#dcc48f"))
	return sections

# A single profile cut follows the floor and ceiling of the interior route.
func _cut_passage(mask: Image, sections: Array[PackedVector3Array], roof: float) -> void:
	var previous := PackedVector2Array()
	for index in range(sections.size()):
		var inner := sections[index][0]
		var outer := sections[index][1]
		var slice := PackedVector2Array()
		var ceiling := minf(roof, PROFILE[0].x - outer.y - 0.023)
		for x: float in [inner.x - 0.023, outer.x + 0.023]:
			for dy: float in [-0.065, ceiling]:
				var point := Vector2(x, -outer.y - dy) / VIEW_SIZE + Vector2(0.5, 0.5)
				slice.append(point * SECTION_RESOLUTION)
		if not previous.is_empty():
			_fill_passage_mask(mask, Geometry2D.convex_hull(previous + slice))
		previous = slice

func _fill_passage_mask(mask: Image, polygon: PackedVector2Array) -> void:
	var bounds := Rect2(polygon[0], Vector2.ZERO)
	for point: Vector2 in polygon:
		bounds = bounds.expand(point)
	bounds = bounds.intersection(Rect2(Vector2.ZERO, Vector2(mask.get_size())))
	for y in range(floori(bounds.position.y), ceili(bounds.end.y)):
		for x in range(floori(bounds.position.x), ceili(bounds.end.x)):
			if Geometry2D.is_point_in_polygon(Vector2(x + 0.5, y + 0.5), polygon):
				mask.set_pixel(x, y, Color.WHITE)

func _build_oceanarium(sections: Array[PackedVector3Array]) -> void:
	var glass := SurfaceTool.new()
	var frame := SurfaceTool.new()
	var seam := SurfaceTool.new()
	for surface: SurfaceTool in [glass, frame, seam]:
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var previous := PackedVector3Array()
	var rib_spacing := 0.0
	for index in range(sections.size()):
		var inner := sections[index][0]
		var outer := sections[index][1]
		var center := (inner + outer) / 2.0
		var half_width := (outer - inner) * 0.57
		var height := minf(0.275, -center.y)
		var arch := PackedVector3Array()
		for point in range(9):
			var angle := PI * float(point) / 8.0
			arch.append(center + half_width * cos(angle) + Vector3.UP * height * sin(angle))
		if index > 0:
			for point in range(8):
				_quad(glass, previous[point], previous[point + 1], arch[point + 1], arch[point])
			_bar(seam, previous[4], arch[4], 0.008)
			rib_spacing += arch[0].distance_to(previous[0])
		if rib_spacing >= 0.41 or index == sections.size() - 1:
			for point in range(8):
				_bar(frame, arch[point], arch[point + 1], 0.010)
			rib_spacing = 0.0
		previous = arch
	var canopy := _mesh("OceanariumGlass", glass, Color(0.60, 0.88, 0.94, 0.20))
	var material := canopy.material_override as StandardMaterial3D
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mesh("OceanariumArchedRibs", frame, Color("#9acbd0"))
	_mesh("OceanariumRoofSeam", seam, Color("#c2e4e4"))

func _summit() -> Vector3:
	return Vector3(PROFILE[0].w * ICE_WIDTH, PROFILE[0].x, 0.0)

func _build_summit_figure() -> void:
	var summit := _summit()
	var outline := SurfaceTool.new()
	var boots := SurfaceTool.new()
	var jacket := SurfaceTool.new()
	for surface: SurfaceTool in [outline, boots, jacket]:
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	_figure_bar(boots, outline, summit, Vector3(-0.057, 0.018, 0.03), Vector3(-0.045, 0.137, 0.03), 0.024)
	_figure_bar(boots, outline, summit, Vector3(0.071, 0.018, -0.02), Vector3(0.035, 0.137, -0.02), 0.024)
	_figure_bar(jacket, outline, summit, Vector3(0, 0.137, 0), Vector3(0.01, 0.286, 0), 0.06)
	_figure_bar(jacket, outline, summit, Vector3(-0.055, 0.264, 0.014), Vector3(-0.093, 0.157, 0.038), 0.019)
	_figure_bar(jacket, outline, summit, Vector3(0.065, 0.264, 0.012), Vector3(0.123, 0.181, 0.049), 0.019)
	_mesh("SummitFigureOutline", outline, Color("#5b7779"))
	_mesh("SummitFigureLegs", boots, Color("#e3eded"))
	_mesh("SummitFigureJacket", jacket, Color("#fffefa"))

	var head := SphereMesh.new()
	head.radius = 0.061
	head.height = 0.143
	head.radial_segments = 8
	head.rings = 4
	var face := SurfaceTool.new()
	face.create_from(head, 0)
	var head_center := summit + FIGURE_HEAD
	_mesh("SummitFigureHead", face, Color("#ffffff")).position = head_center
	var head_outline := _mesh("SummitFigureHeadOutline", face, Color("#5b7779"))
	head_outline.position = head_center - Vector3(0, 0, 0.15)
	head_outline.scale = Vector3.ONE * 1.18

func _figure_bar(surface: SurfaceTool, outline: SurfaceTool, origin: Vector3,
		start: Vector3, finish: Vector3, radius: float) -> void:
	_bar(surface, origin + start, origin + finish, radius)
	var behind := origin - Vector3(0, 0, 0.15)
	var pad := (finish - start).normalized() * 0.009
	_bar(outline, behind + start - pad, behind + finish + pad, radius + 0.010)

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
