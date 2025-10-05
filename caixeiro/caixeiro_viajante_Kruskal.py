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
# Run Kruskal
#mst, custo = kruskal(10, edges)
mst, custo = kruskal_MetaHeuristica(num_nodes, edges)

print("Arestas da Árvore Geradora Mínima:", mst)
print("Custo total:", custo)

# Layout for consistent node positions
pos = nx.spring_layout(G, seed=42)

# Plot original graph
plt.figure(figsize=(12, 6))

plt.subplot(1, 3, 1)
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=800, font_size=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
plt.title("Grafo")

# Plot MST (edges highlighted in red)
plt.subplot(1, 3, 2)
nx.draw(G, pos, with_labels=True, node_color="lightgreen", node_size=800, font_size=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for w, u, v in mst], width=3, edge_color="red")
plt.title(f"Guloso - CUSTO: {custo}")








### MELHORA DO ALGORITMO POR S.A.

# Parâmetros S.A.
T = 100.0
T_min = 0.1
alpha = 0.95
num_iter = 1000

x = mst.copy()
melhor_sol = x.copy()

def calcula(sol):
    custo_total = 0
    for peso, u, v  in sol:
        custo_total += peso
    return custo_total

melhor_valor = calcula(x)
print("sol_gulosa: ", melhor_sol)
print("valor_guloso: ", melhor_valor)

def verificaRank(y, num_nodes):

    #print(y)
    dict_grau = {}
    for i in range(1, num_nodes+1):
        dict_grau[i] = 0
    for edge in y:
        peso, u, v = edge
        dict_grau[u] = dict_grau[u] + 1
        dict_grau[v] = dict_grau[v] + 1
    #print(dict_grau)
    all_equal_2 = all(v == 2 for v in dict_grau.values())
    return all_equal_2

def sorteio(x,num_nodes, edges):
    y = x.copy()
    mst_set = set((min(u,v), max(u,v)) for _, u, v in y)
    candidates = [e for e in edges if (min(e[1], e[2]), max(e[1], e[2])) not in mst_set]
    new_edges = random.sample(candidates, 2)
    replace_indices = random.sample(range(len(x)), 2)
    
    for idx, edge in zip(replace_indices, new_edges):
        #peso, u, v = edge
        #Switch = verifica_ciclo(y, peso, u, v)
        y[idx] = edge
    
    bool_rank = verificaRank(y, num_nodes)
    
    #print("bool_rank: ", bool_rank, " y: ", y)

    #print(y, " SWITCH: ", Switch)
    if(bool_rank):
        return (y, True)   
    else:
        return (0, False)     
    
while T > T_min:
    for _ in range(num_iter):
        # Gerar vizinho: escolhe substitui um caminho aleatório
        flag = False
        while not flag:
            x_novo, flag = sorteio(x, num_nodes, edges)
        f_curr = calcula(x)
        f_new = calcula(x_novo)
        
        if f_new < f_curr:
            x = x_novo
            if f_new < melhor_valor:
                melhor_valor = f_new
                melhor_sol = x_novo
        else:
            # aceitar pior com probabilidade
            delta = f_curr - f_new
            if np.random.rand() < np.exp(-delta / T):
                x = x_novo
    T *= alpha

print("Melhor valor:", melhor_valor)
print("Itens selecionados:", melhor_sol)

# Plot MST (edges highlighted in red)
plt.subplot(1, 3, 3)
nx.draw(G, pos, with_labels=True, node_color="lightgreen", node_size=800, font_size=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for w, u, v in melhor_sol], width=3, edge_color="red")
plt.title(f"S.A. - CUSTO: {melhor_valor}")


# Save figure as PNG (high resolution)
plt.savefig("kruskal_mst.png", dpi=300, bbox_inches="tight")
plt.close()