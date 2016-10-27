#ifdef GL_ES
precision mediump float;
#endif
 
const vec3 SEPIA = vec3(1.2, 1.0, 0.8); 

varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;

void main(void)
{
	vec4 color = texture2D(CC_Texture0, v_texCoord);
	float gray = dot(vec3(color.r,color.g,color.b), vec3(0.299, 0.587, 0.114));

	vec3 gcolor = vec3(gray,gray,gray) * SEPIA;

	float r = (1.0-threshold)*color.r + threshold * gcolor.r;
	float g = (1.0-threshold)*color.g + threshold * gcolor.g;
	float b = (1.0-threshold)*color.b + threshold * gcolor.b;

    gl_FragColor = vec4(vec3(r,g,b),color.a * v_fragmentColor.a);
}