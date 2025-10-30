
from modelo.classes import *
from utils.utils import *
import copy
import pandas as pd
import random

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

def find_locked(t, unit):
    positions = []
    for idx in range(t, min(t + unit.t_on, len(unit.commitment))):
        if unit.locked[idx] == 1:
            positions.append(idx)
    return positions

def verifica_TON_futuro(t, unit):
    locked_ahead = find_locked(t, unit)
    #print("locked_ahead: ", locked_ahead)
    if(len(locked_ahead) != 0):
        values = []
        for idx in locked_ahead:
            values.append(unit.commitment[idx])
        #print("t: ",t, " ", values, " ", unit.commitment, " ", unit.nome, " ", sum(values))
        if(sum(values) ==0):
            return True 
        else: 
            return False
    else:
        return False

def nova_solucao_gulosa(sistema_inicial):
    sistema_guloso = copy.deepcopy(sistema_inicial)
    ordem_termos = sorted(sistema_guloso.geradores, key=lambda u: u.custo)
    for t in range(sistema_guloso.n_estagios):
        lista_caminho_usinas =[]
        for unit in ordem_termos:
            lista_caminho_usinas.append(unit)
            if(unit.locked[t] == False):
                if (sistema_guloso.demanda_liquida[t] > 0):
                    unit.commitment[t] = 1
                    ################# TON
                    flag_unit_locked_off_future = False
                    if(t != 0):
                        unit_anterior = 0 if t == 0 else unit.commitment[t-1]
                        if(unit.commitment[t] == 1) and (unit.commitment[t-1] == 0):
                            flag_unit_locked_off_future = verifica_TON_futuro(t, unit)
                            #print("t: ", t, " unit: ", unit.nome, " TON: ", unit.t_on, " flag_unit_locked_off_future: ", flag_unit_locked_off_future)
                            if(flag_unit_locked_off_future == False):
                                for i in range(t, min(t + unit.t_on, max(sistema_guloso.estagios))):
                                    unit.commitment[i] = 1
                                    unit.geracoes[i] += unit.limite_inferior
                                    unit.locked[i] = True
                                limite_geracao = unit.limite_superior if unit.geracoes[t] == 0 else unit.limite_superior - unit.limite_inferior
                                geracao = max(min(limite_geracao, sistema_guloso.demanda_liquida[t]),0)
                                unit.geracoes[t] += geracao 
                            else:
                                unit.commitment[t] = 0
                                unit.geracoes[t] = 0
                        else:
                            geracao = max(min(unit.limite_superior, sistema_guloso.demanda_liquida[t]),unit.limite_inferior)
                            unit.geracoes[t] = geracao
                            sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
                    elif(t== 0):
                        flag_unit_locked_off_future = verifica_TON_futuro(t, unit)
                        if(flag_unit_locked_off_future == False):
                            for i in range(t, t + unit.t_on):
                                unit.commitment[i] = 1
                                unit.geracoes[i] += unit.limite_inferior
                                unit.locked[i] = True
                            limite_geracao = unit.limite_superior if unit.geracoes[t] == 0 else unit.limite_superior - unit.limite_inferior
                            geracao = max(min(limite_geracao, sistema_guloso.demanda_liquida[t]),0)
                            unit.geracoes[t] += geracao 
                        else:
                            unit.commitment[t] = 0
                            unit.geracoes[t] = 0
                    
                    
                    sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
                else:
                    unit.commitment[t] = 0
                    ############## TOFF
                    if(t != 0):
                        
                        if(unit.commitment[t-1] == 1) and (unit.commitment[t] == 0):
                            for i in range(t, min(t + unit.t_off, max(sistema_guloso.estagios))):
                                unit.commitment[i] = 0
                                unit.geracoes[i] = 0
                                unit.locked[i] = True

                    unit.geracoes[t] = max(unit.geracoes[t],0)
            elif(unit.locked[t] == True):
                
                if(unit.commitment[t] == 1):
                    #print("ENTROU AQUI", sistema_guloso.demanda_liquida[t])

                    geracao += max(min(unit.limite_superior, sistema_guloso.demanda_liquida[t]),unit.limite_inferior)

                else:
                    
                    geracao = 0
                unit.geracoes[t] = geracao 
                sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
            #print("t: ", t, " nome: ", unit.nome, " geracoes: ", unit.geracoes, " commit: ", unit.commitment, " locked: ", unit.locked)
            #if(t == 1 and unit.nome == "g1"):
            #    exit(1)
    #df = pd.concat(
    #    [pd.DataFrame(unit.geracoes), pd.DataFrame(unit.commitment)],
    #    axis=1  # concatena colunas
    #)
    #df['DemandaLiquida'] = sistema_guloso.demanda_liquida
    #df['Demanda'] = sistema_guloso.demanda
    #print(df.round(1))
    print("############################")
    print("CUSTO TOTAL: ", sistema_guloso.total_cost)

    return sistema_guloso



def solucao_gulosa(sistema_inicial):
    sistema_guloso = copy.deepcopy(sistema_inicial)
    ordem_termos = sorted(sistema_guloso.geradores, key=lambda u: u.custo)
    #random.shuffle(ordem_termos) ###### SOLUCAO INICIAL RANDOMICA
    #ordem_menor_termica_maior_termica = [u.nome for u in ordem_termos]
    for t in range(sistema_guloso.n_estagios):
        lista_caminho_usinas =[]
        for unit in ordem_termos:
            lista_caminho_usinas.append(unit)
            if(unit.locked[t] == False):
                if (sistema_guloso.demanda_liquida[t] > 0):
                    unit.commitment[t] = 1
                    ################# TON
                    if(t != 0):
                        if(unit.commitment[t] == 1) and (unit.commitment[t-1] == 0):
                            for i in range(t, min(t + unit.t_on, max(sistema_guloso.estagios))):
                                unit.commitment[i] = 1
                                unit.geracoes[i] += unit.limite_inferior
                                unit.locked[i] = True
                    elif(t== 0):
                        for i in range(t, t + unit.t_on):
                            unit.commitment[i] = 1
                            unit.geracoes[i] += unit.limite_inferior
                            unit.locked[i] = True
                    
                    limite_geracao = unit.limite_superior if unit.geracoes[t] == 0 else unit.limite_superior - unit.limite_inferior
                    geracao = max(min(limite_geracao, sistema_guloso.demanda_liquida[t]),0)
                    unit.geracoes[t] += geracao 
                    sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
                else:
                    unit.commitment[t] = 0
                    ############## TOFF
                    if(t != 0):
                        if(unit.commitment[t-1] == 1) and (unit.commitment[t] == 0):
                            for i in range(t, min(t + unit.t_off, max(sistema_guloso.estagios))):
                                unit.commitment[i] = 0
                                unit.geracoes[i] = 0
                                unit.locked[i] = True

                    unit.geracoes[t] = max(unit.geracoes[t],0)

            elif(unit.locked[t] == True):
                if(unit.commitment[t] == 1):
                    geracao = max(min(unit.limite_superior, sistema_guloso.demanda_liquida[t]),unit.limite_inferior)
                    sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
                else:
                    geracao = 0
                unit.geracoes[t] = geracao 

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
    #gera_log_informacoes(sistema_new)
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
    df['Demanda'] = sistema_new.demanda
    #print("############################")
    #gera_log_informacoes(sistema_new)
    return sistema_new
