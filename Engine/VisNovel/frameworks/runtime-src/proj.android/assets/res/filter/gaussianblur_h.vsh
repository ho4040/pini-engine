attribute vec4 a_position;
attribute vec2 a_texCoord;
attribute vec4 a_color;

#ifdef GL_ES
varying lowp vec4 v_fragmentColor;
varying mediump vec2 v_texCoord;
varying mediump vec2 v_blurTexCoords[14];
#else
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;
varying vec2 v_blurTexCoords[14];
#endif

uniform float threshold;
uniform float power;
//0~1;

void main()
{
    gl_Position = CC_PMatrix * a_position;
    v_fragmentColor = a_color;
    v_texCoord = a_texCoord;

    float dt = (power / 2.0) - power;
    float s = power / 14.0;
    v_blurTexCoords[ 0] = v_texCoord + vec2((dt+s* 0.0)*threshold, 0.0 );
    v_blurTexCoords[ 1] = v_texCoord + vec2((dt+s* 1.0)*threshold, 0.0 );
    v_blurTexCoords[ 2] = v_texCoord + vec2((dt+s* 2.0)*threshold, 0.0 );
    v_blurTexCoords[ 3] = v_texCoord + vec2((dt+s* 3.0)*threshold, 0.0 );
    v_blurTexCoords[ 4] = v_texCoord + vec2((dt+s* 4.0)*threshold, 0.0 );
    v_blurTexCoords[ 5] = v_texCoord + vec2((dt+s* 5.0)*threshold, 0.0 );
    v_blurTexCoords[ 6] = v_texCoord + vec2((dt+s* 6.0)*threshold, 0.0 );
    v_blurTexCoords[ 7] = v_texCoord + vec2((dt+s* 7.0)*threshold, 0.0 );
    v_blurTexCoords[ 8] = v_texCoord + vec2((dt+s* 8.0)*threshold, 0.0 );
    v_blurTexCoords[ 9] = v_texCoord + vec2((dt+s* 9.0)*threshold, 0.0 );
    v_blurTexCoords[10] = v_texCoord + vec2((dt+s*10.0)*threshold, 0.0 );
    v_blurTexCoords[11] = v_texCoord + vec2((dt+s*11.0)*threshold, 0.0 );
    v_blurTexCoords[12] = v_texCoord + vec2((dt+s*12.0)*threshold, 0.0 );
    v_blurTexCoords[13] = v_texCoord + vec2((dt+s*13.0)*threshold, 0.0 );
}
