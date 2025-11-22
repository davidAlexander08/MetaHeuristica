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
        exit(1)
        print("Load:", bus["load"])
        Demanda.extend(bus["load"])
        sistema_inicial.demanda = np.array(Demanda)
        for unit in bus["thermal_units"]:
            unidade_termica = Termica()
            unidade_termica.commitment = [None]*(sistema_inicial.n_estagios)
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
    print(sistema_inicial.estagios)
    return sistema_inicial




def leitura_json_orlib(arquivo):
    with open(arquivo, "r") as f:
        json_data = json.load(f)
    sistema_inicial = Sistema()
    sistema_inicial.estagios = list(range(1, json_data["Parameters"]["Time (h)"] + 1))
    Demanda = []
    lista_unidades_termicas = []
    mapa_nome_objeto_termico = {}
    for bus in json_data["Buses"]:
        print("Bus name:", bus)        
        Demanda.extend(json_data["Buses"][bus]["Load (MW)"])
        sistema_inicial.demanda = np.array(Demanda).astype(int)
        print("Load:", sistema_inicial.demanda)
    for generator in json_data["Generators"]:
        unidade_termica = Termica()
        unidade_termica.commitment = [None]*(sistema_inicial.n_estagios)
        unidade_termica.geracoes = np.zeros(sistema_inicial.n_estagios)
        unidade_termica.locked = np.zeros(sistema_inicial.n_estagios)
        unidade_termica.nome = generator
        unidade_termica.custo = json_data["Generators"][generator]["Production cost curve ($)"][0]
        unidade_termica.limite_superior = json_data["Generators"][generator]["Production cost curve (MW)"][-1]
        unidade_termica.limite_inferior = json_data["Generators"][generator]["Production cost curve (MW)"][0]
        unidade_termica.t_on = json_data["Generators"][generator]["Minimum uptime (h)"]
        unidade_termica.t_off = json_data["Generators"][generator]["Minimum downtime (h)"]
        mapa_nome_objeto_termico[unidade_termica.nome] = unidade_termica
        lista_unidades_termicas.append(unidade_termica)
    sistema_inicial.geradores = lista_unidades_termicas
    sistema_inicial.deficit = np.zeros(sistema_inicial.n_estagios)
    sistema_inicial.custo_deficit = 9999
    return sistema_inicial

