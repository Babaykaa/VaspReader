#version 460

in vec3 Position;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;

struct Light{
    vec4 Position;
    vec3 Intensity;
    int Enabled;
};
uniform Light lights[8];

uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Shininess;

uniform sampler2D textureMap;
uniform int isTextureExist;

layout (location=0) out vec4 FragColor;


vec3 ads(int lightIndex)
{
    if (lights[lightIndex].Enabled == 0)
        return vec3(0.0);
    else
    {
        vec3 n = normalize(Normal);
        vec3 s = normalize(vec3(lights[lightIndex].Position.xyz - Position));
        vec3 v = normalize(-Position);
        vec3 h = normalize(v + s);
        vec3 I = lights[lightIndex].Intensity;
        return I * (Ka + Kd * max(dot(s, n), 0.0) + Ks * pow(max(dot(h, n), 0.0), Shininess)) * Color;
    }
}


vec3 customModel(int lightIndex)
{
    if (lights[lightIndex].Enabled == 0)
        return vec3(0.0);
    else
    {
        vec3 n = normalize(Normal);
        vec3 s = normalize(vec3(lights[lightIndex].Position.xyz - Position));
        float sDotN = max(dot(s, n), 0.0);
        vec3 I = lights[lightIndex].Intensity;
        return I * Color * (Ka + Kd * sDotN + Ks * pow(sDotN, Shininess));
    }
}


void main() {
    vec3 ResColor = vec3(0.0);
    
    for (int i = 0; i < 8; i++)
        ResColor += customModel(i);

    vec4 textureData = texture(textureMap, TexCoord);
    FragColor = vec4(ResColor, 1.0);

    if (isTextureExist != 0) {
        FragColor = mix(FragColor, textureData, 0.5);
    }
}
