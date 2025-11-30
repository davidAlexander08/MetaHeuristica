from modelo.classes import *
from utils.utils import *
from neometaheuristica.algoritmo_guloso import *
from neometaheuristica.neighbour import *
import pandas as pd


def simulated_annealing(sistema_inicial, T0=15000.0, alpha=0.9, n_iter=50, Tf = 100):
    sol_best = nova_solucao_gulosa(sistema_inicial, ativa_random = True)
    sol_curr = copy.deepcopy(sol_best)
    print("#################")
    print("SOL GULOSA")
    print("custo_guloso: ", sol_curr.total_cost)
    print("#################")

    T = T0
    lista_df = []
    df = pd.DataFrame(
        {
            "Temperatura":[T],
            "Iteracao":[0],
            "Custo_Total":[sol_best.total_cost]
        }
    )
    lista_df.append(df)
    
    while T > Tf:
        for iter in range(n_iter):
            sol_new = gera_vizinho_SA(copy.deepcopy(sol_curr))
            delta_fob = sol_new.total_cost - sol_curr.total_cost  
            if delta_fob < 0:
                sol_curr = copy.deepcopy(sol_new)
                if sol_curr.total_cost < sol_best.total_cost:
                    df = pd.DataFrame(
                        {
                            "Temperatura":[T],
                            "Iteracao":[iter],
                            "Custo_Total":[sol_new.total_cost]
                        }
                    )
                    lista_df.append(df)
                    print("##############################")
                    print("T: ", T, " iter: ", iter, " custo: ", sol_new.total_cost)
                    sol_best = copy.deepcopy(sol_curr)
            if(delta_fob > 0):
                if((sol_new.total_cost != sol_curr.total_cost)):
                    probabilidade = np.exp(-delta_fob/T)
                    var_aleatoria = random.random()
                    #print("probabilidade: ", probabilidade, " var_ale: ", var_aleatoria, " T: ", T)
                    if((var_aleatoria < probabilidade)):
                        print("##############################")
                        print("T: ", T, " iter: ", iter, " custo: ", sol_new.total_cost)
                        print("sol_new.total_cost: ", sol_new.total_cost, " sol_curr.total_cost: ", sol_curr.total_cost," random.random(): ", var_aleatoria,  " probabilidade: ", probabilidade, " delta_fob: ", delta_fob, " T: ", T)
                        df = pd.DataFrame(
                            {
                                "Temperatura":[T],
                                "Iteracao":[iter],
                                "Custo_Total":[sol_new.total_cost]
                            }
                        )
                        lista_df.append(df)
                        sol_curr = copy.deepcopy(sol_new)
        T *= alpha
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return sol_best, df_fim 