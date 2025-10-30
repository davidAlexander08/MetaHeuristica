import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import plotly.graph_objects as go
from modelo.classes import *  # your separate file
from modelo.dados_entrada import *
from utils.utils import *
from metaheuristicas.simulated_annealing import *
from metaheuristicas.ILS import *
from metaheuristicas.Tabu_Search import *
from metaheuristicas.graphs import *

import os
os.makedirs('resultados', exist_ok=True)

#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/output_instance.json"
arquivo = "instancias/instancia_teste_TON_sanidade.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TON_sanidade.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TOFF_sanidade.json"
# Read JSON file
sistema_inicial = leitura_json(arquivo)
gera_log_informacoes(sistema_inicial)

resultados = {}

#EXECUTA ILS
sol_best_ils, cost_best_ils, df_fim_ils = ILS(sistema_inicial)
print("EXECUTANDO ILS")
print("Objective (total cost) via ILS:", cost_best_ils)
resultados['ILS'] = {'solucao': sol_best_ils, 'custo': cost_best_ils, 'df': df_fim_ils}
print(df_fim_ils)

# EXECUTA SA
sol_best_sa, cost_best_sa, df_fim_sa = simulated_annealing(sistema_inicial)
print("EXECUTANDO SIMULATED ANNEALING")
print("Objective (total cost) via SA:", cost_best_sa)
resultados['Simulated Annealing'] = {'solucao': sol_best_sa, 'custo': cost_best_sa, 'df': df_fim_sa}
print(df_fim_sa)

# EXECUTA TS
sol_best_ts, cost_best_ts, df_fim_ts = busca_tabu(sistema_inicial)
print("EXECUTANDO BUSCA TABU")
print("Objective (total cost) via TS:", cost_best_ts)
resultados['Busca Tabu'] = {'solucao': sol_best_ts, 'custo': cost_best_ts, 'df': df_fim_ts}
print(df_fim_ts)

# Comparação final
print("\n=== COMPARAÇÃO FINAL ===")
print(f"Busca Tabu: {cost_best_ts}")
print(f"ILS: {cost_best_ils}")
print(f"Simulated Annealing: {cost_best_sa}")



# COMPARAÇÃO FINAL
print("\n" + "="*60)
print("RESULTADOS COMPARATIVOS")
print("="*60)

for metodo, resultado in resultados.items():
    custo_inicial = resultado['df']['Custo_Total'].iloc[0]
    custo_final = resultado['custo']
    melhoria = ((custo_inicial - custo_final) / custo_inicial) * 100
    print(f"{metodo:<20} | Custo Inicial: {custo_inicial:8.2f} | Custo Final: {custo_final:8.2f} | Melhoria: {melhoria:6.2f}%")

# GERAR GRÁFICOS COMPARATIVOS
print("\nGerando gráficos comparativos...")
gerar_grafico_comparativo(resultados)

print("\nExecução concluída! Gráficos salvos na pasta 'resultados/'")

# Após gerar_grafico_comparativo(resultados)
caminho_verificacao = os.path.join('resultados', 'comparativo_metaheuristicas.png')
if os.path.exists(caminho_verificacao):
    print(f"✓ Arquivo gerado com sucesso: {caminho_verificacao}")
    print(f"Tamanho do arquivo: {os.path.getsize(caminho_verificacao)} bytes")
else:
    print(f"✗ Arquivo NÃO foi gerado: {caminho_verificacao}")
    
exit(1)


























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



