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
		+ gust(p, wind_origin + vec2(0.07, -0.025), 0.93, 0.037, 0.11, 0.0035);
	return mix(tint, vec3(0.66, 0.77, 0.71), clamp(wind * 0.61, 0.0, 1.0));
}

float surface_flecks(vec2 pixel) {
	vec2 grid = pixel / 6.0;
	vec2 cell = floor(grid);
	vec2 size = mix(vec2(0.14, 0.13), vec2(0.75, 0.49), vec2(grain(cell + 8.0), grain(cell - 12.0)));
	vec2 offset = (1.0 - size) * vec2(grain(cell - 4.0), grain(cell + 31.0));
	vec2 corner = step(offset, fract(grid)) * (1.0 - step(offset + size, fract(grid)));
	float current = 0.5 + 0.5 * sin(pixel.x * 0.065 + pixel.y * 0.22);
	return corner.x * corner.y * smoothstep(0.44, 0.96, grain(cell)) * mix(0.24, 1.0, current);
}

float application_signals(vec2 pixel) {
	vec2 panel = floor((pixel - vec2(53.0, 268.0)) / 3.0);
	vec2 inside = step(vec2(0.0), panel) * (1.0 - step(vec2(15.0, 9.0), panel));
	float edge = max(max(1.0 - step(1.0, panel.x), step(14.0, panel.x)),
		max(1.0 - step(2.0, panel.y), step(8.0, panel.y)));
	float list = float(panel.x >= 3.0 && panel.x < 12.0 && (panel.y == 4.0 || panel.y == 6.0));
	vec2 network = floor((pixel - vec2(403.0, 285.0)) / 3.0);
	float sides = float((network.x == 0.0 || network.x == 12.0)
		&& (network.y == 0.0 || network.y == 4.0 || network.y == 8.0));
	float middle = float(network.x == 6.0 && (network.y == 2.0 || network.y == 6.0));
	float slope = 2.0 - abs(network.x - 6.0) / 3.0;
	float lines = min(min(abs(network.y - slope), abs(network.y - 4.0 + slope)),
		min(abs(network.y - 4.0 - slope), abs(network.y - 8.0 + slope)));
	float links = float(network.x > 0.0 && network.x < 12.0
		&& lines < 0.4);
	return max(inside.x * inside.y * max(edge * 0.36, list * 0.46), max(sides + middle, links * 0.37));
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
	float wiring = trace(pixel, vec2(22.0, 382.0), vec2(53.0, 382.0), 1.3)
		+ trace(pixel, vec2(53.0, 382.0), vec2(68.0, 397.0), 1.3)
		+ trace(pixel, vec2(76.0, 434.0), vec2(96.0, 454.0), 1.3)
		+ trace(pixel, vec2(96.0, 454.0), vec2(155.0, 454.0), 1.3)
		+ trace(pixel, vec2(370.0, 419.0), vec2(387.0, 402.0), 1.3)
		+ trace(pixel, vec2(387.0, 402.0), vec2(406.0, 402.0), 1.3)
		+ trace(pixel, vec2(454.0, 403.0), vec2(490.0, 403.0), 1.3)
		+ trace(pixel, vec2(430.0, 412.0), vec2(430.0, 438.0), 1.3);
	float circuits = max(chip(pixel - vec2(72.0, 416.0), vec2(15.0)),
		chip(pixel - vec2(430.0, 402.0), vec2(24.0, 11.0)));
	water = mix(water, vec3(0.33, 0.62, 0.59), clamp(circuits + 0.42 * wiring, 0.0, 1.0));
	float row_top = 350.0;
	for (int index = 0; index < 7; index++) {
		float row = float(index);
		float size = floor(5.5 + row * 1.25);
		float stride = size + 5.0;
		float bank = step(250.0, pixel.x);
		float origin = mix(27.0 + mod(row, 3.0) * 9.0, 391.0 - mod(row + 1.0, 3.0) * 12.0, bank);
		float x = pixel.x - origin;
		float column = floor(x / stride);
		float cell_x = mod(x, stride);
		float gap = pixel.y - row_top;
		if (gap >= 0.0 && gap < size && cell_x < size && column >= 0.0 && column < 6.0) {
			vec2 center = vec2(origin + column * stride + size * 0.5, row_top + size * 0.5);
			vec2 clearance = abs(center - mix(vec2(72.0, 416.0), vec2(430.0, 402.0), bank));
			float around_chip = step(35.0, clearance.x) + step(29.0, clearance.y);
			float signal = grain(vec2(row + bank * 10.0, column + 18.0));
			vec3 metal = mix(vec3(0.30, 0.62, 0.62), vec3(0.75, 0.63, 0.40), step(0.94, signal));
			return mix(water, metal, step(1.0, around_chip) * smoothstep(0.33, 1.0, signal) * 0.55);
		}
		row_top += size + 11.0;
	}
	return water;
}

void fragment() {
	vec2 p = UV;
	vec3 tint;
	if (p.y < 0.5) {
		tint = windy_sky(p);
	} else {
		float depth = (p.y - 0.5) * 2.0;
		tint = mix(vec3(0.236, 0.455, 0.47), vec3(0.057, 0.162, 0.206), smoothstep(0.0, 0.98, depth));
		vec2 pixel = p * 500.0;
		float near_surface = 1.0 - smoothstep(0.10, 0.33, depth);
		float flecks = surface_flecks(pixel);
		vec3 signal = mix(vec3(0.35, 0.77, 0.73), vec3(0.94, 0.72, 0.44),
			step(0.97, grain(floor(pixel / 5.0) + 21.0)));
		tint = mix(tint, signal, 0.64 * flecks * near_surface);
		tint = mix(tint, vec3(0.59, 0.79, 0.73), 0.48 * application_signals(pixel));
		tint = circuitry(pixel, tint);
	}
	float surface = 1.0 - smoothstep(0.0007, 0.004, abs(p.y - 0.5));
	ALBEDO = mix(tint, vec3(0.867, 0.974, 0.914), surface * 0.90);
}
