"""
Caixeiro viajante (TSP) - algoritmo HEURÍSTICO
Paradigma: guloso (vizinho mais próximo)   Complexidade: O(n^2) tempo, O(n^2) memória (matriz)

Como usar
---------
Modo interativo (pergunta tudo):
    python heuristico.py

Modo direto (pelos argumentos):
    python heuristico.py --instancia berlin52
    python heuristico.py --instancia st70 --cidades 30 --inicio 5
    python heuristico.py --instancia pr76 --todas-partidas
    python heuristico.py --instancia berlin52 --cidades 10,20,30,52 --repeticoes 10 --csv vizinho.csv

No Colab use o modo direto:   !python heuristico.py --instancia berlin52

Observações
-----------
- As cidades são numeradas pelo ÍNDICE 0..n-1 (a cidade 1 do arquivo é o índice 0).
- "--cidades k" usa as primeiras k cidades da instância. Sem esse argumento, usa a instância inteira.
- A distância é a euclidiana arredondada ao inteiro mais próximo (regra EUC_2D da TSPLIB),
  a mesma usada nos ótimos publicados: berlin52 = 7542, st70 = 675, pr76 = 108159.
"""

import argparse
import math
import os
import statistics
import sys
import time

PASTA_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instances', 'TSP')
INSTANCIAS = {'berlin52': 'berlin52.tsp.txt', 'st70': 'st70.tsp.txt', 'pr76': 'pr76.tsp.txt'}
OTIMOS_TSPLIB = {'berlin52': 7542, 'st70': 675, 'pr76': 108159}


# ---------------------------------------------------------------- funções base

def ler_instancia(caminho):
    """Lê um arquivo com linhas 'id x y' e devolve a lista de coordenadas (x, y)."""
    coords = []
    with open(caminho) as arquivo:
        for linha in arquivo:
            partes = linha.split()
            if len(partes) == 0:
                continue
            coords.append((float(partes[1]), float(partes[2])))
    return coords


def matriz_distancias(coords):
    """Matriz n x n com a distância euclidiana arredondada (TSPLIB EUC_2D)."""
    n = len(coords)
    d = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            dist = int(math.sqrt(dx * dx + dy * dy) + 0.5)
            d[i][j] = dist
            d[j][i] = dist
    return d


def custo_rota(rota, d):
    """Soma das distâncias da rota, incluindo a volta da última cidade para a primeira."""
    total = 0
    for k in range(len(rota) - 1):
        total += d[rota[k]][rota[k + 1]]
    total += d[rota[-1]][rota[0]]
    return total


def medir(algoritmo, d, repeticoes):
    """Roda o algoritmo 'repeticoes' vezes e devolve (resultado, tempo médio, desvio padrão)."""
    tempos = []
    resultado = None
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        resultado = algoritmo(d)
        tempos.append(time.perf_counter() - inicio)
    media = statistics.mean(tempos)
    desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
    return resultado, media, desvio


# ---------------------------------------------------------------- algoritmo

def vizinho_mais_proximo(d, inicio=0):
    """Guloso: a partir de 'inicio', vai sempre para a cidade não visitada mais próxima.
    Empate: fica a de menor índice (comparação com '<')."""
    n = len(d)
    visitado = [False] * n
    rota = [inicio]
    visitado[inicio] = True
    atual = inicio
    for _ in range(n - 1):
        melhor = -1
        melhor_dist = float('inf')
        for j in range(n):
            if not visitado[j] and d[atual][j] < melhor_dist:
                melhor = j
                melhor_dist = d[atual][j]
        rota.append(melhor)
        visitado[melhor] = True
        atual = melhor
    return rota


# ---------------------------------------------------------------- execução

def interpretar_cidades(texto, total):
    """'52' -> [52];  '10,20,30' -> [10, 20, 30];  '5-20' -> [5, 6, ..., 20];  vazio -> [total]."""
    if texto is None or str(texto).strip() == '':
        return [total]
    texto = str(texto).strip()
    if '-' in texto:
        a, b = texto.split('-')
        tamanhos = list(range(int(a), int(b) + 1))
    else:
        tamanhos = [int(x) for x in texto.split(',')]
    for k in tamanhos:
        if not 3 <= k <= total:
            raise ValueError(f"a instância tem {total} cidades: use tamanhos entre 3 e {total} (recebi {k}).")
    return tamanhos


def rodar(nome, coords, k, inicio, repeticoes, todas_partidas):
    d = matriz_distancias(coords[:k])
    otimo = OTIMOS_TSPLIB.get(nome) if k == len(coords) else None

    if todas_partidas:
        inicio_t = time.perf_counter()
        custos = [custo_rota(vizinho_mais_proximo(d, s), d) for s in range(k)]
        tempo_total = time.perf_counter() - inicio_t
        melhor, pior = min(custos), max(custos)
        p_melhor, p_pior = custos.index(melhor), custos.index(pior)
        rota = vizinho_mais_proximo(d, p_melhor)
        linha = {'instancia': nome, 'cidades': k, 'partida': p_melhor, 'repeticoes': 1,
                 'tempo_medio_s': tempo_total, 'tempo_desvio_s': 0.0, 'custo': melhor,
                 'pior_custo': pior, 'pior_partida': p_pior, 'otimo_TSPLIB': otimo}
    else:
        if not 0 <= inicio < k:
            raise ValueError(f"--inicio precisa estar entre 0 e {k - 1}.")
        rota, media, desvio = medir(lambda m: vizinho_mais_proximo(m, inicio), d, repeticoes)
        linha = {'instancia': nome, 'cidades': k, 'partida': inicio, 'repeticoes': repeticoes,
                 'tempo_medio_s': media, 'tempo_desvio_s': desvio, 'custo': custo_rota(rota, d),
                 'otimo_TSPLIB': otimo}

    if otimo:
        linha['acima_do_otimo_pct'] = round((linha['custo'] - otimo) / otimo * 100, 2)
    linha['rota'] = rota
    return linha


def imprimir(r, mostrar_rota):
    print(f"\n=== Vizinho mais próximo | {r['instancia']} | {r['cidades']} cidades ===")
    if 'pior_custo' in r:
        print(f"todas as partidas testadas: melhor = {r['custo']} (partida {r['partida']}), "
              f"pior = {r['pior_custo']} (partida {r['pior_partida']})")
        print(f"tempo total das {r['cidades']} execuções: {r['tempo_medio_s']:.6f} s")
    else:
        print(f"partida = {r['partida']} | custo = {r['custo']}")
        print(f"tempo = {r['tempo_medio_s']:.6f} ± {r['tempo_desvio_s']:.6f} s ({r['repeticoes']} repetições)")
    if r.get('otimo_TSPLIB'):
        print(f"ótimo TSPLIB = {r['otimo_TSPLIB']} | acima do ótimo = {r['acima_do_otimo_pct']:.2f}%")
    if mostrar_rota:
        print("rota (índices):", r['rota'])


def perguntar(texto, padrao):
    resposta = input(f"{texto} [{padrao}]: ").strip()
    return resposta if resposta else padrao


def main():
    p = argparse.ArgumentParser(description="TSP - vizinho mais próximo (guloso)")
    p.add_argument('--instancia', choices=list(INSTANCIAS), help="berlin52, st70 ou pr76")
    p.add_argument('--arquivo', help="caminho de outro arquivo 'id x y' (em vez de --instancia)")
    p.add_argument('--pasta', default=PASTA_PADRAO, help="pasta onde estão os arquivos .tsp.txt")
    p.add_argument('--cidades', help="ex.: 52  ou  10,20,30  ou  5-20 (padrão: instância inteira)")
    p.add_argument('--inicio', type=int, default=0, help="índice da cidade de partida (padrão 0)")
    p.add_argument('--todas-partidas', action='store_true', help="testa todas as partidas e mostra a melhor e a pior")
    p.add_argument('--repeticoes', type=int, default=5, help="repetições para medir o tempo (padrão 5)")
    p.add_argument('--csv', help="salva os resultados neste arquivo .csv")
    p.add_argument('--sem-rota', action='store_true', help="não imprime a rota")

    if len(sys.argv) == 1:      # sem argumentos: modo interativo
        print("Vizinho mais próximo - modo interativo (Enter aceita o padrão)")
        nome = perguntar("Instância (berlin52, st70, pr76)", 'berlin52')
        cidades = perguntar("Cidades (ex.: 52, 10,20,30 ou 5-20; vazio = todas)", '')
        todas = perguntar("Testar todas as partidas? (s/n)", 'n').lower().startswith('s')
        inicio = 0 if todas else int(perguntar("Índice da cidade de partida", '0'))
        repeticoes = int(perguntar("Repetições", '5'))
        args = p.parse_args(['--instancia', nome, '--inicio', str(inicio), '--repeticoes', str(repeticoes)]
                            + (['--cidades', cidades] if cidades else [])
                            + (['--todas-partidas'] if todas else []))
    else:
        args = p.parse_args()

    if args.arquivo:
        nome = os.path.basename(args.arquivo).split('.')[0]
        caminho = args.arquivo
    elif args.instancia:
        nome = args.instancia
        caminho = os.path.join(args.pasta, INSTANCIAS[nome])
    else:
        p.error("informe --instancia ou --arquivo")
    if args.repeticoes < 1:
        p.error("--repeticoes precisa ser pelo menos 1")

    coords = ler_instancia(caminho)
    try:
        tamanhos = interpretar_cidades(args.cidades, len(coords))
        resultados = []
        for k in tamanhos:
            r = rodar(nome, coords, k, args.inicio, args.repeticoes, args.todas_partidas)
            imprimir(r, not args.sem_rota and len(tamanhos) == 1)
            resultados.append(r)
    except ValueError as erro:
        p.error(str(erro))

    if args.csv:
        import csv
        campos = []
        for r in resultados:
            for c in r:
                if c not in campos:
                    campos.append(c)
        with open(args.csv, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(resultados)
        print(f"\nresultados salvos em {args.csv}")


if __name__ == '__main__':
    main()
