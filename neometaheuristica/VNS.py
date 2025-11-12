from modelo.classes import *
from utils.utils import *
from neometaheuristica.algoritmo_guloso import *
from neometaheuristica.neighbour import *
import pandas as pd

def VNS(sistema_inicial, n_iter=3):
    sol_best = solucao_gulosa(sistema_inicial)
    
    gera_log_unitcommitment(sol_best)
    executa_solucao_pl(sol_best)
    
    #exit(1)
    custo_guloso = sol_best.total_cost
    cost_best = sol_best.total_cost
    sol_curr = copy.deepcopy(sol_best)
    cost_curr = cost_best
    print("#################")
    print("SOL GULOSA")
    print("custo_guloso: ", custo_guloso)
    print("#################")
    lista_df = []
    df = pd.DataFrame(
        {
            "Iteracao":[0],
            "Custo_Total":[custo_guloso]
        }
    )
    lista_df.append(df)

    for iter in range(n_iter):
        print("iter: ",  iter, " sol_curr: ", sol_curr.total_cost)
        
        grau = 1
        for a in range(8):
            for i in range(10):
                sol_new = neighbor(copy.deepcopy(sol_curr), grau)
                cost_new = sol_new.total_cost
                delta_fob = cost_new - cost_curr   
            if delta_fob < 0:
                break
            else:
                grau += 1

        if delta_fob < 0:
            sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
            df = pd.DataFrame(
                {
                    "Iteracao":[iter],
                    "Custo_Total":[cost_new]
                }
            )
            lista_df.append(df)
            if cost_curr < cost_best:
                print("##############################")
                print("iter: ", iter)
                print("cost_new: ", cost_new)
                print("Demanda: ", sol_new.demanda)
                sol_best, cost_best = copy.deepcopy(sol_curr), cost_curr
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    gera_log_unitcommitment(sol_best)
    return sol_best, cost_best, df_fim 