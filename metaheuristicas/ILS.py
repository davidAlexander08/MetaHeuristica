from modelo.classes import *
from utils.utils import *
from metaheuristicas.algoritmo_guloso import *
from metaheuristicas.neighbour import *
import pandas as pd

def ILS(sistema_inicial, n_iter=100):
    sol_best_ils = solucao_gulosa(sistema_inicial)
    custo_guloso = sol_best_ils.total_cost
    cost_best_ils = sol_best_ils.total_cost
    sol_curr = copy.deepcopy(sol_best_ils)
    cost_curr = cost_best_ils
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
        print("iter: ",  iter)
        sol_new = neighbor(copy.deepcopy(sol_curr))
        cost_new = sol_new.total_cost
        delta_fob = cost_new - cost_curr   
        if delta_fob < 0:
            sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
            df = pd.DataFrame(
                {
                    "Iteracao":[iter],
                    "Custo_Total":[cost_new]
                }
            )
            lista_df.append(df)
            if cost_curr < cost_best_ils:
                print("##############################")
                print("iter: ", iter)
                print("cost_new: ", cost_new)
                print("Demanda: ", sol_new.demanda)
                sol_best_ils, cost_best_ils = copy.deepcopy(sol_curr), cost_curr
    df_fim_ils = pd.concat(lista_df).reset_index(drop = True)
    return sol_best_ils, cost_best_ils, df_fim_ils 