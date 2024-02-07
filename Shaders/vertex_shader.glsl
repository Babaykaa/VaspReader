#version 430


layout (location=0) in vec3 VertexPosition;
layout (location=1) in vec3 VertexColor;
layout (location=2) in vec3 VertexNormal;
layout (location=3) in vec2 VertexTexCoord;


out vec3 Position;
out vec3 Normal;
out vec3 Color;


uniform mat4 ModelMatrix;
uniform mat4 ViewMatrix;
uniform mat4 ProjectionMatrix;
uniform mat3 NormalMatrix;
uniform mat4 TranslationMatrix;


void main()
{
    Normal = normalize(NormalMatrix * VertexNormal);

    vec4 ModifiedPosition = ViewMatrix * ModelMatrix * TranslationMatrix * vec4(VertexPosition, 1.0);

    Position = vec3(ModifiedPosition);

    Color = VertexColor;

    gl_Position = ProjectionMatrix * ModifiedPosition;
}