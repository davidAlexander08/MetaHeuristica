import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import plotly.graph_objects as go

import json

arquivo = "C:/Users/testa/Documents/Doutorado_materias/Metaheuristica/output_instance.json"
arquivo = "C:/Users/testa/Documents/Doutorado_materias/Metaheuristica/instancia_teste_TON.json"
#arquivo = "C:/Users/testa/Documents/Doutorado_materias/Metaheuristica/instancia_teste_TON_sanidade.json"
#arquivo = "C:/Users/testa/Documents/Doutorado_materias/Metaheuristica/instancia_teste_TOFF_sanidade.json"
# Read JSON file
with open(arquivo, "r") as f:
    json_data = json.load(f)

class Termica:
    def __init__(self):
        self.limite_superior = None
        self.limite_inferior = None
        self.custo = None
        self.t_on = None
        self.t_off = None
        self.nome = None
        self.geracoes = None
        self.commitment = None
        self.locked = None

class Sistema:
    def __init__(self):
        self.geradores = None
        self.estagios = None
        self.demanda = None
        self.deficit = None
        self.custo_deficit = None
    
    @property
    def n_estagios(self):
        if self.estagios is not None:
            return len(self.estagios)
        else:
            return 0  # or None, if you prefer

    @property
    def demanda_liquida(self):
        geracao_total = np.array([0.0]*self.n_estagios)
        for estagio in range(self.n_estagios):
            for usina in self.geradores:
                geracao_total[estagio] += usina.geracoes[estagio]
        return Demanda - geracao_total


    def zera_geracoes(self):
        for gerador in self.geradores:
            if gerador.geracoes is not None:
                gerador.geracoes[:] = [0] * len(gerador.geracoes)  # set all periods to 0
            else:
                print("ERRO: Lista geradores é None, verifique dados de entrada")

    @property
    def total_cost(self):
        cost = sum(unit.custo*unit.geracoes[t] for unit in self.geradores for t in range(self.n_estagios))
        return cost





def gera_log_informacoes(sistema):
    ## Print unit info
    #for t in sistema.geradores:
    #    print(f"Nome: {t.nome}, LimSup: {t.limite_superior}, LimInf: {t.limite_inferior}, "
    #          f"Custo: {t.custo}, T_on: {t.t_on}, T_off: {t.t_off}")
    #print("-"*80)

    # Print all Gerações
    print("Gerações:")
    for t in sistema.geradores:
        geracoes_str = " ".join(f"{int(x):>3}" for x in t.geracoes) if t.geracoes is not None else "-"
        print(f"{t.nome:<6}: {geracoes_str}")
    print("-"*80)

    # Print all Commitment
    print("Commitment:")
    for t in sistema.geradores:
        commit_str = " ".join(str(int(x)) for x in t.commitment) if t.commitment is not None else "-"
        print(f"{t.nome:<6}: {commit_str}")
    print("-"*80)

    ## Print all Locked
    #print("Locked:")
    #for t in sistema.geradores:
    #    locked_str = " ".join(str(int(x)) for x in t.locked) if t.locked is not None else "-"
    #    print(f"{t.nome:<6}: {locked_str}")
    #print("-"*80)
# Initialize containers
#UnitCommitment = {}
sistema_inicial = Sistema()
sistema_inicial.estagios = list(range(1, json_data["instance"] + 1))

Demanda = []
lista_unidades_termicas = []
mapa_nome_objeto_termico = {}
for bus in json_data["buses"]:
    print("Bus name:", bus["bus"])
    print("Load:", bus["load"])
    sistema_inicial.demanda = np.array(Demanda.extend(bus["load"]))
    # Loop over thermal units
    for unit in bus["thermal_units"]:
        unidade_termica = Termica()
        #UnitCommitment[unit["nome"]] = np.zeros(len(P))
        unidade_termica.commitment = np.zeros(sistema_inicial.n_estagios)
        unidade_termica.geracoes = np.zeros(sistema_inicial.n_estagios)
        unidade_termica.locked = np.zeros(sistema_inicial.n_estagios)
        unidade_termica.nome = unit["nome"]
        unidade_termica.custo = unit["CVU"]
        unidade_termica.limite_superior = unit["max_power"]
        unidade_termica.limite_inferior = unit["min_power"]
        unidade_termica.t_on = unit["min_uptime"]
        unidade_termica.t_off = unit["min_downtime"]
        mapa_nome_objeto_termico[unidade_termica.nome] = unidade_termica
        lista_unidades_termicas.append(unidade_termica)
# Other variables


sistema_inicial.geradores = lista_unidades_termicas
sistema_inicial.deficit = np.zeros(sistema_inicial.n_estagios)
sistema_inicial.custo_deficit = json_data["deficit"]


#geracoes = {unit.nome:[0.0]*len(P) for unit in lista_unidades_termicas}
gera_log_informacoes(sistema_inicial)

# --------------------------
# Função objetivo
# --------------------------


def consecutive_ones(v, pos):
    lista = []
    lista.append(pos)
    if v[pos] == 0:
        return 0

    count = 1
    # Left side
    i = pos - 1
    while i >= 0 and v[i] == 1:
        lista.append(i)
        count += 1
        i -= 1

    # Right side
    i = pos + 1
    while i < len(v) and v[i] == 1:
        lista.append(i)
        count += 1
        i += 1

    return count, lista


def verifica_resolve_inviabilidade(sistema_guloso, caminho_usinas):
    #### ADEQUA GERACOES
    ordem_maior_termica = caminho_usinas[::-1]
    for t in range(sistema_guloso.n_estagios):
        if(sistema_guloso.demanda_liquida[t] < 0):
            diff =  -sistema_guloso.demanda_liquida[t]
            for unit in ordem_maior_termica:
                if(diff > 0):
                    corte_possivel = unit.geracoes[t] - unit.limite_inferior
                    if(corte_possivel > 0):
                        subtracao_diff = min(diff, corte_possivel)
                        unit.geracoes[t] = unit.geracoes[t] - subtracao_diff
                        diff = diff - subtracao_diff
    return sistema_guloso




def solucao_gulosa():
    sistema_guloso = copy.deepcopy(sistema_inicial)

    ordem_termos = sorted(sistema_guloso.geradores, key=lambda u: u.custo)
    ordem_menor_termica_maior_termica = [u.nome for u in ordem_termos]
    for t in range(sistema_guloso.n_estagios):
        lista_caminho_usinas =[]
        for unit in ordem_termos:
            lista_caminho_usinas.append(unit)
            if (sistema_guloso.demanda_liquida[t] > 0):
                unit.commitment[t] = 1
                if(t != 0):
                    if(unit.commitment[t] == 1) and (unit.commitment[t-1] == 0):
                        for i in range(t, min(t + unit.t_on, max(sistema_guloso.estagios))):
                            unit.commitment[i] = 1
                            unit.geracoes[i] += unit.limite_inferior
                elif(t== 0):
                    for i in range(t, t + unit.t_on):
                        unit.commitment[i] = 1
                        unit.geracoes[i] += unit.limite_inferior
                limite_geracao = unit.limite_superior if unit.geracoes[t] == 0 else unit.limite_superior - unit.limite_inferior
                geracao = max(min(limite_geracao, sistema_guloso.demanda_liquida[t]),0)
                unit.geracoes[t] += geracao 
                sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
            else:
                unit.geracoes[t] = max(unit.geracoes[t],0)
    df = pd.concat(
        [pd.DataFrame(unit.geracoes), pd.DataFrame(unit.commitment)],
        axis=1  # concatena colunas
    )
    df['DemandaLiquida'] = sistema_guloso.demanda_liquida
    df['Demanda'] = sistema_guloso.demanda
    print(df.round(1))
    print("############################")
    print("CUSTO TOTAL: ", sistema_guloso.total_cost)

    return sistema_guloso


def adequa_balanco_potencia_guloso(sistema_new):

    sistema_new.zera_geracoes()
    gera_log_informacoes(sistema_new)
    ordem_termos = sorted(sistema_new.geradores, key=lambda u: u.custo)
    #ordem_menor_termica_maior_termica = [u.nome for u in ordem_termos]
    for t in range(sistema_new.n_estagios):
        lista_caminho_usinas =[]
        for unit in ordem_termos:
            lista_caminho_usinas.append(unit)
            if(unit.commitment[t] == 1):
                geracao = max(min(unit.limite_superior, sistema_new.demanda_liquida[t]),unit.limite_inferior)
                sistema_new = verifica_resolve_inviabilidade(sistema_new, lista_caminho_usinas)
            else:
                geracao = 0
            unit.geracoes[t] = geracao 
    df = pd.concat(
        [pd.DataFrame(unit.geracoes), pd.DataFrame(unit.commitment)],
        axis=1  # concatena colunas
    )
    df['DemandaLiquida'] = sistema_new.demanda_liquida
    df['Demanda'] = Demanda
    #print("############################")
    gera_log_informacoes(sistema_new)
    return sistema_new

    
# --------------------------
# Variação de solução (neighbor)
# --------------------------
#random.seed(4)
#np.random.seed(2)

def neighbor(sistema_neighbour):
    # Cria cópias da solução atual
    gera_log_informacoes(sistema_neighbour)
    inviavel = True
    contador = 0
    while inviavel == True:
        sistema_new = copy.deepcopy(sistema_neighbour)
        t = random.choice(sistema_new.estagios)-1
        lista_usinas_ligadas_periodo = []
        lista_usinas_desligadas_periodo = []
        capacidade_instalada_periodo = 0

        for unit in sistema_new.geradores:
            if(unit.commitment[t] == 1):
                lista_usinas_ligadas_periodo.append(unit)
                capacidade_instalada_periodo += unit.limite_superior
            else:
                lista_usinas_desligadas_periodo.append(unit)

        if(len(lista_usinas_ligadas_periodo) != 0 and len(lista_usinas_desligadas_periodo) != 0):
            unit_a_ser_desligada = random.choice(lista_usinas_ligadas_periodo)
            ton_consecutivos, lista_consecutivos  = consecutive_ones(unit_a_ser_desligada.commitment, t)
            capacidade_instalada_periodo -= unit_a_ser_desligada.limite_superior

            for i in lista_consecutivos:
                unit_a_ser_desligada.commitment[i] = 0
                aux_usinas_desligadas_periodo = lista_usinas_desligadas_periodo.copy()
                while capacidade_instalada_periodo < Demanda[i]:
                    if(len(aux_usinas_desligadas_periodo) == 0):
                        break
                    unit_a_ser_ligada = random.choice(aux_usinas_desligadas_periodo)
                    aux_usinas_desligadas_periodo.remove(unit_a_ser_ligada)
                    capacidade_instalada_periodo += unit_a_ser_ligada.limite_superior
                    for j in range(i, min(i + unit_a_ser_ligada.t_on, sistema_new.n_estagios)):
                        unit_a_ser_ligada.commitment[j] = 1

            lista_inviavel = []
            for periodo in range(0,sistema_new.n_estagios):
                capacidade_instalada_per = 0
                for unit in sistema_new.geradores:
                    capacidade_instalada_per += unit.limite_superior*unit.commitment[periodo]
                    if(unit.commitment[periodo] == 1):
                        ton_consecutivos, lista_consecutivos = consecutive_ones(unit.commitment, periodo)
                        inviavel = True if ton_consecutivos < unit.t_on else False
                        if(inviavel):
                            if(sistema_new.estagios[periodo] + unit.t_on > max(sistema_new.estagios)):
                                excedente = sistema_new.estagios[periodo] + unit.t_on - max(sistema_new.estagios) - 1
                                if(ton_consecutivos == unit.t_on - excedente):
                                        inviavel = False               
                if(capacidade_instalada_per - Demanda[periodo] < 0):
                    inviavel = True
                lista_inviavel.append(inviavel)
            
            valida_inviabilidades_unit_commitment = sum(lista_inviavel)
            if(valida_inviabilidades_unit_commitment == 0):

                solution  = adequa_balanco_potencia_guloso(sistema_new)
                return solution
            else:
                inviavel = True
            contador += 1

    


# --------------------------
# Simulated Annealing
# --------------------------

def simulated_annealing(T0=100.0, alpha=0.9, n_iter=10, Tf = 70):
    sol_best = solucao_gulosa()
    custo_guloso = sol_best.total_cost
    cost_best = sol_best.total_cost
    sol_curr = copy.deepcopy(sol_best)
    cost_curr = cost_best
    print("#################")
    print("SOL GULOSA")
    print("custo_guloso: ", custo_guloso)
    print("#################")

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
            sol_new = neighbor(copy.deepcopy(sol_curr))
            cost_new = sol_new.total_cost
            delta_fob = cost_new - cost_curr  
            if delta_fob < 0:
                sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
                df = pd.DataFrame(
                    {
                        "Temperatura":[T],
                        "Iteracao":[iter],
                        "Custo_Total":[cost_new]
                    }
                )
                lista_df.append(df)
                if cost_curr < cost_best:
                    print("T: ", T, " iter: ", iter, " custo: ", sol_new.total_cost)
                    print("##############################")
                    print("iter: ", iter)
                    print("cost_new: ", cost_new)
                    print("Demanda: ", Demanda)
                    sol_best, cost_best = copy.deepcopy(sol_curr), cost_curr
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
                    sol_curr, cost_curr = copy.deepcopy(sol_new), cost_new
        T *= alpha
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return sol_best, cost_best, df_fim 

#EXECUTA ILS

# --------------------------
# Executar SA
# --------------------------

solucao, cost_sol, df_fim = simulated_annealing()
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
        "Demand": Demanda[t_idx],
        "TotalGen": total_gen
    })

df_summary = pd.DataFrame(rows)
print(df_summary) 
exit(1)
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



def ILS(n_iter=100):
    p_best, unit_best = solucao_gulosa()
    custo_guloso = total_cost(p_best)
    cost_best = total_cost(p_best)
    p_curr = copy.deepcopy(p_best)
    unit_curr = copy.deepcopy(unit_best)
    cost_curr = cost_best
    print("#################")
    print("SOL GULOSA")
    print("p_best: ", p_best)
    print("custo_guloso: ", custo_guloso)
    print("#################")
    lista_df = []
    df = pd.DataFrame(
        {
            "Iteracao":[0],
            "Custo_Total":[custo_guloso]
        }
    )
    lista_df.append(df)

    for iter in range(n_iter):
        p_new, unit_new = neighbor(copy.deepcopy(unit_curr))
        cost_new = total_cost(p_new)
        delta_fob = cost_new - cost_curr   
        if delta_fob < 0:
            p_curr, unit_curr, cost_curr = copy.deepcopy(p_new), copy.deepcopy(unit_new), cost_new
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
                print("cost_new: ", cost_new)
                print("Demanda: ", Demanda)
                p_best, unit_best, cost_best = copy.deepcopy(p_curr), copy.deepcopy(unit_curr), cost_curr
    df_fim = pd.concat(lista_df).reset_index(drop = True)
    return p_best, unit_best, cost_best, df_fim 

#EXECUTA ILS
exit(1)
p_sol, unit_sol, cost_sol, df_fim = ILS()
print("EXECUTANDO ILS")
print("Objective (total cost) via ILS:", cost_sol)
print("p_sol: ", pd.DataFrame(p_sol))
#print("unit_sol: ", unit_sol)
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