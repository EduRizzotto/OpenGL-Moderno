"""
transformacoes.py
-----------------
Implementação explícita das matrizes 4x4 de Computação Gráfica.

No OpenGL Clássico (Modo Imediato das aulas), usávamos:
  glTranslatef(), glRotatef(), glScalef(), gluPerspective(), gluLookAt()

No OpenGL Moderno (3.3+ Core Profile), a pilha de matrizes fixa foi removida.
A CPU calcula as matrizes 4x4 (Model, View, Projection) e as envia para o
Vertex Shader via variáveis 'uniform' (glUniformMatrix4fv).
"""

import math
import numpy as np


def matriz_identidade() -> np.ndarray:
    """Retorna a matriz identidade 4x4 (float32)."""
    return np.identity(4, dtype=np.float32)


def matriz_translacao(tx: float, ty: float, tz: float) -> np.ndarray:
    """Matriz de translação homogênea 4x4."""
    m = np.identity(4, dtype=np.float32)
    m[0, 3] = tx
    m[1, 3] = ty
    m[2, 3] = tz
    return m


def matriz_escala(sx: float, sy: float, sz: float) -> np.ndarray:
    """Matriz de escala homogênea 4x4."""
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = sx
    m[1, 1] = sy
    m[2, 2] = sz
    return m


def matriz_rotacao_x(angulo_graus: float) -> np.ndarray:
    """Matriz de rotação 3D em torno do eixo X."""
    rad = math.radians(angulo_graus)
    c, s = math.cos(rad), math.sin(rad)
    m = np.identity(4, dtype=np.float32)
    m[1, 1] = c
    m[1, 2] = -s
    m[2, 1] = s
    m[2, 2] = c
    return m


def matriz_rotacao_y(angulo_graus: float) -> np.ndarray:
    """Matriz de rotação 3D em torno do eixo Y."""
    rad = math.radians(angulo_graus)
    c, s = math.cos(rad), math.sin(rad)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c
    m[0, 2] = s
    m[2, 0] = -s
    m[2, 2] = c
    return m


def matriz_rotacao_z(angulo_graus: float) -> np.ndarray:
    """Matriz de rotação 3D em torno do eixo Z."""
    rad = math.radians(angulo_graus)
    c, s = math.cos(rad), math.sin(rad)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c
    m[0, 1] = -s
    m[1, 0] = s
    m[1, 1] = c
    return m


def matriz_visao_lookat(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    """
    Constrói a Matriz de Visão (View Matrix) equivalente ao antigo gluLookAt().
    Transforma coordenadas do Espaço do Mundo para o Espaço da Câmera.
    """
    f = target - eye
    f = f / np.linalg.norm(f)

    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)

    m = np.identity(4, dtype=np.float32)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m


def matriz_perspectiva(fov_graus: float, aspect: float, near: float, far: float) -> np.ndarray:
    """
    Constrói a Matriz de Projeção Perspectiva equivalente ao antigo gluPerspective().
    Transforma o Frustum 3D para o Cubo Canônico de Recorte (Clip Space).
    """
    fov_rad = math.radians(fov_graus)
    f = 1.0 / math.tan(fov_rad / 2.0)

    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m

