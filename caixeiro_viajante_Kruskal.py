import networkx as nx
import matplotlib.pyplot as plt


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
        if(node == edge[0]):
            lista_opcoes_caminho.append(edge)
        if(node == edge[1]):
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
    print("de: ", de, " para: ", para, " peso: ", peso)
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
        print(dicionario_ramos)
        #pai = encontra_pai(mst, de, para)
        #booleano = False if para == pai else True
        #print("pai: ", pai, " b: ", booleano)
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
        if(Switch or len(mst) == n-1):
            print("len: ", len(mst))
            if(dict_grau[u] < 2 and dict_grau[v] < 2):
                dict_grau[u] = dict_grau[u] + 1
                dict_grau[v] = dict_grau[v] + 1
                mst.append((u, v, peso))
                custo_total += peso
                print(mst)
                print(dict_grau)
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

# Para NetworkX, precisamos (u, v, weight)
edges_nx = [(u, v, peso) for peso, u, v in edges]

# Build the graph
G = nx.Graph()
G.add_weighted_edges_from(edges_nx)

# Run Kruskal
#mst, custo = kruskal(10, edges)
mst, custo = kruskal_MetaHeuristica(6, edges)

print("Arestas da Árvore Geradora Mínima:", mst)
print("Custo total:", custo)

# Layout for consistent node positions
pos = nx.spring_layout(G, seed=42)

# Plot original graph
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=800, font_size=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
plt.title("Original Graph")

# Plot MST (edges highlighted in red)
plt.subplot(1, 2, 2)
nx.draw(G, pos, with_labels=True, node_color="lightgreen", node_size=800, font_size=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for u, v, w in mst], width=3, edge_color="red")
plt.title("Minimum Spanning Tree (Kruskal)")

# Save figure as PNG (high resolution)
plt.savefig("kruskal_mst.png", dpi=300, bbox_inches="tight")
plt.close()