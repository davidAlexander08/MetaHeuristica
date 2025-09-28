import networkx as nx
import matplotlib.pyplot as plt


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        
        self.rank = [0] * n

        print(self.parent)

        print(self.rank)

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])  # path compression
        return self.parent[u]

    def union(self, u, v):
        root_u, root_v = self.find(u), self.find(v)
        print("u: ", u, " v: ", v)
        print("root_u: ", root_u, " self.rank[root_u]: ", self.rank[root_u], " root_v: ", root_v, " self.rank[root_v]: ", self.rank[root_v])
        if self.rank[root_u] < self.rank[root_v]:
            self.parent[root_u] = root_v
        elif self.rank[root_u] > self.rank[root_v]:
            self.parent[root_v] = root_u
        else:
            self.parent[root_v] = root_u
            self.rank[root_u] += 1
        print("root_u: ", root_u, " self.rank[root_u]: ", self.rank[root_u], " root_v: ", root_v, " self.rank[root_v]: ", self.rank[root_v])

        return True


def kruskal(n, edges):
    """
    n: número de vértices (0 a n-1)
    edges: lista de arestas no formato (peso, u, v)
    """


    edges.sort()  # ordena por peso

    uf = UnionFind(n)


    mst = []
    custo_total = 0

    for peso, u, v in edges:
        if uf.union(u, v):
            mst.append((u, v, peso))
            custo_total += peso
    print(edges)
    exit(1)
    return mst, custo_total

def busca_pai(lista_edges, de):
    pai = 0
    for edge in lista_edges:
        if(de == edge[0]):
            pai = edge[1]
    return pai

def encontra_pai(lista_edges, de):
    pai = de
    pai_anterior = 0
    while pai != 0:
        pai_anterior = pai
        pai = busca_pai(lista_edges,pai)
        if(pai == 0):
            break
    print(pai_anterior)
    return pai_anterior

def verifica_ciclo(mst, peso, de, para):
    booleano = True
    print("de: ", de, " para: ", para, " peso: ", peso)
    if(len(mst) != 0):
        pai = encontra_pai(mst, de)
        booleano = True if de == pai else False
    return booleano

def kruskal_MetaHeuristica(n, edges):
    """
    n: número de vértices (1 a n)
    edges: lista de arestas no formato (peso, u, v)
    """
    edges.sort()  # ordena por peso
    mst = []
    custo_total = 0
    for peso, u, v in edges:
        Switch = verifica_ciclo(mst, peso, u, v)
        if(Switch):
            mst.append((u, v, peso))
            custo_total += peso
        print(mst)
    return mst, custo_total

edges = [
    (5, 0, 2),
    (10, 1, 2),
    (12, 2, 3),
    (8, 1, 4),
    (8, 4, 5),
    (7, 1, 5),
    (1, 2, 5),
    (5, 5, 6),
    (6, 3, 6),
    (1, 4, 7),
    (4, 5, 7),
    (8, 7, 8),
    (1, 5, 8),
    (5, 8, 9),
    (2, 6, 9),
]

##EXEMPLO AULA

edges = [
    (6, 1, 3),
    (3, 2, 3),
    (9, 3, 4),
    (8, 2, 5),
    (3, 2, 6),
    (2, 5, 6),
    (1, 3, 6),
    (5, 6, 7),
    (1, 4, 7),
]

# Para NetworkX, precisamos (u, v, weight)
edges_nx = [(u, v, peso) for peso, u, v in edges]

# Build the graph
G = nx.Graph()
G.add_weighted_edges_from(edges_nx)

# Run Kruskal
#mst, custo = kruskal(10, edges)
mst, custo = kruskal_MetaHeuristica(10, edges)

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