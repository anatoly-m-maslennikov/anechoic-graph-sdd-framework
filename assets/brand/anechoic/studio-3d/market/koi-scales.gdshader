shader_type spatial;
render_mode cull_disabled;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D normal_texture : hint_normal, filter_linear_mipmap, repeat_enable;
uniform sampler2D orm_texture : filter_linear_mipmap, repeat_enable;
uniform bool use_normal_texture = false;
uniform bool use_orm_texture = false;

varying vec3 local_position;
varying vec3 local_normal;

void vertex() {
	local_position = VERTEX;
	local_normal = NORMAL;
}

void fragment() {
	vec4 base = texture(albedo_texture, UV) * COLOR;
	vec3 n = normalize(local_normal);
	// Limit the pattern to the flanks, away from the head and tail.
	float flank = smoothstep(0.48, 0.75, abs(n.z));
	flank *= 1.0 - smoothstep(0.62, 0.78, abs(local_position.x));
	flank *= 1.0 - smoothstep(0.22, 0.29, abs(local_position.y));

	// Staggered, open crescents follow the length of the fish.
	float row = floor(local_position.y / 0.105);
	vec2 cell = vec2(local_position.x / 0.13 + mod(row, 2.0) * 0.5, local_position.y / 0.105);
	vec2 q = fract(cell) - vec2(0.5);
	float ring = length(vec2((q.x + 0.20) * 0.86, q.y));
	float width = max(fwidth(ring) * 0.72, 0.035);
	float arc = 1.0 - smoothstep(width, width * 2.2, abs(ring - 0.40));
	arc *= smoothstep(-0.18, 0.02, q.x);
	vec3 bronze = base.rgb * vec3(0.57, 0.49, 0.37);
	vec3 gold = base.rgb * vec3(1.15, 1.10, 0.85);
	ALBEDO = mix(base.rgb, mix(bronze, gold, smoothstep(0.05, 0.40, q.y) * 0.35), arc * flank * 0.65);
	if (use_normal_texture) {
		NORMAL_MAP = texture(normal_texture, UV).rgb;
	}
	if (use_orm_texture) {
		vec3 orm = texture(orm_texture, UV).rgb;
		AO = orm.r;
		ROUGHNESS = orm.g;
		METALLIC = orm.b;
	} else {
		ROUGHNESS = 0.65;
	}
}
