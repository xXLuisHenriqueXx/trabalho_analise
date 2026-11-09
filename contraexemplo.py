"""
Busca determinística de um contraexemplo mostrando que o algoritmo do vizinho
mais próximo (NN) não garante a solução ótima, mesmo sem qualquer empate nos passos.
Gera e valida a menor instância euclidiana com n=5.
Salva os resultados em resultados/contraexemplo.json.
"""

import itertools
import json
import os

from exato import custo_rota, forca_bruta, held_karp, matriz_distancias
from heuristico import vizinho_mais_proximo


def verificar_empate_passos_nn(d, inicio=0):
    """
    Verifica se durante a execução do vizinho mais próximo a partir de 'inicio'
    ocorre algum empate na escolha da menor distância entre os vértices não visitados.
    Devolve (tem_empate, lista_de_passos).
    """
    n = len(d)
    visitado = [False] * n
    visitado[inicio] = True
    atual = inicio
    passos = []

    for _ in range(n - 1):
        candidatos = [(d[atual][j], j) for j in range(n) if not visitado[j]]
        candidatos.sort(key=lambda item: item[0])

        dist_minima = candidatos[0][0]
        segunda_dist = candidatos[1][0] if len(candidatos) > 1 else None
        tem_empate = (segunda_dist is not None and dist_minima == segunda_dist)

        escolhido = candidatos[0][1]
        passos.append({
            'origem': atual,
            'escolhido': escolhido,
            'distancia_escolhida': dist_minima,
            'distancias_candidatas': [c[0] for c in candidatos],
            'houve_empate': tem_empate,
        })

        if tem_empate:
            return True, passos

        visitado[escolhido] = True
        atual = escolhido

    return False, passos


def buscar_menor_contraexemplo():
    """
    Busca determinística da menor instância euclidiana (n=5) com coordenadas
    inteiras mínimas onde o vizinho mais próximo com partida 0 é estritamente
    pior que o ótimo e nenhum passo do NN apresenta empate.
    """
    n = 5
    # Busca sistemática e lexicográfica em grade 1D pequena
    # Na reta, a rota ótima é 2 * (max(x) - min(x)), e o NN oscila (pingue-pongue).
    for max_coord in range(5, 20):
        for comb in itertools.combinations(range(1, max_coord + 1), n - 1):
            coords_base = [(0, 0)] + [(x, 0) for x in comb]
            for perm in itertools.permutations(coords_base):
                coords = list(perm)
                d = matriz_distancias(coords)
                tem_empate, passos = verificar_empate_passos_nn(d, inicio=0)
                if not tem_empate:
                    rota_nn = vizinho_mais_proximo(d, inicio=0)
                    custo_nn = custo_rota(rota_nn, d)
                    rota_hk, custo_hk = held_karp(d)
                    if custo_nn > custo_hk:
                        return coords, passos, rota_nn, custo_nn, rota_hk, custo_hk
    raise RuntimeError("Nenhum contraexemplo encontrado no espaço de busca.")


def main():
    print("Buscando contraexemplo determinístico para o algoritmo do Vizinho Mais Próximo...")
    coords, passos, rota_nn, custo_nn, rota_hk, custo_hk = buscar_menor_contraexemplo()

    d = matriz_distancias(coords)
    custo_fb = forca_bruta(d)

    assert custo_hk == custo_fb, "Held-Karp e Força Bruta divergiram!"
    assert custo_nn > custo_hk, "Custo do NN deveria ser estritamente maior que o ótimo!"

    acima_pct = round(((custo_nn - custo_hk) / custo_hk) * 100, 2)

    resultado = {
        'descricao': (
            "Contraexemplo demonstrando que o algoritmo guloso (Vizinho Mais Próximo) "
            "não garante a solução ótima mesmo na ausência de empates em qualquer escolha."
        ),
        'n_cidades': len(coords),
        'coordenadas': coords,
        'rota_vizinho_mais_proximo': rota_nn,
        'custo_vizinho_mais_proximo': custo_nn,
        'rota_otima': rota_hk,
        'custo_otimo': custo_hk,
        'custo_forca_bruta': custo_fb,
        'diferenca_absoluta': custo_nn - custo_hk,
        'acima_do_otimo_pct': acima_pct,
        'validacao_forca_bruta': custo_hk == custo_fb,
        'passos_detalhados_nn': passos,
    }

    # Impressão legível no terminal
    print("\n========================================================")
    print(" CONTRAEXEMPLO: VIZINHO MAIS PRÓXIMO NÃO É ÓTIMO")
    print("========================================================")
    print(f"Número de cidades: {len(coords)}")
    print("Coordenadas (índice: (x, y)):")
    for i, c in enumerate(coords):
        print(f"  {i}: {c}")

    print("\nPassos do NN a partir do vértice 0 (comprovando ausência de empates):")
    for p in passos:
        print(
            f"  De {p['origem']} -> escolheu {p['escolhido']} (distância: {p['distancia_escolhida']}) "
            f"| distâncias disponíveis: {p['distancias_candidatas']} (mínimo estrito: {not p['houve_empate']})"
        )

    print("\nResultados:")
    print(f"  Rota NN (partida 0):  {rota_nn}")
    print(f"  Custo NN:             {custo_nn}")
    print(f"  Rota Ótima (Held-Karp): {rota_hk}")
    print(f"  Custo Ótimo:          {custo_hk} (conferido com Força Bruta: {custo_fb})")
    print(f"  Diferença percentual: {acima_pct}% acima do ótimo")
    print("========================================================\n")

    # Salva em resultados/contraexemplo.json
    pasta_saida = 'resultados'
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_json = os.path.join(pasta_saida, 'contraexemplo.json')
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"Arquivo salvo com sucesso em: {caminho_json}")


if __name__ == '__main__':
    main()
