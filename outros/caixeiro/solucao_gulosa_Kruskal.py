import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

from instancia import *

def kruskal_MetaHeuristica(n, edges):
    """
    n: número de vértices (1 a n)
    edges: lista de arestas no formato (peso, u, v)
    """
    edges.sort()  # ordena por peso
    print(edges)
    dict_grau = {}
    for i in range(1, n+1):
        dict_grau[i] = 0
    mst = []
    custo_total = 0
    for peso, u, v in edges:
        Switch = verifica_ciclo(mst, peso, u, v)
        print("----------")
        print("len: ", len(mst))
        print("peso: ", peso)
        print("u: ", u, " dict_grau[u]:  ", dict_grau[u])
        print("v: ", v, " dict_grau[v] :  ", dict_grau[v] )
        print(mst)
        print(dict_grau)
        if(Switch or len(mst) == n-1):

            if(dict_grau[u] < 2 and dict_grau[v] < 2):
                dict_grau[u] = dict_grau[u] + 1
                dict_grau[v] = dict_grau[v] + 1
                mst.append((peso, u, v))
                custo_total += peso
                
                
    return mst, custo_total









