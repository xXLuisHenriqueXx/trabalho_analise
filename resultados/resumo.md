# Resumo Comparativo: Teoria vs. Prática no TSP

## 1. Algoritmo Heurístico: Vizinho Mais Próximo (Guloso)

- **Complexidade teórica:** O(n²) de tempo e O(n²) de memória (matriz de distâncias).
- **Ajuste empírico log-log (tempo × n):** inclinação = **1.9521** (esperado ≈ 2.0000), com R² = **0.9974**.
- **Maior tamanho sintético com tempo ≤ 1,0 s:** n = **3200** cidades.
- **Qualidade média nas subinstâncias (k ≤ 22):**
  - Partida 0: **13.29%** acima do ótimo do Held-Karp.
  - Média de todas as partidas: **14.74%** acima do ótimo.
- **Qualidade nas instâncias completas (TSPLIB):**
  - Partida 0: gap médio = **27.97%**.
  - Melhor partida: gap médio = **15.81%**.

## 2. Algoritmo Exato: Held-Karp (Programação Dinâmica)

- **Complexidade teórica:** O(n² · 2ⁿ) de tempo e O(n · 2ⁿ) de memória.
- **Regressão de log₂(tempo) × k:** inclinação = **1.2203**, intercepto = **-21.1278**, R² = **0.9987**.
- **Fator empírico médio de crescimento por cidade a mais:** **2.37×** (teórico assintótico ≈ 2,2×).
- **Maior k resolvido em tempo razoável (≤ 60.0 s):** k = **22** cidades.

## 3. Extrapolação do Tempo de Execução do Held-Karp

> [!WARNING]
> Os valores a seguir são **EXTRAPOLAÇÕES TEÓRICAS/EMPÍRICAS** obtidas a partir do modelo de regressão.

| Cidades (k) | Tempo Extrapolado Estimado | Classificação |
|---|---|---|
| **23** | 2.05 min (122.8 s) | **EXTRAPOLAÇÃO** |
| **25** | 11.11 min (666.7 s) | **EXTRAPOLAÇÃO** |
| **30** | 12.72 h (45783 s) | **EXTRAPOLAÇÃO** |

## 4. Conclusão da Comparação Teoria vs. Prática

1. **Concordância da ordem de grandeza assintótica:** O expoente experimental do Vizinho Mais Próximo reproduz com fidelidade a curva quadrática O(n²), enquanto o Held-Karp confirma o crescimento exponencial intrínseco de ~2,2× a cada vértice inserido.
2. **Barreira da computabilidade prática:** Enquanto o algoritmo guloso processa milhares de cidades em frações de segundo com erro médio na faixa de 10% a 20%, o algoritmo exato atinge o limite do tempo aceitável em torno de 20 a 22 cidades, tornando-se inviável computacionalmente acima de k=23 sem técnicas adicionais de branch-and-cut.
