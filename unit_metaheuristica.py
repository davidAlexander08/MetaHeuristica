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


def plota(df_fim, titulo):
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
        title=titulo,
        xaxis_title="Iteração",
        yaxis_title="FOB",
        template="plotly_white",
        font=dict(size=14),
        width=800,
        height=500
    )

    fig.write_html(f"evolucao_{titulo}.html", include_plotlyjs='cdn')
    print("Plot saved as sa_best_cost.html")



def plota_SA(df_fim, titulo):
    # Create Plotly line plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_fim["Iteracao"].astype(str) +"_"+ df_fim["Temperatura"].round(0).astype(str),
        y=df_fim["Custo_Total"],
        mode='lines+markers',
        line=dict(width=3, color='royalblue'),
        marker=dict(size=8),
        name="Best Cost"
    ))

    fig.update_layout(
        title=titulo,
        xaxis_title="Iteração",
        yaxis_title="FOB",
        template="plotly_white",
        font=dict(size=14),
        width=800,
        height=500
    )

    fig.write_html(f"evolucao_{titulo}.html", include_plotlyjs='cdn')
    print("Plot saved as sa_best_cost.html")


arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/output_instance.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TON.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/output_instance_teste.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TON_sanidade.json"
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/10_0_1_w.json" #138735335 OTIMALIDADE
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/10_0_3_w.json" #131001977 OTIMALIDADE
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/20_0_1_w.json" #199058315 OTIMALIDADE
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/50_0_1_w.json" 
#arquivo = "C:/Users/testa/Documents/git/MetaHeuristica/instancias/instancia_teste_TOFF_sanidade.json"
# Read JSON file
sistema_inicial = leitura_json(arquivo)
#sistema_inicial = leitura_json_orlib(arquivo)
#gera_log_informacoes(sistema_inicial)



#EXECUTA ILS
solucao, df_fim = ILS(sistema_inicial)
print("EXECUTANDO ILS")
print("Objective (total cost) via ILS:", solucao.total_cost)
print(df_fim)
plota(df_fim, "Evolução ILS")
data = {termica.nome: termica.geracoes for termica in solucao.geradores}
df_generation = pd.DataFrame(data)
df_generation["SOMA_GERACAO"] = df_generation.sum(axis=1)
df_generation["DEMANDA"] = solucao.demanda
print(df_generation)
#exit(1)


######### VNS
solucao, df_fim = VNS(sistema_inicial)
print("SOLUCAO SIMULATED ANEELING")
print("Objective (total cost) via VNS:", solucao.total_cost)
print(df_fim)
plota(df_fim, "Evolução VNS")

data = {termica.nome: termica.geracoes for termica in solucao.geradores}
df_generation = pd.DataFrame(data)
df_generation["SOMA_GERACAO"] = df_generation.sum(axis=1)
df_generation["DEMANDA"] = solucao.demanda
print(df_generation)
#exit(1)

########## ILS ESPECIAL
solucao, df_fim = ILS(sistema_inicial, True)
print("SOLUCAO SIMULATED ANEELING")
print("Objective (total cost) via ILS Especial:", solucao.total_cost)
plota(df_fim, "Evolução ILS Customizado")
print(df_fim)
data = {termica.nome: termica.geracoes for termica in solucao.geradores}
df_generation = pd.DataFrame(data)
df_generation["SOMA_GERACAO"] = df_generation.sum(axis=1)
df_generation["DEMANDA"] = solucao.demanda
print(df_generation)
exit(1)

######### S.A.
solucao, df_fim = simulated_annealing(sistema_inicial)
print("SOLUCAO SIMULATED ANEELING")
print("Objective (total cost) via SA:", solucao.total_cost)
print(df_fim)
plota_SA(df_fim, "Evolução S.A.")
data = {termica.nome: termica.geracoes for termica in solucao.geradores}
df_generation = pd.DataFrame(data)
df_generation["SOMA_GERACAO"] = df_generation.sum(axis=1)
df_generation["DEMANDA"] = solucao.demanda
print(df_generation)
#exit(1)