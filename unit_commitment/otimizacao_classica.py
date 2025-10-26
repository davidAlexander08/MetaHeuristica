"""
Unit Commitment pequeno (3 períodos) - resolução por enumeração
- Modifique a seção "Dados do problema" para testar outros casos.
- Regras consideradas: Pmin/Pmax, limite de rampa (MW/periodo), custo variável,
  custo fixo por unidade ligada e custo de startup (0->1).
- Método: para cada cronograma binário (on/off) tenta-se achar despacho viável
  por período (alocação por ordem de mérito, respeitando rampa). Guarda melhor custo.
"""

import itertools
from math import inf
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Dados do problema (editáveis)
# -------------------------
units = [
    # nome, Pmin, Pmax, custo_var (R$/MWh), custo_startup, custo_fixo_por_periodo, ramp (MW/period)
    {"name": "U1", "Pmin": 50.0, "Pmax": 150.0, "var_cost": 20.0, "start_cost": 120.0, "fixed_cost": 10.0, "ramp": 100.0},
    {"name": "U2", "Pmin": 30.0, "Pmax": 100.0, "var_cost": 40.0, "start_cost": 50.0,  "fixed_cost": 5.0,  "ramp": 80.0},
    {"name": "U3", "Pmin": 0.0,  "Pmax": 60.0,  "var_cost": 80.0, "start_cost": 10.0,  "fixed_cost": 2.0,  "ramp": 60.0},
]

# Demanda por período (3 períodos)
demand = [120.0, 160.0, 140.0]
n_periods = len(demand)
assert n_periods == 3, "Este script espera exatamente 3 períodos."

n_units = len(units)

# -------------------------
# Funções auxiliares
# -------------------------
def generate_commitments(n_units, n_periods):
    """Gera todas matrizes de compromisso binário (n_units x n_periods)."""
    for bits in itertools.product([0,1], repeat=n_units*n_periods):
        mat = [list(bits[i*n_periods:(i+1)*n_periods]) for i in range(n_units)]
        yield mat

def feasible_and_dispatch(commit):
    """
    Dado um compromisso (lista de listas commit[unit][t] em {0,1}),
    tenta construir despacho P[unit][t] e calcula custo.
    Retorna (feasible, P, total_cost, details)
    """
    # Inicializa
    P = [[0.0]*n_periods for _ in range(n_units)]
    prev_output = [0.0]*n_units
    details = {"var_cost":0.0, "fixed_cost":0.0, "start_cost":0.0}

    for t in range(n_periods):
        Pd = demand[t]
        on_idx = [i for i in range(n_units) if commit[i][t]==1]

        # checagens rápidas
        total_max = sum(units[i]["Pmax"] for i in on_idx)
        total_min = sum(units[i]["Pmin"] for i in on_idx)
        if Pd > total_max + 1e-8:
            return False, None, None, None
        if on_idx and Pd + 1e-8 < total_min:
            return False, None, None, None
        if not on_idx and Pd > 1e-8:
            return False, None, None, None

        # Inicial: atribui Pmin aos ligados
        for i in on_idx:
            P[i][t] = units[i]["Pmin"]
        remaining = Pd - sum(P[i][t] for i in on_idx)

        # Aloca restante pela ordem de mérito (custo variável) respeitando headroom e ramp up
        merit = sorted(on_idx, key=lambda i: units[i]["var_cost"])
        for i in merit:
            if remaining <= 1e-8:
                break
            headroom = units[i]["Pmax"] - P[i][t]
            # limite de subida: P[i][t] - prev_output[i] <= ramp
            # então máximo adicional = min(headroom, prev_output[i] + ramp - P[i][t])
            allowed_ramp_up = prev_output[i] + units[i]["ramp"] - P[i][t]
            avail = max(0.0, min(headroom, allowed_ramp_up))
            take = min(avail, remaining)
            P[i][t] += take
            remaining -= take

        if remaining > 1e-6:
            # falha em atender demanda (provavelmente por rampa)
            return False, None, None, None

        # checar limites de rampa (subida e descida)
        for i in range(n_units):
            if abs(P[i][t] - prev_output[i]) > units[i]["ramp"] + 1e-8:
                return False, None, None, None

        # custos deste período
        for i in range(n_units):
            details["var_cost"] += units[i]["var_cost"] * P[i][t]
            if commit[i][t] == 1:
                details["fixed_cost"] += units[i]["fixed_cost"]
                # startup cost (0->1)
                if t == 0:
                    # se está ligado no período 0, tratamos como startup (ou poderia modelar estado inicial)
                    details["start_cost"] += units[i]["start_cost"]
                else:
                    if commit[i][t-1] == 0:
                        details["start_cost"] += units[i]["start_cost"]
        # atualiza prev_output
        prev_output = [P[i][t] for i in range(n_units)]

    total_cost = details["var_cost"] + details["fixed_cost"] + details["start_cost"]
    return True, P, total_cost, details

# -------------------------
# Resolução (enumeração)
# -------------------------
best = {"cost": inf}
all_feasible = []

for commit in generate_commitments(n_units, n_periods):
    feasible, P, cost, details = feasible_and_dispatch(commit)
    if feasible:
        rec = {"commit": commit, "P": P, "cost": cost, "details": details}
        all_feasible.append(rec)
        if cost < best["cost"]:
            best = rec.copy()
            best["cost"] = cost

# -------------------------
# Saída
# -------------------------
if best["cost"] == inf:
    print("Nenhuma solução viável encontrada com os parâmetros fornecidos.")
else:
    print(f"Total de cronogramas viáveis encontrados: {len(all_feasible)}")
    print(f"Melhor custo total: {best['cost']:.2f}\n")

    # montar dataframes para exibir
    commit_df = pd.DataFrame({f"t{t+1}": [best["commit"][i][t] for i in range(n_units)] for t in range(n_periods)}, index=[u["name"] for u in units])
    gen_df = pd.DataFrame({f"t{t+1}": [best["P"][i][t] for i in range(n_units)] for t in range(n_periods)}, index=[u["name"] for u in units])
    cost_break = pd.DataFrame([best["details"]], index=["values"])

    print("Commitment (1=on, 0=off):")
    print(commit_df)
    print("\nDespacho (MW):")
    print(gen_df)
    print("\nDetalhes dos custos:")
    print(cost_break)

    # gráfico empilhado do despacho
    df_plot = gen_df.transpose()
    df_plot.index = [f"t{t+1}" for t in range(n_periods)]
    ax = df_plot.plot(kind="bar", stacked=True, figsize=(8,4))
    ax.set_ylabel("Geração (MW)")
    ax.set_title("Despacho empilhado por unidade")
    plt.tight_layout()
    plt.show()

# -------------------------
# Fim do script
# -------------------------
