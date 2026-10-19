# Roteiro Completo do Seminário e Guia dos Checkpoints
**Tema 2:** OpenGL Moderno: VAO, VBO, EBO e GLSL

---

## Como Executar o Protótipo (Checkpoint 3)

No terminal, dentro da pasta do projeto:

```bash
.venv/bin/python main.py
```

### Atalhos Ao Vivo durante a Apresentação (Bloco 3)
| Tecla | O que modifica ao vivo | Conceito de CG demonstrado |
| :--- | :--- | :--- |
| **`1` / `2` / `3`** | Alterna entre **Cubo (8 vértices)**, **Octaedro (6 vértices)** e **Superfície 16x16** | Troca de **VAO** (`glBindVertexArray`) contendo diferentes **VBOs** e **EBOs** |
| **`+` / `-`** | Desenha o objeto **triângulo por triângulo** (e **`T`** mostra todos) | Mostra na prática como o **EBO** (`glDrawElements`) monta a malha a partir dos índices |
| **`W`** | Alterna **Wireframe (`GL_LINE`)** vs. **Preenchido (`GL_FILL`)** | Etapa de **Rasterização** e montagem de primitivas triangulares |
| **`M`** | Alterna o **Fragment Shader** (0: Cores VBO, 1: Phong, 2: Normais RGB, 3: Procedural) | Programação da GPU via **GLSL**, interpolação baricêntrica e iluminação |
| **`D`** | Liga/Desliga **Onda Senoidal no Vertex Shader** | Deformação geométrica direto na **GPU** sem reenviar o **VBO** pela CPU |
| **`Espaço` / `Setas`** | Pausa rotação automática / Gira nos eixos X e Y | Transformações 3D na matriz **Model (`u_model`)** |
| **`Z` / `X`** | Aproxima / Afasta a câmera | Matriz **View (`u_view` / LookAt)** |
| **`F` / `V`** | Diminui / Aumenta o ângulo de abertura da lente (FOV) | Matriz **Projection (`u_projection` / Perspectiva)** |
| **`R`** | Reseta todos os parâmetros para o estado inicial | Controle de estado da aplicação |

---

## Estrutura dos 3 Blocos Obrigatórios (20 Minutos)

> **Atenção ao Sorteio:** Como o professor sorteia quem apresenta cada bloco na hora, **todos os integrantes devem ler os 3 blocos abaixo**.

---

### BLOCO 1 — Contextualização e Fundamentos (4 a 5 minutos)

1. **O que é o tema e Contexto:**
   - Até o OpenGL 2.1, usava-se o **Modo Imediato (*Fixed-Function Pipeline*)**, baseado em `glBegin()` e `glEnd()`.
   - A partir do **OpenGL 3.3+ (*Core Profile*)**, surgiu o **OpenGL Moderno (*Programmable Pipeline*)**, focado na arquitetura das GPUs modernas.
2. **Problemas que resolve:**
   - **Gargalo de barramento CPU $\rightarrow$ GPU:** No modo antigo, cada vértice exigia uma chamada de função (`glVertex3f`) enviada pela CPU a cada frame (60 vezes por segundo).
   - **Vértices duplicados:** Para desenhar um cubo (12 triângulos), enviavam-se 36 vértices, mesmo o cubo tendo apenas 8 cantos físicos.
   - **Falta de flexibilidade visual:** A iluminação e as transformações eram fixas no driver; não era possível criar efeitos customizados por pixel.
3. **Conceitos Fundamentais (Os 4 Pilares):**
   - **VBO (*Vertex Buffer Object*):** Array bruto de floats alocado direto na memória da GPU (VRAM) contendo posição, cor, normal e coordenadas de textura dos vértices.
   - **EBO (*Element Buffer Object*):** Array de inteiros na GPU com os **índices** que dizem quais vértices do VBO formam cada triângulo (evita repetição de vértices).
   - **VAO (*Vertex Array Object*):** Objeto gerenciador que armazena o layout de memória do VBO (*stride*, *offset*, tipos) e qual EBO está vinculado.
   - **GLSL (*OpenGL Shading Language*):** Linguagem estilo C compilada para rodar massivamente em paralelo nos núcleos da GPU (*Vertex Shader* e *Fragment Shader*).
4. **Principais Aplicações, Possibilidades e Limitações:**
   - **Aplicações:** Motores de jogos (Godot, engines próprias), CAD, visualização científica (VisPy), simuladores.
   - **Possibilidades:** Milhões de triângulos em 60+ FPS, iluminação realista por pixel.
   - **Limitações:** Mais verboso no início (exige configurar buffers e matrizes manualmente até para desenhar um único triângulo).

---

### BLOCO 2 — Funcionamento e Computação Gráfica (7 a 8 minutos)

1. **Arquitetura, Pipeline Gráfico e Como a Imagem é Gerada:**
   - **Etapa 1 (CPU $\rightarrow$ VRAM):** Na inicialização, a CPU envia os arrays NumPy para o **VBO** e **EBO** e configura o **VAO**.
   - **Etapa 2 (Vertex Shader — GLSL):** Para cada vértice único do VBO, a GPU multiplica a posição local pelas matrizes $4 \times 4$ de transformação:
     $$\mathbf{v}_{\text{clip}} = \mathbf{M}_{\text{Projection}} \cdot \mathbf{M}_{\text{View}} \cdot \mathbf{M}_{\text{Model}} \cdot \mathbf{v}_{\text{local}}$$
   - **Etapa 3 (Montagem de Primitivas via EBO + Rasterização):** A GPU lê as trincas de índices do **EBO**, monta os triângulos na tela, converte em fragmentos (candidatos a pixels) e **interpola baricentricamente** as cores e normais entre os 3 vértices.
   - **Etapa 4 (Fragment Shader — GLSL):** Calcula a cor final de cada pixel (ex: cálculo de luz Ambiente + Difusa + Especular de Phong).
   - **Etapa 5 (Framebuffer e Z-Buffer):** O teste de profundidade (`GL_DEPTH_TEST`) descarta fragmentos escondidos atrás de outros e grava o pixel final na tela.
2. **Papel da CPU vs. Papel da GPU:**
   - **CPU (Python):** Lê teclado, controla o tempo, monta as 3 matrizes $4 \times 4$ (`u_model`, `u_view`, `u_projection`) que têm apenas 16 floats cada, e dispara **uma única ordem de desenho** (`glDrawElements`).
   - **GPU (GLSL + VRAM):** Guarda toda a malha pesada no VBO/EBO e processa milhares de vértices e centenas de milhares de pixels simultaneamente em paralelo.
3. **Comparação com o Python e OpenGL das Aulas (O que é mantido, substituído ou abstraído):**

| Conceito de CG | OpenGL Clássico (Aulas) | OpenGL Moderno (Nosso Trabalho) | O que mudou? |
| :--- | :--- | :--- | :--- |
| **Envio de Vértices** | `glBegin(GL_TRIANGLES)` / `glVertex3f` / `glEnd()` | `VBO` (`glBufferData`) + `VAO` (`glVertexAttribPointer`) | **Substituído:** Sai do loop da CPU e vai para buffer fixo na GPU |
| **Reuso de Vértices** | Repetia `glVertex3f` para cada triângulo | `EBO` (`GL_ELEMENT_ARRAY_BUFFER`) + `glDrawElements` | **Novo/Otimizado:** 8 vértices + 36 índices em vez de 36 vértices |
| **Transformações** | `glTranslatef`, `glRotatef`, `glScalef` | Matriz $4 \times 4$ (`transformacoes.py`) + `uniform mat4 u_model` | **Desabstraído:** Calculamos a matriz explícita e multiplicamos no Vertex Shader |
| **Câmera e Projeção** | `gluLookAt`, `gluPerspective` | Matrizes `u_view` e `u_projection` no Vertex Shader | **Substituído:** Controle total da matemática da câmera |
| **Cores e Iluminação** | `glColor3f`, `glEnable(GL_LIGHTING)` | Atributos no VBO + cálculo no `fragment_shader.glsl` | **Programável:** Podemos programar Phong, Normais ou efeitos procedurais |
| **Z-Buffer e Janela** | `glEnable(GL_DEPTH_TEST)`, `glClear` | `glEnable(GL_DEPTH_TEST)`, `glClear` | **Mantido:** O controle do Framebuffer e Z-Buffer permanece igual |

---

### BLOCO 3 — Código, Demonstração e Conclusões (7 a 8 minutos)

1. **Estrutura Geral da Implementação:**
   - [`geometria.py`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/geometria.py): Cria os arrays NumPy `float32` (VBO) e `uint32` (EBO) para o Cubo, Octaedro e Superfície.
   - [`transformacoes.py`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/transformacoes.py): Cria as matrizes $4 \times 4$ homogêneas de Translação, Rotação, Escala, LookAt e Perspectiva.
   - [`shaders/vertex_shader.glsl`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/shaders/vertex_shader.glsl) e [`shaders/fragment_shader.glsl`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/shaders/fragment_shader.glsl): Programas executados na GPU.
   - [`main.py`](file:///home/eduzera/Desktop/Programs/Aula/Grafico/Trabalho/main.py): Inicializa o contexto OpenGL 3.3 Core, configura VAO/VBO/EBO e executa o loop de renderização.
2. **Trechos Principais do Código para Mostrar nos Slides / IDE:**
   - **Trecho 1 (`geometria.py` — linhas 23 a 49):** Mostrar que o cubo tem apenas **8 linhas** na matriz `vertices` (VBO) e **12 duplas de triângulos (36 números)** na matriz `indices` (EBO).
   - **Trecho 2 (`main.py` — função `criar_vao_vbo_ebo`):** Mostrar o `stride = 9 * 4 = 36 bytes` e os 3 `glVertexAttribPointer` (Atributo 0 = Posição no byte 0; Atributo 1 = Cor no byte 12; Atributo 2 = Normal no byte 24).
   - **Trecho 3 (`vertex_shader.glsl` e `fragment_shader.glsl`):** Mostrar `gl_Position = u_projection * u_view * worldPos;` e o cálculo de luz de Phong.
3. **Roteiro da Demonstração Prática ao Vivo (Passo a Passo de 3 minutos):**
   - **Passo 1:** Rodar o programa com o **Cubo Indexado**. Apertar **`W`** (Wireframe) e usar a tecla **`-`** para diminuir os triângulos desenhados pelo EBO até ficar só 1 triângulo, e depois **`+`** para ir montando o cubo triângulo por triângulo na frente da turma!
   - **Passo 2:** Apertar **`W`** para voltar ao preenchimento sólido e apertar **`M`** para alternar os modos do *Fragment Shader*: mostrar a interpolação pura do VBO (Modo 0), a iluminação Phong (Modo 1), as Normais em RGB (Modo 2) e o shader procedural (Modo 3).
   - **Passo 3:** Apertar **`3`** para abrir a **Malha de Superfície 16x16**, ativar o Wireframe (**`W`**) e apertar **`D`** para ligar a **Deformação de Onda Senoidal na GPU**, explicando que a CPU **não** está atualizando o VBO — é o *Vertex Shader* movendo o eixo $Y$ com $\sin(x + t)$ em tempo real!
   - **Passo 4:** Usar **`Z`/`X`** e **`F`/`V`** para demonstrar a alteração das matrizes *View* e *Projection* (FOV).
4. **Conclusões:**
   - O trio **VAO + VBO + EBO** resolve o gargalo de memória entre CPU e GPU, enquanto o **GLSL** dá liberdade matemática total sobre vértices e pixels.
   - Apesar de exigir mais código inicial que o `glBegin`/`glEnd`, toda a indústria gráfica moderna (OpenGL 3.3+, WebGL, Vulkan, WebGPU) baseia-se exatamente nesse paradigma de buffers na GPU e shaders.

