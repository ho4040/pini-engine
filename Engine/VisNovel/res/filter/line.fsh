#ifdef GL_ES
precision mediump float;
#endif
 
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;

void main()
{
    vec4 color = texture2D(CC_Texture0, v_texCoord);
    float lum = length(color.rgb);
     
    vec4 c = vec4(1.0, 1.0, 1.0, 1.0);
     
    if (lum < 1.00*threshold) {
        if (mod(gl_FragCoord.x + gl_FragCoord.y, 10.0) == 0.0) {
            c = vec4(0.0, 0.0, 0.0, color.a);
        }
    }
     
    if (lum < 0.75*threshold) {
        if (mod(gl_FragCoord.x - gl_FragCoord.y, 10.0) == 0.0) {
            c = vec4(0.0, 0.0, 0.0, color.a);
        }
    }
     
    if (lum < 0.50*threshold) {
        if (mod(gl_FragCoord.x + gl_FragCoord.y - 5.0, 10.0) == 0.0) {
            c = vec4(0.0, 0.0, 0.0, color.a);
        }
    }
     
    if (lum < 0.3*threshold) {
        if (mod(gl_FragCoord.x - gl_FragCoord.y - 5.0, 10.0) == 0.0) {
            c = vec4(0.0, 0.0, 0.0, color.a);
        }
    }

    float r = (1.0-threshold)*color.r + threshold*c.r;
    float g = (1.0-threshold)*color.g + threshold*c.g;
    float b = (1.0-threshold)*color.b + threshold*c.b;

    gl_FragColor = vec4(r,g,b,color.a);
    gl_FragColor *= vec4(1.0,1.0,1.0,v_fragmentColor.a);
}