#version 330 core

// Atributos lidos do VBO (configurados pelo VAO no Python)
layout (location = 0) in vec3 aPos;   // Posição (X, Y, Z) -> offset 0 bytes
layout (location = 1) in vec3 aColor; // Cor (R, G, B)     -> offset 12 bytes

// Cor enviada para a etapa de Rasterização (será interpolada entre os vértices)
out vec3 vColor;

// Matriz combinada (Projection * View * Model) enviada pela CPU
uniform mat4 u_mvp;

void main()
{
    vColor = aColor;
    gl_Position = u_mvp * vec4(aPos, 1.0);
}
