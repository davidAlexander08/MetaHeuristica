from modelo.classes import *
from utils.utils import *
from neometaheuristica.algoritmo_guloso import *
from neometaheuristica.neighbour import *
import pandas as pd

def ILS(sistema_inicial, n_iter=150, especial = False):
    sol_best = nova_solucao_gulosa(sistema_inicial, False)
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
        if(especial == False):
            sol_new = gera_vizinho_ILS(copy.deepcopy(sol_curr))
        if(especial == True):
            sol_new = gera_solucao_vizinhos_custom(copy.deepcopy(sol_curr))
        delta_fob = sol_new.total_cost - sol_curr.total_cost   
        if delta_fob < 0:
            sol_curr= copy.deepcopy(sol_new)
            df = pd.DataFrame(
                {
                    "Iteracao":[iter],
                    "Custo_Total":[sol_new.total_cost]
                }
            )
            lista_df.append(df)
            if sol_curr.total_cost < sol_best.total_cost:
                print("##############################")
                print("iter: ", iter, " sol_new.total_cost: ", sol_new.total_cost)
                sol_best = copy.deepcopy(sol_curr)
                gera_log_informacoes(sol_best)
                if(sol_new.total_cost <906700 ):
                    exit(1)
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    gera_log_unitcommitment(sol_best)
    return sol_best, df_fim 