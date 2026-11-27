shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

float grain(vec2 cell) {
	return fract(sin(dot(cell, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec2 p = UV;
	vec3 tint;
	if (p.y < 0.5) {
		vec3 ivory = vec3(0.961, 0.922, 0.851);
		vec3 mist = vec3(0.766, 0.848, 0.812);
		tint = mix(ivory, mist, smoothstep(0.18, 0.52, p.y));
		for (int i = 0; i < 8; i++) {
			float lane = float(i);
			float across = p.x + 0.055 * sin(lane * 3.6);
			float y = 0.246 + lane * 0.027
				+ 0.031 * sin(across * 6.9 + lane * 0.41)
				+ 0.012 * sin(across * 14.0 - lane * 0.22);
			float ends = smoothstep(0.03 + 0.07 * mod(lane, 3.0), 0.23, across)
				* (1.0 - smoothstep(0.72, 0.96 - 0.045 * mod(lane, 3.0), across));
			float ribbon = 1.0 - smoothstep(0.0008, 0.0029, abs(p.y - y));
			vec3 vapor = mix(vec3(0.266, 0.497, 0.461), vec3(0.99, 0.99, 0.94), mod(lane, 2.0));
			tint = mix(tint, vapor, ribbon * ends * 0.48);
		}
	} else {
		float depth = (p.y - 0.5) * 2.0;
		tint = mix(vec3(0.211, 0.424, 0.468), vec3(0.059, 0.174, 0.248), smoothstep(0.0, 0.95, depth));
		vec2 grid = p * vec2(105.0, 143.0);
		vec2 cell = floor(grid);
		float value = grain(cell);
		float line = grain(vec2(floor(grid.x / 5.0), cell.y) + 18.0);
		float burst = grain(vec2(floor(grid.x / 13.0), floor(grid.y / 7.0)));
		float bands = 0.5 + 0.5 * cos(cell.y * 0.34 + floor(cell.x / 7.0) * 0.61);
		float dark_edge = smoothstep(0.04, 0.39, fract(grid.x)) * smoothstep(0.02, 0.19, fract(grid.y));
		float activity = (0.20 + 0.52 * bands) * (0.25 + 0.75 * burst);
		vec3 phosphor = mix(vec3(0.198, 0.588, 0.603), vec3(0.537, 0.831, 0.773), line);
		tint = mix(tint, phosphor, dark_edge * activity * smoothstep(0.48, 0.92, value));
		tint = mix(tint, vec3(0.824, 0.517, 0.308), step(0.991, value) * burst * 0.68);
		tint = mix(tint, vec3(0.37, 0.64, 0.69), step(0.94, line) * burst * 0.28);
	}
	float surface = 1.0 - smoothstep(0.0007, 0.004, abs(p.y - 0.5));
	ALBEDO = mix(tint, vec3(0.867, 0.974, 0.914), surface * 0.90);
}
