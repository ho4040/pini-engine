#ifdef GL_ES
precision mediump float;
#endif
 
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;

uniform float pixel; // 15.0

void main() 
{ 
    vec4 color = texture2D(CC_Texture0, v_texCoord);
    vec2 uv = v_texCoord.xy;
    vec3 tc = vec3(1.0, 0.0, 0.0);
    float d = pixel * threshold;
    vec2 coord = vec2(d*floor(uv.x/d), d*floor(uv.y/d));
    tc = texture2D(CC_Texture0, coord).rgb;

    float r = (1.0-threshold)*color.r + threshold*tc.r;
    float g = (1.0-threshold)*color.g + threshold*tc.g;
    float b = (1.0-threshold)*color.b + threshold*tc.b;

    gl_FragColor = vec4(r,g,b,color.a * v_fragmentColor.a);
}