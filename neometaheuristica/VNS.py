from modelo.classes import *
from utils.utils import *
from neometaheuristica.algoritmo_guloso import *
from neometaheuristica.neighbour import *
import pandas as pd

def VNS(sistema_inicial, n_iter=150):
    sol_best = solucao_gulosa(sistema_inicial)
    gera_log_unitcommitment(sol_best)
    executa_solucao_pl(sol_best)    
    sol_curr = copy.deepcopy(sol_best)
    print("#################")
    print("SOL GULOSA")
    print("custo_guloso: ", sol_best.total_cost)
    print("#################")
    lista_df = []
    df = pd.DataFrame(
        {
            "Iteracao":[0],
            "Custo_Total":[sol_best.total_cost]
        }
    )
    lista_df.append(df)

    for iter in range(n_iter):
        print("iter: ",  iter, " sol_curr: ", sol_curr.total_cost)
        
        grau = 1
        for a in range(8):
            for i in range(10):
                sol_new = gera_vizinho_VNS(copy.deepcopy(sol_curr))
                delta_fob = sol_new.total_cost - sol_best.total_cost   
            if delta_fob < 0:
                break
            else:
                grau += 1

        if delta_fob < 0:
            sol_curr = copy.deepcopy(sol_new)
            df = pd.DataFrame(
                {
                    "Iteracao":[iter],
                    "Custo_Total":[sol_new.total_cost]
                }
            )
            lista_df.append(df)
            if sol_best.total_cost < sol_best.total_cost:
                print("##############################")
                print("iter: ", iter)
                print("cost_new: ", sol_new.total_cost)
                #print("Demanda: ", sol_new.demanda)
                sol_best = copy.deepcopy(sol_curr)
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    gera_log_unitcommitment(sol_best)
    return sol_best, df_fim 