#ifdef GL_ES
precision mediump float;
#endif
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;
uniform float pixelsNum; 


#define KERNEL_SIZE 9
vec2 texCoords[KERNEL_SIZE]; //stores texture lookup offsets from a base case

float tolerance = 0.3; 
float pixelRadius = 0.6; 

int luminanceSteps = 10; 
float luminanceBoost = 0.0;

vec4 applyLuminanceStepping(in vec4 color)
{
     float sum = color.r + color.g + color.b;
     float luminance = sum/3.0; 
     
     vec3 ratios = vec3(color.r/luminance, color.g/luminance, color.b/luminance); 

     float luminanceStep = 1.0/float(luminanceSteps);
     float luminanceBin = ceil(luminance/luminanceStep);     
     float luminanceFactor = luminanceStep * luminanceBin + luminanceBoost; 

     return vec4(ratios * luminanceFactor,1.0); 
}

void main(void)
{
    vec4 avgColor;
    
    vec2 texCoordsStep = vec2( (1.0/pixelsNum) * threshold,(1.0/pixelsNum) * threshold);
    vec2 pixelBin = floor(v_texCoord.st/texCoordsStep); 
    
    vec2 inPixelStep = texCoordsStep/3.0; 
    vec2 inPixelHalfStep = inPixelStep/2.0;

    vec2 pixelRegionCoords = fract(v_texCoord.st/texCoordsStep);

    vec2 offset = pixelBin * texCoordsStep;
    
    texCoords[0] = vec2(inPixelHalfStep.x                       , inPixelStep.y*2.0 + inPixelHalfStep.y) + offset;
    texCoords[1] = vec2(inPixelStep.x + inPixelHalfStep.x       , inPixelStep.y*2.0 + inPixelHalfStep.y) + offset;
    texCoords[2] = vec2(inPixelStep.x*2.0 + inPixelHalfStep.x   , inPixelStep.y*2.0 + inPixelHalfStep.y) + offset;
    texCoords[3] = vec2(inPixelHalfStep.x                       , inPixelStep.y + inPixelHalfStep.y) + offset;
    texCoords[4] = vec2(inPixelStep.x + inPixelHalfStep.x       , inPixelStep.y + inPixelHalfStep.y) + offset;
    texCoords[5] = vec2(inPixelStep.x*2.0 + inPixelHalfStep.x   , inPixelStep.y + inPixelHalfStep.y) + offset;
    texCoords[6] = vec2(inPixelHalfStep.x                       , inPixelHalfStep.y) + offset;
    texCoords[7] = vec2(inPixelStep.x + inPixelHalfStep.x       , inPixelHalfStep.y) + offset;
    texCoords[8] = vec2(inPixelStep.x*2.0 + inPixelHalfStep.x   , inPixelHalfStep.y) + offset;

    avgColor = texture2D(CC_Texture0, texCoords[0]) +
                    texture2D(CC_Texture0, texCoords[1]) +
                    texture2D(CC_Texture0, texCoords[2]) +
                    texture2D(CC_Texture0, texCoords[3]) +
                    texture2D(CC_Texture0, texCoords[4]) +
                    texture2D(CC_Texture0, texCoords[5]) +
                    texture2D(CC_Texture0, texCoords[6]) +
                    texture2D(CC_Texture0, texCoords[7]) +
                    texture2D(CC_Texture0, texCoords[8]);

    avgColor /= float(KERNEL_SIZE);

    avgColor = applyLuminanceStepping(avgColor);

    vec2 powers = pow(abs(pixelRegionCoords - 0.5),vec2(2.0));
    float radiusSqrd = pow(pixelRadius,2.0);
    float gradient = smoothstep(radiusSqrd-tolerance, radiusSqrd+tolerance, powers.x+powers.y);

    gl_FragColor = mix(avgColor, vec4(0.1,0.1,0.1,1.0), gradient);
    gl_FragColor *= vec4(1.0,1.0,1.0,v_fragmentColor.a);
}
