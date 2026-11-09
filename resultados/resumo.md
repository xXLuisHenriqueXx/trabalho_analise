# Resumo Comparativo: Teoria vs. Prática no TSP

## 1. Algoritmo Heurístico: Vizinho Mais Próximo (Guloso)

- **Complexidade teórica:** O(n²) de tempo e O(n²) de memória (matriz de distâncias).
- **Ajuste empírico log-log (tempo × n):** inclinação = **1.8571** (esperado ≈ 2.0000), com R² = **0.9982**.
- **Maior tamanho sintético com tempo ≤ 1,0 s:** n = **800** cidades.
- **Qualidade média nas subinstâncias (k ≤ 16):**
  - Partida 0: **11.01%** acima do ótimo do Held-Karp.
  - Média de todas as partidas: **12.86%** acima do ótimo.
- **Qualidade nas instâncias completas (TSPLIB):**
  - Partida 0: gap médio = **27.97%**.
  - Melhor partida: gap médio = **15.81%**.

## 2. Algoritmo Exato: Held-Karp (Programação Dinâmica)

- **Complexidade teórica:** O(n² · 2ⁿ) de tempo e O(n · 2ⁿ) de memória.
- **Regressão de log₂(tempo) × k:** inclinação = **1.2941**, intercepto = **-21.6610**, R² = **0.9994**.
- **Fator empírico médio de crescimento por cidade a mais:** **2.49×** (teórico assintótico ≈ 2,2×).
- **Maior k resolvido em tempo razoável (≤ 60.0 s):** k = **16** cidades.

## 3. Extrapolação do Tempo de Execução do Held-Karp

> [!WARNING]
> Os valores a seguir são **EXTRAPOLAÇÕES TEÓRICAS/EMPÍRICAS** obtidas a partir do modelo de regressão.

| Cidades (k) | Tempo Extrapolado Estimado | Classificação |
|---|---|---|
| **23** | 4.58 min (275.0 s) | **EXTRAPOLAÇÃO** |
| **25** | 27.56 min (1653.6 s) | **EXTRAPOLAÇÃO** |
| **30** | 1.70 dias | **EXTRAPOLAÇÃO** |

## 4. Conclusão da Comparação Teoria vs. Prática

1. **Concordância da ordem de grandeza assintótica:** O expoente experimental do Vizinho Mais Próximo reproduz com fidelidade a curva quadrática O(n²), enquanto o Held-Karp confirma o crescimento exponencial intrínseco de ~2,2× a cada vértice inserido.
2. **Barreira da computabilidade prática:** Enquanto o algoritmo guloso processa milhares de cidades em frações de segundo com erro médio na faixa de 10% a 20%, o algoritmo exato atinge o limite do tempo aceitável em torno de 20 a 22 cidades, tornando-se inviável computacionalmente acima de k=23 sem técnicas adicionais de branch-and-cut.
