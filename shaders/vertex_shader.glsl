#version 330 core

// ============================================================================
// VERTEX SHADER (Executado na GPU uma vez para CADA vértice do VBO)
// ============================================================================
// Os 'locations' abaixo correspondem exatamente aos configurados no VAO via
// glVertexAttribPointer(location, ...) no código Python!

// ★★★ [1. EXPLICAR NA APRESENTAÇÃO — ENTRADAS DO VBO CONFIGURADAS PELO VAO] ★★★
layout (location = 0) in vec3 aPos;    // Atributo 0: Posição local (X, Y, Z) -> offset 0B
layout (location = 1) in vec3 aColor;  // Atributo 1: Cor do vértice (R, G, B) -> offset 12B
layout (location = 2) in vec3 aNormal; // Atributo 2: Vetor Normal (Nx, Ny, Nz) -> offset 24B

// Dados de saída que serão INTERPOLADOS pelo Rasterizador e entregues
// ao Fragment Shader (um para cada pixel/fragmento gerado)
out vec3 vColor;
out vec3 vNormal;
out vec3 vFragPos;

// Variáveis UNIFORM: parâmetros enviados da CPU para a GPU a cada frame
uniform mat4 u_model;       // Transformação do Objeto (Rotação, Escala, Translação)
uniform mat4 u_view;        // Câmera (Posição e orientação do observador)
uniform mat4 u_projection;  // Projeção Perspectiva (Lente / FOV / Recorte 3D)
uniform float u_time;       // Tempo decorrido (para animação direto na GPU)
uniform int u_deform;       // 0 = Geometria original, 1 = Onda senoidal na GPU

void main()
{
    vec3 pos = aPos;

    // Demonstração de poder do Vertex Shader:
    // Podemos deformar os vértices matematicamente na GPU em tempo real
    // SEM precisar reenviar ou modificar o VBO na memória da CPU!
    if (u_deform == 1) {
        float onda = sin(pos.x * 3.5 + u_time * 3.0) * cos(pos.z * 3.5 + u_time * 3.0) * 0.25;
        pos.y += onda;
    }

    // Posição do vértice no Espaço do Mundo (World Space) para cálculo de luz
    vec4 worldPos = u_model * vec4(pos, 1.0);
    vFragPos = worldPos.xyz;

    // Ajusta a normal de acordo com a rotação/escala do modelo
    mat3 normalMatrix = mat3(transpose(inverse(u_model)));
    vNormal = normalize(normalMatrix * aNormal);

    // Repassa a cor do vértice para ser interpolada na rasterização
    vColor = aColor;

    // ★★★ [2. EXPLICAR NA APRESENTAÇÃO — TRANSFORMAÇÃO MVP NA GPU] ★★★
    // v_clip = Projection * View * Model * v_local
    gl_Position = u_projection * u_view * worldPos;
}

