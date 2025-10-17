import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import plotly.graph_objects as go


Hydros = []
Terms = ["T1", "T2", "T3"]
N = Hydros + Terms 
P = [1,2,3,4,5,6,7,8]
Custo = {"T1": 10, "T2":20 , "T3":30}
LimSup = {"H1": 200, "T1": 100, "T2":50, "T3":100}
LimInf = {"H1": 0, "T1": 10, "T2":30, "T3": 10}
Demanda = np.array([90, 90, 110, 80, 90, 160, 90, 90])
Deficit = np.zeros(len(P))
custo_deficit = 1000
geracoes = {unit:[0.0]*len(P) for unit in N}

TON = {"T1": 2, "T2": 2, "T3":2}
Toff = {"T1": 1, "T2": 1, "T3":1}
UnitCommitment = {"T1": np.zeros(8), "T2": np.zeros(8), "T3": np.zeros(8)}
#random.seed(1)
#np.random.seed(1)


Terms = ["T1", "T2", "T3"]
N = Terms 
P = [1,2,3,4,5,6,7,8]
Custo = {"T1": 10, "T2":20, "T3":30}
LimSup = {"T1": 100, "T2":50, "T3":100}
LimInf = {"T1": 10, "T2":30, "T3": 10}
Demanda = np.array([90, 90, 110, 90, 90, 90, 90, 90])
geracoes = {unit:[0.0]*len(P) for unit in N}
TON = {"T1": 2, "T2": 5, "T3":2}
Toff = {"T1": 1, "T2": 1, "T3":1}
UnitCommitment = {"T1": np.zeros(8), "T2": np.zeros(8), "T3": np.zeros(8)}

# --------------------------
# Função objetivo
# --------------------------
def total_cost(p):
    cost = sum(Custo[unit]*p[unit][t] for unit in N for t in range(len(P)))
    return cost

def consecutive_ones(v, pos):
    if v[pos] == 0:
        return 0

    count = 1
    # Left side
    i = pos - 1
    while i >= 0 and v[i] == 1:
        count += 1
        i -= 1

    # Right side
    i = pos + 1
    while i < len(v) and v[i] == 1:
        count += 1
        i += 1

    return count

def atualiza_demanda_liquida(dic_geracao, vetor_usinas):
    geracao_total = np.array([0.0]*len(P))
    for estagio in range(len(P)):
        for usina in vetor_usinas:
            geracao_total[estagio] += dic_geracao[usina][estagio]
    return Demanda - geracao_total

def verifica_resolve_inviabilidade(demanda_liquida, p_solucao_relaxada, caminho_usinas):
    #### ADEQUA GERACOES
    ordem_maior_termica = caminho_usinas[::-1]
    for t in range(len(P)):
        if(demanda_liquida[t] < 0):
            diff =  -demanda_liquida[t]
            for unit in ordem_maior_termica:
                if(diff > 0):
                    corte_possivel = p_solucao_relaxada[unit][t] - LimInf[unit]
                    if(corte_possivel > 0):
                        subtracao_diff = min(diff, corte_possivel)
                        p_solucao_relaxada[unit][t] = p_solucao_relaxada[unit][t] - subtracao_diff
                        diff = diff - subtracao_diff
    return p_solucao_relaxada




def solucao_gulosa():
    unit_commitment_g = copy.deepcopy(UnitCommitment)
    p_solucao_relaxada = copy.deepcopy(geracoes)
    ordem_menor_termica_maior_termica = sorted(Custo, key=Custo.get)
    N_linha = copy.deepcopy(ordem_menor_termica_maior_termica)
    for t in range(len(P)):
        lista_caminho_usinas =[]
        for unit in N_linha:
            lista_caminho_usinas.append(unit)
            demanda_liquida = atualiza_demanda_liquida(p_solucao_relaxada, ordem_menor_termica_maior_termica)  
            if (demanda_liquida[t] > 0):
                unit_commitment_g[unit][t] = 1
                if(t != 0):
                    if(unit_commitment_g[unit][t] == 1) and (unit_commitment_g[unit][t-1] == 0):
                        for i in range(t, min(t + TON[unit], max(P))):
                            unit_commitment_g[unit][i] = 1
                            p_solucao_relaxada[unit][i] += LimInf[unit]
                elif(t== 0):
                    for i in range(t, t + TON[unit]):
                        unit_commitment_g[unit][i] = 1
                        p_solucao_relaxada[unit][i] += LimInf[unit]
                demanda_liquida = atualiza_demanda_liquida(p_solucao_relaxada, ordem_menor_termica_maior_termica)    
                limite_geracao = LimSup[unit] if p_solucao_relaxada[unit][t] == 0 else LimSup[unit] - LimInf[unit]
                geracao = max(min(limite_geracao, demanda_liquida[t]),0)
                p_solucao_relaxada[unit][t] += geracao 
                p_solucao_relaxada = verifica_resolve_inviabilidade(demanda_liquida, p_solucao_relaxada, lista_caminho_usinas)
            else:
                p_solucao_relaxada[unit][t] = max(p_solucao_relaxada[unit][t],0)
    df = pd.concat(
        [pd.DataFrame(p_solucao_relaxada), pd.DataFrame(unit_commitment_g)],
        axis=1  # concatena colunas
    )
    df['DemandaLiquida'] = demanda_liquida
    df['Demanda'] = Demanda
    print(df.round(1))
    print("############################")

    print("CUSTO TOTAL: ", total_cost(p_solucao_relaxada))
    return p_solucao_relaxada, unit_commitment_g


def adequa_balanco_potencia_guloso(unit_commitment_entrada):
    p_solucao_relaxada = copy.deepcopy(geracoes)
    ordem_menor_termica_maior_termica = sorted(Custo, key=Custo.get)
    N_linha = copy.deepcopy(ordem_menor_termica_maior_termica)
    inviavel = False
    for t in range(len(P)):
        lista_caminho_usinas =[]
        for unit in N_linha:
            lista_caminho_usinas.append(unit)
            demanda_liquida = atualiza_demanda_liquida(p_solucao_relaxada, ordem_menor_termica_maior_termica)  
            if(unit_commitment_entrada[unit][t] == 1):
                ton_consecutivos = consecutive_ones(unit_commitment_entrada[unit], t)
                inviavel = True if ton_consecutivos < TON[unit] else False
                if(inviavel):
                    df = pd.concat(
                        [pd.DataFrame(unit_commitment_entrada)],
                        axis=1  # concatena colunas
                    )
                    print(df.round(1))
                    print("CUSTO TOTAL: ", total_cost(p_solucao_relaxada))
                    return p_solucao_relaxada, inviavel
                #print("unit: ", unit, " ", consecutive_ones(unit_commitment_entrada[unit], t))
                geracao = max(min(LimSup[unit], demanda_liquida[t]),LimInf[unit])
                p_solucao_relaxada = verifica_resolve_inviabilidade(demanda_liquida, p_solucao_relaxada, lista_caminho_usinas)
            else:
                geracao = 0
            p_solucao_relaxada[unit][t] = geracao 
    df = pd.concat(
        [pd.DataFrame(p_solucao_relaxada), pd.DataFrame(unit_commitment_entrada)],
        axis=1  # concatena colunas
    )
    df['DemandaLiquida'] = demanda_liquida
    df['Demanda'] = Demanda
    print(df.round(1))
    print("############################")
    print("CUSTO TOTAL: ", total_cost(p_solucao_relaxada))
    return p_solucao_relaxada, inviavel

potencia, unit_commitment = solucao_gulosa()
#UnitCommitment = {"T1": [1,1,1,1,1,1,1,1], "T2": np.zeros(8), "T3": [0,0,1,1,0,1,0,0]}
#potencia, inviavel  = adequa_balanco_potencia_guloso(UnitCommitment)
#print("inviavel: ", inviavel)

def reset_unit(unit_n):
    unit_new = {}
    for u, v in unit_n.items():
        if isinstance(v, np.ndarray):
            unit_new[u] = v.copy()  # safe independent copy of array
        else:
            unit_new[u] = copy.deepcopy(v)  # safe copy of list or other objects
    return unit_new
    
# --------------------------
# Variação de solução (neighbor)
# --------------------------
def neighbor(unit_n):
    # Cria cópias da solução atual
    print("ESCOLHENDO VIZINHO")
    # Escolhe período aleatório para alterar
    inviavel = True
    contador = 0
    while inviavel == True:
        unit_new = copy.deepcopy(unit_n)
        t = random.choice(P)-1
        unit = random.choice(N)
        unit_new[unit][t] = 1 - unit_new[unit][t]
        print("t: ",t, " unit: ", unit)
        print("unit_new: ", unit_new)
        print("contador: ", contador)
        ton_unit = TON[unit]


        potencia, inviavel  = adequa_balanco_potencia_guloso(unit_new)
        #print("unit_new: ", unit_new)
        #if(inviavel):
        #    unit_new[unit][t] = 1 - unit_new[unit][t]
        print("inviavel: ", inviavel)
        print("#########################")
        contador += 1
        
        if(contador == 2):
            exit(1)
    return potencia, unit_new


# --------------------------
# Simulated Annealing
# --------------------------

def simulated_annealing(T0=100.0, alpha=0.95, n_iter=100, Tf = 1):
    p_best, unit_best = solucao_gulosa()
    custo_guloso = total_cost(p_best)
    cost_best = total_cost(p_best)
    p_curr = copy.deepcopy(p_best)
    unit_curr = copy.deepcopy(unit_best)
    cost_curr = cost_best
    print("###SOL GULOSA")
    print("p_best: ", p_best)
    print("custo_guloso: ", custo_guloso)
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
            p_new, unit_new = neighbor(copy.deepcopy(unit_curr))
            cost_new = total_cost(p_new)
            delta_fob = cost_new - cost_curr   
            if delta_fob < 0:
                p_curr, unit_curr, cost_curr = copy.deepcopy(p_new), copy.deepcopy(unit_new), cost_new
                df = pd.DataFrame(
                    {
                        "Temperatura":[T],
                        "Iteracao":[iter],
                        "Custo_Total":[cost_new]
                    }
                )
                lista_df.append(df)
                if cost_curr < cost_best:
                    print("##############################")
                    print("iter: ", iter)
                    print("p_new: ", p_new)
                    print("cost_new: ", cost_new)
                    print("Demanda: ", Demanda)
                    p_best, unit_best, cost_best = copy.deepcopy(p_curr), copy.deepcopy(unit_curr), cost_curr
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
                    p_curr, unit_curr, cost_curr = copy.deepcopy(p_new), copy.deepcopy(unit_new), cost_new
        T *= alpha
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return p_best, unit_best, cost_best, df_fim 

#EXECUTA ILS

# --------------------------
# Executar SA
# --------------------------


p_sol, def_sol, armaz_sol, cost_sol, df_fim = simulated_annealing()
print("Objective (total cost) via SA:", cost_sol)
print("p_sol: ", p_sol)
print("def_sol: ", def_sol)
print("armaz_sol: ", armaz_sol)
print(df_fim)



temperaturas = df_fim["Temperatura"].unique()
for temperatura in temperaturas:
    # Create Plotly line plot
    df_plot = df_fim.loc[(df_fim["Temperatura"] == temperatura)].reset_index(drop = True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["Iteracao"],
        y=df_plot["Custo_Total"],
        mode='lines+markers',
        line=dict(width=3, color='royalblue'),
        marker=dict(size=8),
        name="Best Cost"
    ))

    fig.update_layout(
        title=f"S.A. Temperatura {temperatura}",
        xaxis_title="Iteration",
        yaxis_title="Objective Function Value",
        template="plotly_white",
        font=dict(size=14),
        width=800,
        height=500
    )

    #fig.write_html(f"sa_best_cost_{temperatura}.html", include_plotlyjs='cdn')
    #print("Plot saved as sa_best_cost.html")

# --------------------------
# Exportar resultados
# --------------------------
rows = []
for t_idx, t in enumerate(P):
    total_gen = sum(p_sol[unit][t_idx] for unit in N)
    rows.append({
        "Period": t,
        "Demand": Demanda[t_idx],
        "TotalGen": total_gen
    })

df_summary = pd.DataFrame(rows)
df_summary.to_csv("summary_uc_SA.csv", index=False)
print("Summary written to summary_uc_SA.csv")

# --------------------------
# Plot dispatch
# --------------------------
#plt.figure(figsize=(10,6))
#plt.plot(df_summary["Period"], df_summary["Demand"], label="Demand", lw=2)
#plt.plot(df_summary["Period"], df_summary["TotalGen"], label="Total Generation", lw=2)
#plt.xlabel("Period")
#plt.ylabel("MW")
#plt.title("Dispatch via Simulated Annealing")
#plt.legend()
#plt.grid(True)
#plt.tight_layout()
#plt.savefig("dispatch_plot_SA.png")
#plt.show()
