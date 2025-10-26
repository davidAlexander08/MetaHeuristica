from modelo.classes import *
import json

def leitura_json(arquivo):
    with open(arquivo, "r") as f:
        json_data = json.load(f)
    sistema_inicial = Sistema()
    sistema_inicial.estagios = list(range(1, json_data["instance"] + 1))
    Demanda = []
    lista_unidades_termicas = []
    mapa_nome_objeto_termico = {}
    for bus in json_data["buses"]:
        print("Bus name:", bus["bus"])
        print("Load:", bus["load"])
        Demanda.extend(bus["load"])
        sistema_inicial.demanda = np.array(Demanda)
        for unit in bus["thermal_units"]:
            unidade_termica = Termica()
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
    sistema_inicial.geradores = lista_unidades_termicas
    sistema_inicial.deficit = np.zeros(sistema_inicial.n_estagios)
    sistema_inicial.custo_deficit = json_data["deficit"]
    return sistema_inicial