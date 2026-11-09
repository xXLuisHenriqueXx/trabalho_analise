# Caixeiro Viajante (TSP): algoritmo heurístico e algoritmo exato

Trabalho de Projeto e Análise de Algoritmos. São dois programas independentes para o problema do caixeiro viajante simétrico, além de scripts complementares para testes, contraexemplo, experimentação automatizada e visualização:

| Arquivo | Algoritmo / Função | Paradigma | Tempo | Memória |
|---|---|---|---|---|
| `heuristico.py` | Vizinho mais próximo | Guloso | O(n²) | O(n²) (matriz de distâncias) |
| `exato.py` | Held-Karp | Programação dinâmica | O(n² · 2ⁿ) | O(n · 2ⁿ) |
| `testes.py` | Testes unitários e regressão | unittest (stdlib) | < 1 s | Mínima |
| `contraexemplo.py` | Busca e validação do contraexemplo | Exaustivo / Verificação | < 1 s | Mínima |
| `experimentos.py` | Pipeline de experimentos (E1..E5) | Empírico / Autônomo | Adaptativo | O(n²) a O(n · 2ⁿ) |
| `graficos.py` | Geração de figuras e tabelas | matplotlib / numpy | ~5 s | Mínima |

O heurístico é rápido e roda em qualquer tamanho, mas não garante a rota ótima. O exato sempre encontra a rota ótima, mas só é viável com poucas cidades (até cerca de 21 em tempo razoável).

---

## Requisitos

- Python 3.8 ou superior
- Biblioteca padrão para `exato.py`, `heuristico.py`, `testes.py`, `contraexemplo.py` e `experimentos.py`
- `matplotlib` e `numpy` para `graficos.py` (instale com `pip install -r requirements.txt`)

---

## Estrutura de Pastas

```
trabalho_analise/
├── heuristico.py               # Algoritmo guloso (vizinho mais próximo)
├── exato.py                    # Algoritmo exato (Held-Karp com DP)
├── testes.py                   # Suíte de testes unitários e de regressão
├── contraexemplo.py            # Geração do contraexemplo sem empates (n=5)
├── experimentos.py             # Pipeline completo de experimentação (E1 a E5)
├── graficos.py                 # Geração automatizada de figuras e tabelas
├── requirements.txt            # Dependências opcionais para gráficos (matplotlib, numpy)
├── README.md                   # Documentação do projeto e decisões de projeto
├── trabalho_GA_PAA.pdf         # Enunciado do trabalho acadêmico
├── instances/                  # Instâncias do problema
│   └── TSP/
│       ├── berlin52.tsp.txt    (52 cidades, ótimo TSPLIB = 7542)
│       ├── st70.tsp.txt        (70 cidades, ótimo TSPLIB = 675)
│       └── pr76.tsp.txt        (76 cidades, ótimo TSPLIB = 108159)
├── resultados/                 # Dados gerados pelos experimentos
│   ├── ambiente.txt            # Especificação de hardware, SO e parâmetros
│   ├── contraexemplo.json      # Dados da instância de contraexemplo
│   ├── hk_tempo.csv            # Held-Karp: tempo, memória e razão teórica
│   ├── nn_prefixos.csv         # NN nos prefixos das instâncias reais
│   ├── nn_sintetico.csv        # NN em instâncias sintéticas uniformes
│   ├── qualidade_completas.csv # NN nas instâncias completas da TSPLIB
│   ├── qualidade_subinstancias.csv # NN vs Held-Karp nas subinstâncias
│   └── resumo.md               # Análise comparativa Teoria vs Prática
├── figuras/                    # Gráficos em PNG (200 dpi) e PDF vetorial
│   ├── hk_tempo.{png,pdf}
│   ├── hk_razao.{png,pdf}
│   ├── hk_memoria.{png,pdf}
│   ├── nn_loglog.{png,pdf}
│   ├── nn_gap_subinstancias.{png,pdf}
│   ├── nn_gap_completas.{png,pdf}
│   └── contraexemplo.{png,pdf}
└── tabelas/                    # Tabelas para relatório em Markdown e LaTeX
    ├── tempo_hk.{md,tex}
    ├── qualidade_nn_completas.{md,tex}
    └── nn_sintetico.{md,tex}
```

Os programas procuram as instâncias em `instances/TSP`, ao lado do próprio arquivo `.py`. Se elas estiverem em outro lugar, use `--pasta`. Cada arquivo de instância tem uma cidade por linha, no formato `id x y`.

---

## Como Reproduzir

### 1. Instalação das dependências
```bash
pip install -r requirements.txt
```

### 2. Executar os testes unitários
Roda a suíte de testes em menos de 1 segundo:
```bash
python testes.py
```

### 3. Gerar o contraexemplo
Encontra deterministamente a menor instância euclidiana ($n=5$) sem empates onde o NN erra o ótimo:
```bash
python contraexemplo.py
```

### 4. Executar os experimentos
- **Modo rápido (< 1 min):** Held-Karp até $k=16$, NN sintético até $n=800$:
  ```bash
  python experimentos.py --rapido
  ```
- **Modo completo:** Held-Karp até $k=22$, NN sintético até $n=3200$:
  ```bash
  python experimentos.py
  ```

### 5. Gerar os gráficos e tabelas
Lê os CSV de `resultados/` e gera todas as figuras e tabelas:
```bash
python graficos.py
```

---

## Decisões de Implementação que Afetam o Custo

### 1. Vizinho Mais Próximo (`heuristico.py`)
- **Varredura linear $O(n)$ na seleção do próximo vértice:** O grafo do TSP é completo e denso ($m = n(n-1)/2$). A utilização de uma fila de prioridade / heap binário exigiria overhead de inserção e remoção de $O(\log n)$, além do custo constante elevado de manipulação de ponteiros e tuplas na linguagem Python. A varredura direta sobre o vetor de distâncias é contígua em memória (altamente favorável a cache) e garante tempo estrito de $O(n)$ por iteração, resultando no custo global de $O(n^2)$.
- **Vetor de visitados booleano:** Implementado como lista booleana indexada `visitado = [False] * n`. A consulta e atualização são executadas em tempo estrito $O(1)$, evitando overheads de tabela de dispersão (`set`) ou remoções em listas (`list.remove`, que seria $O(n)$).
- **Matriz de distâncias pré-calculada $O(n^2)$:** Todas as distâncias euclidianas arredondadas (regra TSPLIB EUC_2D) são pré-computadas em uma matriz $n \times n$. Isso elimina o cálculo redundante de raízes quadradas e diferenças quadráticas durante a navegação do algoritmo guloso.

### 2. Held-Karp (`exato.py`)
- **Máscara de bits para conjuntos $S$:** O subconjunto de vértices visitados é representado por um inteiro em que o bit $j-1$ indica a presença da cidade $j$ (para $j \ge 1$). As operações de pertinência e exclusão de vértices são realizadas diretamente via operadores bitwise (`&`, `|`, `~`, `<<`), operando em um único ciclo de instrução de máquina ($O(1)$).
- **Vértice 0 fixado como origem e término:** Como o ciclo hamiltoniano é simétrico e fechado, a escolha do vértice inicial é arbitrária. Fixar a cidade 0 reduz o espaço de estados de $2^n \cdot n$ para $2^{n-1} \cdot n$, cortando o tempo e a memória necessários exatamente pela metade.
- **Tabelas de programação dinâmica $C$ e $P$:** As matrizes `C[S][j]` e `P[S][j]` têm dimensões $2^{n-1} \times n$. A tabela $C$ armazena o custo ótimo acumulado do caminho, enquanto $P$ armazena o predecessor (pai) imediato no caminho ótimo. Manter a tabela $P$ é indispensável para permitir a reconstrução da rota ótima, mas dobra o consumo de memória do algoritmo.
- **Reconstrução da rota pelos predecessores:** A rota final é reconstruída em tempo $O(n)$ retrocedendo pelos ponteiros da matriz $P$, partindo do estado terminal `(TODAS, j)` até a origem 0.
- **Limite de 23 cidades:** Para $n = 24$, as tabelas exigiriam $2^{23} \times 24 \approx 2 \times 10^8$ entradas em listas Python, demandando mais de 10 GB de memória RAM e levando ao esgotamento de recursos (*Out of Memory*). A imposição do limite rígido protege o sistema contra travamentos.

---

## Dois Modos de Uso dos Scripts Base

**1. Interativo:** rode sem argumentos e o programa pergunta tudo. Enter aceita o valor padrão, mostrado entre colchetes.

```bash
python heuristico.py
python exato.py
```

**2. Direto:** passe as escolhas na linha de comando. É o modo recomendado para scripts, experimentos e para o Colab.

```bash
python heuristico.py --instancia berlin52
python exato.py --instancia berlin52 --cidades 15
```

Para ver todas as opções: `python heuristico.py -h` ou `python exato.py -h`.

---

## heuristico.py: vizinho mais próximo

Começa numa cidade e vai sempre para a cidade **não visitada mais próxima**. Quando visita todas, volta para o início. Em caso de empate, escolhe a cidade de menor índice.

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--instancia` | (obrigatório*) | `berlin52`, `st70` ou `pr76` |
| `--arquivo` | (nenhum) | caminho de outro arquivo `id x y`, em vez de `--instancia` |
| `--pasta` | `instances/TSP` | pasta onde estão os arquivos de instância |
| `--cidades` | instância inteira | um número (`30`), uma lista (`10,20,30`) ou um intervalo (`5-20`). Usa as **primeiras k cidades** |
| `--inicio` | `0` | índice da cidade de partida (de 0 a n−1) |
| `--todas-partidas` | desligado | roda a partir de **todas** as cidades e mostra a melhor e a pior partida |
| `--repeticoes` | `5` | quantas vezes repetir para medir o tempo (média ± desvio padrão) |
| `--csv` | (nenhum) | salva os resultados num arquivo `.csv` |
| `--sem-rota` | desligado | não imprime a rota |

\* `--instancia` ou `--arquivo`.

---

## exato.py: Held-Karp

Programação dinâmica. Para cada conjunto S de cidades visitadas e cada cidade final j, guarda o menor custo `C(S, j)` de sair da cidade 0, passar por todas as cidades de S e terminar em j:

```
C(S, j) = min { C(S − {j}, i) + d(i, j) }   para i em S, i ≠ j
```

O conjunto S é guardado como uma máscara de bits. A rota é reconstruída seguindo, de trás para frente, de qual cidade se chegou em cada passo.

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--instancia` | (obrigatório*) | `berlin52`, `st70` ou `pr76` |
| `--arquivo` | (nenhum) | caminho de outro arquivo `id x y`, em vez de `--instancia` |
| `--pasta` | `instances/TSP` | pasta onde estão os arquivos de instância |
| `--cidades` | **obrigatório** | um número (`15`), uma lista (`10,12,14`) ou um intervalo (`5-20`). Usa as **primeiras k cidades** |
| `--repeticoes` | `5` | quantas vezes repetir para medir o tempo (média ± desvio padrão) |
| `--limite` | (nenhum) | numa sequência de tamanhos, para quando o tempo médio passar de X segundos |
| `--verificar` | desligado | confere o resultado com a força bruta (testa todas as rotas). Só até 10 cidades |
| `--forcar` | desligado | permite mais de 23 cidades. **Cuidado:** tempo e memória explodem |
| `--csv` | (nenhum) | salva os resultados num arquivo `.csv` |
| `--sem-rota` | desligado | não imprime a rota |

\* `--instancia` ou `--arquivo`.

---

## Descrição dos Arquivos de Saída

### Pasta `resultados/`
- **`ambiente.txt`**: Registro formal do ambiente computacional (SO, processador, versão do Python, data, parâmetros de execução e semente 42).
- **`contraexemplo.json`**: Detalhamento da instância mínima euclidiana ($n=5$) onde o NN não atinge a rota ótima, sem ocorrência de empates.
- **`hk_tempo.csv`**: Resultados de tempo de execução, desvio padrão amostral, repetições adaptativas, custo ótimo, razão empírica/teórica $T(k)/(k^2 \cdot 2^k)$ e pico de memória tracemalloc ($k \le 18$) para o Held-Karp.
- **`nn_prefixos.csv`**: Medições do Vizinho Mais Próximo com partida 0 em todos os prefixos ($k=5..n$) com 30 repetições e comparação percentual contra o ótimo conhecido.
- **`nn_sintetico.csv`**: Medições em instâncias sintéticas uniformes ($n=100..3200$), registrando separadamente o tempo de montagem da matriz de distâncias $O(n^2)$, o tempo do algoritmo guloso $O(n^2)$ e a memória alocada pela matriz.
- **`qualidade_completas.csv`**: Análise exaustiva de todas as cidades de partida possíveis nas instâncias completas (`berlin52`, `st70`, `pr76`) versus os valores de referência da TSPLIB.
- **`qualidade_subinstancias.csv`**: Comparação da qualidade média e da partida 0 do NN em relação à solução ótima exata do Held-Karp nas subinstâncias ($k \le 22$).
- **`resumo.md`**: Síntese analítica comparando Teoria e Prática, incluindo coeficientes de regressão log-log do NN, regressão exponencial do Held-Karp, extrapolações de tempo e identificação dos maiores tamanhos viáveis.

### Pasta `figuras/`
- **`hk_tempo.{png,pdf}`**: Curva de tempo de execução do Held-Karp com escala logarítmica no eixo y, barras de erro (desvio padrão) e curva teórica ajustada $c \cdot k^2 2^k$.
- **`hk_razao.{png,pdf}`**: Gráfico da razão teórica $T(k)/(k^2 \cdot 2^k)$, demonstrando a estabilização assintótica da constante.
- **`hk_memoria.{png,pdf}`**: Consumo de pico de memória (MB) do Held-Karp em escala logarítmica comparado com a curva teórica $k \cdot 2^k$.
- **`nn_loglog.{png,pdf}`**: Escala log-log de tempo vs. tamanho para o Vizinho Mais Próximo, com reta ajustada por regressão linear e reta teórica $O(n^2)$.
- **`nn_gap_subinstancias.{png,pdf}`**: Dispersão percentual acima do ótimo para as subinstâncias avaliadas.
- **`nn_gap_completas.{png,pdf}`**: Gráfico de barras comparando a melhor partida, partida 0, média e pior partida em relação aos ótimos oficiais da TSPLIB.
- **`contraexemplo.{png,pdf}`**: Visualização gráfica comparativa das rotas do NN e do Held-Karp lado a lado para o contraexemplo de 5 cidades.

### Pasta `tabelas/`
- **`tempo_hk.{md,tex}`**: Tabela de desempenho detalhada do Held-Karp formatada em Markdown e LaTeX (padrão `booktabs`).
- **`qualidade_nn_completas.{md,tex}`**: Tabela consolidada da heurística nas instâncias completas da TSPLIB em Markdown e LaTeX.
- **`nn_sintetico.{md,tex}`**: Tabela de escalabilidade do NN em instâncias sintéticas em Markdown e LaTeX.
