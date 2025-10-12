import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import plotly.graph_objects as go

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

# --------------------------
# Função objetivo
# --------------------------
def total_cost(p, defic):
    cost = sum(Custo[unit]*p[unit][t] for unit in N for t in range(len(P)))
    cost += sum(custo_deficit*defic[t]for t in range(len(P)))  # custo de déficit
    return cost

def solucao_gulosa(p_g, flag, usina, t):
    Deficit_g = copy.deepcopy(Deficit)
    Armazenamento_g = copy.deepcopy(Armazenamento_orig)
    ordem_menor_termica_maior_termica = sorted(Custo, key=Custo.get)
    N_linha = N.copy()
    if(flag == 1):
        N_linha.remove(usina)
    for t in range(len(P)):
        total_gen = 0 if flag == 0 else  p_g[usina][t]
        for unit in N_linha:
            if unit in Hydros:
                Armazenamento_g[unit][t] = Armazenamento_g[unit][t] + Afluencia[unit][t]
                #print("Armazenamento_g[unit][t]: ", Armazenamento_g[unit][t])
                if (total_gen != Demanda[t]):
                    geracao = min(LimSup[unit], Armazenamento_g[unit][t], Demanda[t]- total_gen)
                    p_g[unit][t] = geracao
                    Armazenamento_g[unit][t] = Armazenamento_g[unit][t] - geracao
                    if(t+1 != len(P)):
                        Armazenamento_g[unit][t+1] = Armazenamento_g[unit][t]
                    #else:
                        #print("VERTEU: ", Armazenamento_g[unit][t])
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
    t = random.randint(0, len(P)-1)
    # Escolhe unidade aleatória para alterar
    unit = random.choice(N)

    # Perturbação aleatória (subir ou descer geração)
    delta = random.randint(-10, 10)  # por exemplo ±10 MW
    #delta = 0
    #unit = "H1"
    #t = 1
    #unit = "H1"
    #delta = 10
    #print("delta: ", delta, " t: ", t, " unit: ", unit)
    #print("pnew: ", p_new)
    #print("deficit_new: ", deficit_new)
    #print("Armazenamento_new: ", Armazenamento_new)

    p_new[unit][t] = p_new[unit][t] + delta 

    if(p_new[unit][t] < 0):
        p_new[unit][t] = p[unit][t]
        delta = 0
    if(p_new[unit][t] > LimSup[unit]):
        p_new[unit][t] = p[unit][t]
        delta = 0
    
    if(p_new[unit][t] > Demanda[t]):
        p_new[unit][t] = p[unit][t]
        delta = 0

    if(unit in Hydros):
        indices = range(len(P)) 
        energia_disponivel_hidro = sum(Afluencia[unit][t] for t in indices) + sum(Armazenamento_orig[unit][t] for t in indices)
        energia_geracao_hidro = sum(p_new[unit][t] for t in indices)  
        if(energia_geracao_hidro > energia_disponivel_hidro):
            p_new[unit][t] = p[unit][t]
            Armazenamento_new[unit][t] = Armazenamento_n[unit][t] 

        Armazenamento_new[unit][t] = Armazenamento_n[unit][t] - delta
        if(Armazenamento_new[unit][t] > Armazenamento_max[unit][t]):
            p_new[unit][t] = p[unit][t]
            Armazenamento_new[unit][t] = Armazenamento_n[unit][t] 
        if(Armazenamento_new[unit][t] < Armazenamento_min[unit][t]):
            p_new[unit][t] = p[unit][t]
            Armazenamento_new[unit][t] = Armazenamento_n[unit][t] 
    p_new, deficit_new, Armazenamento_new = solucao_gulosa(copy.deepcopy(p_new), 1, unit, t)
    return p_new, deficit_new, Armazenamento_new


# --------------------------
# Simulated Annealing
# --------------------------

def simulated_annealing(T0=1000.0, alpha=0.9, n_iter=150):
    p_best, def_best, armazenamento_best = solucao_gulosa(copy.deepcopy(p), 0, "0", 0)
    cost_best = total_cost(p_best, def_best)
    p_curr, def_curr, armaz_curr = copy.deepcopy(p_best), copy.deepcopy(def_best), copy.deepcopy(armazenamento_best)
    cost_curr = cost_best
    T = T0
    iteracoes = {}
    for iter in range(n_iter):
        p_new, def_new, armaz_new = neighbor(copy.deepcopy(p_curr), copy.deepcopy(def_curr), copy.deepcopy(armaz_curr))
        cost_new = total_cost(p_new, def_new)
        #exit(1)
        delta_fob = cost_new - cost_curr   
        if delta_fob < 0 or random.random() < np.exp(-delta_fob/T):
            p_curr, def_curr, armaz_curr, cost_curr = p_new, def_new, armaz_new, cost_new
            iteracoes[iter] = cost_new
            print("##############################")
            print("iter: ", iter)
            print("p_new: ", p_new)
            print("def_new: ", def_new)
            print("armaz_new: ", armaz_new)
            print("cost_new: ", cost_new)
            print("Demanda: ", Demanda)
            if cost_curr < cost_best:
                p_best, def_best, armazenamento_best, cost_best = p_curr.copy(), def_curr.copy(), armaz_curr.copy(), cost_curr
        T *= alpha
    return p_best, def_best, armazenamento_best, cost_best, iteracoes

# --------------------------
# Executar SA
# --------------------------
p_sol, def_sol, armaz_sol, cost_sol, iteracoes = simulated_annealing()
print("Objective (total cost) via SA:", cost_sol)
print("p_sol: ", p_sol)
print("def_sol: ", def_sol)
print("armaz_sol: ", armaz_sol)
print("iter: ", iteracoes)

# Convert to sorted lists for plotting
iterations = sorted(iteracoes.keys())
costs = [iteracoes[i] for i in iterations]

# Create Plotly line plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=iterations,
    y=costs,
    mode='lines+markers',
    line=dict(width=3, color='royalblue'),
    marker=dict(size=8),
    name="Best Cost"
))

fig.update_layout(
    title="Evolution of Best Cost (Simulated Annealing)",
    xaxis_title="Iteration",
    yaxis_title="Objective Function Value",
    template="plotly_white",
    font=dict(size=14),
    width=800,
    height=500
)

fig.write_html("sa_best_cost.html", include_plotlyjs='cdn')
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
plt.figure(figsize=(10,6))
plt.plot(df_summary["Period"], df_summary["Demand"], label="Demand", lw=2)
plt.plot(df_summary["Period"], df_summary["TotalGen"], label="Total Generation", lw=2)
plt.xlabel("Period")
plt.ylabel("MW")
plt.title("Dispatch via Simulated Annealing")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("dispatch_plot_SA.png")
plt.show()
