from modelo.classes import *
from utils.utils import *
from metaheuristicas.algoritmo_guloso import *
from metaheuristicas.neighbour import *
import pandas as pd


def simulated_annealing(sistema_inicial, T0=100.0, alpha=0.9, n_iter=100, Tf = 50):
    sol_best_sa = solucao_gulosa(sistema_inicial)
    custo_guloso = sol_best_sa.total_cost
    cost_best_sa = sol_best_sa.total_cost
    sol_curr = copy.deepcopy(sol_best_sa)
    cost_curr = cost_best_sa
    print("#################")
    print("SOL GULOSA")
    print("custo_guloso: ", custo_guloso)
    print("#################")

    T = T0
    lista_df = []
    df = pd.DataFrame(
        {
            "Temperatura":[T],
            "Iteracao":[0],
            "Custo_Total":[custo_guloso]
        }
    )
    lista_df.append(df)
    
    while T > Tf:
        for iter in range(n_iter):
            sol_new = neighbor(copy.deepcopy(sol_curr))
            cost_new = sol_new.total_cost
            delta_fob = cost_new - cost_curr  
            if delta_fob < 0:
                sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
                df = pd.DataFrame(
                    {
                        "Temperatura":[T],
                        "Iteracao":[iter],
                        "Custo_Total":[cost_new]
                    }
                )
                lista_df.append(df)
                if cost_curr < cost_best_sa:
                    print("T: ", T, " iter: ", iter, " custo: ", sol_new.total_cost)
                    print("##############################")
                    print("iter: ", iter)
                    print("cost_new: ", cost_new)
                    print("Demanda: ", sol_new.demanda)
                    sol_best_sa, cost_best_sa = copy.deepcopy(sol_curr), cost_curr
            else:
                if(random.random() < np.exp(-delta_fob/T)):
                    df = pd.DataFrame(
                        {
                            "Temperatura":[T],
                            "Iteracao":[iter],
                            "Custo_Total":[cost_new]
                        }
                    )
                    lista_df.append(df)
                    sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
        T *= alpha
    df_fim_sa = pd.concat(lista_df).reset_index(drop = True)
    return sol_best_sa, cost_best_sa, df_fim_sa 