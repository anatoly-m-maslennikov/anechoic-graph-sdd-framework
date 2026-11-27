shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform sampler2D opening_mask : filter_linear, repeat_disable;
uniform float view_size;
uniform float route_strength = 1.0;
varying vec3 ice_position;

void vertex() {
	ice_position = VERTEX;
}

void fragment() {
	vec2 section = vec2(ice_position.x, -ice_position.y) / view_size + vec2(0.5);
	float opening = texture(opening_mask, section).r;
	if (route_strength == 1.0 && opening > 0.5 && ice_position.z > 0.0) {
		discard;
	}
	float ceiling = texture(opening_mask, section - vec2(0.0, 0.007)).r;
	float bevel = max(0.0, ceiling - opening);
	vec3 ice = mix(COLOR.rgb, vec3(0.92, 0.98, 0.91), bevel * 0.24 * route_strength);
	vec3 wall = mix(ice, vec3(0.13, 0.24, 0.26), 0.54 + 0.16 * (1.0 - ceiling));
	ALBEDO = mix(ice, wall, opening * route_strength);
}
