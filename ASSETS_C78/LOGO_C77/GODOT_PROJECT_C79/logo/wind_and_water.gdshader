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

float surface_waves(vec2 pixel) {
	// The floating letters follow the same swell in iceberg.gd.
	float x = pixel.x;
	float swell = 5.0 * sin(x * 0.066) + 2.8 * sin(x * 0.16 + 0.8) + 1.5 * sin(x * 0.33);
	float backwash = 3.7 * sin(x * 0.096 + 1.7) - 2.6 * sin(x * 0.22);
	float crest = 1.0 - smoothstep(0.45, 1.65, abs(pixel.y - 265.0 - swell));
	float wake = 1.0 - smoothstep(0.35, 1.45, abs(pixel.y - 277.0 - backwash));
	float tail = 1.0 - smoothstep(0.3, 1.25, abs(pixel.y - 284.0 - swell * 0.55));
	float gaps = smoothstep(-0.5, 0.7, sin(x * 0.19) + 0.6 * sin(x * 0.41));
	return clamp(0.55 * crest + 0.49 * wake + 0.42 * gaps * tail, 0.0, 1.0);
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

vec3 building_blocks(vec2 pixel, vec3 water) {
	vec2 grid = (pixel - vec2(4.0, 420.0)) / 16.0;
	float row = floor(grid.y);
	if (row < 0.0 || row >= 3.0) {
		return water;
	}
	grid.x += mod(row, 2.0) * 0.5;
	float signal = grain(floor(grid));
	vec2 block = (fract(grid) - 0.5) * 16.0;
	float face = box(block, vec2(6.6));
	float bevel = box(block + vec2(1.0), vec2(5.4));
	vec3 ink = mix(vec3(0.21, 0.44, 0.46), vec3(0.43, 0.65, 0.58), signal);
	return mix(water, ink, face * (0.4 + 0.3 * bevel));
}

vec3 electricity(vec2 pixel, vec3 water) {
	float phase = pixel.x * 0.088;
	float wave = 6.0 * sin(phase) + 2.0 * sin(phase * 2.0);
	float distance = abs(pixel.y - 483.0 - wave);
	float glow = (1.0 - smoothstep(1.0, 6.0, distance)) * 0.27;
	float current = 1.0 - smoothstep(0.6, 2.0, distance);
	float pulse = 1.0 - smoothstep(0.0, 0.15, abs(fract(pixel.x / 58.0) - 0.5));
	vec3 spark = mix(vec3(0.25, 0.78, 0.74), vec3(0.99, 0.78, 0.38), pulse);
	water = mix(water, spark, glow);
	return mix(water, spark, current * 0.74);
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
		tint = mix(tint, vec3(0.47, 0.74, 0.70), surface_waves(pixel));
		tint = circuitry(pixel, tint);
		tint = building_blocks(pixel, tint);
		tint = electricity(pixel, tint);
	}
	float surface = 1.0 - smoothstep(0.0007, 0.004, abs(p.y - 0.5));
	ALBEDO = mix(tint, vec3(0.867, 0.974, 0.914), surface * 0.90);
}
