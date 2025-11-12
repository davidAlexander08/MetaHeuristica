import json
import math
from collections import OrderedDict
import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, PULP_CBC_CMD, GLPK_CMD, LpStatus, value
from modelo.classes import *
from utils.utils import *

def executa_solucao_pl(sistema):
    penalty_deficit = sistema.custo_deficit
    model = LpProblem("UnitCommitment", LpMinimize)
    p = LpVariable.dicts("p", [(u.nome, t) for u in sistema.geradores for t in range(sistema.n_estagios)], lowBound=0, cat="Continuous")
    deficit = LpVariable.dicts("deficit", np.array(sistema.estagios)-1, lowBound=0, cat="Continuous")
    for unit in sistema.geradores:
        for t in range(sistema.n_estagios):
            model += p[(unit.nome, t)] <= unit.limite_superior * unit.commitment[t], f"max_power_{unit.nome}_{t}"
            model += p[(unit.nome, t)] >= unit.limite_inferior * unit.commitment[t], f"min_power_{unit.nome}_{t}"
    for t in range(sistema.n_estagios):
        model += lpSum(p[(unit.nome, t)] for unit in sistema.geradores) + deficit[t] == sistema.demanda[t], f"balance_{t}"

    model += lpSum(unit.custo * p[(unit.nome, t)] for unit in sistema.geradores for t in range(sistema.n_estagios)) + sistema.custo_deficit*lpSum(deficit[t] for t in range(sistema.n_estagios))
    solver = PULP_CBC_CMD(msg=True, timeLimit=None)   # change to GLPK_CMD() if desired
    # solver = GLPK_CMD(msg=True)
    solver = PULP_CBC_CMD(msg=False)  # <--- no log
    model.solve(solver)
    status = LpStatus[model.status]
    #print("Status:", status)
    #if status not in ("Optimal", "Optimal (within gap)"):
    #    print("Solver did not find optimal solution. Status:", status)
    obj = value(model.objective)
    #print("Objective (total cost):", obj)
    # Save results back into sistema
    for u in sistema.geradores:
        # extract all generation values for this generator
        u.geracoes = [value(p[(u.nome, t)]) if value(p[(u.nome, t)]) is not None else 0.0
                    for t in range(sistema.n_estagios)]

    sistema.deficit = [value(deficit[t]) if value(deficit[t]) is not None else 0.0
                    for t in range(sistema.n_estagios)]

    #print("\nTabela de Geração (p):")
    ## Build dynamic header: "Periodo | g0 g1 g2 ... | Soma_Geracao | Demanda | Custo"
    #header = (
    #    ["Periodo"]
    #    + [u.nome for u in sistema.geradores]
    #    + ["Soma_Geracao", "Demanda", "Custo"]
    #)
    #print("\t".join(header))
    #print("-" * 100)
#
    #table_rows = []
    #for t in range(sistema.n_estagios):
    #    geracoes = [
    #        value(p[(u.nome, t)]) if value(p[(u.nome, t)]) is not None else 0.0
    #        for u in sistema.geradores
    #    ]
    #    custos = [
    #        (value(p[(u.nome, t)]) if value(p[(u.nome, t)]) is not None else 0.0) * u.custo
    #        for u in sistema.geradores
    #    ]
    #    soma_geracao = sum(geracoes)
    #    soma_custos = sum(custos)
    #    demanda_t = float(sistema.demanda[t]) if t < len(sistema.demanda) else 0.0
#
    #    # print formatted row
    #    formatted = (
    #        [str(t)]
    #        + [f"{g:7.2f}" for g in geracoes]
    #        + [f"{soma_geracao:7.2f}", f"{demanda_t:7.2f}", f"{soma_custos:7.2f}"]
    #    )
    #    print("\t".join(formatted))
#
    #    # Save for DataFrame
    #    row = {"Periodo": t}
    #    for idx, u in enumerate(sistema.geradores):
    #        row[u.nome] = geracoes[idx]
    #    row["Soma_Geracao"] = soma_geracao
    #    row["Demanda"] = demanda_t
    #    row["Custo"] = soma_custos
    #    table_rows.append(row)
#
    #df_table = pd.DataFrame(table_rows)
    #print("\nObjective (total cost):", obj)
    return sistema