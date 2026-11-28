shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform vec2 wind_origin;
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

float rolling_crest(float delta, float front, float back) {
	float spread = delta / (delta < 0.0 ? front : back);
	return exp(-spread * spread);
}

float surface_swell(float x) {
	// The floating letters follow this profile in iceberg.gd.
	return 11.0 + 4.5 * sin(x * 0.041 + 0.4)
		- 46.0 * rolling_crest(x - 74.0, 36.0, 17.0)
		- 15.0 * rolling_crest(x - 141.0, 23.0, 40.0)
		- 57.0 * rolling_crest(x - 421.0, 21.0, 49.0)
		- 13.0 * rolling_crest(x - 488.0, 16.0, 30.0);
}

vec3 distant_water(vec2 pixel, vec3 sky) {
	float horizon = 242.0 + 2.8 * sin(pixel.x * 0.041 + 0.48);
	float depth = pixel.y - horizon;
	float seen = smoothstep(-1.1, 0.9, depth);
	float reflected_light = 1.0 - smoothstep(0.0, 8.0, depth);
	vec3 mist = mix(vec3(0.24, 0.45, 0.47), vec3(0.48, 0.61, 0.61), reflected_light);
	return mix(sky, mist, seen);
}

vec3 surface_water(vec2 pixel, float swell, float depth, vec3 water) {
	float crest = 1.0 - smoothstep(-43.0, 3.0, swell);
	float slope = surface_swell(pixel.x + 1.0) - swell;
	float front = 1.0 - smoothstep(-0.85, 0.57, slope);
	float face = 1.0 - smoothstep(1.0, 27.0, depth);
	vec3 glass = mix(vec3(0.13, 0.37, 0.43), vec3(0.22, 0.54, 0.56), crest);
	water = mix(water, glass, face * 0.84);

	float rim = (1.0 - smoothstep(0.40, 2.7, abs(depth))) * (0.15 + 0.80 * crest);
	float trough = 4.5 + 7.2 * crest + 4.4 * front;
	float wake = (1.0 - smoothstep(0.20, 1.65, abs(depth - trough))) * crest * (0.10 + 0.38 * front);
	return mix(water, vec3(0.78, 0.92, 0.87), rim + wake);
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
	float swell = surface_swell(pixel.x);
	float depth_below_swell = pixel.y - 250.0 - swell;
	vec3 tint = distant_water(pixel, windy_sky(p));
	if (depth_below_swell > -1.0) {
		float depth = (p.y - 0.5) * 2.0;
		vec3 water = mix(vec3(0.236, 0.455, 0.47), vec3(0.057, 0.162, 0.206), smoothstep(0.0, 0.98, depth));
		water = surface_water(pixel, swell, depth_below_swell, water);
		if (show_technology) {
			water = circuitry(pixel, water);
			water = electricity(pixel, water);
			water = atoms_and_molecules(pixel, water);
		}
		tint = mix(tint, water, smoothstep(-1.0, 1.0, depth_below_swell));
	}
	ALBEDO = tint;
}
