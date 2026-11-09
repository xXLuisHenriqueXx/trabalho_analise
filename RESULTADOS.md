### 1. Lista de Arquivos Criados e Estrutura do Projeto

• Código-fonte:
• testes.py: Suíte de testes unitários e de regressão (unittest, stdlib, tempo de execução < 0,5 s).
• contraexemplo.py: Busca determinística e validação da menor instância euclidiana (n = 5) sem empates em nenhum
passo.
• experimentos.py: Automação completa dos experimentos (E1 a E5) com repetições adaptativas, flush linha a linha
e perfil de memória com tracemalloc.
• graficos.py: Gerador das 7 figuras em PNG (200 dpi) e PDF vetorial e das 3 tabelas em Markdown e LaTeX
(booktabs).
• requirements.txt: Especificação de dependências (matplotlib e numpy).
• Dados experimentais (resultados/):
• ambiente.txt, contraexemplo.json, hk_tempo.csv, nn_prefixos.csv, nn_sintetico.csv, qualidade_completas.csv,
qualidade_subinstancias.csv, resumo.md.
• Figuras geradas (figuras/):
• hk_tempo.{png,pdf}, hk_razao.{png,pdf}, hk_memoria.{png,pdf}, nn_loglog.{png,pdf}, nn_gap_subinstancias.{png,
pdf}, nn_gap_completas.{png,pdf}, contraexemplo.{png,pdf}.
• Tabelas para relatório (tabelas/):
• tempo_hk.{md,tex}, qualidade_nn_completas.{md,tex}, nn_sintetico.{md,tex}.
• Documentação:
• README.md atualizado com instruções de reprodução, detalhamento dos arquivos e análise aprofundada das
decisões de implementação que afetam o custo.

──────

### 2. Tabela de Resultados Síntese

Métrica / Aspecto │ Resultado Obtido │ Referência Teórica / Observação
──────────────────────────────────────┼──────────────────────────────────────┼──────────────────────────────────────
Contraexemplo encontrado │ n = 5 cidades em grade 1D: [(3,0), │ Sem nenhum empate nos passos; Rota
│ (0,0), (1,0), (4,0), (8,0)] │ NN: [0,3,2,1,4] (custo 18) vs.
│ │ Ótimo: [0,4,3,2,1] (custo 16,
│ │ +12,5%)
Maior k do Held-Karp (≤ 60 s) │ k = 22 cidades │ Tempo médio no k = 22: ~44 s a 46 s
│ │ (próximo do limite de 60 s)
Fator médio de crescimento HK │ 2, 37 × por cidade a mais │ Esperado teoricamente ≈ 2, 2 × (R² =
│ │ 0, 9987)
Extrapolações Held-Karp │ k = 23: 2,05 min | k = 25: 11,11 min │ Marcadas expressamente como
│ | k = 30: 12,72 horas │ EXTRAPOLAÇÃO no resumo
Inclinação log-log do NN (tempo × n) │ 1, 9521 │ Esperado assintótico ≈ 2, 0000
│ │ (O(n²), com R² = 0, 9974)
Maior n do NN com tempo ≤ 1 s │ n = 3200 cidades │ Tempo médio para n = 3200: 0,3368 s
│ │ (matriz: 1,46 s)
Gap médio do NN nas subinstâncias (k │ 13, 29% (partida 0) e 14, 74% (média │ Variação típica em instâncias
≤ 22) │ partidas) │ métricas
Gap do NN nas completas (TSPLIB) │ Partida 0: 27, 97% | Melhor partida: │ berlin52: +8,47% (melhor) a +36,54%
│ 15, 81% │ (pior)
──────

### 3. Comandos para Reproduzir

    # 1. Instalar dependências (apenas para geração gráfica)
    pip install -r requirements.txt

    # 2. Executar suíte de testes unitários (< 0,5 s)
    python testes.py

    # 3. Gerar e validar o contraexemplo determinístico (< 1 s)
    python contraexemplo.py

    # 4. Modo Rápido dos experimentos (< 1 min, k até 16, n até 800)
    python experimentos.py --rapido

    # 5. Modo Completo dos experimentos (k até 22, n até 3200)
    python experimentos.py

    # 6. Gerar todas as figuras e tabelas (lê a pasta resultados/)
    python graficos.py

──────

### 4. Desvios das Regras

• Nenhum desvio: A lógica original de exato.py e heuristico.py foi mantida intacta; todas as novas rotinas importam
as funções originais; foi mantido o determinismo absoluto com random.Random(42); medições separadas de tempo (time.
perf_counter) e memória (tracemalloc); commits locais individuais realizados por fase sem push remoto.
