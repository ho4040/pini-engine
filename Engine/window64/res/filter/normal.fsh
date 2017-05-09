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
    gl_FragColor = vec4(color * v_fragmentColor);
}