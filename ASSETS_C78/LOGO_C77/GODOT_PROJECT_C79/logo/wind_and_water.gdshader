shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform vec2 wind_origin;

float grain(vec2 cell) {
	return fract(sin(dot(cell, vec2(127.1, 311.7))) * 43758.5453);
}

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

float surface_swell(float x) {
	// The floating letters follow this profile in iceberg.gd.
	float phase = x * 0.078 + 0.73 * sin(x * 0.027);
	float height = 10.0 + 3.8 * sin(x * 0.041 + 1.1);
	return height * sin(phase) + 3.5 * cos(phase * 2.0 + 0.95) + 1.0 * sin(x * 0.29);
}

vec3 surface_water(vec2 pixel, float swell, float depth, vec3 water) {
	float crest = 1.0 - smoothstep(-13.0, -3.0, swell);
	float transmission = 1.0 - smoothstep(0.0, 23.0, depth);
	water = mix(water, vec3(0.26, 0.67, 0.64), transmission * (0.24 + crest * 0.35));

	float foam_edge = 1.0 - smoothstep(0.45, 1.3 + 2.7 * crest, abs(depth));
	float patches = smoothstep(-0.25, 0.78, sin(pixel.x * 0.16) + 0.6 * sin(pixel.x * 0.39));
	float whitecap = (1.0 - smoothstep(0.9, 5.5, depth)) * smoothstep(0.45, 0.9, crest + 0.24 * patches);
	float trail = 6.7 + 1.4 * sin(pixel.x * 0.38);
	float broken_foam = 1.0 - smoothstep(0.2, 1.55, abs(depth - trail));
	float foam = foam_edge * (0.26 + 0.68 * crest) + 0.52 * whitecap + broken_foam * patches * crest * 0.6;
	return mix(water, vec3(0.91, 0.99, 0.94), clamp(foam, 0.0, 1.0));
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
	float ring = abs(length(point / vec2(10.0, 4.0)) - 1.0);
	return 1.0 - smoothstep(0.07, 0.21, ring);
}

vec3 atoms(vec2 pixel, vec3 water) {
	vec2 grid = (pixel - vec2(0.0, 454.0)) / vec2(34.0, 23.0);
	float row = floor(grid.y);
	if (row < 0.0 || row >= 2.0) {
		return water;
	}
	grid.x += mod(row, 2.0) * 0.5;
	vec2 point = (fract(grid) - 0.5) * vec2(34.0, 23.0);
	float orbits = max(atom_orbit(point), max(
		atom_orbit(mat2(vec2(0.5, 0.866), vec2(-0.866, 0.5)) * point),
		atom_orbit(mat2(vec2(0.5, -0.866), vec2(0.866, 0.5)) * point)));
	float nucleus = 1.0 - smoothstep(1.5, 2.5, length(point));
	float brightness = mix(0.46, 0.79, grain(floor(grid)));
	water = mix(water, vec3(0.34, 0.63, 0.63), orbits * brightness);
	return mix(water, vec3(0.98, 0.77, 0.46), nucleus * brightness);
}

vec3 electricity(vec2 pixel, vec3 water) {
	float wave = 6.0 * sin(pixel.x * 0.085);
	float distance = abs(pixel.y - 438.0 - wave);
	float glow = (1.0 - smoothstep(1.0, 5.0, distance)) * 0.24;
	float current = 1.0 - smoothstep(0.55, 1.65, distance);
	water = mix(water, vec3(0.19, 0.77, 0.72), glow);
	return mix(water, vec3(0.49, 0.94, 0.85), current * 0.75);
}

void fragment() {
	vec2 p = UV;
	vec2 pixel = p * 500.0;
	float swell = surface_swell(pixel.x);
	float depth_below_swell = pixel.y - 250.0 - swell;
	vec3 tint = windy_sky(p);
	if (depth_below_swell > -1.0) {
		float depth = (p.y - 0.5) * 2.0;
		vec3 water = mix(vec3(0.236, 0.455, 0.47), vec3(0.057, 0.162, 0.206), smoothstep(0.0, 0.98, depth));
		water = surface_water(pixel, swell, depth_below_swell, water);
		water = circuitry(pixel, water);
		water = electricity(pixel, water);
		water = atoms(pixel, water);
		tint = mix(tint, water, smoothstep(-1.0, 1.0, depth_below_swell));
	}
	ALBEDO = tint;
}
