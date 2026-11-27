extends Node3D

const BACKDROP = preload("res://wind_and_water.gdshader")
const CUTAWAY = preload("res://ice_cutaway.gdshader")
const VIEW_SIZE := 6.4
const SECTION_RESOLUTION := 1000
const SIDES := 15
const ICE_WIDTH := 0.876
const FIGURE_HEAD := Vector3(0, 0.35, 0)
const ICON_FIGURE_SCALE := 2.0
const ROUTE_TOP := 1.79
const ROUTE_BOTTOM := -2.62
const ARCH_SEGMENTS := 20
const PRISM := [
	Color("#6654af"), Color("#3e6abb"), Color("#3baebf"), Color("#8ed8bb"),
	Color("#b3d98e"), Color("#dce27d"), Color("#f9d863"), Color("#f9c848"),
]
# Height, horizontal radius, depth radius, and horizontal center.
const PROFILE := [
	Vector4(1.92, 0.16, 0.12, 0.00),
	Vector4(1.62, 0.57, 0.43, -0.04),
	Vector4(1.11, 0.98, 0.73, -0.10),
	Vector4(0.55, 1.37, 0.96, -0.12),
	Vector4(0.00, 1.58, 1.11, -0.03),
	Vector4(-0.56, 1.88, 1.28, 0.05),
	Vector4(-1.18, 2.00, 1.37, 0.06),
	Vector4(-1.83, 1.63, 1.13, -0.08),
	Vector4(-2.40, 0.97, 0.67, -0.32),
	Vector4(-2.85, 0.10, 0.12, -0.74),
]

func _ready() -> void:
	var arguments := OS.get_cmdline_user_args()
	var icon := arguments.has("--icon")
	var figure_scale := ICON_FIGURE_SCALE if icon else 1.0
	_build_view(figure_scale)
	var ice := _build_ice()
	ice.set_shader_parameter("opening_mask", _build_path())
	_build_summit_figure(figure_scale, icon)
	_build_title(icon)
	var export_index := arguments.find("--render")
	if export_index >= 0:
		if export_index + 1 >= arguments.size():
			push_error("--render requires an output PNG path.")
			get_tree().quit(1)
		else:
			_save_png(arguments[export_index + 1])

func _build_view(figure_scale: float) -> void:
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
	var figure_head := _summit() + FIGURE_HEAD * figure_scale
	var wind_origin := Vector2(figure_head.x, -figure_head.y) / VIEW_SIZE + Vector2(0.5, 0.5)
	shader.set_shader_parameter("wind_origin", wind_origin)
	var panel := MeshInstance3D.new()
	panel.name = "AnalogSkyDigitalWater"
	panel.mesh = background
	panel.material_override = shader
	panel.position.z = -7.0
	add_child(panel)
	_build_water_text()

func _build_water_text() -> void:
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Menlo", "DejaVu Sans Mono", "monospace"])
	var letters := "aWdeIrTpsNoMtyAVeLcgUkn"
	for index in range(71):
		var x := 3.5 + index * 7.0 + 1.4 * sin(index * 1.8)
		var crest := _surface_swell(x)
		var y := 251.0 + crest + 2.0 * sin(index * 2.1)
		var slope := (_surface_swell(x + 1.0) - _surface_swell(x - 1.0)) * 0.5
		var size := 9 + (index * 7) % 10 + roundi(2.0 * (1.0 - smoothstep(-11.0, 1.0, crest)))
		var letter := _water_label(font, letters[index % letters.length()], Vector2(x, y), size, Color("#e1f6e9"))
		letter.rotation.z = -atan(slope) + 0.15 * sin(index * 3.7)
		letter.outline_size = 1
		letter.outline_modulate = Color("#386460")

	_water_label(font, "def idea(): ...", Vector2(59, 286), 11, Color("#c7edba"))
	_water_label(font, "record Idea() {}", Vector2(59, 301), 11, Color("#c6e6f0"))
	_water_label(font, "let n: number\n    = 1;", Vector2(444, 294), 11, Color("#b4daf4"))
	_water_label(font, "int n = 1;", Vector2(59, 324), 11, Color("#9edccf"))
	_water_label(font, "let mut n = 1;", Vector2(446, 324), 11, Color("#9edccf"))
	_water_label(font, "MOV AX, 1\nADD AX, BX", Vector2(55, 350), 11, Color("#e1c78a"))
	_water_label(font, "DEC CX\nJNZ .loop", Vector2(446, 350), 11, Color("#e1c78a"))

func _surface_swell(x: float) -> float:
	# Match the crest in wind_and_water.gdshader.
	var phase := x * 0.077 + sin(x * 0.026) + 0.36 * sin(x * 0.101 + 0.7)
	var height := 11.0 + 4.6 * sin(x * 0.041 + 1.1) + 2.2 * sin(x * 0.12 - 0.5)
	return height * sin(phase) + 3.8 * cos(phase * 2.0 + 0.95) + 1.7 * sin(x * 0.29) + 0.9 * sin(x * 0.53)

func _water_label(font: Font, copy: String, pixel: Vector2, size: int, ink: Color) -> Label3D:
	var label := Label3D.new()
	label.font = font
	label.font_size = size
	label.outline_size = 0
	label.pixel_size = VIEW_SIZE / 500.0
	label.modulate = ink
	label.text = copy
	label.position = Vector3(pixel.x - 250.0, 250.0 - pixel.y, 0.0) * label.pixel_size
	label.position.z = -6.9
	add_child(label)
	return label

func _build_ice() -> ShaderMaterial:
	var rings: Array[PackedVector3Array] = []
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

func _build_path() -> ImageTexture:
	var above := _route_sections(ROUTE_TOP, 0.0, 140)
	var underwater := _route_sections(0.0, ROUTE_BOTTOM, 200)
	assert(above[-1] == underwater[0])
	_build_path_section(above, false)
	_build_path_section(underwater, true)
	_build_oceanarium(underwater)
	var mask := Image.create_empty(SECTION_RESOLUTION, SECTION_RESOLUTION, false, Image.FORMAT_R8)
	_cut_passage(mask, above)
	_cut_passage(mask, underwater)
	return ImageTexture.create_from_image(mask)

func _ramp_x(progress: float) -> float:
	const FIRST_TURN := 0.42
	const SECOND_TURN := 0.677
	const LEFT_EDGE := -1.53
	const RIGHT_EDGE := 2.19
	var approach := LEFT_EDGE / FIRST_TURN
	var traverse := (RIGHT_EDGE - LEFT_EDGE) / (SECOND_TURN - FIRST_TURN)
	var descent := (-0.57 - RIGHT_EDGE) / (1.0 - SECOND_TURN)
	return (
		approach * progress
		+ (traverse - approach) * _rounded_turn(progress - FIRST_TURN)
		+ (descent - traverse) * _rounded_turn(progress - SECOND_TURN)
	)

# Replace each sharp change of slope with a short parabolic turn.
func _rounded_turn(distance: float) -> float:
	const RADIUS := 0.079
	var blend := clampf(distance + RADIUS, 0.0, 2.0 * RADIUS)
	return maxf(0.0, distance - RADIUS) + blend * blend / (4.0 * RADIUS)

func _route_sections(top: float, bottom: float, steps: int) -> Array[PackedVector3Array]:
	var sections: Array[PackedVector3Array] = []
	for index in range(steps + 1):
		var y := lerpf(top, bottom, float(index) / steps)
		var progress := inverse_lerp(ROUTE_TOP, ROUTE_BOTTOM, y)
		var target_x := _ramp_x(progress)
		var headroom := _route_headroom(y)
		var floor_profile := _ellipse_at(y)
		var roof_profile := _ellipse_at(y + headroom)
		var phase := asin(clampf((target_x - floor_profile.z) / floor_profile.x, -0.99, 0.99))
		var heading := Vector3(sin(phase), 0, cos(phase))
		var floor_spoke := heading * Vector3(floor_profile.x, 0, floor_profile.y)
		var roof_spoke := heading * Vector3(roof_profile.x, 0, roof_profile.y)
		var taper := floor_spoke.length() - roof_spoke.length()
		var roof_weight := smoothstep(-0.13, 0.13, taper)
		var spoke := floor_spoke.lerp(roof_spoke, roof_weight)
		var center := Vector3(lerpf(floor_profile.z, roof_profile.z, roof_weight), y, 0)
		var direction := spoke.normalized()
		var outer := center + spoke - direction * minf(0.08, spoke.length() * 0.33)
		var inner := outer - direction * minf(0.27, spoke.length() * 0.47)
		var guard := outer + Vector3.UP * minf(0.15, headroom)
		sections.append(PackedVector3Array([inner, outer, guard]))
	return sections

func _route_headroom(y: float) -> float:
	var headroom := lerpf(0.24, 0.32, smoothstep(0.0, 0.32, -y))
	return minf(headroom, PROFILE[0].x - y - 0.025)

# Ellipse radii and horizontal center, in the same coordinates as the ice.
func _ellipse_at(y: float) -> Vector3:
	for i in range(PROFILE.size() - 1):
		var top: Vector4 = PROFILE[i]
		var bottom: Vector4 = PROFILE[i + 1]
		if y >= bottom.x:
			var before: Vector4 = PROFILE[maxi(i - 1, 0)]
			var after: Vector4 = PROFILE[mini(i + 2, PROFILE.size() - 1)]
			var span := top.x - bottom.x
			var start := Vector3(top.y, top.z, top.w)
			var end := Vector3(bottom.y, bottom.z, bottom.w)
			var lead := Vector3(before.y, before.z, before.w)
			var follow := Vector3(after.y, after.z, after.w)
			var section := start.cubic_interpolate_in_time(
				end, lead, follow, (top.x - y) / span, span, top.x - before.x, top.x - after.x
			)
			return section * Vector3(ICE_WIDTH, 1.0, ICE_WIDTH)
	assert(false, "The route must remain inside the height of the ice.")
	return Vector3.ZERO

func _build_path_section(sections: Array[PackedVector3Array], submerged: bool) -> void:
	var track := SurfaceTool.new()
	var guardrail := SurfaceTool.new()
	for surface: SurfaceTool in [track, guardrail]:
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var handrail := PackedVector3Array()
	var distance_since_post := 1.0
	for index in range(sections.size()):
		var inner := sections[index][0]
		var outer := sections[index][1]
		var guard := sections[index][2]
		if index > 0:
			var previous := sections[index - 1]
			_quad(track, previous[0], previous[1], outer, inner)
			_quad(track, previous[1], previous[1] + Vector3.DOWN * 0.067, outer + Vector3.DOWN * 0.067, outer)
			distance_since_post += outer.distance_to(previous[1])
		handrail.append(guard)
		if distance_since_post >= 0.49 or index == sections.size() - 1:
			_route_tube(guardrail, PackedVector3Array([outer, guard]), 0.010)
			distance_since_post = 0.0
	_route_tube(guardrail, handrail, 0.018)
	if submerged:
		_mesh("OceanariumWalkway", track, Color("#76b9b5"))
		_mesh("OceanariumGuardrail", guardrail, Color("#e3f4e5"))
	else:
		_mesh("Walkway", track, Color("#d1ae72"))
		_mesh("Guardrail", guardrail, Color("#fff1c5"))

# A single profile cut follows the floor and ceiling of the interior route.
func _cut_passage(mask: Image, sections: Array[PackedVector3Array]) -> void:
	var previous := PackedVector2Array()
	for index in range(sections.size()):
		var inner := sections[index][0]
		var outer := sections[index][1]
		var slice := PackedVector2Array()
		var ceiling := _route_headroom(outer.y)
		var floor_clearance := 0.083
		var center := Vector2((inner.x + outer.x) * 0.5, -outer.y - (ceiling - floor_clearance) * 0.5)
		var radius := Vector2(absf(inner.x - outer.x) * 0.5 + 0.054, (ceiling + floor_clearance) * 0.5)
		for side in range(16):
			var edge := center + Vector2.from_angle(float(side) * TAU / 16.0) * radius
			var point := edge / VIEW_SIZE + Vector2(0.5, 0.5)
			slice.append(point * SECTION_RESOLUTION)
		if not previous.is_empty():
			_fill_passage_mask(mask, Geometry2D.convex_hull(previous + slice))
		previous = slice

func _fill_passage_mask(mask: Image, polygon: PackedVector2Array) -> void:
	var bounds := Rect2(polygon[0], Vector2.ZERO)
	for point: Vector2 in polygon:
		bounds = bounds.expand(point)
	var first_row := maxi(0, floori(bounds.position.y))
	var last_row := mini(mask.get_height(), ceili(bounds.end.y))
	for y in range(first_row, last_row):
		var sample := y + 0.5
		var left := float(mask.get_width())
		var right := 0.0
		for i in range(polygon.size()):
			var a := polygon[i]
			var b := polygon[(i + 1) % polygon.size()]
			if sample < minf(a.y, b.y) or sample >= maxf(a.y, b.y):
				continue
			var x := lerpf(a.x, b.x, (sample - a.y) / (b.y - a.y))
			left = minf(left, x)
			right = maxf(right, x)
		var first := maxi(0, ceili(left - 0.5))
		var last := mini(mask.get_width(), ceili(right - 0.5))
		if last > first:
			mask.fill_rect(Rect2i(first, y, last - first, 1), Color.WHITE)

func _build_oceanarium(sections: Array[PackedVector3Array]) -> void:
	var glass := SurfaceTool.new()
	glass.begin(Mesh.PRIMITIVE_TRIANGLES)
	var previous := PackedVector3Array()
	for index in range(sections.size()):
		var inner := sections[index][0]
		var outer := sections[index][1]
		var center := (inner + outer) / 2.0
		var half_width := (outer - inner) * 0.57
		var height := 0.273 * smoothstep(0.0, 0.46, -center.y)
		var arch := PackedVector3Array()
		for point in range(ARCH_SEGMENTS + 1):
			var angle := PI * float(point) / ARCH_SEGMENTS
			arch.append(center + half_width * cos(angle) + Vector3.UP * height * sin(angle))
		if index > 0:
			for point in range(ARCH_SEGMENTS):
				_quad(glass, previous[point], previous[point + 1], arch[point + 1], arch[point])
		previous = arch
	var canopy := _mesh("OceanariumGlass", glass, Color(0.60, 0.88, 0.94, 0.10))
	var material := canopy.material_override as StandardMaterial3D
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.cull_mode = BaseMaterial3D.CULL_BACK

func _route_tube(surface: SurfaceTool, points: PackedVector3Array, radius: float) -> void:
	const SIDES_AROUND_TUBE := 10
	var previous := PackedVector3Array()
	var basis := Vector3.ZERO
	for index in range(points.size()):
		var before := points[maxi(index - 1, 0)]
		var after := points[mini(index + 1, points.size() - 1)]
		var tangent := (after - before).normalized()
		if index == 0:
			var reference := Vector3.RIGHT if absf(tangent.x) < 0.9 else Vector3.UP
			basis = tangent.cross(reference).normalized()
		else:
			basis = (basis - tangent * basis.dot(tangent)).normalized()
		var u := basis * radius
		var v := tangent.cross(u)
		var ring := PackedVector3Array()
		for side in range(SIDES_AROUND_TUBE):
			var angle := TAU * float(side) / SIDES_AROUND_TUBE
			ring.append(points[index] + u * cos(angle) + v * sin(angle))
		if index > 0:
			for side in range(SIDES_AROUND_TUBE):
				var next := (side + 1) % SIDES_AROUND_TUBE
				_quad(surface, previous[side], previous[next], ring[next], ring[side])
		previous = ring

func _summit() -> Vector3:
	return Vector3(PROFILE[0].w * ICE_WIDTH, PROFILE[0].x, 0.0)

func _build_summit_figure(figure_scale: float, icon: bool) -> void:
	var figure := Node3D.new()
	figure.name = "SummitFigure"
	figure.position = _summit()
	figure.scale = Vector3.ONE * figure_scale
	add_child(figure)

	var outline := SurfaceTool.new()
	var boots := SurfaceTool.new()
	var jacket := SurfaceTool.new()
	for surface: SurfaceTool in [outline, boots, jacket]:
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var stroke := 0.021 if icon else 0.010
	var outline_color := Color("#365954") if icon else Color("#5b7779")
	var sole := 0.009 if icon else 0.018
	_figure_bar(boots, outline,
		Vector3(-0.060, sole, 0.02), Vector3(-0.041, 0.137, 0.02), 0.024, stroke)
	_figure_bar(boots, outline,
		Vector3(0.060, sole, -0.02), Vector3(0.041, 0.137, -0.02), 0.024, stroke)
	_figure_bar(jacket, outline,
		Vector3(0, 0.137, 0), Vector3(0, 0.286, 0), 0.06, stroke)
	_figure_bar(jacket, outline,
		Vector3(-0.060, 0.264, 0.014), Vector3(-0.106, 0.157, 0.038), 0.019, stroke)
	_figure_bar(jacket, outline,
		Vector3(0.060, 0.264, 0.012), Vector3(0.106, 0.181, 0.049), 0.019, stroke)
	_mesh("SummitFigureOutline", outline, outline_color).reparent(figure, false)
	_mesh("SummitFigureLegs", boots, Color("#e3eded")).reparent(figure, false)
	_mesh("SummitFigureJacket", jacket, Color("#fffefa")).reparent(figure, false)

	var head := SphereMesh.new()
	head.radius = 0.061
	head.height = 0.143
	head.radial_segments = 8
	head.rings = 4
	var face := SurfaceTool.new()
	face.create_from(head, 0)
	var face_mesh := _mesh("SummitFigureHead", face, Color.WHITE)
	face_mesh.reparent(figure, false)
	face_mesh.position = FIGURE_HEAD
	var head_outline := _mesh("SummitFigureHeadOutline", face, outline_color)
	head_outline.reparent(figure, false)
	head_outline.position = FIGURE_HEAD - Vector3(0, 0, 0.15)
	head_outline.scale = Vector3.ONE * (1.34 if icon else 1.18)

func _figure_bar(surface: SurfaceTool, outline: SurfaceTool,
		start: Vector3, finish: Vector3, radius: float, stroke: float) -> void:
	_bar(surface, start, finish, radius)
	var behind := Vector3(0, 0, -0.15)
	var pad := (finish - start).normalized() * 0.009
	_bar(outline, behind + start - pad, behind + finish + pad, radius + stroke)

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

func _build_title(icon: bool) -> void:
	var overlay := CanvasLayer.new()
	overlay.name = "Wordmark"
	add_child(overlay)

	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Avenir Next", "DejaVu Sans", "sans-serif"])
	font.font_weight = 600
	var title := Label.new()
	title.text = "A" if icon else "Anechoic"
	title.anchor_right = 1.0
	# The icon glyph starts at the summit in the 500 px viewport.
	title.offset_top = -147.0 if icon else 13.0
	title.offset_bottom = 769.0 if icon else 76.0
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title.add_theme_font_override("font", font)
	title.add_theme_font_size_override("font_size", 530 if icon else 46)
	title.add_theme_color_override("font_color", Color(0.96, 0.98, 0.90, 0.51) if icon else Color("#173d34"))
	if icon:
		title.add_theme_color_override("font_outline_color", Color(0.13, 0.29, 0.28, 0.66))
		title.add_theme_constant_override("outline_size", 10)
	overlay.add_child(title)

func _save_png(output: String) -> void:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var result := get_viewport().get_texture().get_image().save_png(output)
	if result != OK:
		push_error("Could not save logo: %s" % error_string(result))
	get_tree().quit(result)
