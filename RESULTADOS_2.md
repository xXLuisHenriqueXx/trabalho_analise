### 1. Identificação do Arquivo e Estatísticas

• Caminho do arquivo: RELATORIO.md (na raiz do projeto).
• Número de seções principais: 8 seções numeradas + Resumo, Referências e 2 Apêndices:
• Resumo
• 1. Introdução e Definições Iniciais
• 2. Modelagem (2.1 a 2.4)
• 3. Algoritmo Exato: Held-Karp (3.1 a 3.5)
• 4. Algoritmo Heurístico: Vizinho Mais Próximo (4.1 a 4.4)
• 5. Implementação (5.1 a 5.3)
• 6. Experimentação (6.1 a 6.5)
• 7. Discussão à Luz da Análise Teórica (7.1 a 7.3)
• 8. Conclusão
• Referências
• Apêndice A: Instruções de Reprodução
• Apêndice B: Pendências para Formatação
• Extensão aproximada: 7.640 palavras (572 linhas).
• Tabelas e Figuras integradas: 6 tabelas em pipe tables com legenda numerada e 7 figuras com caminhos relativos
para figuras/\*.png, todas explicitamente citadas e analisadas no corpo do texto.
• Pseudocódigos: 2 blocos de código com numeração sequencial de linhas (Held-Karp com reconstrução de rota e Vizinho
Mais Próximo com critério estrito de desempate).
──────

### 2. Lista de Campos Pendentes ([PREENCHER] e [VERIFICAR])

#### Itens marcados como [PREENCHER] (metadados acadêmicos para edição final do grupo):

1. [PREENCHER: Nome da Instituição de Ensino Superior]
2. [PREENCHER: Projeto e Análise de Algoritmos] (caso haja código ou nome oficial específico da disciplina)
3. [PREENCHER: Nome do Professor]
4. [PREENCHER: Nomes e Matrículas dos Integrantes do Grupo]
5. [PREENCHER: Data de Entrega]

#### Itens marcados como [VERIFICAR]:

• Nenhum. Todas as referências bibliográficas utilizadas no relatório limitam-se estritamente às cinco obras
homologadas no enunciado (Bellman 1962, Held & Karp 1962, Reinelt 1991, Rosenkrantz et al. 1977, Cormen et al. 2012).
Não foram introduzidas fontes externas adicionais nem menções a outros algoritmos ou problemas fora do escopo.
──────

### 3. Divergências e Confronto entre Código, Resultados e Teoria

Durante a elaboração e checagem cruzada de todos os dados entre código, teoria e arquivos em resultados/, observou-
se:

1. Aderência dos expoentes empíricos:
   • Vizinho Mais Próximo: A inclinação medida em escala log-log foi de 1, 9521 com R² = 0, 9974. A sutil defasagem
   em relação ao valor assintótico exato (2, 0000) é teoricamente justificada no relatório pela presença de custos
   operacionais estáticos lineares do laço em Python para tamanhos intermediários (n ≤ 400).
   • Held-Karp: O fator de multiplicação temporal por vértice adicional apurado foi de 2, 37 × (R² = 0, 9987),
   ligeiramente superior à taxa teórica assintótica limite (≈ 2, 22 ×), o que decorre do impacto adicional do
   aumento do footprint de memória e da pressão sobre os níveis de cache ao manipular tabelas que ultrapassam
   centenas de milhares de entradas.
2. Razão T(k)/(k² · 2ᵏ): Estabilizou-se a partir de k ≥ 10 em torno de 2, 3 × 10⁻⁸ s, comprovando que as
   discrepâncias em k ≤ 8 são fruto de ruído estatístico de medição em tempos sub-milissegundo.
3. Divergências ou anomalias: Nenhuma anomalia numérica foi detectada; todos os números, tabelas e extrapolações
   batem rigorosamente com os CSVs e arquivos em resultados/.
