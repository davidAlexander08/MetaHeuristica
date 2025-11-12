from modelo.classes import *
from utils.utils import *
from neometaheuristica.algoritmo_guloso import *
from neometaheuristica.neighbour import *
import pandas as pd


def simulated_annealing(sistema_inicial, T0=100.0, alpha=0.9, n_iter=10, Tf = 70):
    sol_best = solucao_gulosa(sistema_inicial)
    custo_guloso = sol_best.total_cost
    cost_best = sol_best.total_cost
    sol_curr = copy.deepcopy(sol_best)
    cost_curr = cost_best
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
                if cost_curr < cost_best:
                    print("T: ", T, " iter: ", iter, " custo: ", sol_new.total_cost)
                    print("##############################")
                    print("iter: ", iter)
                    print("cost_new: ", cost_new)
                    print("Demanda: ", sol_new.demanda)
                    sol_best, cost_best = copy.deepcopy(sol_curr), cost_curr
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
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return sol_best, cost_best, df_fim 