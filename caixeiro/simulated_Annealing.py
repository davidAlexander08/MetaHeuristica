

from instancia import *


### MELHORA DO ALGORITMO POR S.A.



def calcula(sol):
    custo_total = 0
    for peso, u, v  in sol:
        custo_total += peso
    return custo_total



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
    

def simulated_Annealing(mst):

    # Parâmetros S.A.
    T = 100.0
    T_min = 0.1
    alpha = 0.95
    num_iter = 1000

    x = mst.copy()
    melhor_sol = x.copy()

    melhor_valor = calcula(x)
    print("sol_gulosa: ", melhor_sol)
    print("valor_guloso: ", melhor_valor)

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
    return (melhor_valor, melhor_sol)