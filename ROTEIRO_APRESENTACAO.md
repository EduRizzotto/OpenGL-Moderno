# Roteiro da Apresentação — OpenGL Moderno: VAO, VBO, EBO e GLSL

## Como Executar o Projeto
```bash
.venv/bin/python main.py
```

### Controles Ao Vivo para a Demonstração (Bloco 3)
| Tecla | Parâmetro modificado | Conceito de CG demonstrado |
| :--- | :--- | :--- |
| **`W`** | Alterna **Wireframe (`GL_LINE`)** vs. **Preenchido (`GL_FILL`)** | Rasterização das primitivas triangulares |
| **`-` / `+`** | Diminui / aumenta os triângulos desenhados (de 1 a 12) | Como o **EBO** (`glDrawElements`) monta o cubo a partir dos 8 vértices do **VBO** |
| **`B`** | Alterna o brilho no Fragment Shader (`u_brilho`: `0.4x`, `1.0x`, `1.5x`) | Envio de variável `uniform` da CPU para o **Fragment Shader** em GLSL |
| **`Espaço` / `Setas`** | Pausa/retoma o giro ou rotaciona nos eixos X e Y | Transformações 3D na matriz **MVP** enviada ao **Vertex Shader** |

---

## Bloco 1 — Contextualização e Fundamentos (4 a 5 min)

1. **O que é o tema e finalidade:**
   - Até o OpenGL 2.1 usava-se o **Modo Imediato (`glBegin`/`glEnd`)**, onde a CPU enviava vértice por vértice a cada *frame*.
   - O **OpenGL Moderno (3.3+ Core Profile)** substitui esse modo pelo **Pipeline Programável**, guardando a geometria direto na memória da GPU (VRAM) e usando **Shaders em GLSL**.
2. **Problemas que resolve:**
   - **Gargalo CPU $\rightarrow$ GPU:** Os vértices são enviados **uma única vez** na inicialização (`glBufferData`), e não 60 vezes por segundo.
   - **Redundância de Vértices:** Um cubo tem 12 triângulos (36 pontas), mas apenas **8 cantos únicos**. Com o **EBO**, guardamos só 8 vértices em vez de 36.
3. **Os 4 Pilares:**
   - **VBO (*Vertex Buffer Object*):** Buffer na GPU que guarda os atributos dos 8 vértices (`[X, Y, Z, R, G, B]`).
   - **EBO (*Element Buffer Object*):** Buffer na GPU que guarda os **36 índices** dizendo quais vértices formam cada um dos 12 triângulos.
   - **VAO (*Vertex Array Object*):** Objeto que grava o formato de leitura do VBO (*stride* de 24 bytes e *offsets*) e o vínculo com o EBO.
   - **GLSL (*OpenGL Shading Language*):** Linguagem dos programas que rodam na GPU (**Vertex Shader** para posição 3D e **Fragment Shader** para cor dos pixels).
4. **Aplicações, vantagens e limitações:**
   - Usado em engines de jogos, CAD e visualização científica. Oferece altíssimo desempenho na GPU, tendo como única limitação exigir mais linhas de configuração inicial que o `glBegin`.

---

## Bloco 2 — Funcionamento e Computação Gráfica (7 a 8 min)

1. **Como a imagem é gerada (Pipeline Gráfico):**
   - **CPU $\rightarrow$ GPU:** Na inicialização, `configurar_vao_vbo_ebo()` envia `VERTICES` para o **VBO** e `INDICES` para o **EBO**.
   - **Vertex Shader (`vertex_shader.glsl`):** Multiplica cada um dos 8 vértices pela matriz combinada $4 \times 4$:
     $$\mathbf{v}_{\text{clip}} = \mathbf{M}_{\text{MVP}} \cdot \mathbf{v}_{\text{local}}$$
   - **Rasterização:** Conecta os triângulos usando os índices do **EBO** e faz a **interpolação baricêntrica** das cores entre os 3 vértices de cada triângulo.
   - **Fragment Shader (`fragment_shader.glsl`):** Recebe a cor interpolada (`vColor`), multiplica pelo brilho (`u_brilho`) e grava no **Framebuffer** (usando o **Z-Buffer** `GL_DEPTH_TEST` para profundidade).
2. **Comparação com o Python e OpenGL das Aulas:**

   > **Citação do Slide 1 do Professor (`SlidesOK.pdf`):**
   > *"Nesta disciplina estamos utilizando inicialmente o OpenGL legado (fixed function pipeline) por facilitar a compreensão dos conceitos. No OpenGL moderno, a renderização é realizada principalmente com triângulos, buffers e shaders."*

| Conceito de CG | OpenGL das Aulas (Legado) | OpenGL Moderno (Nosso Código) | O que mudou? |
| :--- | :--- | :--- | :--- |
| **Envio de Vértices** | `glBegin()` / `glVertex3f()` / `glEnd()` | `VBO` (`glBufferData`) + `VAO` | **Substituído:** Fica gravado na VRAM da GPU |
| **Primitivas e Reuso** | `GL_QUADS` repetindo vértices | `GL_TRIANGLES` + `EBO` (`glDrawElements`) | **Otimizado:** 8 vértices + 36 índices |
| **Transformações e Projeção** | `glRotatef()`, `glTranslatef()`, `gluPerspective()` | Matriz $4 \times 4$ `u_mvp` (`calcular_matriz_mvp`) | **Desabstraído:** Matemática explícita enviada ao Vertex Shader |
| **Cores e Z-Buffer** | `glColor3f()` + `GL_DEPTH_TEST` | Atributo no VBO + Fragment Shader + `GL_DEPTH_TEST` | Cores interpoladas via shader; Z-Buffer **mantido** |

---

## Bloco 3 — Código, Demonstração e Conclusões (7 a 8 min)

1. **Estrutura Enxuta do Código:**
   - [`main.py`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/main.py) (~160 linhas divididas em 4 blocos claros: Dados do Cubo, Matriz MVP, Configuração GLSL + VAO/VBO/EBO e Loop Principal).
   - [`shaders/vertex_shader.glsl`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/shaders/vertex_shader.glsl) (16 linhas) e [`shaders/fragment_shader.glsl`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/shaders/fragment_shader.glsl) (14 linhas).
2. **Demonstração ao Vivo (2 minutos):**
   - Apertar **`W`** para ativar o *Wireframe* e apertar **`-`** várias vezes até ficar 1 único triângulo na tela; depois apertar **`+`** para montar o cubo triângulo por triângulo mostrando o **EBO** em ação!
   - Apertar **`W`** novamente para ver o cubo preenchido com interpolação de cores e apertar **`B`** para alterar o `uniform float u_brilho` no *Fragment Shader* em tempo real.
   - Apertar **`Espaço`** e usar as **Setas** para mostrar a atualização da matriz `u_mvp` no *Vertex Shader*.
