#ifdef GL_ES
precision mediump float;
#endif
 
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;

uniform float _r;
uniform float _g;
uniform float _b;

void main(void)
{
	vec4 color = texture2D(CC_Texture0, v_texCoord);

	float r = (1.0-threshold)*color.r + threshold*_r;
	float g = (1.0-threshold)*color.g + threshold*_g;
	float b = (1.0-threshold)*color.b + threshold*_b;

    gl_FragColor = vec4(r,g,b,color.a * v_fragmentColor.a);
}