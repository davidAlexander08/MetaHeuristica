import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np



def busca_pai(lista_edges, de):
    pai = 0
    for edge in lista_edges:
        if(de == edge[0]):
            pai = edge[1]
    return pai

def encontra_pai(lista_edges, de, para):
    pai = de
    pai_anterior = 0
    while pai != 0:
        pai_anterior = pai
        pai = busca_pai(lista_edges,pai)
        if(pai == 0):
            break
        if(pai == para):
            pai_anterior = pai
            break
    return pai_anterior

def busca_conexao(lista_mst_aux, node):
    lista_opcoes_caminho =[]
    for edge in lista_mst_aux:
        if(node == edge[1]):
            lista_opcoes_caminho.append(edge)
        if(node == edge[2]):
            lista_opcoes_caminho.append(edge)
    return lista_opcoes_caminho

def encontra_caminhos(dicionario_ramos, lista_auxiliar_mst, contador_recursivo):
    keys_iniciais = list(dicionario_ramos.keys())
    #print("lista_auxiliar_mst: ", lista_auxiliar_mst)
    for key in keys_iniciais:
        no_busca = dicionario_ramos[key][-1]
        ramos_de_conexao = busca_conexao(lista_auxiliar_mst.copy(), no_busca)
        #print("no_busca: ", no_busca, " ramos_de_conexao: ", ramos_de_conexao)
        
        if(len(ramos_de_conexao) != 0):
            ultima_lista = max(dicionario_ramos.keys())
            contador = 1
            for ramo in ramos_de_conexao:
                #print(ramo)
                lista_auxiliar_mst.remove(ramo)
                candidato = ramo[0] if ramo[0] != no_busca else ramo[1]

                if(contador == 1):
                    dicionario_ramos[key].append(candidato)
                else:
                    proxima_lista = ultima_lista + 1
                    dicionario_ramos[proxima_lista] = dicionario_ramos[key].copy()
                    dicionario_ramos[proxima_lista].pop()
                    dicionario_ramos[proxima_lista].append(candidato)
                    ultima_lista += 1
                contador += 1
            #print(dicionario_ramos)
        else:
            dicionario_ramos[key].append(0)
    contador_recursivo += 1
    soma = 0
    for key in keys_iniciais:
        soma += dicionario_ramos[key][-1]
    if(soma == 0):
        return
    else:
        encontra_caminhos(dicionario_ramos,lista_auxiliar_mst, contador_recursivo)

def verifica_ciclo(mst, peso, de, para):
    booleano = True
    #print("de: ", de, " para: ", para, " peso: ", peso)
    dicionario_ramos = {}
    dicionario_ramos[1] = [de]
    contador_recursivo = 0
    if(len(mst) != 0):
        lista_auxiliar_mst = mst.copy()
        encontra_caminhos(dicionario_ramos, lista_auxiliar_mst, contador_recursivo)
        keys_iniciais = list(dicionario_ramos.keys())
        for key in keys_iniciais:
            if(para in dicionario_ramos[key]):
                booleano = False
    return booleano



edges = [
    (9, 1, 2),
    (2, 1, 3),
    (8, 1, 4),
    (12, 1, 5),
    (11, 1, 6),
    (7, 2, 3),
    (19, 2, 4),
    (10, 2, 5),
    (32, 2, 6),
    (29, 3, 4),
    (18, 3, 5),
    (6, 3, 6),
    (24, 4, 5),
    (3, 4, 6),
    (19, 5, 6)
]


edges = [
    (100, 1, 2),
    (2, 1, 3),
    (2, 1, 4),
    (1, 1, 5),
    (1, 2, 3),
    (3, 2, 4),
    (2, 2, 5),
    (1, 3, 4),
    (3, 3, 5),
    (1, 4, 5)
]


# Para NetworkX, precisamos (u, v, weight)
edges_nx = [(u, v, peso) for peso, u, v in edges]

# Build the graph
G = nx.Graph()
G.add_weighted_edges_from(edges_nx)

nodes = set()
for _, u, v in edges:
    nodes.add(u)
    nodes.add(v)

num_nodes = len(nodes)
print("num_nodes: ", num_nodes)