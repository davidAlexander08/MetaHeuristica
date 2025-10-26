
from solucao_gulosa_Kruskal import *
from simulated_Annealing import *



# Run Kruskal
#mst, custo = kruskal(10, edges)
mst, custo = kruskal_MetaHeuristica(num_nodes, edges)
melhor_valor, melhor_sol = simulated_Annealing(mst)


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






# Plot MST (edges highlighted in red)
plt.subplot(1, 3, 3)
nx.draw(G, pos, with_labels=True, node_color="lightgreen", node_size=800, font_size=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for w, u, v in melhor_sol], width=3, edge_color="red")
plt.title(f"S.A. - CUSTO: {melhor_valor}")


# Save figure as PNG (high resolution)
plt.savefig("kruskal_mst.png", dpi=300, bbox_inches="tight")
plt.close()