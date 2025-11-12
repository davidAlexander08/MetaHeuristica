import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import plotly.graph_objects as go
from modelo.classes import *  # your separate file
from modelo.dados_entrada import *
from utils.utils import *
from neometaheuristica.simulated_annealing import *
from neometaheuristica.ILS import *
from neometaheuristica.VNS import *


#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/output_instance.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TON.json"
arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/output_instance_teste.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TON_sanidade.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TOFF_sanidade.json"
# Read JSON file
sistema_inicial = leitura_json(arquivo)




#gera_log_informacoes(sistema_inicial)

#EXECUTA ILS
solucao, cost_sol, df_fim = ILS(sistema_inicial)
print("EXECUTANDO ILS")
print("Objective (total cost) via ILS:", cost_sol)
print(df_fim)
data = {termica.nome: termica.geracoes for termica in solucao.geradores}
df_generation = pd.DataFrame(data)
df_generation["SOMA_GERACAO"] = df_generation.sum(axis=1)
df_generation["DEMANDA"] = solucao.demanda
print(df_generation)

#rows = []
#for t_idx, t in enumerate(solucao.estagios):
#    total_gen = 0
#    for termica in solucao.geradores:
#        total_gen += termica.geracoes[t_idx]
#    rows.append({
#        "Period": t,
#        "Demand": solucao.demanda[t_idx],
#        "TotalGen": total_gen
#    })
#
#df_summary = pd.DataFrame(rows)
#print(df_summary) 

exit(1)

solucao, cost_sol, df_fim = simulated_annealing(sistema_inicial)
print("SOLUCAO SIMULATED ANEELING")
print("Objective (total cost) via SA:", cost_sol)
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
generators = list(Custo.keys())

df = pd.DataFrame({
    "Generator": generators,
    "Custo": [Custo[g] for g in generators],
    "LimSup": [LimSup[g] for g in generators],
    "LimInf": [LimInf[g] for g in generators],
    "TON": [TON[g] for g in generators],
    "Toff": [Toff[g] for g in generators]
})
df = df.sort_values(by="Custo").reset_index(drop=True)

print(df)

exit(1)
# --------------------------
# Executar SA
# --------------------------
solucao, cost_sol, df_fim = simulated_annealing(sistema_inicial)
print("SOLUCAO SIMULATED ANEELING")
print("Objective (total cost) via SA:", cost_sol)
print(df_fim)

#temperaturas = df_fim["Temperatura"].unique()
#for temperatura in temperaturas:
#    # Create Plotly line plot
#    df_plot = df_fim.loc[(df_fim["Temperatura"] == temperatura)].reset_index(drop = True)
#    fig = go.Figure()
#    fig.add_trace(go.Scatter(
#        x=df_plot["Iteracao"],
#        y=df_plot["Custo_Total"],
#        mode='lines+markers',
#        line=dict(width=3, color='royalblue'),
#        marker=dict(size=8),
#        name="Best Cost"
#    ))
#
#    fig.update_layout(
#        title=f"S.A. Temperatura {temperatura}",
#        xaxis_title="Iteration",
#        yaxis_title="Objective Function Value",
#        template="plotly_white",
#        font=dict(size=14),
#        width=800,
#        height=500
#    )
#
#    fig.write_html(f"sa_best_cost_{temperatura}.html", include_plotlyjs='cdn')
#    print("Plot saved as sa_best_cost.html")

# --------------------------
# Exportar resultados
# --------------------------
data = {termica.nome: termica.geracoes for termica in solucao.geradores}
df_generation = pd.DataFrame(data)
print(df_generation)

rows = []
for t_idx, t in enumerate(solucao.estagios):
    total_gen = 0
    for termica in solucao.geradores:
        total_gen += termica.geracoes[t_idx]
    rows.append({
        "Period": t,
        "Demand": solucao.demanda[t_idx],
        "TotalGen": total_gen
    })

df_summary = pd.DataFrame(rows)
print(df_summary) 
exit(1)
df_summary.to_csv("summary_uc_SA.csv", index=False)
print("Summary written to summary_uc_SA.csv")



