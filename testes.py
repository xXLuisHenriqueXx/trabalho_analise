import os
import unittest

from exato import (
    PASTA_PADRAO,
    INSTANCIAS,
    custo_rota,
    forca_bruta,
    held_karp,
    ler_instancia,
    matriz_distancias,
)
from heuristico import vizinho_mais_proximo


class TestesTSP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instancias = {}
        for nome, arq in INSTANCIAS.items():
            caminho = os.path.join(PASTA_PADRAO, arq)
            cls.instancias[nome] = ler_instancia(caminho)

    def test_distancia_euc_2d_propriedades_e_arredondamento(self):
        coords = [
            (0.0, 0.0),
            (3.0, 4.0),     
            (1.0, 1.0),     
            (1.0, 2.0),    
            (565.0, 575.0), 
            (25.0, 185.0),  
        ]
        d = matriz_distancias(coords)
        n = len(coords)

        for i in range(n):
            self.assertEqual(d[i][i], 0)
            for j in range(n):
                self.assertEqual(d[i][j], d[j][i])

        self.assertEqual(d[0][1], 5)
        self.assertEqual(d[0][2], 1)
        self.assertEqual(d[0][3], 2)
        self.assertEqual(d[4][5], 666)

    def test_held_karp_igual_forca_bruta_prefixos_pequenos(self):
        for nome in ('berlin52', 'st70', 'pr76'):
            coords = self.instancias[nome]
            for k in range(4, 10):
                d = matriz_distancias(coords[:k])
                rota_hk, custo_hk = held_karp(d)
                custo_fb = forca_bruta(d)
                self.assertEqual(
                    custo_hk,
                    custo_fb,
                    f"Held-Karp diferente da força bruta na instância {nome} com k={k}",
                )

    def test_held_karp_rota_valida_e_coerente(self):
        coords = self.instancias['berlin52']
        for k in range(4, 11):
            d = matriz_distancias(coords[:k])
            rota, custo = held_karp(d)

            self.assertEqual(len(rota), k)
            self.assertEqual(rota[0], 0, f"Rota não inicia no vértice 0 para k={k}")
            self.assertEqual(
                sorted(rota),
                list(range(k)),
                f"Rota não é permutação de 0..{k-1}",
            )
            self.assertEqual(
                custo_rota(rota, d),
                custo,
                f"custo_rota difere do custo retornado por held_karp para k={k}",
            )

    def test_vizinho_mais_proximo_propriedades_e_passo_a_passo(self):
        coords = self.instancias['berlin52'][:15]
        d = matriz_distancias(coords)
        n = len(coords)

        for inicio in (0, 3, 7, n - 1):
            rota = vizinho_mais_proximo(d, inicio=inicio)

            self.assertEqual(len(rota), n)
            self.assertEqual(rota[0], inicio)
            self.assertEqual(sorted(rota), list(range(n)))

            visitados = [False] * n
            visitados[inicio] = True
            atual = inicio
            for passo in range(1, n):
                proximo = rota[passo]
                melhor_dist = float('inf')
                melhor_indice = -1
                for j in range(n):
                    if not visitados[j] and d[atual][j] < melhor_dist:
                        melhor_dist = d[atual][j]
                        melhor_indice = j
                self.assertEqual(
                    proximo,
                    melhor_indice,
                    f"Passo {passo} a partir de {atual} escolheu {proximo}, esperado {melhor_indice}",
                )
                visitados[proximo] = True
                atual = proximo

    def test_regressoes(self):
        coords_berlin = self.instancias['berlin52']
        d_berlin = matriz_distancias(coords_berlin)
        rota_nn = vizinho_mais_proximo(d_berlin, inicio=0)
        custo_nn = custo_rota(rota_nn, d_berlin)
        self.assertEqual(
            custo_nn,
            8980,
            f"NN em berlin52 partida 0 deveria ser 8980, obtido: {custo_nn}",
        )

        for nome in ('berlin52', 'st70', 'pr76'):
            coords = self.instancias[nome]
            for k in range(4, 15):
                d = matriz_distancias(coords[:k])
                _, custo_hk = held_karp(d)
                rota_k = vizinho_mais_proximo(d, inicio=0)
                custo_k = custo_rota(rota_k, d)
                self.assertGreaterEqual(
                    custo_k,
                    custo_hk,
                    f"Custo do NN ({custo_k}) menor que ótimo ({custo_hk}) para {nome} k={k}",
                )


if __name__ == '__main__':
    unittest.main()
