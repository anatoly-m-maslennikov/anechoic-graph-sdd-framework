shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform sampler2D opening_mask : filter_nearest, repeat_disable;
uniform float view_size;
varying vec3 ice_position;

void vertex() {
	ice_position = VERTEX;
}

void fragment() {
	vec2 section = vec2(ice_position.x, -ice_position.y) / view_size + vec2(0.5);
	float opening = texture(opening_mask, section).r;
	if (opening > 0.5 && ice_position.z > 0.0) {
		discard;
	}
	ALBEDO = mix(COLOR.rgb, vec3(0.10, 0.23, 0.27), opening * 0.82);
}
