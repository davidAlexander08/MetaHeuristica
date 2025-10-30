from modelo.classes import *
from utils.utils import *
from metaheuristicas.algoritmo_guloso import *
from metaheuristicas.neighbour import *
import pandas as pd
import copy

def busca_tabu(sistema_inicial, n_iter=100, tabu_tenure=10):
    # Solução inicial gulosa
    sol_best_ts = solucao_gulosa(sistema_inicial)
    custo_guloso = sol_best_ts.total_cost
    cost_best_ts = sol_best_ts.total_cost
    sol_curr = copy.deepcopy(sol_best_ts)
    cost_curr = cost_best_ts
    
    print("#################")
    print("SOLUÇÃO INICIAL GULOSA")
    print("custo_guloso: ", custo_guloso)
    print("#################")
    
    # Lista tabu - armazena as soluções/movimentos proibidos
    lista_tabu = []
    lista_df = []
    
    df = pd.DataFrame(
        {
            "Iteracao": [0],
            "Custo_Total": [custo_guloso]
        }
    )
    lista_df.append(df)

    for iter in range(n_iter):
        print("iter: ", iter)
        
        # Gera vizinho
        sol_new = neighbor(copy.deepcopy(sol_curr))
        cost_new = sol_new.total_cost
        
        # Critério de aspiração: aceita se for melhor que a melhor solução global
        # ou se a solução não estiver na lista tabu
        if cost_new < cost_best_ts or sol_new not in lista_tabu:
            sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
            
            df = pd.DataFrame(
                {
                    "Iteracao": [iter + 1],
                    "Custo_Total": [cost_new]
                }
            )
            lista_df.append(df)
            
            # Atualiza melhor solução global
            if cost_curr < cost_best_ts:
                print("##############################")
                print("iter: ", iter)
                print("Nova melhor solução encontrada!")
                print("cost_new: ", cost_new)
                print("Demanda: ", sol_new.demanda)
                sol_best_ts, cost_best_ts = copy.deepcopy(sol_curr), cost_curr
        
        # Adiciona solução atual à lista tabu
        lista_tabu.append(copy.deepcopy(sol_curr))
        
        # Mantém o tamanho da lista tabu (estratégia FIFO)
        if len(lista_tabu) > tabu_tenure:
            lista_tabu.pop(0)
    
    df_fim = pd.concat(lista_df).reset_index(drop=True)
    return sol_best_ts, cost_best_ts, df_fim