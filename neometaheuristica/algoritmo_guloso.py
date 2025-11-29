
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

def find_locked(t, unit, T_discr):
    positions = []
    for idx in range(t, min(t + T_discr, len(unit.commitment))):
        if unit.locked[idx] == 1:
            positions.append(idx)
    return positions

def verifica_futuro(t, unit, TEMPO):
    locked_ahead = find_locked(t, unit, TEMPO)
    #print("locked_ahead: ", locked_ahead)
    encontrou_ton = False
    encontrou_toff = False
    if(len(locked_ahead) != 0):
        values = []
        for idx in locked_ahead:
            values.append(unit.commitment[idx])
        #print("t: ",t, " ", values, " ", unit.commitment, " ", unit.nome, " ", sum(values))
        if(sum(values) > 1):
            encontrou_ton = True
        if(sum(values) ==0):
            encontrou_toff =  True 
    return encontrou_ton, encontrou_toff






def nova_solucao_gulosa(sistema_inicial, ativa_random = False, flag_debug = False):    
    sistema_guloso = copy.deepcopy(sistema_inicial)
    ordem_termos = sorted(sistema_guloso.geradores, key=lambda u: u.custo)
    if(ativa_random == True):
        random.shuffle(ordem_termos) ###### SOLUCAO INICIAL RANDOMICA
    
    for t in range(sistema_guloso.n_estagios):
        lista_caminho_usinas =[]
        for unit in ordem_termos:
            lista_caminho_usinas.append(unit)
            if(unit.locked[t] == False):
                #if(flag_debug):
                #    print("FALSE: t: ", t, " unit: ", unit.nome, " ger: ", unit.geracoes[t], " dem: ", sistema_guloso.demanda_liquida[t], " locked: ", unit.locked)
                if (sistema_guloso.demanda_liquida[t] > 0):
                    unit.commitment[t] = 1
                    ################# TON
                    unit_anterior = 0 if t == 0 else unit.commitment[t-1]
                    if(unit.commitment[t] == 1) and (unit_anterior == 0):
                        encontrou_ton, encontrou_toff = verifica_futuro(t, unit, unit.t_on)
                        if(encontrou_toff == False):
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
                        #print("nome: ", unit.nome)
                        geracao = max(min(unit.limite_superior, sistema_guloso.demanda_liquida[t]),unit.limite_inferior)
                        unit.geracoes[t] = geracao
                else:
                    unit.commitment[t] = 0
                    ############## TOFF
                    if(t != 0):
                        if(unit.commitment[t-1] == 1) and (unit.commitment[t] == 0):
                            encontrou_ton, encontrou_toff = verifica_futuro(t, unit, unit.t_off)
                            if(encontrou_ton == False):
                                for i in range(t, min(t + unit.t_off, max(sistema_guloso.estagios))):
                                    unit.commitment[i] = 0
                                    unit.geracoes[i] = 0
                                    unit.locked[i] = True
                                unit.geracoes[t] = max(unit.geracoes[t],0)
                            else:
                                unit.commitment[t] = 1
                                geracao = max(min(unit.limite_superior, sistema_guloso.demanda_liquida[t]),unit.limite_inferior)
                                unit.geracoes[t] = geracao
            elif(unit.locked[t] == True):
                #if(flag_debug):
                #    print("t: ", t, " unit: ", unit.nome, " ger: ", unit.geracoes[t], " dem: ", sistema_guloso.demanda_liquida[t])
                if(unit.commitment[t] == 1):
                    limite_geracao = unit.limite_superior if unit.geracoes[t] == 0 else unit.limite_superior - unit.limite_inferior

                    geracao = max(min(limite_geracao, sistema_guloso.demanda_liquida[t]),0)
                    unit.geracoes[t] += geracao if unit.geracoes[t] < unit.limite_superior else 0
                    #if(flag_debug):
                    #    print("t: ", t, " unit: ", unit.nome, " ger: ", unit.geracoes[t], " dem: ", sistema_guloso.demanda_liquida[t])
                else:
                    unit.geracoes[t] = 0
            sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
        #if(t == 0 and flag_debug):
        #    gera_log_informacoes(sistema_guloso)
        #    print("ENTROU AQUI")
        #    exit(1)
    return sistema_guloso



def solucao_gulosa(sistema_inicial):
    sistema_guloso = copy.deepcopy(sistema_inicial)
    ordem_termos = sorted(sistema_guloso.geradores, key=lambda u: u.custo)
    random.shuffle(ordem_termos) ###### SOLUCAO INICIAL RANDOMICA
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
                        temp = sistema_guloso.demanda_liquida
                        if(unit.commitment[t] == 1) and (unit.commitment[t-1] == 0):
                            for i in range(t, min(t + unit.t_on, max(sistema_guloso.estagios))):
                                unit.commitment[i] = 1
                                unit.geracoes[i] += unit.limite_inferior
                                unit.locked[i] = True
                        else:
                                                    #print("nome: ", unit.nome)
                            #geracao = max(min(unit.limite_superior, sistema_guloso.demanda_liquida[t]),unit.limite_inferior)
                            #unit.geracoes[t] = geracao
                            print("t: ", t, " nome: ", unit.nome, " geracao: ", unit.geracoes[t], " Lsup: ", unit.limite_superior, " Linf: ", unit.limite_inferior, " demLiq: ", temp)

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
                temp = sistema_guloso.demanda_liquida
                if(unit.commitment[t] == 1):
                    limite_geracao = unit.limite_superior if unit.geracoes[t] == 0 else unit.limite_superior - unit.limite_inferior
                    geracao = max(min(limite_geracao, sistema_guloso.demanda_liquida[t]),0)
                    unit.geracoes[t] += geracao
                else:
                    geracao = 0
                    unit.geracoes[t] = geracao 
                #print("t: ", t, " nome: ", unit.nome, " geracao: ", unit.geracoes[t], " Lsup: ", unit.limite_superior, " Linf: ", unit.limite_inferior, " demLiq: ", temp)
                sistema_guloso = verifica_resolve_inviabilidade(sistema_guloso, lista_caminho_usinas)
                #print("t: ", t, " nome: ", unit.nome, " geracao: ", unit.geracoes[t])
    #df = pd.concat(
    #    [pd.DataFrame(unit.geracoes), pd.DataFrame(unit.commitment)],
    #    axis=1  # concatena colunas
    #)
    #df['DemandaLiquida'] = sistema_guloso.demanda_liquida
    #df['Demanda'] = sistema_guloso.demanda
    #print(df.round(1))
    #print("############################")
    #print("CUSTO TOTAL: ", sistema_guloso.total_cost)

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
    #df = pd.concat(
    #    [pd.DataFrame(unit.geracoes), pd.DataFrame(unit.commitment)],
    #    axis=1  # concatena colunas
    #)
    #df['DemandaLiquida'] = sistema_new.demanda_liquida
    #df['Demanda'] = sistema_new.demanda
    #print("############################")
    #gera_log_informacoes(sistema_new)
    return sistema_new
