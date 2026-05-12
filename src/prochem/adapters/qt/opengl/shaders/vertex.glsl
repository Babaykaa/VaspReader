#version 460


layout (location=0) in vec3 PositionIn;
layout (location=1) in vec3 NormalIn;
layout (location=2) in vec2 TexCoordIn;


out vec3 Position;
out vec3 Normal;
out vec3 Color;
out vec2 TexCoord;

uniform vec3 ObjColor;
uniform mat4 Rotation;
uniform mat4 Translation;
uniform mat4 View;
uniform mat4 Projection;
// uniform mat3 Normal;


void main()
{
    mat4 Model = Rotation * Translation; 
    vec4 Mod_Position = View * Model * vec4(PositionIn, 1.0);

    Position = vec3(Mod_Position);
    Normal = normalize(mat3(transpose(inverse(Model))) * NormalIn);
    Color = ObjColor;
    TexCoord = vec2(TexCoordIn[0], 1 - TexCoordIn[1]);
    
    gl_Position = Projection * Mod_Position;
}
