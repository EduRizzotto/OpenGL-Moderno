#version 330 core

// ============================================================================
// FRAGMENT SHADER (Executado na GPU para CADA fragmento/pixel rasterizado)
// ============================================================================

// Dados interpolados baricentricamente a partir dos 3 vértices do triângulo
in vec3 vColor;
in vec3 vNormal;
in vec3 vFragPos;

// Cor de saída final enviada para o Framebuffer (R, G, B, A)
out vec4 FragColor;

// Parâmetros Uniform enviados pela CPU
uniform int u_shader_mode;  // 0 = Cor por vértice, 1 = Phong, 2 = Normais, 3 = Procedural
uniform vec3 u_light_pos;   // Posição da fonte de luz no espaço 3D
uniform vec3 u_view_pos;    // Posição da câmera para reflexo especular
uniform float u_time;       // Tempo para efeitos dinâmicos
uniform float u_ambient;    // Intensidade da luz ambiente (modificável ao vivo)

void main()
{
    // [8] Cálculo da cor final (FragColor): Interpolação Baricêntrica das cores ou Iluminação de Phong
    // Modo 0: Interpolação Baricêntrica Pura (Cores dos Vértices do VBO)
    if (u_shader_mode == 0) {
        FragColor = vec4(vColor, 1.0);
        return;
    }

    // Modo 1: Modelo de Iluminação de Phong (Ambiente + Difusa + Especular)
    if (u_shader_mode == 1) {
        vec3 norm = normalize(vNormal);
        vec3 lightDir = normalize(u_light_pos - vFragPos);

        // 1. Componente Ambiente
        vec3 ambient = u_ambient * vColor;

        // 2. Componente Difusa (Lei de Lambert: produto escalar N . L)
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = diff * vColor;

        // 3. Componente Especular (Brilho / Reflexo na direção da câmera)
        vec3 viewDir = normalize(u_view_pos - vFragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
        vec3 specular = 0.6 * spec * vec3(1.0, 1.0, 1.0);

        vec3 resultado = ambient + diffuse + specular;
        FragColor = vec4(resultado, 1.0);
        return;
    }

    // Modo 2: Visualização dos Vetores Normais como RGB
    // Mapeia o intervalo [-1, 1] do vetor normal para [0, 1] de cor (R=X, G=Y, B=Z)
    if (u_shader_mode == 2) {
        vec3 normColor = normalize(vNormal) * 0.5 + 0.5;
        FragColor = vec4(normColor, 1.0);
        return;
    }

    // Modo 3: Efeito Procedural em GLSL (Faixas luminosas calculadas na GPU)
    float padrao = 0.5 + 0.5 * sin(vFragPos.x * 8.0 + vFragPos.y * 8.0 + u_time * 4.0);
    vec3 corProcedural = mix(vColor * 0.3, vec3(0.1, 0.95, 1.0), padrao);
    FragColor = vec4(corProcedural, 1.0);
}

