#version 330 core

// Cor interpolada pelo Rasterizador para cada pixel do triângulo
in vec3 vColor;

// Cor final gravada no Framebuffer
out vec4 FragColor;

// Parâmetro enviado pela CPU para ajustar o brilho em tempo real (tecla B)
uniform float u_brilho;

void main()
{
    FragColor = vec4(vColor * u_brilho, 1.0);
}
