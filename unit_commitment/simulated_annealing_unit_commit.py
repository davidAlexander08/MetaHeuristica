import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# Dados
# --------------------------
N = ["T1", "T2"]       # térmicas
NEol = ["W1"]          # eólica
P = list(range(1, 9))  # períodos

Demanda = np.array([100, 100, 150])
Eolica = np.array([0, 20, 40, 60, 40, 30, 20, 0])
print(Demanda - Eolica)
Custo = {"T1": 10, "T2": 100}
LimSup = {"T1": 100, "T2": 250}
LimInf = {"T1": 10, "T2": 30}
Ton = {"T1":1, "T2":3}  
Combustivel = {"T1": 300, "T2": 300}

# --------------------------
# Função objetivo
# --------------------------
def total_cost(p, u):
    cost = sum(Custo[unit]*p[unit][t] for unit in N for t in range(len(P)))
    #cost += 150000  # custo de déficit
    return cost


# --------------------------
# Inicialização aleatória
# --------------------------
def init_solution():
    p = {unit:[0.0]*len(P) for unit in N}
    u = {unit:[0.0]*len(P) for unit in N}


    for t in range(len(P)):
        total_gen = 0
        while total_gen != Demanda[t]:
            for unit in N:
                u[unit][t] = random.randint(0,1)
                if u[unit][t]==1:
                    p[unit][t] = random.randint(int(LimInf[unit]), int(LimSup[unit]))
                else:
                    p[unit][t] = 0.0
            total_gen = sum(p[unit][t] for unit in N) + Eolica[t]
    return p, u


def solucao_gulosa(p,u):
    ordem_menor_termica_maior_termica = sorted(Custo, key=Custo.get)
    print(ordem_menor_termica_maior_termica)
    for t in range(len(P)):
        total_gen = 0
        #while total_gen != Demanda[t]:
        for unit in N:
            if(Combustivel[unit] > 0):
                if u[unit][t]==1:
                    p[unit][t] = LimSup[unit] if LimSup[unit] < (Demanda[t] - Eolica[t]) else  Demanda[t] - Eolica[t] - total_gen
                    if(Combustivel[unit] - p[unit][t] < 0):
                        Combustivel[unit] = 0
                        p[unit][t] = Combustivel[unit]
                    Combustivel[unit] = Combustivel[unit] - p[unit][t]

                else:
                    p[unit][t] = 0.0
            else:
                p[unit][t] = 0.0

        total_gen = sum(p[unit][t] for unit in N) + Eolica[t]
        print("p: ", p )
        print("t: ", t, " total_gen: ", total_gen, " dem: ", Demanda[t])
    print(p)
    print(u)



def solucao_gulosa_com_unit(N):
    p = {unit:[0.0]*len(P) for unit in N}
    u = {unit:[0.0]*len(P) for unit in N}
    ordem_menor_termica_maior_termica = sorted(Custo, key=Custo.get)
    print(ordem_menor_termica_maior_termica)
    for t in range(len(P)):
        total_gen = 0
        for unit in N:
            print("Combustivel[unit] : ", Combustivel[unit] )
            if(Combustivel[unit] > 0):
                if (total_gen != Demanda[t]):
                    p[unit][t] = LimSup[unit] if LimSup[unit] < (Demanda[t] - Eolica[t]) else  Demanda[t] - Eolica[t] - total_gen
                    if(Combustivel[unit] - p[unit][t] < 0):
                        Combustivel[unit] = 0
                        p[unit][t] = Combustivel[unit]
                    Combustivel[unit] = Combustivel[unit] - p[unit][t]
                else:
                    p[unit][t] = 0.0
            else:
                p[unit][t] = 0
            u[unit][t] = 0 if p[unit][t] == 0 else 1
            total_gen +=  p[unit][t]
    return p,u
p,u = solucao_gulosa_com_unit(N)
print("p gulosa: ", p)
print("u gulosa: ", u)
exit(1)


p,u = init_solution()
solucao_gulosa(p,u)
exit(1)

# --------------------------
# Variação de solução (neighbor)
# --------------------------
def neighbor(p, u):
    u_new = {unit:list(u[unit]) for unit in N}
    p_new = {unit:list(p[unit]) for unit in N}
    
    t = random.randint(0,len(P)-1)
    unit = random.choice(N)
    u_new[unit][t] = 1 - u_new[unit][t]

    for t_idx in range(len(P)):
        for unit in N:
            if u_new[unit][t_idx]==1:
                p_new[unit][t_idx] = LimInf[unit] + random.random()*(LimSup[unit]-LimInf[unit])
            else:
                p_new[unit][t_idx] = 0.0    
    return p_new, u_new

# --------------------------
# Simulated Annealing
# --------------------------
def simulated_annealing(T0=1000.0, alpha=0.9, n_iter=500):
    p_best, u_best = init_solution()
    cost_best = total_cost(p_best, u_best)
    p_curr, u_curr = p_best.copy(), u_best.copy(),
    cost_curr = cost_best
    T = T0

    for _ in range(n_iter):
        p_new, u_new = neighbor(p_curr, u_curr)
        print("p_new: ", p_new)
        print("u_new: ", u_new)
        exit(1)
        cost_new = total_cost(p_new, u_new)
        delta = cost_new - cost_curr   
        if delta < 0 or random.random() < np.exp(-delta/T):
            p_curr, u_curr, cost_curr = p_new, u_new, cost_new
            if cost_curr < cost_best:
                p_best, u_best, cost_best = p_curr.copy(), u_curr.copy(), cost_curr
        T *= alpha
    
    return p_best, u_best, cost_best

# --------------------------
# Executar SA
# --------------------------
p_sol, u_sol, cost_sol = simulated_annealing()
print("Objective (total cost) via SA:", cost_sol)
print(u_sol)
# --------------------------
# Exportar resultados
# --------------------------
rows = []
for t_idx, t in enumerate(P):
    total_thermal = sum(p_sol[unit][t_idx] for unit in N)
    total_gen = total_thermal + Eolica[t_idx]
    rows.append({
        "Period": t,
        "Demand": Demanda[t_idx],
        "Wind": Eolica[t_idx],
        "TotalThermal": total_thermal,
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
plt.plot(df_summary["Period"], df_summary["Wind"], label="Wind", lw=2)
plt.plot(df_summary["Period"], df_summary["TotalThermal"], label="Thermal", lw=2)
plt.plot(df_summary["Period"], df_summary["TotalGen"], label="Total", lw=2)
plt.xlabel("Period")
plt.ylabel("MW")
plt.title("Dispatch (thermal units) via SA")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("dispatch_plot_SA.png")
plt.show()

# --------------------------
# Plot individual thermal units
# --------------------------
for unit in N:
    plt.figure(figsize=(8,4))
    plt.plot(P, p_sol[unit], lw=2, marker='o', label="Generation (p)")
    plt.bar(P, u_sol[unit], alpha=0.3, label="Commitment (u)")
    plt.xlabel("Period")
    plt.ylabel("MW")
    plt.title(f"Thermal Unit {unit} Dispatch")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"thermal_unit_{unit}_SA.png")
    plt.show()
