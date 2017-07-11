#ifdef GL_ES
precision mediump float;
#endif
varying vec4 v_fragmentColor;
varying vec2 v_texCoord;

uniform float threshold;
uniform float power;

void main()
{
	vec4 color = texture2D(CC_Texture0, v_texCoord);
	vec4 sum = vec4(0.0);
	vec2 texcoord = vec2(v_texCoord);
	float j;
	float i;

	for( i= -4.0 ;i < 4.0; i++)
	{
		for (j = -3.0; j < 3.0; j++)
		{
			sum += texture2D(CC_Texture0, texcoord + vec2(j, i)*0.004) * 0.25;
		}
	}
	for( i = 1.0; i<15.0;i++){
		float d = i/15.0;
		if (color.r < d || i >= 14.0)
		{
			gl_FragColor = sum*sum*0.005*(1.0/i)*power + color;
			break;
		}
	}

	float r = (1.0-threshold)*color.r + threshold*gl_FragColor.r;
	float g = (1.0-threshold)*color.g + threshold*gl_FragColor.g;
	float b = (1.0-threshold)*color.b + threshold*gl_FragColor.b;

	gl_FragColor = vec4(r,g,b,v_fragmentColor.a);
}
