"""
Geração de figuras e tabelas prontas para o relatório e apresentação.
Lê os arquivos CSV e JSON em resultados/ e gera:
  - figuras/*.png (200 dpi) e figuras/*.pdf (vetorial)
  - tabelas/*.md (Markdown) e tabelas/*.tex (LaTeX com booktabs)
Uso: python graficos.py [--resultados resultados] [--figuras figuras] [--tabelas tabelas]
"""

import argparse
import csv
import json
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


# Paleta e configuração visual consistente
CORES = {
    'berlin52': '#1f77b4',  # azul
    'st70': '#2ca02c',      # verde
    'pr76': '#d62728',      # vermelho
    'nn': '#ff7f0e',        # laranja
    'teorico': '#333333',   # cinza escuro / preto
    'p0': '#1f77b4',        # azul
    'melhor': '#2ca02c',    # verde
    'pior': '#d62728',      # vermelho
    'media': '#9467bd',     # roxo
}

MARCADORES = {
    'berlin52': 'o',
    'st70': 's',
    'pr76': '^',
}


def configurar_estilo():
    plt.rcParams.update({
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'figure.dpi': 200,
        'savefig.dpi': 200,
        'axes.grid': True,
        'grid.alpha': 0.4,
        'grid.linestyle': '--',
    })


def salvar_figura(fig, pasta_figuras, nome_base):
    caminho_png = os.path.join(pasta_figuras, f"{nome_base}.png")
    caminho_pdf = os.path.join(pasta_figuras, f"{nome_base}.pdf")
    fig.savefig(caminho_png, dpi=200, bbox_inches='tight')
    fig.savefig(caminho_pdf, bbox_inches='tight')
    plt.close(fig)
    print(f"  Figura gerada: {caminho_png} e {caminho_pdf}")


# ---------------------------------------------------------------- GRÁFICOS

def grafico_1_hk_tempo(pasta_resultados, pasta_figuras):
    """1. hk_tempo.* : tempo × k, eixo y log, séries por instância com barras de erro e curva teórica ajustada."""
    caminho_csv = os.path.join(pasta_resultados, 'hk_tempo.csv')
    if not os.path.exists(caminho_csv):
        print(f"Arquivo não encontrado: {caminho_csv}")
        return

    dados = {}
    with open(caminho_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            inst = r['instancia']
            dados.setdefault(inst, []).append({
                'k': int(r['cidades']),
                'tempo': float(r['tempo_medio_s']),
                'desvio': float(r['tempo_desvio_s']),
                'razao': float(r['razao_teorica']),
            })

    fig, ax = plt.subplots(figsize=(8, 5))

    todas_razoes = []
    max_k = 0
    min_k = 100

    for inst, itens in dados.items():
        itens.sort(key=lambda x: x['k'])
        ks = [x['k'] for x in itens]
        tempos = [x['tempo'] for x in itens]
        desvios = [x['desvio'] for x in itens]
        todas_razoes.extend([x['razao'] for x in itens if x['k'] >= 10])

        min_k = min(min_k, min(ks))
        max_k = max(max_k, max(ks))

        ax.errorbar(
            ks, tempos, yerr=desvios,
            label=f"{inst}",
            color=CORES.get(inst, '#333'),
            marker=MARCADORES.get(inst, 'o'),
            capsize=3, capthick=1, elinewidth=1,
            linewidth=1.5, markersize=5
        )

    # Curva teórica ajustada: c * k^2 * 2^k
    if todas_razoes:
        c_medio = np.median(todas_razoes)
        ks_teoricos = np.linspace(min_k, max_k, 200)
        tempos_teoricos = c_medio * (ks_teoricos ** 2) * (2.0 ** ks_teoricos)
        ax.plot(
            ks_teoricos, tempos_teoricos,
            'k--', linewidth=1.5,
            label=f"Teórico ajustado $c \\cdot k^2 2^k$ ($c={c_medio:.2e}$)"
        )

    ax.set_yscale('log')
    ax.set_xlabel("Número de cidades ($k$)")
    ax.set_ylabel("Tempo de execução médio (s) [escala log]")
    ax.set_title("Held-Karp: Tempo de Execução vs. Número de Cidades ($k$)")
    ax.legend(loc='upper left')

    salvar_figura(fig, pasta_figuras, 'hk_tempo')


def grafico_2_hk_razao(pasta_resultados, pasta_figuras):
    """2. hk_razao.* : tempo/(k²·2^k) × k (deve ficar ~constante)."""
    caminho_csv = os.path.join(pasta_resultados, 'hk_tempo.csv')
    if not os.path.exists(caminho_csv):
        return

    dados = {}
    with open(caminho_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            inst = r['instancia']
            dados.setdefault(inst, []).append({
                'k': int(r['cidades']),
                'razao': float(r['razao_teorica']),
            })

    fig, ax = plt.subplots(figsize=(8, 5))

    todas_razoes = []
    for inst, itens in dados.items():
        itens.sort(key=lambda x: x['k'])
        ks = [x['k'] for x in itens]
        razoes = [x['razao'] for x in itens]
        todas_razoes.extend([x['razao'] for x in itens if x['k'] >= 10])

        ax.plot(
            ks, razoes,
            label=f"{inst}",
            color=CORES.get(inst, '#333'),
            marker=MARCADORES.get(inst, 'o'),
            linewidth=1.5, markersize=5
        )

    if todas_razoes:
        r_media = float(np.mean(todas_razoes))
        ax.axhline(
            r_media, color='black', linestyle=':', linewidth=1.5,
            label=f"Média assintótica ($k \\geq 10$): {r_media:.2e}"
        )

    ax.set_xlabel("Número de cidades ($k$)")
    ax.set_ylabel(r"Razão $\frac{T(k)}{k^2 \cdot 2^k}$ (s)")
    ax.set_title(r"Held-Karp: Verificação da Constante Assintótica $\frac{T(k)}{k^2 \cdot 2^k}$")
    ax.ticklabel_format(style='sci', scilimits=(0, 0), axis='y')
    ax.legend(loc='upper right')

    salvar_figura(fig, pasta_figuras, 'hk_razao')


def grafico_3_hk_memoria(pasta_resultados, pasta_figuras):
    """3. hk_memoria.* : pico de memória × k, escala log, com referência n·2ⁿ."""
    caminho_csv = os.path.join(pasta_resultados, 'hk_tempo.csv')
    if not os.path.exists(caminho_csv):
        return

    dados = {}
    with open(caminho_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            mem = r['pico_memoria_mb']
            if mem != "":
                inst = r['instancia']
                dados.setdefault(inst, []).append({
                    'k': int(r['cidades']),
                    'mem': float(mem),
                })

    fig, ax = plt.subplots(figsize=(8, 5))

    razoes_mem = []
    min_k, max_k = 100, 0
    for inst, itens in dados.items():
        itens.sort(key=lambda x: x['k'])
        ks = [x['k'] for x in itens]
        mems = [x['mem'] for x in itens]
        for x in itens:
            if x['k'] >= 10:
                razoes_mem.append(x['mem'] / (x['k'] * (2 ** x['k'])))

        min_k = min(min_k, min(ks))
        max_k = max(max_k, max(ks))

        ax.plot(
            ks, mems,
            label=f"{inst}",
            color=CORES.get(inst, '#333'),
            marker=MARCADORES.get(inst, 'o'),
            linewidth=1.5, markersize=5
        )

    if razoes_mem:
        c_mem = float(np.median(razoes_mem))
        ks_ref = np.linspace(min_k, max_k, 100)
        mems_ref = c_mem * ks_ref * (2.0 ** ks_ref)
        ax.plot(
            ks_ref, mems_ref,
            'k--', linewidth=1.5,
            label=r"Referência teórica $\propto k \cdot 2^k$"
        )

    ax.set_yscale('log')
    ax.set_xlabel("Número de cidades ($k$)")
    ax.set_ylabel("Pico de Memória (MB) [escala log]")
    ax.set_title("Held-Karp: Consumo de Memória vs. Tamanho ($k \\leq 18$)")
    ax.legend(loc='upper left')

    salvar_figura(fig, pasta_figuras, 'hk_memoria')


def grafico_4_nn_loglog(pasta_resultados, pasta_figuras):
    """4. nn_loglog.* : tempo × n em log-log (sintético + prefixos), com reta ajustada e referência n²."""
    caminho_sintetico = os.path.join(pasta_resultados, 'nn_sintetico.csv')
    caminho_prefixos = os.path.join(pasta_resultados, 'nn_prefixos.csv')

    fig, ax = plt.subplots(figsize=(8, 5))

    ns_sint, tempos_sint = [], []
    if os.path.exists(caminho_sintetico):
        with open(caminho_sintetico, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                ns_sint.append(int(r['n']))
                tempos_sint.append(float(r['tempo_nn_medio_s']))

    # Prefixos
    prefixos = {}
    if os.path.exists(caminho_prefixos):
        with open(caminho_prefixos, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                inst = r['instancia']
                prefixos.setdefault(inst, []).append((int(r['cidades']), float(r['tempo_medio_s'])))

    for inst, pts in prefixos.items():
        pts.sort(key=lambda x: x[0])
        ks = [x[0] for x in pts]
        ts = [x[1] for x in pts]
        ax.scatter(
            ks, ts,
            color=CORES.get(inst, '#777'),
            marker=MARCADORES.get(inst, 'o'),
            alpha=0.6, s=25,
            label=f"Prefixos {inst}"
        )

    if ns_sint:
        ax.scatter(
            ns_sint, tempos_sint,
            color='#ff7f0e', marker='D', s=45, zorder=5,
            label="Sintético uniforme [0, 1000]²"
        )

        # Ajuste log-log nos sintéticos
        log_ns = np.log(ns_sint)
        log_ts = np.log(tempos_sint)
        poly = np.polyfit(log_ns, log_ts, 1)
        slope = poly[0]
        intercept = poly[1]

        # R2
        preds = np.polyval(poly, log_ns)
        r2 = 1.0 - (np.sum((log_ts - preds) ** 2) / np.sum((log_ts - np.mean(log_ts)) ** 2))

        n_grid = np.geomspace(min(ns_sint[0], 5), max(ns_sint[-1], 3200), 200)
        t_ajustado = np.exp(intercept) * (n_grid ** slope)

        ax.plot(
            n_grid, t_ajustado,
            'r-', linewidth=1.8,
            label=f"Ajuste log-log: $t \\propto n^{{{slope:.2f}}}$ ($R^2={r2:.4f}$)"
        )

        # Referência teórica n^2
        c_quad = np.exp(intercept)
        t_ref_quad = c_quad * (n_grid ** 2.0)
        ax.plot(
            n_grid, t_ref_quad,
            'k--', linewidth=1.2, alpha=0.7,
            label=r"Referência teórica $O(n^2)$"
        )

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Número de Cidades ($n$) [escala log]")
    ax.set_ylabel("Tempo de Execução do NN (s) [escala log]")
    ax.set_title("Vizinho Mais Próximo: Escala de Tempo em Log-Log")
    ax.legend(loc='upper left')

    salvar_figura(fig, pasta_figuras, 'nn_loglog')


def grafico_5_nn_gap_subinstancias(pasta_resultados, pasta_figuras):
    """5. nn_gap_subinstancias.* : % acima do ótimo × k (partida 0 e média das partidas)."""
    caminho_csv = os.path.join(pasta_resultados, 'qualidade_subinstancias.csv')
    if not os.path.exists(caminho_csv):
        return

    dados = {}
    with open(caminho_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            inst = r['instancia']
            dados.setdefault(inst, []).append({
                'k': int(r['cidades']),
                'pct_p0': float(r['pct_acima_partida_0']),
                'pct_media': float(r['pct_acima_media']),
                'pct_melhor': float(r['pct_acima_melhor']),
            })

    fig, ax = plt.subplots(figsize=(8, 5))

    for inst, itens in dados.items():
        itens.sort(key=lambda x: x['k'])
        ks = [x['k'] for x in itens]
        p0 = [x['pct_p0'] for x in itens]
        media = [x['pct_media'] for x in itens]

        cor = CORES.get(inst, '#333')
        ax.plot(ks, p0, marker='o', markersize=4, linewidth=1.5, color=cor, label=f"{inst} (Partida 0)")
        ax.plot(ks, media, marker='x', markersize=4, linewidth=1.2, linestyle='--', color=cor, alpha=0.7, label=f"{inst} (Média partidas)")

    ax.axhline(0, color='black', linestyle='-', linewidth=1.0)
    ax.set_xlabel("Número de cidades ($k$)")
    ax.set_ylabel("% Acima do Ótimo do Held-Karp")
    ax.set_title("Qualidade da Heurística NN em Subinstâncias ($k \\leq 22$)")
    ax.legend(loc='upper right', ncol=2, fontsize=8.5)

    salvar_figura(fig, pasta_figuras, 'nn_gap_subinstancias')


def grafico_6_nn_gap_completas(pasta_resultados, pasta_figuras):
    """6. nn_gap_completas.* : barras (melhor, partida 0, pior) vs ótimo TSPLIB por instância."""
    caminho_csv = os.path.join(pasta_resultados, 'qualidade_completas.csv')
    if not os.path.exists(caminho_csv):
        return

    instancias = []
    pct_melhor = []
    pct_p0 = []
    pct_pior = []
    pct_media = []

    with open(caminho_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            instancias.append(f"{r['instancia']} ({r['cidades']} cid.)")
            pct_melhor.append(float(r['pct_acima_melhor']))
            pct_p0.append(float(r['pct_acima_partida_0']))
            pct_pior.append(float(r['pct_acima_pior']))
            pct_media.append(float(r['pct_acima_media']))

    x = np.arange(len(instancias))
    largura = 0.2

    fig, ax = plt.subplots(figsize=(8, 5))

    b1 = ax.bar(x - 1.5 * largura, pct_melhor, largura, label='Melhor Partida', color=CORES['melhor'])
    b2 = ax.bar(x - 0.5 * largura, pct_p0, largura, label='Partida 0 (Padrão)', color=CORES['p0'])
    b3 = ax.bar(x + 0.5 * largura, pct_media, largura, label='Média das Partidas', color=CORES['media'])
    b4 = ax.bar(x + 1.5 * largura, pct_pior, largura, label='Pior Partida', color=CORES['pior'])

    # Rótulos de valor nas barras
    for barras in (b1, b2, b3, b4):
        for b in barras:
            altura = b.get_height()
            ax.annotate(
                f"{altura:.1f}%",
                xy=(b.get_x() + b.get_width() / 2, altura),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8, rotation=0
            )

    ax.set_xticks(x)
    ax.set_xticklabels(instancias)
    ax.set_ylabel("% Acima do Ótimo TSPLIB")
    ax.set_title("Qualidade da Heurística NN nas Instâncias Completas da TSPLIB")
    ax.legend(loc='upper left')

    # Margem superior para os números não cortarem
    lim_atual = ax.get_ylim()
    ax.set_ylim(0, lim_atual[1] * 1.15)

    salvar_figura(fig, pasta_figuras, 'nn_gap_completas')


def grafico_7_contraexemplo(pasta_resultados, pasta_figuras):
    """7. contraexemplo.* : rota NN e rota ótima lado a lado."""
    caminho_json = os.path.join(pasta_resultados, 'contraexemplo.json')
    if not os.path.exists(caminho_json):
        return

    with open(caminho_json, encoding='utf-8') as f:
        dados = json.load(f)

    coords = dados['coordenadas']
    rota_nn = dados['rota_vizinho_mais_proximo']
    custo_nn = dados['custo_vizinho_mais_proximo']
    rota_otima = dados['rota_otima']
    custo_otimo = dados['custo_otimo']
    pct_acima = dados['acima_do_otimo_pct']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Para visualização das rotas em 1D, elevamos os arcos em alturas diferentes para distinguir as sobreposições
    def plotar_rota_1d(ax, rota, titulo, cor_linha, custo, rotulo_status):
        xs = [coords[i][0] for i in range(len(coords))]
        # Desenha nós na reta y=0
        ax.scatter(xs, [0] * len(xs), color='darkblue', s=90, zorder=5)

        for i, (x, y) in enumerate(coords):
            ax.annotate(
                f" {i} (x={int(x)})",
                (x, 0),
                xytext=(0, -18),
                textcoords='offset points',
                ha='center', fontsize=9, fontweight='bold'
            )

        # Destaca o nó de partida 0
        x0 = coords[rota[0]][0]
        ax.scatter([x0], [0], color='crimson', s=160, zorder=6, edgecolors='black', linewidth=1.5)
        ax.annotate("Partida (0)", (x0, 0), xytext=(0, 18), textcoords='offset points',
                    ha='center', fontsize=9, color='crimson', fontweight='bold')

        # Conecta os arcos com arcos parabólicos para não sobrepor na reta
        n_passos = len(rota)
        ciclo = rota + [rota[0]]
        for idx in range(n_passos):
            u, v = ciclo[idx], ciclo[idx + 1]
            xu, xv = coords[u][0], coords[v][0]
            # Altura proporcional à distância e ao sentido
            altura = 0.35 * (idx + 1)
            x_meio = (xu + xv) / 2.0
            curva_x = np.linspace(xu, xv, 50)
            # Parábola
            curva_y = 4 * altura * (curva_x - xu) * (xv - curva_x) / ((xv - xu) ** 2) if xu != xv else np.zeros_like(curva_x)

            ax.plot(curva_x, curva_y, color=cor_linha, linewidth=1.6, alpha=0.85)

            # Seta no ponto médio
            meio_idx = 25
            ax.annotate(
                "",
                xy=(curva_x[meio_idx + 1], curva_y[meio_idx + 1]),
                xytext=(curva_x[meio_idx], curva_y[meio_idx]),
                arrowprops=dict(arrowstyle="->", color=cor_linha, lw=2.0)
            )

        ax.set_title(f"{titulo}\nCusto = {custo} {rotulo_status}", fontsize=11)
        ax.set_ylim(-0.8, 2.6)
        ax.set_xlim(-1, 9)
        ax.set_yticks([])
        ax.set_xlabel("Posição na Reta ($x$)")

    plotar_rota_1d(
        ax1, rota_nn,
        f"Vizinho Mais Próximo (Guloso)",
        '#d62728', custo_nn, f"(+{pct_acima}%)"
    )

    plotar_rota_1d(
        ax2, rota_otima,
        f"Solução Ótima (Held-Karp)",
        '#2ca02c', custo_otimo, "(ÓTIMO)"
    )

    fig.suptitle(
        f"Contraexemplo Minimal do Vizinho Mais Próximo (n=5, sem empates)",
        fontsize=13, fontweight='bold', y=1.02
    )

    salvar_figura(fig, pasta_figuras, 'contraexemplo')


# ---------------------------------------------------------------- TABELAS

def gerar_tabelas(pasta_resultados, pasta_tabelas):
    """Gera tabelas/*.md e tabelas/*.tex (booktabs)."""
    os.makedirs(pasta_tabelas, exist_ok=True)

    # 1. Tabela Held-Karp por k
    caminho_hk = os.path.join(pasta_resultados, 'hk_tempo.csv')
    if os.path.exists(caminho_hk):
        linhas_hk = []
        with open(caminho_hk, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                linhas_hk.append(r)

        # Markdown
        caminho_md = os.path.join(pasta_tabelas, 'tempo_hk.md')
        with open(caminho_md, 'w', encoding='utf-8') as f:
            f.write("| Instância | Cidades ($k$) | Repetições | Tempo Médio (s) | Desvio Padrão (s) | Custo Ótimo | Razão Teórica | Pico Memória (MB) |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            for r in linhas_hk:
                mem = f"{float(r['pico_memoria_mb']):.2f}" if r['pico_memoria_mb'] != "" else "-"
                f.write(
                    f"| {r['instancia']} | {r['cidades']} | {r['repeticoes']} | "
                    f"{float(r['tempo_medio_s']):.6f} | {float(r['tempo_desvio_s']):.6f} | "
                    f"{r['custo_otimo']} | {r['razao_teorica']} | {mem} |\n"
                )
        print(f"  Tabela gerada: {caminho_md}")

        # LaTeX (booktabs)
        caminho_tex = os.path.join(pasta_tabelas, 'tempo_hk.tex')
        with open(caminho_tex, 'w', encoding='utf-8') as f:
            f.write("% Tabela: Tempo e Memória do Held-Karp\n")
            f.write("\\begin{table}[htbp]\n\\centering\n\\small\n")
            f.write("\\caption{Desempenho experimental do algoritmo exato de Held-Karp por tamanho de subinstância ($k$).}\n")
            f.write("\\label{tab:tempo_hk}\n")
            f.write("\\begin{tabular}{lrrrrrrr}\n\\toprule\n")
            f.write("Instância & $k$ & Rep. & Tempo Médio (s) & Desvio (s) & Custo Ótimo & Razão Teórica & Memória (MB) \\\\\n\\midrule\n")
            for r in linhas_hk:
                mem = f"{float(r['pico_memoria_mb']):.2f}" if r['pico_memoria_mb'] != "" else "--"
                razao_formatada = f"{float(r['razao_teorica']):.2e}".replace('e-0', '\\times 10^{-').replace('e-', '\\times 10^{-') + '}'
                f.write(
                    f"{r['instancia']} & {r['cidades']} & {r['repeticoes']} & "
                    f"{float(r['tempo_medio_s']):.6f} & {float(r['tempo_desvio_s']):.6f} & "
                    f"{r['custo_otimo']} & ${razao_formatada}$ & {mem} \\\\\n"
                )
            f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
        print(f"  Tabela gerada: {caminho_tex}")

    # 2. Tabela Qualidade NN Completas
    caminho_comp = os.path.join(pasta_resultados, 'qualidade_completas.csv')
    if os.path.exists(caminho_comp):
        linhas_comp = []
        with open(caminho_comp, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                linhas_comp.append(r)

        # Markdown
        caminho_md = os.path.join(pasta_tabelas, 'qualidade_nn_completas.md')
        with open(caminho_md, 'w', encoding='utf-8') as f:
            f.write("| Instância | Cidades ($n$) | Ótimo TSPLIB | Partida 0 (Custo / Gap) | Melhor Partida (Custo / Partida / Gap) | Pior Partida (Custo / Partida / Gap) | Média Custos | Desvio Custos | Gap Médio |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")
            for r in linhas_comp:
                f.write(
                    f"| {r['instancia']} | {r['cidades']} | {r['otimo_TSPLIB']} | "
                    f"{r['custo_partida_0']} (+{r['pct_acima_partida_0']}%) | "
                    f"{r['melhor_custo']} (p={r['melhor_partida']}, +{r['pct_acima_melhor']}%) | "
                    f"{r['pior_custo']} (p={r['pior_partida']}, +{r['pct_acima_pior']}%) | "
                    f"{r['media_custos']} | {r['desvio_custos']} | +{r['pct_acima_media']}% |\n"
                )
        print(f"  Tabela gerada: {caminho_md}")

        # LaTeX (booktabs)
        caminho_tex = os.path.join(pasta_tabelas, 'qualidade_nn_completas.tex')
        with open(caminho_tex, 'w', encoding='utf-8') as f:
            f.write("% Tabela: Qualidade do Vizinho Mais Próximo nas Instâncias Completas\n")
            f.write("\\begin{table}[htbp]\n\\centering\n\\small\n")
            f.write("\\caption{Qualidade da rota obtida pelo algoritmo do Vizinho Mais Próximo nas instâncias completas da TSPLIB.}\n")
            f.write("\\label{tab:qualidade_nn_completas}\n")
            f.write("\\begin{tabular}{lrrrrrrrr}\n\\toprule\n")
            f.write("Instância & $n$ & Ótimo & Partida 0 & Gap P0 & Melhor Partida & Gap Melhor & Média & Gap Médio \\\\\n\\midrule\n")
            for r in linhas_comp:
                f.write(
                    f"{r['instancia']} & {r['cidades']} & {r['otimo_TSPLIB']} & "
                    f"{r['custo_partida_0']} & +{r['pct_acima_partida_0']}\\% & "
                    f"{r['melhor_custo']} (p={r['melhor_partida']}) & +{r['pct_acima_melhor']}\\% & "
                    f"{r['media_custos']} & +{r['pct_acima_media']}\\% \\\\\n"
                )
            f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
        print(f"  Tabela gerada: {caminho_tex}")

    # 3. Tabela NN Sintético
    caminho_sint = os.path.join(pasta_resultados, 'nn_sintetico.csv')
    if os.path.exists(caminho_sint):
        linhas_sint = []
        with open(caminho_sint, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                linhas_sint.append(r)

        # Markdown
        caminho_md = os.path.join(pasta_tabelas, 'nn_sintetico.md')
        with open(caminho_md, 'w', encoding='utf-8') as f:
            f.write("| $n$ | Repetições | Tempo Matriz (s) | Desvio Matriz (s) | Tempo NN (s) | Desvio NN (s) | Memória Matriz (MB) | Custo NN |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            for r in linhas_sint:
                f.write(
                    f"| {r['n']} | {r['repeticoes']} | "
                    f"{float(r['tempo_matriz_medio_s']):.6f} | {float(r['tempo_matriz_desvio_s']):.6f} | "
                    f"{float(r['tempo_nn_medio_s']):.6f} | {float(r['tempo_nn_desvio_s']):.6f} | "
                    f"{float(r['pico_memoria_matriz_mb']):.2f} | {r['custo_nn']} |\n"
                )
        print(f"  Tabela gerada: {caminho_md}")

        # LaTeX (booktabs)
        caminho_tex = os.path.join(pasta_tabelas, 'nn_sintetico.tex')
        with open(caminho_tex, 'w', encoding='utf-8') as f:
            f.write("% Tabela: Desempenho do NN em Instâncias Sintéticas\n")
            f.write("\\begin{table}[htbp]\n\\centering\n\\small\n")
            f.write("\\caption{Tempo de construção da matriz de distâncias e tempo de execução do Vizinho Mais Próximo em instâncias sintéticas uniformes.}\n")
            f.write("\\label{tab:nn_sintetico}\n")
            f.write("\\begin{tabular}{rrrrrrr}\n\\toprule\n")
            f.write("$n$ & Rep. & Tempo Matriz (s) & Desvio Matriz (s) & Tempo NN (s) & Desvio NN (s) & Memória Matriz (MB) \\\\\n\\midrule\n")
            for r in linhas_sint:
                f.write(
                    f"{r['n']} & {r['repeticoes']} & "
                    f"{float(r['tempo_matriz_medio_s']):.6f} & {float(r['tempo_matriz_desvio_s']):.6f} & "
                    f"{float(r['tempo_nn_medio_s']):.6f} & {float(r['tempo_nn_desvio_s']):.6f} & "
                    f"{float(r['pico_memoria_matriz_mb']):.2f} \\\\\n"
                )
            f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
        print(f"  Tabela gerada: {caminho_tex}")


def main():
    parser = argparse.ArgumentParser(description="Geração de gráficos e tabelas para o TSP")
    parser.add_argument('--resultados', default='resultados', help="Pasta onde estão os arquivos de resultados")
    parser.add_argument('--figuras', default='figuras', help="Pasta onde salvar as figuras geradas")
    parser.add_argument('--tabelas', default='tabelas', help="Pasta onde salvar as tabelas geradas")

    args = parser.parse_args()

    os.makedirs(args.figuras, exist_ok=True)
    os.makedirs(args.tabelas, exist_ok=True)

    configurar_estilo()

    print("================================================================")
    print(" GERANDO GRÁFICOS E TABELAS EXPERIMENTAIS")
    print(f" Resultados: {args.resultados} | Figuras: {args.figuras} | Tabelas: {args.tabelas}")
    print("================================================================")

    print("\n1. Gerando figuras...")
    grafico_1_hk_tempo(args.resultados, args.figuras)
    grafico_2_hk_razao(args.resultados, args.figuras)
    grafico_3_hk_memoria(args.resultados, args.figuras)
    grafico_4_nn_loglog(args.resultados, args.figuras)
    grafico_5_nn_gap_subinstancias(args.resultados, args.figuras)
    grafico_6_nn_gap_completas(args.resultados, args.figuras)
    grafico_7_contraexemplo(args.resultados, args.figuras)

    print("\n2. Gerando tabelas (Markdown e LaTeX)...")
    gerar_tabelas(args.resultados, args.tabelas)

    print("\n================================================================")
    print(" GERAÇÃO CONCLUÍDA COM SUCESSO!")
    print("================================================================")


if __name__ == '__main__':
    main()
