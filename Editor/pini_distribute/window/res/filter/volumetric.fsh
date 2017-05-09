#ifdef GL_ES
precision mediump float;
#endif

varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;

vec3 resolution = vec3(1.0,1.0,1.0); // screen resolution

void main() 
{
    vec4 color = texture2D(CC_Texture0,v_texCoord);
    float power = 1.0 - 0.005*threshold;

    vec3 p = vec3(v_texCoord.xy,0.0)/resolution-0.5;
    vec2 c = 0.5+(p.xy*=power);
    vec4 cc = texture2D(CC_Texture0,c);
    vec3 o = cc.rbb * color.a;
    for (float i=0.0;i<30.0;i++){
        c = 0.5+(p.xy*=power);
        cc = texture2D(CC_Texture0,c);
        p.z += pow(max(0.0,0.5-length(cc.rgb* color.a)),2.0)*exp(-i*0.08);
    }
    
    gl_FragColor = vec4(o*o+p.z,1.0);
    
    float r = (1.0-threshold)*color.r + threshold * gl_FragColor.r;
    float g = (1.0-threshold)*color.g + threshold * gl_FragColor.g;
    float b = (1.0-threshold)*color.b + threshold * gl_FragColor.b;

    gl_FragColor = vec4(r,g,b,v_fragmentColor.a);
}