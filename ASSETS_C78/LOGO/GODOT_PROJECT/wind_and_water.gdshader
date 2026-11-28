shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform vec2 wind_origin;
uniform sampler2D waterline : filter_linear, repeat_disable;
uniform bool show_technology = true;

float gust(vec2 p, vec2 start, float end, float rise, float bow, float width) {
	float t = clamp((p.x - start.x) / (end - start.x), 0.0, 1.0);
	float y = start.y - rise * t + bow * t * (1.0 - t);
	float fade = smoothstep(0.0, 0.14, t) * (1.0 - smoothstep(0.62, 1.0, t));
	return fade * (1.0 - smoothstep(width * 0.35, width, abs(p.y - y)));
}

vec3 windy_sky(vec2 p) {
	vec3 ivory = vec3(0.961, 0.922, 0.851);
	vec3 mist = vec3(0.766, 0.848, 0.812);
	vec3 tint = mix(ivory, mist, smoothstep(0.13, 0.51, p.y));
	float haze = gust(p, vec2(-0.26, 0.39), 0.76, 0.17, 0.14, 0.035)
		+ gust(p, vec2(0.38, 0.44), 1.34, 0.18, 0.19, 0.045);
	tint = mix(tint, vec3(0.94, 0.97, 0.88), haze * 0.27);
	float drift = gust(p, vec2(-0.23, 0.21), 0.53, 0.087, 0.08, 0.0036)
		+ gust(p, vec2(-0.15, 0.32), 0.43, 0.046, 0.10, 0.0043)
		+ gust(p, vec2(-0.21, 0.45), 0.52, 0.10, 0.11, 0.0044)
		+ gust(p, vec2(0.51, 0.325), 1.19, 0.083, 0.115, 0.0042)
		+ gust(p, vec2(0.39, 0.50), 1.15, 0.12, 0.05, 0.0047);
	tint = mix(tint, vec3(0.97, 0.98, 0.90), clamp(drift * 0.46, 0.0, 1.0));
	float wind = gust(p, wind_origin + vec2(0.018, -0.004), 1.02, 0.060, 0.15, 0.0057)
		+ gust(p, wind_origin + vec2(0.13, 0.031), 1.10, 0.060, 0.10, 0.0038)
		+ gust(p, wind_origin + vec2(0.07, -0.025), 0.93, 0.037, 0.11, 0.0035)
		+ gust(p, wind_origin + vec2(-0.020, 0.003), -0.12, 0.014, 0.12, 0.0050)
		+ gust(p, wind_origin + vec2(-0.112, 0.037), -0.075, 0.022, 0.14, 0.0037);
	return mix(tint, vec3(0.66, 0.77, 0.71), clamp(wind * 0.61, 0.0, 1.0));
}

float surface_y(float x) {
	return texture(waterline, vec2(x / 500.0, 0.5)).r * 500.0;
}

vec3 distant_water(vec2 pixel, vec3 sky) {
	float horizon = 241.0 + 3.2 * sin(pixel.x * 0.018 + 0.30)
		+ 2.4 * sin(pixel.x * 0.043 + 0.82);
	float depth = pixel.y - horizon;
	float seen = smoothstep(-2.0, 4.5, depth);
	float reflected_light = 1.0 - smoothstep(1.0, 10.0, depth);
	vec3 mist = mix(vec3(0.27, 0.46, 0.48), vec3(0.47, 0.62, 0.61), reflected_light);
	return mix(sky, mist, seen);
}

vec3 surface_water(vec2 pixel, float surface, float depth, vec3 water) {
	float crest = 1.0 - smoothstep(201.0, 249.0, surface);
	float slope = surface_y(pixel.x + 1.0) - surface;
	float face = 1.0 - smoothstep(1.0, 29.0, depth);
	float front = 1.0 - smoothstep(-0.95, 0.15, slope);
	float drift = pixel.x + depth * 1.08;
	float folds = 0.56 + 0.29 * sin(drift * 0.19) + 0.15 * sin(drift * 0.42 + depth * 0.17);
	vec3 underside = mix(vec3(0.09, 0.25, 0.33), vec3(0.14, 0.35, 0.41), 1.0 - front);
	vec3 glass = mix(underside, vec3(0.36, 0.62, 0.61), crest * folds);
	water = mix(water, glass, face * 0.89);

	float edge = 1.0 - smoothstep(0.35, 2.2 + 2.9 * folds, abs(depth));
	float patches = smoothstep(0.30, 0.80, folds);
	float rim = edge * crest * (0.12 + 0.54 * patches);

	float curl = 6.5 + 4.5 * front + 3.7 * sin(drift * 0.071 + 0.5);
	float ribbon = 1.0 - smoothstep(0.35, 2.0, abs(depth - curl));
	float trail = 1.0 - smoothstep(0.30, 1.6, abs(depth - curl - 5.5 - 2.4 * folds));
	float sheen = crest * patches * (ribbon * 0.38 + trail * 0.19);
	vec2 p = pixel / 500.0;
	float streaks = gust(p, vec2(-0.04, 0.522), 0.22, 0.037, 0.021, 0.0038)
		+ gust(p, vec2(0.012, 0.551), 0.25, 0.041, 0.018, 0.0026)
		+ gust(p, vec2(0.713, 0.541), 1.04, 0.053, 0.014, 0.0035)
		+ gust(p, vec2(0.762, 0.552), 1.14, 0.034, 0.010, 0.0026);
	float light = clamp(rim + sheen + streaks * (0.09 + 0.13 * folds), 0.0, 1.0);
	return mix(water, vec3(0.76, 0.90, 0.86), light);
}

float trace(vec2 pixel, vec2 a, vec2 b, float width) {
	vec2 along = b - a;
	float t = clamp(dot(pixel - a, along) / dot(along, along), 0.0, 1.0);
	return 1.0 - smoothstep(width * 0.45, width, length(pixel - a - along * t));
}

float box(vec2 p, vec2 half_size) {
	vec2 edge = abs(p) - half_size;
	return 1.0 - smoothstep(-0.6, 0.6, max(edge.x, edge.y));
}

float chip(vec2 p, vec2 half_size) {
	float rim = box(p, half_size) - box(p, half_size - vec2(1.8));
	float die = box(p, half_size * 0.47);
	vec2 pin = 1.0 - smoothstep(vec2(0.8), vec2(1.5), abs(mod(p + 3.0, 6.0) - 3.0));
	float pins = pin.x * (box(p, half_size + vec2(-3.0, 4.0)) - box(p, half_size))
		+ pin.y * (box(p, half_size + vec2(4.0, -3.0)) - box(p, half_size));
	return rim * 0.52 + die * 0.25 + pins * 0.75;
}

vec3 circuitry(vec2 pixel, vec3 water) {
	float wiring = trace(pixel, vec2(24.0, 369.0), vec2(47.0, 369.0), 1.3)
		+ trace(pixel, vec2(47.0, 369.0), vec2(56.0, 378.0), 1.3)
		+ trace(pixel, vec2(75.0, 392.0), vec2(88.0, 405.0), 1.3)
		+ trace(pixel, vec2(88.0, 405.0), vec2(148.0, 405.0), 1.3)
		+ trace(pixel, vec2(397.0, 387.0), vec2(408.0, 376.0), 1.3)
		+ trace(pixel, vec2(408.0, 376.0), vec2(419.0, 376.0), 1.3)
		+ trace(pixel, vec2(461.0, 376.0), vec2(485.0, 376.0), 1.3)
		+ trace(pixel, vec2(439.0, 388.0), vec2(439.0, 409.0), 1.3);
	float pads = box(pixel - vec2(24.0, 369.0), vec2(2.0))
		+ box(pixel - vec2(148.0, 405.0), vec2(2.0))
		+ box(pixel - vec2(485.0, 376.0), vec2(2.0))
		+ box(pixel - vec2(439.0, 409.0), vec2(2.0));
	float circuits = max(chip(pixel - vec2(70.0, 382.0), vec2(14.0)),
		chip(pixel - vec2(440.0, 376.0), vec2(21.0, 10.0)));
	return mix(water, vec3(0.46, 0.72, 0.66), clamp(circuits + 0.58 * wiring + 0.50 * pads, 0.0, 1.0));
}

float atom_orbit(vec2 point) {
	float ring = abs(length(point / vec2(6.3, 2.6)) - 1.0);
	return 1.0 - smoothstep(0.06, 0.23, ring);
}

vec3 atoms_and_molecules(vec2 pixel, vec3 water) {
	vec2 pitch = vec2(24.0, 16.0);
	vec2 grid = (pixel - vec2(0.0, 476.0)) * 2.0 / pitch;
	float row = floor(grid.y);
	if (row < 0.0 || row >= 3.0) {
		return water;
	}
	grid.x += mod(row, 2.0) * 0.5;
	vec2 point = (fract(grid) - 0.5) * pitch;
	float center = 1.0 - smoothstep(0.95, 1.75, length(point));
	vec3 line_ink = vec3(0.43, 0.72, 0.70);
	if (mod(floor(grid.x) + row, 2.0) == 0.0) {
		float orbits = max(atom_orbit(vec2(point.x + point.y, point.y - point.x) * 0.7071),
			atom_orbit(vec2(point.x - point.y, point.x + point.y) * 0.7071));
		water = mix(water, line_ink, 0.66 * orbits);
	} else {
		vec2 left = vec2(-5.2, -2.5);
		vec2 right = vec2(4.5, -3.5);
		float bonds = max(trace(point, vec2(0.0), left, 1.0), trace(point, vec2(0.0), right, 1.0));
		float ends = 1.0 - smoothstep(1.3, 2.3, min(length(point - left), length(point - right)));
		water = mix(water, line_ink, max(0.56 * bonds, 0.85 * ends));
	}
	return mix(water, vec3(0.97, 0.76, 0.49), 0.85 * center);
}

float electrical_wave_y(float x, float row) {
	return 429.0 + row * 11.0 + 2.6 * sin(x * (0.17 + row * 0.018) + row * 1.4);
}

vec3 electricity(vec2 pixel, vec3 water) {
	bool left = pixel.x < 250.0;
	float start = left ? 5.0 : 342.0;
	float pitch = left ? 18.5 : 17.0;
	float count = left ? 8.0 : 9.0;
	float index_on_side = floor((pixel.x - start) / pitch);
	vec2 bolt = vec2(500.0);
	if (index_on_side >= 0.0 && index_on_side < count) {
		float x = start + pitch * (index_on_side + 0.5) + 2.1 * sin(index_on_side * 2.4);
		float row = mod(index_on_side * 2.0 + (left ? 0.0 : 1.0), 3.0);
		bolt = (pixel - vec2(x, electrical_wave_y(x, row))) * 3.0;
	}
	float clear_space = 1.0 - smoothstep(6.0, 12.0, length(bolt * vec2(1.0, 0.62)));
	for (int index = 0; index < 3; index++) {
		float distance = abs(pixel.y - electrical_wave_y(pixel.x, float(index)));
		float glow = (1.0 - smoothstep(0.6, 3.1, distance)) * 0.15;
		float current = 1.0 - smoothstep(0.3, 1.25, distance);
		water = mix(water, vec3(0.34, 0.84, 0.77), (glow + 0.66 * current) * (1.0 - 0.84 * clear_space));
	}
	float flash = max(trace(bolt, vec2(3.5, -9.0), vec2(-3.5, 0.0), 2.5),
		max(trace(bolt, vec2(-3.5, 0.0), vec2(3.5, -1.0), 2.2),
			trace(bolt, vec2(3.5, -1.0), vec2(-2.5, 9.0), 2.4)));
	return mix(water, vec3(1.0, 0.79, 0.38), flash);
}

void fragment() {
	vec2 p = UV;
	vec2 pixel = p * 500.0;
	float surface = surface_y(pixel.x);
	float depth_below_swell = pixel.y - surface;
	vec3 tint = distant_water(pixel, windy_sky(p));
	if (depth_below_swell > -1.0) {
		float depth = (p.y - 0.5) * 2.0;
		vec3 water = mix(vec3(0.236, 0.455, 0.47), vec3(0.057, 0.162, 0.206), smoothstep(0.0, 0.98, depth));
		water = surface_water(pixel, surface, depth_below_swell, water);
		if (show_technology) {
			water = circuitry(pixel, water);
			water = electricity(pixel, water);
			water = atoms_and_molecules(pixel, water);
		}
		tint = mix(tint, water, smoothstep(-1.0, 1.0, depth_below_swell));
	}
	ALBEDO = tint;
}
