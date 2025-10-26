import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import plotly.graph_objects as go


Hydros = []
Terms = ["T1", "T2"]
N = Hydros + Terms 
P = [1,2,3]
Custo = {"H1": 0, "T1": 10, "T2":20}
LimSup = {"H1": 200, "T1": 100, "T2":50}
Demanda = np.array([50, 100, 150])
Afluencia = {"H1":[100, 50, 0]}
Armazenamento_orig = {"H1":[0,0,0]}
Armazenamento_min = {"H1":[0,0,0]}
Armazenamento_max = {"H1":[999,999,999]}
Deficit = np.zeros(len(P))
custo_deficit = 1000
p = {unit:[0.0]*len(P) for unit in N}


#random.seed(1)
#np.random.seed(1)

# --------------------------
# Dados
# --------------------------
Hydros = ["H1"]
Terms = ["T1"]
N = Hydros + Terms 
P = [1,2,3]
Custo = {"H1": 0, "T1": 10}
LimSup = {"H1": 200, "T1": 100}
Demanda = np.array([50, 100, 150])
Afluencia = {"H1":[100, 50, 0]}
Armazenamento_orig = {"H1":[0,0,0]}
Armazenamento_min = {"H1":[0,0,0]}
Armazenamento_max = {"H1":[999,999,999]}
Deficit = np.zeros(len(P))
custo_deficit = 1000
p = {unit:[0.0]*len(P) for unit in N}





#Hydros = ["H1"]
#Terms = ["T1", "T2"]
#N = Hydros + Terms 
#P = [1,2,3]
#Custo = {"H1": 0, "H2":0, "T1": 10, "T2":20}
#LimSup = {"H1": 200, "H2":200, "T1": 100, "T2":100}
#Demanda = np.array([100, 200, 250])
#Afluencia = {"H1":[100, 50, 0], "H2":[100, 50, 0]}
#Armazenamento_orig = {"H1":[0,0,0], "H2":[0,0,0]}
#Armazenamento_min = {"H1":[0,0,0], "H2":[0,0,0]}
#Armazenamento_max = {"H1":[999,999,999], "H2":[999,999,999]}
#Deficit = np.zeros(len(P))
#custo_deficit = 1000
#p = {unit:[0.0]*len(P) for unit in N}



#Hydros = ["H1", "H2"]
#Terms = ["T1", "T2"]
#N = Hydros + Terms 
#P = [1,2,3]
#Custo = {"H1": 0, "H2":1, "T1": 10, "T2":20}
#LimSup = {"H1": 200, "H2":200, "T1": 100, "T2":100}
#Demanda = np.array([100, 200, 300])
#Afluencia = {"H1":[100, 50, 0], "H2":[150, 0, 0]}
#Armazenamento_orig = {"H1":[0,0,0], "H2":[0,0,0]}
#Armazenamento_min = {"H1":[0,0,0], "H2":[0,0,0]}
#Armazenamento_max = {"H1":[999,999,999], "H2":[999,999,999]}
#Deficit = np.zeros(len(P))
#custo_deficit = 1000
#p = {unit:[0.0]*len(P) for unit in N}

# --------------------------
# Função objetivo
# --------------------------
def total_cost(p, defic):
    cost = sum(Custo[unit]*p[unit][t] for unit in N for t in range(len(P)))
    cost += sum(custo_deficit*defic[t]for t in range(len(P)))  # custo de déficit
    return cost

def solucao_gulosa(p_g, flag, usina, t_perturba):
    Deficit_g = copy.deepcopy(Deficit)
    Armazenamento_g = copy.deepcopy(Armazenamento_orig)
    ordem_menor_termica_maior_termica = sorted(Custo, key=Custo.get)
    N_linha = copy.deepcopy(N)
    if(flag == 1):
        for usi in usina:
            N_linha.remove(usi)
    for t in range(len(P)):
        total_gen = 0 
        if(flag == 1):
            total_gen  += p_g[usi][t]

        for unit in N_linha:
            if unit in Hydros:
                #print("unit: ", unit)
                Armazenamento_g[unit][t] = Armazenamento_g[unit][t] + Afluencia[unit][t]
                #print("Armazenamento_g[unit][t]: ", Armazenamento_g[unit][t])
                if (total_gen != Demanda[t]):
                    geracao = 0
                    geracao = min(LimSup[unit], Armazenamento_g[unit][t], Demanda[t]- total_gen)
                    p_g[unit][t] = geracao
                    Armazenamento_g[unit][t] = Armazenamento_g[unit][t] - geracao
                if(t+1 != len(P)):
                    Armazenamento_g[unit][t+1] = Armazenamento_g[unit][t]
                else:
                    p_g[unit][t] = 0
            else:
                if (total_gen != Demanda[t]):
                    geracao = min(LimSup[unit], Demanda[t] - total_gen)            
                    p_g[unit][t] = geracao
                else:
                    p_g[unit][t] = 0
            total_gen +=  p_g[unit][t]
        Deficit_g[t] = Demanda[t] - total_gen
    return p_g, Deficit_g, Armazenamento_g


# --------------------------
# Variação de solução (neighbor)
# --------------------------
def neighbor(p_n, Deficit_n, Armazenamento_n):
    # Cria cópias da solução atual

    p_new = copy.deepcopy(p_n)
    deficit_new = copy.deepcopy(Deficit_n)
    Armazenamento_new = copy.deepcopy(Armazenamento_n)

    # Escolhe período aleatório para alterar
    t = random.choice(P)-1
    unit = random.choice(N)
    delta = random.randint(-20, 20)
    #delta = random.uniform(-3, 3)

    #unit = "H2"
    #t = 1
    #delta = -1

    #print("delta: ", delta, " t: ", t, " unit: ", unit)


    p_new[unit][t] = p_new[unit][t] + delta 


    if(p_new[unit][t] < 0):
        p_new = copy.deepcopy(p_n)
        delta = 0
    if(p_new[unit][t] > LimSup[unit]):
        p_new = copy.deepcopy(p_n)
        delta = 0
    
    if(p_new[unit][t] > Demanda[t]):
        p_new = copy.deepcopy(p_n)
        delta = 0


    if(unit in Hydros):
        P_linha = P.copy()
        P_linha.remove(t+1)
        t_linha = random.choice(P_linha)-1
        p_new[unit][t_linha] = p_new[unit][t_linha] - delta 

        if(p_new[unit][t_linha] < 0):
            p_new = copy.deepcopy(p_n)
            delta = 0
        if(p_new[unit][t_linha] > LimSup[unit]):
            p_new = copy.deepcopy(p_n)
            delta = 0
        
        if(p_new[unit][t_linha] > Demanda[t_linha]):
            p_new = copy.deepcopy(p_n)
            delta = 0

    p_new, deficit_new, Armazenamento_new = solucao_gulosa(copy.deepcopy(p_new), 1, [unit], t)
    #print("p_new: ", p_new)
    #print("deficit_new: ", deficit_new)
    #print("Armazenamento_new: ", Armazenamento_new)
    #exit(1)
    return p_new, deficit_new, Armazenamento_new


# --------------------------
# Simulated Annealing
# --------------------------

def simulated_annealing(T0=100.0, alpha=0.95, n_iter=100, Tf = 1):
    p_best, def_best, armazenamento_best = solucao_gulosa(copy.deepcopy(p), 0, "0", 0)
    custo_guloso = total_cost(p_best, def_best)
    cost_best = total_cost(p_best, def_best)
    p_curr, def_curr, armaz_curr = copy.deepcopy(p_best), copy.deepcopy(def_best), copy.deepcopy(armazenamento_best)
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
            p_new, def_new, armaz_new = neighbor(copy.deepcopy(p_curr), copy.deepcopy(def_curr), copy.deepcopy(armaz_curr))
            cost_new = total_cost(p_new, def_new)
            delta_fob = cost_new - cost_curr   
            if delta_fob < 0:
                p_curr, def_curr, armaz_curr, cost_curr = copy.deepcopy(p_new), copy.deepcopy(def_new), copy.deepcopy(armaz_new), cost_new
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
                    print("def_new: ", def_new)
                    print("armaz_new: ", armaz_new)
                    print("cost_new: ", cost_new)
                    print("Demanda: ", Demanda)
                    p_best, def_best, armazenamento_best, cost_best = copy.deepcopy(p_curr), copy.deepcopy(def_curr), copy.deepcopy(armaz_curr), cost_curr
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
                    p_curr, def_curr, armaz_curr, cost_curr = copy.deepcopy(p_new), copy.deepcopy(def_new), copy.deepcopy(armaz_new), cost_new
        T *= alpha
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return p_best, def_best, armazenamento_best, cost_best, df_fim 

def ILS(n_iter=100):
    p_best, def_best, armazenamento_best = solucao_gulosa(copy.deepcopy(p), 0, "0", 0)
    custo_guloso = total_cost(p_best, def_best)
    cost_best = total_cost(p_best, def_best)
    p_curr, def_curr, armaz_curr = copy.deepcopy(p_best), copy.deepcopy(def_best), copy.deepcopy(armazenamento_best)
    cost_curr = cost_best
    print("###SOL GULOSA")
    print("p_best: ", p_best)
    print("custo_guloso: ", custo_guloso)
    lista_df = []
    df = pd.DataFrame(
        {
            "Iteracao":[0],
            "Custo_Total":[custo_guloso]
        }
    )
    lista_df.append(df)

    for iter in range(n_iter):
        p_new, def_new, armaz_new = neighbor(copy.deepcopy(p_curr), copy.deepcopy(def_curr), copy.deepcopy(armaz_curr))
        cost_new = total_cost(p_new, def_new)
        delta_fob = cost_new - cost_curr   
        if delta_fob < 0:
            p_curr, def_curr, armaz_curr, cost_curr = copy.deepcopy(p_new), copy.deepcopy(def_new), copy.deepcopy(armaz_new), cost_new
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
                print("p_new: ", p_new)
                print("def_new: ", def_new)
                print("armaz_new: ", armaz_new)
                print("cost_new: ", cost_new)
                print("Demanda: ", Demanda)
                p_best, def_best, armazenamento_best, cost_best = copy.deepcopy(p_curr), copy.deepcopy(def_curr), copy.deepcopy(armaz_curr), cost_curr
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return p_best, def_best, armazenamento_best, cost_best, df_fim 

#EXECUTA ILS

p_sol, def_sol, armaz_sol, cost_sol, df_fim = ILS()
print("Objective (total cost) via SA:", cost_sol)
print("p_sol: ", p_sol)
print("def_sol: ", def_sol)
print("armaz_sol: ", armaz_sol)
print(df_fim)


# Create Plotly line plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_fim["Iteracao"],
    y=df_fim["Custo_Total"],
    mode='lines+markers',
    line=dict(width=3, color='royalblue'),
    marker=dict(size=8),
    name="Best Cost"
))

fig.update_layout(
    title=f"ILS",
    xaxis_title="Iteration",
    yaxis_title="Objective Function Value",
    template="plotly_white",
    font=dict(size=14),
    width=800,
    height=500
)

fig.write_html(f"sa_best_cost_ILS.html", include_plotlyjs='cdn')
print("Plot saved as sa_best_cost.html")


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

    fig.write_html(f"sa_best_cost_{temperatura}.html", include_plotlyjs='cdn')
    print("Plot saved as sa_best_cost.html")

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
