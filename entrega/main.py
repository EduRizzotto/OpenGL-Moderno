"""
Seminário Técnico de Computação Gráfica — Tema 2
OpenGL Moderno: VAO, VBO, EBO e GLSL
"""

import ctypes
import math
from pathlib import Path
import glfw
import numpy as np
from OpenGL.GL import *

# ============================================================================
# 1. DADOS GEOMÉTRICOS: CUBO 3D INDEXADO (VBO = 8 VÉRTICES | EBO = 36 ÍNDICES)
# ============================================================================
# Cada vértice tem 6 floats (24 bytes): [ X, Y, Z (Posição),  R, G, B (Cor) ]
VERTICES = np.array([
    # Frente (Z = +0.8)
    [-0.8, -0.8,  0.8,   1.0, 0.2, 0.2],  # 0: Vermelho
    [ 0.8, -0.8,  0.8,   0.2, 1.0, 0.2],  # 1: Verde
    [ 0.8,  0.8,  0.8,   0.2, 0.4, 1.0],  # 2: Azul
    [-0.8,  0.8,  0.8,   1.0, 0.9, 0.1],  # 3: Amarelo
    # Trás (Z = -0.8)
    [-0.8, -0.8, -0.8,   1.0, 0.2, 0.9],  # 4: Magenta
    [ 0.8, -0.8, -0.8,   0.1, 0.9, 0.9],  # 5: Ciano
    [ 0.8,  0.8, -0.8,   1.0, 0.5, 0.1],  # 6: Laranja
    [-0.8,  0.8, -0.8,   0.9, 0.9, 0.9],  # 7: Branco
], dtype=np.float32)

# EBO: 12 triângulos (6 faces * 2 triângulos) reaproveitando os 8 vértices acima
INDICES = np.array([
    0, 1, 2,   2, 3, 0,  # Face Frontal
    1, 5, 6,   6, 2, 1,  # Face Direita
    5, 4, 7,   7, 6, 5,  # Face Traseira
    4, 0, 3,   3, 7, 4,  # Face Esquerda
    3, 2, 6,   6, 7, 3,  # Face Superior
    4, 5, 1,   1, 0, 4,  # Face Inferior
], dtype=np.uint32)


# ============================================================================
# 2. MATRIZES DE TRANSFORMAÇÃO 4x4 (SUBSTITUEM glRotatef / gluPerspective)
# ============================================================================
def calcular_matriz_mvp(ang_x: float, ang_y: float, aspecto: float) -> np.ndarray:
    """Calcula a matriz combinada MVP = Projection * View * Model."""
    rx, ry = math.radians(ang_x), math.radians(ang_y)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)

    # Matriz Model: Rotação nos eixos X e Y
    rot_x = np.array([[1, 0, 0, 0], [0, cx, -sx, 0], [0, sx, cx, 0], [0, 0, 0, 1]], dtype=np.float32)
    rot_y = np.array([[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]], dtype=np.float32)
    model = rot_x @ rot_y

    # Matriz View (Câmera afastada em Z = -3.8)
    view = np.identity(4, dtype=np.float32)
    view[2, 3] = -3.8

    # Matriz Projection (Perspectiva com FOV = 45 graus)
    f = 1.0 / math.tan(math.radians(45.0) / 2.0)
    near, far = 0.1, 100.0
    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = f / aspecto
    proj[1, 1] = f
    proj[2, 2] = (far + near) / (near - far)
    proj[2, 3] = (2.0 * far * near) / (near - far)
    proj[3, 2] = -1.0

    return proj @ view @ model


# ============================================================================
# 3. SHADERS GLSL E CONFIGURAÇÃO DE VAO, VBO E EBO NA GPU
# ============================================================================
def criar_programa_glsl() -> int:
    """Compila e linka o Vertex Shader e o Fragment Shader na GPU."""
    pasta = Path(__file__).resolve().parent / "shaders"
    vs_src = (pasta / "vertex_shader.glsl").read_text(encoding="utf-8")
    fs_src = (pasta / "fragment_shader.glsl").read_text(encoding="utf-8")

    vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vs, vs_src)
    glCompileShader(vs)

    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fs, fs_src)
    glCompileShader(fs)

    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)

    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog


def configurar_vao_vbo_ebo():
    """Aloca VBO e EBO na VRAM da GPU e registra o layout no VAO."""
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    # 1. Ativa o VAO (passa a gravar a configuração dos buffers abaixo)
    glBindVertexArray(vao)

    # 2. VBO: copia os 8 vértices da CPU para a GPU
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, VERTICES.nbytes, VERTICES, GL_STATIC_DRAW)

    # 3. EBO: copia os 36 índices dos triângulos da CPU para a GPU
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, INDICES.nbytes, INDICES, GL_STATIC_DRAW)

    # 4. Layout dos atributos no VBO: cada vértice tem 6 floats = 24 bytes (stride)
    stride = 6 * ctypes.sizeof(ctypes.c_float)

    # Atributo 0 (aPos): 3 floats começando no byte 0
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Atributo 1 (aColor): 3 floats começando no byte 12 (3 * 4 bytes)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    glBindVertexArray(0)
    return vao, vbo, ebo


# ============================================================================
# 4. PROGRAMA PRINCIPAL E LOOP DE RENDERIZAÇÃO
# ============================================================================
def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    janela = glfw.create_window(900, 650, "OpenGL Moderno: VAO, VBO, EBO e GLSL", None, None)
    glfw.make_context_current(janela)
    glEnable(GL_DEPTH_TEST)

    programa = criar_programa_glsl()
    vao, vbo, ebo = configurar_vao_vbo_ebo()

    # Parâmetros modificáveis ao vivo na apresentação
    wireframe = False
    girar_auto = True
    brilho = 1.0
    triangulos = 12  # Total = 12 triângulos (36 índices no EBO)
    ang_x, ang_y = 25.0, -35.0

    def teclado(window, key, scancode, action, mods):
        nonlocal wireframe, girar_auto, brilho, triangulos, ang_x, ang_y
        if action not in (glfw.PRESS, glfw.REPEAT):
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_W and action == glfw.PRESS:
            wireframe = not wireframe
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
        elif key == glfw.KEY_SPACE and action == glfw.PRESS:
            girar_auto = not girar_auto
        elif key == glfw.KEY_B and action == glfw.PRESS:
            brilho = 0.4 if brilho == 1.0 else (1.5 if brilho == 0.4 else 1.0)
        elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD):
            triangulos = min(12, triangulos + 1)
        elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT):
            triangulos = max(1, triangulos - 1)
        elif key == glfw.KEY_UP:
            ang_x -= 6.0
        elif key == glfw.KEY_DOWN:
            ang_x += 6.0
        elif key == glfw.KEY_LEFT:
            ang_y -= 6.0
        elif key == glfw.KEY_RIGHT:
            ang_y += 6.0

    glfw.set_key_callback(janela, teclado)
    print("Controles: [W] Wireframe | [+/-] Triângulos EBO | [B] Brilho Shader | [Espaço/Setas] Rotação")

    loc_mvp = glGetUniformLocation(programa, "u_mvp")
    loc_brilho = glGetUniformLocation(programa, "u_brilho")

    while not glfw.window_should_close(janela):
        glClearColor(0.08, 0.09, 0.12, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if girar_auto:
            ang_y += 0.6

        w, h = glfw.get_framebuffer_size(janela)
        glViewport(0, 0, max(1, w), max(1, h))
        mvp = calcular_matriz_mvp(ang_x, ang_y, w / max(1, h))

        # Ativa o Shader GLSL e envia os Uniforms (CPU -> GPU)
        glUseProgram(programa)
        glUniformMatrix4fv(loc_mvp, 1, GL_TRUE, mvp)
        glUniform1f(loc_brilho, brilho)

        # Ativa o VAO e desenha os triângulos usando os índices do EBO!
        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, triangulos * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))

        glfw.set_window_title(
            janela,
            f"OpenGL Moderno | EBO: {triangulos}/12 tri ({triangulos*3} ind) | "
            f"{'Wireframe' if wireframe else 'Preenchido'} | Brilho GLSL: {brilho}x"
        )
        glfw.swap_buffers(janela)
        glfw.poll_events()

    glDeleteVertexArrays(1, [vao])
    glDeleteBuffers(1, [vbo, ebo])
    glDeleteProgram(programa)
    glfw.terminate()


if __name__ == "__main__":
    main()
