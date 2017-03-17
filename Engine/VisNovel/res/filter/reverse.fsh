#ifdef GL_ES
precision mediump float;
#endif
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;

void main(void)
{
    vec4 color = texture2D(CC_Texture0, v_texCoord);
    
    float r = (1.0-threshold)*color.r + threshold*(1.0-color.r);
    float g = (1.0-threshold)*color.g + threshold*(1.0-color.g);
    float b = (1.0-threshold)*color.b + threshold*(1.0-color.b);

    gl_FragColor = vec4(r,g,b,color.a * v_fragmentColor.a);
}
