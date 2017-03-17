#ifdef GL_ES
precision mediump float;
#endif
 
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;
uniform float nums;

float rand(vec2 n)
{
	return 0.5 + 0.5 * fract(sin(dot(n.xy, vec2(12.9898, 78.233)))* 43758.5453);
}

void main(void)
{
	vec2 v = vec2(float(int(v_texCoord.x*nums))/nums,float(int(v_texCoord.y*nums))/nums);
	float x = rand(v.xy+threshold-threshold*threshold);
	vec4 color = texture2D(CC_Texture0, v_texCoord);

	vec3 noise = vec3(color.r*x,color.g*x,color.b*x);

	//float r = (1.0-threshold)*color.r + threshold*noise.r;
	//float g = (1.0-threshold)*color.g + threshold*noise.g;
	//float b = (1.0-threshold)*color.b + threshold*noise.b;

    gl_FragColor = vec4(noise,color.a * v_fragmentColor.a);
}