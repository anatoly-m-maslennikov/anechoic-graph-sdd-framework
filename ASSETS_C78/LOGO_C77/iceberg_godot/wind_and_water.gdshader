shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform vec2 wind_origin;

float grain(vec2 cell) {
	return fract(sin(dot(cell, vec2(127.1, 311.7))) * 43758.5453);
}

float surface_flecks(vec2 pixel) {
	vec2 grid = pixel / 5.0;
	vec2 cell = floor(grid);
	vec2 size = mix(vec2(0.17, 0.14), vec2(0.89, 0.72), vec2(grain(cell + 8.0), grain(cell - 12.0)));
	vec2 offset = (1.0 - size) * vec2(grain(cell - 4.0), grain(cell + 31.0));
	vec2 corner = step(offset, fract(grid)) * (1.0 - step(offset + size, fract(grid)));
	return corner.x * corner.y * smoothstep(0.28, 0.96, grain(cell));
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

vec3 circuit_rows(vec2 pixel, vec3 water) {
	float row_top = 329.0;
	for (int index = 0; index < 10; index++) {
		float row = float(index);
		float size = floor(7.5 + row * 1.24);
		float stride = size + 3.0;
		float x = pixel.x - 15.0;
		float bank = floor(x / 118.0);
		float local_x = mod(x, 118.0);
		float column = floor(local_x / stride);
		float cell_x = mod(local_x, stride);
		float gap = pixel.y - row_top;
		if (gap >= 0.0 && gap < size && cell_x < size && local_x < 108.0) {
			float chip = 1.0 - step(2.0, abs(column - floor(48.0 / stride)));
			float lanes = 1.0 - step(3.0, mod(column, 5.0));
			float die = mix(lanes, chip, smoothstep(4.0, 8.0, row));
			float bright = 0.17 + 0.4 * die + 0.12 * grain(vec2(bank + row, column));
			vec3 metal = mix(vec3(0.19, 0.61, 0.64), vec3(0.54, 0.79, 0.73), chip);
			return mix(water, metal, bright);
		}
		row_top += size + 4.0;
	}
	return water;
}

void fragment() {
	vec2 p = UV;
	vec3 tint;
	if (p.y < 0.5) {
		vec3 ivory = vec3(0.961, 0.922, 0.851);
		vec3 mist = vec3(0.766, 0.848, 0.812);
		tint = mix(ivory, mist, smoothstep(0.18, 0.52, p.y));
		for (int i = 0; i < 11; i++) {
			float lane = float(i);
			float dx = p.x - wind_origin.x;
			float edge = mix(wind_origin.x, 1.0 - wind_origin.x, step(0.0, dx));
			float travel = abs(dx) / edge;
			float destination = 0.012 + lane * 0.048 + 0.026 * sin(dx * 6.0 + lane);
			float y = mix(wind_origin.y, destination, pow(travel, 0.75))
				+ 0.037 * travel * sin(travel * 8.0 + lane * 0.59 + sign(dx));
			float ends = smoothstep(0.018, 0.10, travel) * (1.0 - smoothstep(0.89, 1.05, travel));
			float ribbon = 1.0 - smoothstep(0.0008, 0.0029, abs(p.y - y));
			vec3 vapor = mix(vec3(0.56, 0.71, 0.66), vec3(0.99, 0.99, 0.94), mod(lane, 2.0));
			tint = mix(tint, vapor, ribbon * ends * 0.34);
		}
	} else {
		float depth = (p.y - 0.5) * 2.0;
		tint = mix(vec3(0.211, 0.424, 0.468), vec3(0.059, 0.174, 0.248), smoothstep(0.0, 0.95, depth));
		vec2 pixel = p * 500.0;
		float near_surface = 1.0 - smoothstep(0.18, 0.38, depth);
		float flecks = surface_flecks(pixel);
		vec3 signal = mix(vec3(0.35, 0.77, 0.73), vec3(0.94, 0.72, 0.44),
			step(0.97, grain(floor(pixel / 5.0) + 21.0)));
		tint = mix(tint, signal, 0.53 * flecks * near_surface);
		tint = mix(tint, vec3(0.60, 0.87, 0.79), 0.59 * application_signals(pixel));
		tint = circuit_rows(pixel, tint);
	}
	float surface = 1.0 - smoothstep(0.0007, 0.004, abs(p.y - 0.5));
	ALBEDO = mix(tint, vec3(0.867, 0.974, 0.914), surface * 0.90);
}
