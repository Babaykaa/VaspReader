#version 430

in vec3 Position;
in vec3 Normal;
in vec3 Color;


struct LightInfo{
    vec4 Position;
    vec3 Intensity;
};
uniform LightInfo lights[8];


uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Shininess;


layout (location=0) out vec4 FragColor;


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
    for (int i = 0; i < 8; i++)
        ResColor += ads(i);

    FragColor = vec4(ResColor, 1.0);
}