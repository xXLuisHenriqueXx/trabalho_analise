# Caixeiro Viajante (TSP): algoritmo heurístico e algoritmo exato

Trabalho de Projeto e Análise de Algoritmos. São dois programas independentes para o problema do caixeiro viajante simétrico:

| Arquivo | Algoritmo | Paradigma | Tempo | Memória |
|---|---|---|---|---|
| `heuristico.py` | Vizinho mais próximo | Guloso | O(n²) | O(n²) (matriz de distâncias) |
| `exato.py` | Held-Karp | Programação dinâmica | O(n² · 2ⁿ) | O(n · 2ⁿ) |

O heurístico é rápido e roda em qualquer tamanho, mas não garante a rota ótima. O exato sempre encontra a rota ótima, mas só é viável com poucas cidades (até cerca de 21 em tempo razoável).

---

## Requisitos

- Python 3.8 ou superior
- Só a biblioteca padrão do Python, nada para instalar

## Estrutura da pasta

```
Trabalho_aa/
├── heuristico.py
├── exato.py
├── README.md
└── instances/
    └── TSP/
        ├── berlin52.tsp.txt   (52 cidades, ótimo = 7542)
        ├── st70.tsp.txt       (70 cidades, ótimo = 675)
        └── pr76.tsp.txt       (76 cidades, ótimo = 108159)
```

Os programas procuram as instâncias em `instances/TSP`, ao lado do próprio arquivo `.py`. Se elas estiverem em outro lugar, use `--pasta`.

Cada arquivo de instância tem uma cidade por linha, no formato `id x y`.

---

## Dois modos de uso

**1. Interativo:** rode sem argumentos e o programa pergunta tudo. Enter aceita o valor padrão, mostrado entre colchetes.

```
python heuristico.py
python exato.py
```

**2. Direto:** passe as escolhas na linha de comando. É o modo recomendado para scripts, experimentos e para o Colab.

```
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

### Exemplos

```
# instância inteira, partida 0 (compara com o ótimo da TSPLIB)
python heuristico.py --instancia berlin52

# 30 primeiras cidades do st70, partindo da cidade de índice 5
python heuristico.py --instancia st70 --cidades 30 --inicio 5

# testar todas as partidas no pr76
python heuristico.py --instancia pr76 --todas-partidas

# vários tamanhos, 10 repetições cada, salvando em CSV
python heuristico.py --instancia pr76 --cidades 5-76 --repeticoes 10 --csv vizinho.csv
```

### Exemplo de saída

```
=== Vizinho mais próximo | berlin52 | 52 cidades ===
partida = 0 | custo = 8980
tempo = 0.000077 ± 0.000006 s (5 repetições)
ótimo TSPLIB = 7542 | acima do ótimo = 19.07%
rota (índices): [0, 21, 48, 31, 35, ...]
```

O ótimo da TSPLIB e a diferença percentual só aparecem quando a instância é usada **inteira**.

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

### Exemplos

```
# 15 primeiras cidades do berlin52
python exato.py --instancia berlin52 --cidades 15

# conferir com a força bruta de 4 a 9 cidades
python exato.py --instancia berlin52 --cidades 4-9 --verificar

# sequência de tamanhos, parando se passar de 60 s, salvando em CSV
python exato.py --instancia berlin52 --cidades 5-22 --repeticoes 3 --limite 60 --csv held_karp.csv
```

### Exemplo de saída

```
=== Held-Karp | berlin52 | 12 cidades ===
custo ótimo = 4056 | rota coerente: True
tempo = 0.014279 ± 0.000318 s (3 repetições)
rota (índices): [0, 4, 5, 3, 11, 10, 9, 8, 7, 2, 6, 1]
```

`rota coerente: True` quer dizer que o custo calculado a partir da rota devolvida é igual ao custo ótimo encontrado.

### Quanto tempo leva

Medido no Colab com as primeiras k cidades do berlin52:

| Cidades | Tempo médio |
|---|---|
| 12 | 0,05 s |
| 16 | 0,99 s |
| 18 | 4,75 s |
| 20 | 22,6 s |
| 21 | 50,7 s |
| 22 | 109,3 s |

O tempo cresce cerca de 2,2 vezes a cada cidade a mais, como prevê o O(n² · 2ⁿ).

---

## Colunas do CSV

**heuristico.py:** `instancia`, `cidades`, `partida`, `repeticoes`, `tempo_medio_s`, `tempo_desvio_s`, `custo`, `otimo_TSPLIB`, `acima_do_otimo_pct`, `rota`.

Com `--todas-partidas`, também aparecem `pior_custo` e `pior_partida`.

**exato.py:** `instancia`, `cidades`, `repeticoes`, `tempo_medio_s`, `tempo_desvio_s`, `custo_otimo`, `rota_coerente`, `rota`.

Com `--verificar`, também aparecem `forca_bruta` e `igual_forca_bruta`.

Os tempos estão em segundos. Cada linha do CSV corresponde a um tamanho testado.

---

## Usando no Google Colab

1. Coloque `heuristico.py`, `exato.py` e a pasta `instances` na mesma pasta do Google Drive (por exemplo, `MyDrive/PAA`).
2. Monte o Drive:

   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

3. Rode no **modo direto**, porque o modo interativo não funciona bem no Colab:

   ```
   !python /content/drive/MyDrive/PAA/heuristico.py --instancia berlin52
   !python /content/drive/MyDrive/PAA/exato.py --instancia berlin52 --cidades 15
   ```

---

## Observações importantes

- **Numeração das cidades:** os programas usam o **índice 0 a n−1**. A cidade 1 do arquivo é o índice 0, a cidade 2 é o índice 1, e assim por diante.
- **Distância:** é a euclidiana arredondada para o inteiro mais próximo, `int(√(dx² + dy²) + 0,5)`. É a regra EUC_2D da TSPLIB, a mesma usada nos ótimos publicados. Com essa regra, a rota ótima oficial do berlin52 custa exatamente 7542.
- **Sub-instâncias:** `--cidades k` usa as **primeiras k cidades** do arquivo. Nessas sub-instâncias não existe ótimo publicado. A referência é o próprio Held-Karp, que é exato.
- **Partida:** o resultado do vizinho mais próximo depende da cidade de partida. No berlin52, ele vai de 8,47% (partida 39) a 36,54% (partida 20) acima do ótimo. O Held-Karp sempre parte da cidade 0. Como a rota é um ciclo, o custo ótimo é o mesmo para qualquer partida.
- **Limite do Held-Karp:** acima de 23 cidades o programa recusa, a não ser com `--forcar`. A tabela tem cerca de n · 2ⁿ⁻¹ posições, e com 25 cidades isso já passa de 7 GB de memória.
- **Valores ótimos:** TSPLIB, Universidade de Heidelberg. Reinelt, G. *TSPLIB: A Traveling Salesman Problem Library*. ORSA Journal on Computing, 3(4), 1991.
