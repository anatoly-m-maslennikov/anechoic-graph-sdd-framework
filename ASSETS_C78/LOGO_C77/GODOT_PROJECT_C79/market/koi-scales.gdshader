shader_type spatial;

uniform vec4 body_color : source_color = vec4(0.925, 0.396, 0.173, 1.0);

varying vec3 body_point;
varying vec3 body_normal;

void vertex() {
	body_point = VERTEX;
	body_normal = NORMAL;
}

void fragment() {
	// Stagger the crescent edges across the sides of the faceted body.
	float row = body_point.y / 0.095;
	float column = body_point.z / 0.078 + mod(floor(row), 2.0) * 0.5;
	vec2 cell = fract(vec2(column, row)) - vec2(0.5);
	float arc = length(vec2((cell.x + 0.19) * 0.91, cell.y));
	float width = max(0.042, fwidth(arc) * 0.76);
	float edge = 1.0 - smoothstep(width, width * 2.0, abs(arc - 0.42));
	edge *= smoothstep(-0.18, 0.0, cell.x);
	float flank = smoothstep(0.32, 0.67, abs(normalize(body_normal).x));
	flank *= 1.0 - smoothstep(0.22, 0.35, abs(body_point.y + 0.023));
	ALBEDO = mix(body_color.rgb, body_color.rgb * vec3(0.62, 0.48, 0.40), edge * flank * 0.87);
	ROUGHNESS = 0.78;
}
