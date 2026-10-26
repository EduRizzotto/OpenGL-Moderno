"""
===============================================================================
SEMINÁRIO TÉCNICO DE COMPUTAÇÃO GRÁFICA
Tema 2: OpenGL Moderno — VAO, VBO, EBO e GLSL
===============================================================================
Este arquivo implementa o pipeline programável completo do OpenGL 3.3 Core:
  1. Compilação e Linkagem de Shaders (Vertex Shader + Fragment Shader em GLSL)
  2. Alocação de Buffers na GPU:
     - VBO (Vertex Buffer Object): armazena atributos dos vértices (Pos, Cor, Normal)
     - EBO (Element Buffer Object): armazena índices para reaproveitar vértices
     - VAO (Vertex Array Object): registra o formato/layout dos atributos do VBO
  3. Envio de Matrizes 4x4 (Model, View, Projection) e parâmetros via Uniforms
  4. Renderização indexada na GPU via glDrawElements()
===============================================================================
"""

import ctypes
from pathlib import Path
import sys
import time
import glfw
import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_BUFFER_BIT,
    GL_COMPILE_STATUS,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_FALSE,
    GL_FILL,
    GL_FLOAT,
    GL_FRAGMENT_SHADER,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_LINK_STATUS,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    GL_TRUE,
    GL_UNSIGNED_INT,
    GL_VERTEX_SHADER,
    glAttachShader,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glClear,
    glClearColor,
    glCompileShader,
    glCreateProgram,
    glCreateShader,
    glDeleteBuffers,
    glDeleteProgram,
    glDeleteShader,
    glDeleteVertexArrays,
    glDrawElements,
    glEnable,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    glGetUniformLocation,
    glLinkProgram,
    glPolygonMode,
    glShaderSource,
    glUniform1f,
    glUniform1i,
    glUniform3f,
    glUniformMatrix4fv,
    glUseProgram,
    glVertexAttribPointer,
    glViewport,
)

from geometria import (
    criar_cubo_indexado,
    criar_malha_superficie,
    criar_octaedro_indexado,
)
from transformacoes import (
    matriz_escala,
    matriz_perspectiva,
    matriz_rotacao_x,
    matriz_rotacao_y,
    matriz_rotacao_z,
    matriz_translacao,
    matriz_visao_lookat,
)


# ============================================================================
# ★★★ [1. EXPLICAR NA APRESENTAÇÃO — COMPILAÇÃO DOS SHADERS GLSL] ★★★
# Como o código dos arquivos .glsl é enviado e compilado na GPU
# ============================================================================
def compilar_shader(codigo_fonte: str, tipo_shader: int) -> int:
    """Compila um Vertex ou Fragment Shader na GPU e verifica erros de sintaxe."""
    shader = glCreateShader(tipo_shader)
    glShaderSource(shader, codigo_fonte)
    glCompileShader(shader)

    sucesso = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not sucesso:
        erro = glGetShaderInfoLog(shader).decode("utf-8")
        nome_tipo = "VERTEX" if tipo_shader == GL_VERTEX_SHADER else "FRAGMENT"
        raise RuntimeError(f"Erro ao compilar {nome_tipo} SHADER:\n{erro}")
    return shader


def criar_programa_glsl(caminho_vertex: Path, caminho_fragment: Path) -> int:
    """Lê os arquivos .glsl, compila ambos os shaders e cria o Shader Program."""
    codigo_vertex = caminho_vertex.read_text(encoding="utf-8")
    codigo_fragment = caminho_fragment.read_text(encoding="utf-8")

    vs = compilar_shader(codigo_vertex, GL_VERTEX_SHADER)
    fs = compilar_shader(codigo_fragment, GL_FRAGMENT_SHADER)

    programa = glCreateProgram()
    glAttachShader(programa, vs)
    glAttachShader(programa, fs)
    glLinkProgram(programa)

    sucesso = glGetProgramiv(programa, GL_LINK_STATUS)
    if not sucesso:
        erro = glGetProgramInfoLog(programa).decode("utf-8")
        raise RuntimeError(f"Erro na linkagem do Shader Program:\n{erro}")

    # Depois de linkados no programa, os objetos individuais podem ser liberados
    glDeleteShader(vs)
    glDeleteShader(fs)
    return programa


# ============================================================================
# ★★★ [2. PRINCIPAL PARTE PARA EXPLICAR — CONFIGURAÇÃO DE VAO, VBO E EBO] ★★★
# Esta função é o coração do tema! Ela mostra:
#   - VBO (GL_ARRAY_BUFFER): copia os vértices para a VRAM da GPU
#   - EBO (GL_ELEMENT_ARRAY_BUFFER): copia os índices dos triângulos para a GPU
#   - VAO (glVertexAttribPointer): define o stride (36 bytes) e offsets (0, 12, 24)
# ============================================================================
def criar_vao_vbo_ebo(vertices: np.ndarray, indices: np.ndarray):
    """
    Cria e configura os 3 objetos fundamentais do OpenGL Moderno:
      - VAO: lembra toda a configuração de atributos e o vínculo com o EBO.
      - VBO: armazena o array de floats (Posição + Cor + Normal) na GPU.
      - EBO: armazena o array de uint32 (Índices dos triângulos) na GPU.
    """
    # 1. Gera os identificadores (IDs) na GPU
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    # 2. Ativa o VAO primeiro! Tudo o que fizermos a seguir ficará salvo nele.
    glBindVertexArray(vao)

    # 3. Configura o VBO (Vertex Buffer Object) e copia os vértices da CPU -> GPU
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # 4. Configura o EBO (Element Buffer Object) e copia os índices da CPU -> GPU
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # 5. Explica para o VAO como ler os atributos dentro do VBO:
    # Cada vértice tem 9 floats (3 Pos + 3 Cor + 3 Normal) = 9 * 4 bytes = 36 bytes (stride)
    stride = 9 * ctypes.sizeof(ctypes.c_float)

    # Atributo 0 (layout location = 0 no Vertex Shader): Posição (X, Y, Z) -> offset 0
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Atributo 1 (layout location = 1 no Vertex Shader): Cor (R, G, B) -> offset 3 floats (12 bytes)
    offset_cor = 3 * ctypes.sizeof(ctypes.c_float)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_cor))
    glEnableVertexAttribArray(1)

    # Atributo 2 (layout location = 2 no Vertex Shader): Normal (Nx, Ny, Nz) -> offset 6 floats (24 bytes)
    offset_normal = 6 * ctypes.sizeof(ctypes.c_float)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_normal))
    glEnableVertexAttribArray(2)

    # Desvincula o VAO por segurança (o EBO continua registrado dentro do VAO!)
    glBindVertexArray(0)

    return vao, vbo, ebo, len(indices)


# ============================================================================
# [CÓDIGO AUXILIAR — NÃO PRECISA EXPLICAR NA APRESENTAÇÃO]
# Controle de variáveis da demonstração e painel de ajuda no terminal
# ============================================================================
class EstadoDemonstracao:
    def __init__(self):
        self.indice_malha = 0          # 0 = Cubo, 1 = Octaedro, 2 = Malha Superfície
        self.modo_shader = 1           # 0 = Cores VBO, 1 = Phong, 2 = Normais, 3 = Procedural
        self.wireframe = False         # Alterna GL_FILL vs GL_LINE
        self.deformar_gpu = 0          # 0 = Desligado, 1 = Onda senoidal no Vertex Shader
        self.rotacao_auto = True       # Gira automaticamente o objeto
        self.ang_x = 25.0
        self.ang_y = -35.0
        self.ang_z = 0.0
        self.escala = 1.0
        self.fov = 45.0                # Campo de visão da projeção perspectiva
        self.cam_dist = 3.8            # Distância da câmera no eixo Z
        self.luz_ambiente = 0.25       # Intensidade ambiente no Fragment Shader
        self.triangulos_ativos = None  # None = desenha todos os triângulos do EBO


NOMES_SHADER = {
    0: "0: Cores Interpoladas (VBO puro)",
    1: "1: Iluminacao Phong (Amb + Dif + Spec)",
    2: "2: Visualizacao das Normais (RGB)",
    3: "3: Efeito Procedural GLSL",
}


def imprimir_painel_ajuda(estado: EstadoDemonstracao, info_malha: str, total_triangulos: int):
    tri_atuais = total_triangulos if estado.triangulos_ativos is None else estado.triangulos_ativos
    print("\n" + "=" * 78)
    print("  CONTROLES INTERATIVOS DA APRESENTAÇÃO (OPENGL MODERNO: VAO, VBO, EBO, GLSL)")
    print("=" * 78)
    print("  [1 / 2 / 3] : Trocar Geometria (1=Cubo Indexado, 2=Octaedro, 3=Superfície)")
    print("  [M]         : Alternar Modo do Fragment Shader (Cores / Phong / Normais / Procedural)")
    print("  [W]         : Alternar Wireframe (GL_LINE) vs Preenchido (GL_FILL)")
    print("  [D]         : Ligar/Desligar Deformação de Vértices na GPU (Vertex Shader)")
    print("  [ESPAÇO]    : Pausar/Retomar rotação automática")
    print("  [Setas]     : Rotacionar manualmente nos eixos X e Y")
    print("  [+ / -]     : Aumentar/Diminuir nº de triângulos desenhados pelo EBO (Passo a Passo!)")
    print("  [T]         : Mostrar TODOS os triângulos do EBO novamente")
    print("  [Z / X]     : Zoom da Câmera (aproximar / afastar)")
    print("  [F / V]     : Alterar FOV da Projeção Perspectiva")
    print("  [R]         : Resetar todos os parâmetros")
    print("  [ESC]       : Sair")
    print("-" * 78)
    print(f"  -> Malha Ativa     : {info_malha}")
    print(f"  -> Shader Ativo    : {NOMES_SHADER[estado.modo_shader]}")
    print(f"  -> Wireframe       : {'ATIVADO (GL_LINE)' if estado.wireframe else 'DESATIVADO (GL_FILL)'}")
    print(f"  -> Deformação GPU  : {'ATIVADA (Vertex Shader)' if estado.deformar_gpu else 'DESATIVADA'}")
    print(f"  -> EBO Desenhando  : {tri_atuais}/{total_triangulos} triângulos ({tri_atuais * 3} índices)")
    print(f"  -> Câmera / FOV    : Distância={estado.cam_dist:.1f} | FOV={estado.fov:.0f}°")
    print("=" * 78)


def inicializar_glfw() -> bool:
    """Inicializa o GLFW tentando a plataforma padrão e X11 como fallback."""
    if glfw.init():
        return True
    if hasattr(glfw, "PLATFORM") and hasattr(glfw, "PLATFORM_X11"):
        glfw.init_hint(glfw.PLATFORM, glfw.PLATFORM_X11)
        if glfw.init():
            return True
    return False


# ============================================================================
# PROGRAMA PRINCIPAL E LOOP DE RENDERIZAÇÃO
# ============================================================================
def main():
    if not inicializar_glfw():
        print("Erro ao inicializar o GLFW!")
        sys.exit(1)

    # Solicita explicitamente o OpenGL 3.3 Core Profile (sem funções legadas!)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    largura, altura = 1024, 720
    janela = glfw.create_window(
        largura, altura, "OpenGL Moderno: VAO, VBO, EBO e GLSL", None, None
    )
    if not janela:
        glfw.terminate()
        print("Erro ao criar a janela OpenGL 3.3 Core!")
        sys.exit(1)

    glfw.make_context_current(janela)
    glfw.swap_interval(1)  # V-Sync ativado

    # Habilita o Z-Buffer (Teste de Profundidade) no Framebuffer
    glEnable(GL_DEPTH_TEST)

    # Compila os Shaders GLSL
    pasta_base = Path(__file__).resolve().parent
    programa_shader = criar_programa_glsl(
        pasta_base / "shaders" / "vertex_shader.glsl",
        pasta_base / "shaders" / "fragment_shader.glsl",
    )

    # Cria as 3 geometrias na GPU (cada uma com seu próprio VAO, VBO e EBO)
    dados_malhas = [
        criar_cubo_indexado(),
        criar_octaedro_indexado(),
        criar_malha_superficie(16),
    ]
    objetos_gpu = []
    for verts, inds, info in dados_malhas:
        vao, vbo, ebo, qtd_indices = criar_vao_vbo_ebo(verts, inds)
        objetos_gpu.append((vao, vbo, ebo, qtd_indices, info))

    estado = EstadoDemonstracao()

    def total_triangulos_atual():
        return objetos_gpu[estado.indice_malha][3] // 3

    def atualizar_status():
        _, _, _, qtd_ind, info = objetos_gpu[estado.indice_malha]
        imprimir_painel_ajuda(estado, info, qtd_ind // 3)

    # ========================================================================
    # [CÓDIGO AUXILIAR — NÃO PRECISA EXPLICAR: ATALHOS DO TECLADO]
    # ========================================================================
    def key_callback(window, key, scancode, action, mods):
        if action not in (glfw.PRESS, glfw.REPEAT):
            return

        tot_tri = total_triangulos_atual()

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_1 and action == glfw.PRESS:
            estado.indice_malha = 0
            estado.triangulos_ativos = None
            atualizar_status()
        elif key == glfw.KEY_2 and action == glfw.PRESS:
            estado.indice_malha = 1
            estado.triangulos_ativos = None
            atualizar_status()
        elif key == glfw.KEY_3 and action == glfw.PRESS:
            estado.indice_malha = 2
            estado.triangulos_ativos = None
            atualizar_status()
        elif key == glfw.KEY_M and action == glfw.PRESS:
            estado.modo_shader = (estado.modo_shader + 1) % 4
            atualizar_status()
        elif key == glfw.KEY_W and action == glfw.PRESS:
            estado.wireframe = not estado.wireframe
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if estado.wireframe else GL_FILL)
            atualizar_status()
        elif key == glfw.KEY_D and action == glfw.PRESS:
            estado.deformar_gpu = 1 - estado.deformar_gpu
            atualizar_status()
        elif key == glfw.KEY_SPACE and action == glfw.PRESS:
            estado.rotacao_auto = not estado.rotacao_auto
            atualizar_status()
        elif key == glfw.KEY_UP:
            estado.ang_x -= 6.0
        elif key == glfw.KEY_DOWN:
            estado.ang_x += 6.0
        elif key == glfw.KEY_LEFT:
            estado.ang_y -= 6.0
        elif key == glfw.KEY_RIGHT:
            estado.ang_y += 6.0
        elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD):
            atual = tot_tri if estado.triangulos_ativos is None else estado.triangulos_ativos
            estado.triangulos_ativos = min(tot_tri, atual + 1)
            atualizar_status()
        elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT):
            atual = tot_tri if estado.triangulos_ativos is None else estado.triangulos_ativos
            estado.triangulos_ativos = max(1, atual - 1)
            atualizar_status()
        elif key == glfw.KEY_T and action == glfw.PRESS:
            estado.triangulos_ativos = None
            atualizar_status()
        elif key == glfw.KEY_Z:
            estado.cam_dist = max(1.5, estado.cam_dist - 0.25)
            atualizar_status()
        elif key == glfw.KEY_X:
            estado.cam_dist = min(10.0, estado.cam_dist + 0.25)
            atualizar_status()
        elif key == glfw.KEY_F:
            estado.fov = max(20.0, estado.fov - 5.0)
            atualizar_status()
        elif key == glfw.KEY_V:
            estado.fov = min(90.0, estado.fov + 5.0)
            atualizar_status()
        elif key == glfw.KEY_R and action == glfw.PRESS:
            estado.__init__()
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            atualizar_status()

    glfw.set_key_callback(janela, key_callback)

    # Ajusta o Viewport automaticamente se a janela for redimensionada
    def framebuffer_size_callback(window, w, h):
        glViewport(0, 0, max(1, w), max(1, h))

    glfw.set_framebuffer_size_callback(janela, framebuffer_size_callback)

    # Localizações das variáveis Uniform no programa GLSL
    glUseProgram(programa_shader)
    loc_model = glGetUniformLocation(programa_shader, "u_model")
    loc_view = glGetUniformLocation(programa_shader, "u_view")
    loc_proj = glGetUniformLocation(programa_shader, "u_projection")
    loc_time = glGetUniformLocation(programa_shader, "u_time")
    loc_deform = glGetUniformLocation(programa_shader, "u_deform")
    loc_mode = glGetUniformLocation(programa_shader, "u_shader_mode")
    loc_light = glGetUniformLocation(programa_shader, "u_light_pos")
    loc_view_pos = glGetUniformLocation(programa_shader, "u_view_pos")
    loc_ambient = glGetUniformLocation(programa_shader, "u_ambient")

    atualizar_status()
    tempo_anterior = time.time()

    # ========================================================================
    # LOOP PRINCIPAL DE RENDERIZAÇÃO
    # ========================================================================
    while not glfw.window_should_close(janela):
        tempo_atual = time.time()
        dt = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual

        # 1. Limpa o Framebuffer (Cor de fundo escura + Z-Buffer de profundidade)
        glClearColor(0.08, 0.09, 0.12, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 2. Atualiza o ângulo de rotação se a rotação automática estiver ativa
        if estado.rotacao_auto:
            estado.ang_y += 35.0 * dt

        # 3. Constrói as Matrizes de Transformação (Model, View, Projection) na CPU
        m_rot_x = matriz_rotacao_x(estado.ang_x)
        m_rot_y = matriz_rotacao_y(estado.ang_y)
        m_rot_z = matriz_rotacao_z(estado.ang_z)
        m_esc = matriz_escala(estado.escala, estado.escala, estado.escala)
        m_trans = matriz_translacao(0.0, 0.0, 0.0)
        m_model = m_trans @ m_rot_x @ m_rot_y @ m_rot_z @ m_esc

        pos_camera = np.array([0.0, 0.6, estado.cam_dist], dtype=np.float32)
        m_view = matriz_visao_lookat(
            eye=pos_camera,
            target=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            up=np.array([0.0, 1.0, 0.0], dtype=np.float32),
        )

        w, h = glfw.get_framebuffer_size(janela)
        aspecto = w / max(1, h)
        m_proj = matriz_perspectiva(estado.fov, aspecto, 0.1, 100.0)

        # ====================================================================
        # ★★★ [3. EXPLICAR NA APRESENTAÇÃO — ENVIO DE UNIFORMS (CPU -> GPU)] ★★★
        # Ativa o Shader GLSL e envia as matrizes 4x4 (Model, View, Projection)
        # ====================================================================
        glUseProgram(programa_shader)
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, m_model)
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, m_view)
        glUniformMatrix4fv(loc_proj, 1, GL_TRUE, m_proj)
        glUniform1f(loc_time, float(glfw.get_time()))
        glUniform1i(loc_deform, estado.deformar_gpu)
        glUniform1i(loc_mode, estado.modo_shader)
        glUniform3f(loc_light, 2.5, 3.0, 3.0)
        glUniform3f(loc_view_pos, pos_camera[0], pos_camera[1], pos_camera[2])
        glUniform1f(loc_ambient, estado.luz_ambiente)

        # ====================================================================
        # ★★★ [4. EXPLICAR NA APRESENTAÇÃO — DESENHO COM VAO E EBO] ★★★
        # Ativa o VAO e chama glDrawElements() para desenhar usando os índices do EBO!
        # ====================================================================
        vao, _, _, qtd_indices_total, info = objetos_gpu[estado.indice_malha]
        if estado.triangulos_ativos is None:
            qtd_indices_desenhar = qtd_indices_total
        else:
            qtd_indices_desenhar = min(qtd_indices_total, estado.triangulos_ativos * 3)

        glBindVertexArray(vao)
        # glDrawElements lê os índices direto do EBO vinculado ao VAO ativo!
        glDrawElements(GL_TRIANGLES, qtd_indices_desenhar, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindVertexArray(0)

        # Atualiza o título da janela com os parâmetros ativos para o público ver
        tri_str = f"{qtd_indices_desenhar // 3}/{qtd_indices_total // 3} tri"
        wf_str = "Wireframe" if estado.wireframe else "Fill"
        def_str = "OndaGPU:ON" if estado.deformar_gpu else "OndaGPU:OFF"
        titulo = (
            f"OpenGL 3.3 | {info.split('(')[0].strip()} ({tri_str}) | "
            f"{NOMES_SHADER[estado.modo_shader]} | {wf_str} | {def_str}"
        )
        glfw.set_window_title(janela, titulo)

        glfw.swap_buffers(janela)
        glfw.poll_events()

    # Limpeza final da memória da GPU (VRAM)
    for vao, vbo, ebo, _, _ in objetos_gpu:
        glDeleteVertexArrays(1, [vao])
        glDeleteBuffers(1, [vbo])
        glDeleteBuffers(1, [ebo])
    glDeleteProgram(programa_shader)
    glfw.terminate()


if __name__ == "__main__":
    main()

