"""
geometria.py
------------
Definição dos dados geométricos para o VBO (Vertex Buffer Object) e
dos índices de conectividade para o EBO (Element Buffer Object).

Formato de cada vértice no VBO (9 floats = 36 bytes por vértice):
  [ X, Y, Z,    R, G, B,    Nx, Ny, Nz ]
  | Posição |  |  Cor  |   |  Normal  |
"""

import numpy as np


# [1] Dados do VBO (8 vértices únicos) e EBO (36 índices formando 12 triângulos)
def criar_cubo_indexado():
    """
    Cria um Cubo 3D usando APENAS 8 vértices únicos no VBO e 36 índices no EBO.

    - Um cubo possui 6 faces quadradas = 12 triângulos = 36 vértices se não usarmos EBO.
    - Com o EBO, armazenamos somente os 8 cantos do cubo no VBO e dizemos para a GPU
      como conectá-los em 12 triângulos através da lista de índices!
    """
    # 8 vértices únicos: [x, y, z,   r, g, b,   nx, ny, nz]
    # As normais aqui apontam do centro (0,0,0) para cada canto (normal suave/esférica)
    s = 0.57735  # 1 / sqrt(3) para vetor normal unitário nos cantos
    vertices = np.array([
        # Frente (Z = +0.8)
        [-0.8, -0.8,  0.8,   1.0, 0.2, 0.2,  -s, -s,  s],  # 0: Frente-Inf-Esq (Vermelho)
        [ 0.8, -0.8,  0.8,   0.2, 1.0, 0.2,   s, -s,  s],  # 1: Frente-Inf-Dir (Verde)
        [ 0.8,  0.8,  0.8,   0.2, 0.4, 1.0,   s,  s,  s],  # 2: Frente-Sup-Dir (Azul)
        [-0.8,  0.8,  0.8,   1.0, 0.9, 0.1,  -s,  s,  s],  # 3: Frente-Sup-Esq (Amarelo)

        # Trás (Z = -0.8)
        [-0.8, -0.8, -0.8,   1.0, 0.2, 0.9,  -s, -s, -s],  # 4: Trás-Inf-Esq (Magenta)
        [ 0.8, -0.8, -0.8,   0.1, 0.9, 0.9,   s, -s, -s],  # 5: Trás-Inf-Dir (Ciano)
        [ 0.8,  0.8, -0.8,   1.0, 0.5, 0.1,   s,  s, -s],  # 6: Trás-Sup-Dir (Laranja)
        [-0.8,  0.8, -0.8,   0.9, 0.9, 0.9,  -s,  s, -s],  # 7: Trás-Sup-Esq (Branco)
    ], dtype=np.float32)

    # 12 triângulos (6 faces * 2 triângulos) = 36 índices no EBO
    indices = np.array([
        0, 1, 2,   2, 3, 0,  # Face Frontal
        1, 5, 6,   6, 2, 1,  # Face Direita
        5, 4, 7,   7, 6, 5,  # Face Traseira
        4, 0, 3,   3, 7, 4,  # Face Esquerda
        3, 2, 6,   6, 7, 3,  # Face Superior
        4, 5, 1,   1, 0, 4,  # Face Inferior
    ], dtype=np.uint32)

    info = "Cubo Indexado (VBO: 8 vértices únicos | EBO: 36 índices / 12 triângulos)"
    return vertices, indices, info


def criar_octaedro_indexado():
    """
    Cria um Octaedro / Cristal 3D com APENAS 6 vértices únicos no VBO
    e 24 índices (8 faces triangulares) no EBO.
    """
    vertices = np.array([
        # [x,    y,    z,     r,   g,   b,     nx,   ny,   nz]
        [ 0.0,  1.2,  0.0,   1.0, 0.9, 0.2,   0.0,  1.0,  0.0],  # 0: Topo (Dourado)
        [ 0.0, -1.2,  0.0,   0.6, 0.1, 0.9,   0.0, -1.0,  0.0],  # 1: Base (Roxo)
        [ 1.0,  0.0,  0.0,   1.0, 0.2, 0.3,   1.0,  0.0,  0.0],  # 2: Direita (Vermelho)
        [-1.0,  0.0,  0.0,   0.1, 0.8, 0.4,  -1.0,  0.0,  0.0],  # 3: Esquerda (Verde)
        [ 0.0,  0.0,  1.0,   0.2, 0.6, 1.0,   0.0,  0.0,  1.0],  # 4: Frente (Azul)
        [ 0.0,  0.0, -1.0,   0.1, 0.9, 0.9,   0.0,  0.0, -1.0],  # 5: Trás (Ciano)
    ], dtype=np.float32)

    indices = np.array([
        # Pirâmide Superior (4 triângulos compartilhando o vértice 0)
        0, 4, 2,
        0, 2, 5,
        0, 5, 3,
        0, 3, 4,
        # Pirâmide Inferior (4 triângulos compartilhando o vértice 1)
        1, 2, 4,
        1, 5, 2,
        1, 3, 5,
        1, 4, 3,
    ], dtype=np.uint32)

    info = "Octaedro / Cristal (VBO: 6 vértices únicos | EBO: 24 índices / 8 triângulos)"
    return vertices, indices, info


def criar_malha_superficie(divisoes: int = 16):
    """
    Cria uma malha de superfície 3D (grade) onde cada vértice interno é
    compartilhado por até 6 triângulos no EBO.
    Ideal para demonstrar a deformação por ondas no Vertex Shader (tecla D).
    """
    lista_vertices = []
    tamanho = 2.2
    passo = tamanho / divisoes
    inicio = -tamanho / 2.0

    for i in range(divisoes + 1):
        for j in range(divisoes + 1):
            x = inicio + j * passo
            z = inicio + i * passo
            y = 0.0

            # Gradiente de cores baseado na posição (U, V) da malha
            u = j / divisoes
            v = i / divisoes
            r = 0.15 + 0.85 * u
            g = 0.25 + 0.65 * (1.0 - abs(u - v))
            b = 0.95 - 0.75 * v

            # Normal apontando para cima (0, 1, 0)
            lista_vertices.append([x, y, z, r, g, b, 0.0, 1.0, 0.0])

    vertices = np.array(lista_vertices, dtype=np.float32)

    lista_indices = []
    cols = divisoes + 1
    for i in range(divisoes):
        for j in range(divisoes):
            v0 = i * cols + j
            v1 = v0 + 1
            v2 = (i + 1) * cols + j
            v3 = v2 + 1

            # Dois triângulos formando cada quadrado da malha
            lista_indices.extend([v0, v2, v1])
            lista_indices.extend([v1, v2, v3])

    indices = np.array(lista_indices, dtype=np.uint32)
    n_verts = len(vertices)
    n_inds = len(indices)
    info = f"Malha {divisoes}x{divisoes} (VBO: {n_verts} vértices | EBO: {n_inds} índices / {n_inds // 3} triângulos)"
    return vertices, indices, info

