#version 430

in vec3 Position;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;

struct LightInfo{
    vec4 Position;
    vec3 Intensity;
};
uniform LightInfo lights[8];

struct FogInfo{
    vec4 FogColor;
    float FogMaxDist;
    float FogMinDist;
    float FogDensity;
    int FogPower;
};
uniform FogInfo fog;

uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Shininess;
uniform vec3 EyePosition;

uniform sampler2D textureMap;
uniform int isTextureExist;

layout (location=0) out vec4 FragColor;


float FogSetLinear(vec3 Position, vec3 EyePosition)
{
    float d = distance(EyePosition, Position);
    return 1 - clamp((fog.FogMaxDist - d) / (fog.FogMaxDist - fog.FogMinDist), 0.0, 1.0);
}

float FogSetExp(vec3 Position, vec3 EyePosition)
{
    float d = distance(EyePosition, Position) / 10;
    return 1 - exp(-fog.FogDensity * d);
}

float FogSetExpMod(vec3 Position, vec3 EyePosition)
{
    float d = distance(EyePosition, Position) / 10;
    return 1 - exp(-pow(fog.FogDensity * d, fog.FogPower));
}

vec3 ads(int lightIndex)
{
    vec3 n = normalize(Normal);

    vec3 s;
    if (lights[lightIndex].Position.w == 0.0)
        s = normalize(vec3(lights[lightIndex].Position));
    else
        s = normalize(vec3(lights[lightIndex].Position.xyz - Position));
    vec3 v = normalize(-Position);
    vec3 h = normalize(v + s);
    vec3 I = lights[lightIndex].Intensity;
    return I * (Ka + Kd * max(dot(s, Normal), 0.0) + Ks * pow(max(dot(h, n), 0.0), Shininess)) * Color;
}


vec3 customModel(int lightIndex)
{
    vec3 s;
    if (lights[lightIndex].Position.w == 0.0)
        s = normalize(vec3(lights[lightIndex].Position));
    else
        s = normalize(vec3(lights[lightIndex].Position.xyz - Position));
    float sDotN = max(dot(s, Normal), 0.0);
    vec3 I = lights[lightIndex].Intensity;
    return I * Color * (Ka + Kd * sDotN + Ks * pow(sDotN, Shininess));
}


void main() {
    vec3 ResColor = vec3(0.0);
    float alpha = FogSetExpMod(Position, EyePosition);
    // float alpha = pow(smoothstep(fog.FogMaxDist - fog.FogMinDist, 1, distance(Position, EyePosition)), fog.FogDensity);
    for (int i = 0; i < 8; i++)
        ResColor += ads(i);

    vec4 textureData = texture(textureMap, TexCoord);

    FragColor = mix(vec4(ResColor, 1.0), fog.FogColor, alpha);
    if (isTextureExist != 0) {
        FragColor = mix(FragColor, textureData, 0.5);
    }
    // FragColor = min(FragColor, textureData);
    // FragColor = textureData ; // + vec4(ResColor, 1.0);
    // FragColor = vec4(ResColor, 1.0);
}