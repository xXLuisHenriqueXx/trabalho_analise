"""
Caixeiro viajante (TSP) - algoritmo EXATO
Paradigma: programação dinâmica (Held-Karp)   Complexidade: O(n^2 * 2^n) tempo, O(n * 2^n) memória

Como usar
---------
Modo interativo (pergunta tudo):
    python exato.py

Modo direto (pelos argumentos):
    python exato.py --instancia berlin52 --cidades 15
    python exato.py --instancia st70 --cidades 12 --repeticoes 10
    python exato.py --instancia berlin52 --cidades 5-20 --limite 60 --csv held_karp.csv
    python exato.py --instancia berlin52 --cidades 4-9 --verificar

No Colab use o modo direto:   !python exato.py --instancia berlin52 --cidades 15

Observações
-----------
- "--cidades k" usa as primeiras k cidades da instância. É obrigatório: a instância inteira
  (52, 70 ou 76 cidades) é grande demais para o Held-Karp.
- Por segurança o programa recusa mais de 23 cidades (tempo e memória explodem).
  Use --forcar para passar desse limite por sua conta.
- --verificar compara o resultado com a força bruta (testa todas as rotas); só para até 10 cidades.
- As cidades são numeradas pelo ÍNDICE 0..n-1 (a cidade 1 do arquivo é o índice 0).
- A distância é a euclidiana arredondada ao inteiro mais próximo (regra EUC_2D da TSPLIB).
"""

import argparse
import itertools
import math
import os
import statistics
import sys
import time

PASTA_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instances', 'TSP')
INSTANCIAS = {'berlin52': 'berlin52.tsp.txt', 'st70': 'st70.tsp.txt', 'pr76': 'pr76.tsp.txt'}
OTIMOS_TSPLIB = {'berlin52': 7542, 'st70': 675, 'pr76': 108159}
MAX_CIDADES = 23


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

def held_karp(d):
    """Programação dinâmica de Held-Karp. Devolve (rota, custo ótimo).
    C[S][j] = menor custo saindo da cidade 0, visitando o conjunto S e terminando em j.
    S é uma máscara de bits: a cidade j (j >= 1) usa o bit j-1."""
    n = len(d)
    m = n - 1
    INF = float('inf')
    C = [[INF] * n for _ in range(1 << m)]
    P = [[-1] * n for _ in range(1 << m)]

    for j in range(1, n):                       # tamanho 1: 0 -> j
        C[1 << (j - 1)][j] = d[0][j]
        P[1 << (j - 1)][j] = 0

    for S in range(1, 1 << m):                  # S em ordem crescente
        for j in range(1, n):
            if not (S >> (j - 1)) & 1:
                continue
            S_sem_j = S & ~(1 << (j - 1))
            if S_sem_j == 0:
                continue
            for i in range(1, n):
                if (S_sem_j >> (i - 1)) & 1:
                    custo = C[S_sem_j][i] + d[i][j]
                    if custo < C[S][j]:
                        C[S][j] = custo
                        P[S][j] = i

    TODAS = (1 << m) - 1                        # fechar a volta para 0
    melhor = INF
    ultima = -1
    for j in range(1, n):
        custo = C[TODAS][j] + d[j][0]
        if custo < melhor:
            melhor = custo
            ultima = j

    rota = []                                   # reconstrução pelos "pais"
    S = TODAS
    j = ultima
    while j != 0:
        rota.append(j)
        i = P[S][j]
        S = S & ~(1 << (j - 1))
        j = i
    rota.append(0)
    rota.reverse()
    return rota, melhor


def forca_bruta(d):
    """Testa todas as rotas (só para conferir o Held-Karp em instâncias pequenas)."""
    n = len(d)
    melhor = float('inf')
    for perm in itertools.permutations(range(1, n)):
        melhor = min(melhor, custo_rota([0] + list(perm), d))
    return melhor


# ---------------------------------------------------------------- execução

def interpretar_cidades(texto, total, forcar):
    """'15' -> [15];  '10,12,14' -> [10, 12, 14];  '5-20' -> [5, 6, ..., 20]."""
    texto = str(texto).strip()
    if '-' in texto:
        a, b = texto.split('-')
        tamanhos = list(range(int(a), int(b) + 1))
    else:
        tamanhos = [int(x) for x in texto.split(',')]
    for k in tamanhos:
        if not 3 <= k <= total:
            raise ValueError(f"a instância tem {total} cidades: use tamanhos entre 3 e {total} (recebi {k}).")
        if k > MAX_CIDADES and not forcar:
            raise ValueError(f"{k} cidades é demais para o Held-Karp (limite {MAX_CIDADES}). "
                             f"Use --forcar se quiser tentar mesmo assim.")
    return tamanhos


def rodar(nome, coords, k, repeticoes, verificar):
    d = matriz_distancias(coords[:k])
    (rota, custo), media, desvio = medir(held_karp, d, repeticoes)
    r = {'instancia': nome, 'cidades': k, 'repeticoes': repeticoes,
         'tempo_medio_s': media, 'tempo_desvio_s': desvio, 'custo_otimo': custo,
         'rota_coerente': custo_rota(rota, d) == custo}
    if verificar:
        if k > 10:
            r['forca_bruta'] = 'não testado (k > 10)'
        else:
            fb = forca_bruta(d)
            r['forca_bruta'] = fb
            r['igual_forca_bruta'] = fb == custo
    if k == len(coords) and nome in OTIMOS_TSPLIB:
        r['otimo_TSPLIB'] = OTIMOS_TSPLIB[nome]
    r['rota'] = rota
    return r


def imprimir(r, mostrar_rota):
    print(f"\n=== Held-Karp | {r['instancia']} | {r['cidades']} cidades ===")
    print(f"custo ótimo = {r['custo_otimo']} | rota coerente: {r['rota_coerente']}")
    print(f"tempo = {r['tempo_medio_s']:.6f} ± {r['tempo_desvio_s']:.6f} s ({r['repeticoes']} repetições)")
    if 'forca_bruta' in r:
        extra = f" | igual: {r['igual_forca_bruta']}" if 'igual_forca_bruta' in r else ''
        print(f"força bruta = {r['forca_bruta']}{extra}")
    if mostrar_rota:
        print("rota (índices):", r['rota'])


def perguntar(texto, padrao):
    resposta = input(f"{texto} [{padrao}]: ").strip()
    return resposta if resposta else padrao


def main():
    p = argparse.ArgumentParser(description="TSP - Held-Karp (programação dinâmica, exato)")
    p.add_argument('--instancia', choices=list(INSTANCIAS), help="berlin52, st70 ou pr76")
    p.add_argument('--arquivo', help="caminho de outro arquivo 'id x y' (em vez de --instancia)")
    p.add_argument('--pasta', default=PASTA_PADRAO, help="pasta onde estão os arquivos .tsp.txt")
    p.add_argument('--cidades', help="ex.: 15  ou  10,12,14  ou  5-20")
    p.add_argument('--repeticoes', type=int, default=5, help="repetições para medir o tempo (padrão 5)")
    p.add_argument('--limite', type=float, help="para a sequência se o tempo médio passar de X segundos")
    p.add_argument('--verificar', action='store_true', help="confere com a força bruta (até 10 cidades)")
    p.add_argument('--forcar', action='store_true', help=f"permite mais de {MAX_CIDADES} cidades")
    p.add_argument('--csv', help="salva os resultados neste arquivo .csv")
    p.add_argument('--sem-rota', action='store_true', help="não imprime a rota")

    if len(sys.argv) == 1:      # sem argumentos: modo interativo
        print("Held-Karp - modo interativo (Enter aceita o padrão)")
        nome = perguntar("Instância (berlin52, st70, pr76)", 'berlin52')
        cidades = perguntar(f"Cidades (ex.: 15, 10,12,14 ou 5-20; máximo {MAX_CIDADES})", '15')
        repeticoes = perguntar("Repetições", '5')
        verificar = perguntar("Conferir com força bruta? (s/n)", 'n').lower().startswith('s')
        args = p.parse_args(['--instancia', nome, '--cidades', cidades, '--repeticoes', repeticoes]
                            + (['--verificar'] if verificar else []))
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
    if not args.cidades:
        p.error("informe --cidades (a instância inteira é grande demais para o Held-Karp)")
    if args.repeticoes < 1:
        p.error("--repeticoes precisa ser pelo menos 1")

    coords = ler_instancia(caminho)
    try:
        tamanhos = interpretar_cidades(args.cidades, len(coords), args.forcar)
    except ValueError as erro:
        p.error(str(erro))

    resultados = []
    for k in tamanhos:
        r = rodar(nome, coords, k, args.repeticoes, args.verificar)
        imprimir(r, not args.sem_rota and len(tamanhos) == 1)
        resultados.append(r)
        if args.limite is not None and r['tempo_medio_s'] > args.limite:
            print(f"\nPassou de {args.limite} s com {k} cidades. Parando aqui.")
            break

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
