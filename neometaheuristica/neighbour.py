

from modelo.classes import *
from utils.utils import *
from neometaheuristica.algoritmo_guloso import *
import pandas as pd
import copy
from random import randint
from neometaheuristica.adequa_otimizacao import *
from itertools import groupby
import math

# --------------------------
# Variação de solução (neighbor)
# --------------------------

def gera_solucao_vizinhos_custom(sistema_neighbour):
    mapa_sistemas = {}
    sistema_SA = gera_vizinho_SA(sistema_neighbour)
    mapa_sistemas[sistema_SA.total_cost] = sistema_SA
    sistema_VNS = gera_vizinho_VNS(sistema_neighbour)
    mapa_sistemas[sistema_VNS.total_cost] =  sistema_VNS
    sistema_ILS = gera_vizinho_ILS(sistema_neighbour)
    mapa_sistemas[sistema_ILS.total_cost] = sistema_ILS
    lowest_system = mapa_sistemas[min(mapa_sistemas.keys())]
    sistema_resultante = lowest_system
    return lowest_system

def gera_vizinho_SA(sistema_neighbour): ### PARA O SA
    sistema_neighbour.zera_geracoes_e_commitment()
    sistema_resultante = nova_solucao_gulosa(sistema_neighbour, True)
    return sistema_resultante

def gera_vizinho_VNS(sistema_neighbour):
    ### VNS
    mapa_sistemas = {}
    #max_grau = int(len(sistema_neighbour.geradores)/2)
    max_grau = max(1, math.ceil(len(sistema_neighbour.geradores) / 5))
    for grau in range(1,max_grau+1):
        sistema_1  = forca_ligar(sistema_neighbour, grau)
        mapa_sistemas[sistema_1.total_cost] = sistema_1

    lowest_system = mapa_sistemas[min(mapa_sistemas.keys())]
    sistema_resultante = lowest_system
    return lowest_system

def gera_vizinho_ILS(sistema_neighbour):
    ### Perturba Busca Local
    mapa_sistemas = {}
    #max_grau_usinas_fixadas = 
    #max_grau = 

    max_grau_usinas_fixadas = max(1, math.ceil(len(sistema_neighbour.geradores) / 5))
    max_grau = max(1, math.ceil(len(sistema_neighbour.geradores) / 5))
    #print("max_grau_usinas_fixadas: ", max_grau_usinas_fixadas, " max_grau: ", max_grau)
    for grau_usi in range(1,max_grau_usinas_fixadas+1):
        for grau in range(1,max_grau+1):
            sistema_1  = forca_estado(sistema_neighbour, grau_usi, grau)
            mapa_sistemas[sistema_1.total_cost] = sistema_1
    lowest_system = mapa_sistemas[min(mapa_sistemas.keys())]
    sistema_resultante = lowest_system
    #exit(1)
    return lowest_system

def forca_estado(sistema, grau_usi, grau):
    t = random.choice(sistema.estagios)
    sistema_new = copy.deepcopy(sistema)
    sistema_new.zera_geracoes_e_commitment()
    listaNomesUsinas = sistema.listaNomesUsinas.copy()
    for sorteio_usi in range(1,grau_usi+1):
        if(len(listaNomesUsinas) != 0):
            usina_aleatoria  = random.choice(listaNomesUsinas)
            #usina_aleatoria = "g1"
            sistema_new.getUsina(usina_aleatoria).locked = [1]*sistema.n_estagios
            sistema_new.getUsina(usina_aleatoria).commitment = sistema.getUsina(usina_aleatoria).commitment.copy()
            sistema_new.getUsina(usina_aleatoria).geracoes = sistema.getUsina(usina_aleatoria).geracoes.copy()
            listaNomesUsinas.remove(usina_aleatoria)

    for sorteio_usi in range(1, grau+1):
        if(len(listaNomesUsinas) != 0):
            usina_aleatoria  = random.choice(listaNomesUsinas)
            #usina_aleatoria = "g2"
            for t in sistema.estagios:
                estado = randint(0,1)
                if(sistema_new.getUsina(usina_aleatoria).locked[t-1] != 1):
                    #print("usina: ", usina_aleatoria, " t: ", t, " estado: ", estado)
                    if(estado == 1):
                        TON = sistema_new.getUsina(usina_aleatoria).t_on
                        for i in range(0,TON):
                            periodo = min(sistema.n_estagios-1, t-1+i)
                            
                            sistema_new.getUsina(usina_aleatoria).commitment[periodo] = 1
                            sistema_new.getUsina(usina_aleatoria).locked[periodo] = True
                            sistema_new.getUsina(usina_aleatoria).geracoes[periodo] = sistema_new.getUsina(usina_aleatoria).limite_inferior
                            #print("periodo: ", periodo, " estado: ", estado)
                        #print("commit: ", sistema_new.getUsina(usina_aleatoria).commitment)
                        #print("locked: ", sistema_new.getUsina(usina_aleatoria).locked)
                    if(t != 0 and estado == 0):
                        if(sistema_new.getUsina(usina_aleatoria).commitment[t-2] == 1):
                            TOFF = sistema_new.getUsina(usina_aleatoria).t_off
                            for i in range(0,TOFF):
                                periodo = min(sistema.n_estagios-1, t-1+i)
                                sistema_new.getUsina(usina_aleatoria).commitment[periodo] = 0
                                sistema_new.getUsina(usina_aleatoria).locked[periodo] = True
                            #    print("periodo: ", periodo, " estado: ", estado)
                            #print("commit: ", sistema_new.getUsina(usina_aleatoria).commitment)
                            #print("locked: ", sistema_new.getUsina(usina_aleatoria).locked)
                        else:
                            sistema_new.getUsina(usina_aleatoria).locked[t-1] = True
    #gera_log_informacoes(sistema_new)
    solution  = nova_solucao_gulosa(sistema_new, False, True)
    viavel = verifica_viabilidade_sistema(solution)
    #print("viavel: ", viavel)
    if(viavel == False):
        return sistema
    else:
        #gera_log_informacoes(solution)
        return solution

def sorteia_periodo_retorna_listas(sistema):
    lista_usinas_desligadas_periodo = []
    while len(lista_usinas_desligadas_periodo) == 0:
        t = random.choice(sistema.estagios)
        lista_ligadas, lista_usinas_desligadas_periodo = seleciona_usinas(sistema, t)
    return t, lista_ligadas, lista_usinas_desligadas_periodo
def forca_ligar(sistema_neighbour, grau):
    sistema_new = copy.deepcopy(sistema_neighbour)
    sistema_new.zera_geracoes_e_commitment()
    for idx_grau in range(grau):
        t, usinas_ligadas, lista_usinas_desligadas_periodo = sorteia_periodo_retorna_listas(sistema_neighbour)
        nome_usina_ser_ligada = random.choice(lista_usinas_desligadas_periodo)
        #print(t, "nome_usina_ser_ligada: ", nome_usina_ser_ligada )
        unit_a_ser_ligada = sistema_new.getUsina(nome_usina_ser_ligada)
        for i in range(unit_a_ser_ligada.t_on):
            indice = min(t-1 +i, sistema_new.n_estagios-1)
            unit_a_ser_ligada.locked[indice] = True
            unit_a_ser_ligada.commitment[indice] = 1
            unit_a_ser_ligada.geracoes[indice] = unit_a_ser_ligada.limite_inferior
    #print("GRAU: ", grau)
    #gera_log_informacoes(sistema_new)
    solution  = nova_solucao_gulosa(sistema_new)
    return solution


def seleciona_usinas(sistema_new, estagio):
    lista_usinas_ligadas_periodo = []
    lista_usinas_desligadas_periodo = []
    for unit in sistema_new.geradores:
        if(unit.commitment[estagio-1] == 1):
            lista_usinas_ligadas_periodo.append(unit.nome)
        else:
            lista_usinas_desligadas_periodo.append(unit.nome)
    
    return lista_usinas_ligadas_periodo, lista_usinas_desligadas_periodo

def check_ton_toff(unit):
    for val, group in groupby(unit.commitment):
        run_length = len(list(group))
        if val == 1 and run_length < unit.t_on:
            return True
        if val == 0 and run_length < unit.t_off:
            return True
    return False

def verifica_viabilidade_sistema(sistema):
    lista_inviavel = [True]*sistema.n_estagios
    for idx_est in range(sistema.n_estagios):
        capacidade_instalada_maxima = 0
        capacidade_instalada_minima = 0
        for unit in sistema.geradores:
            capacidade_instalada_maxima += unit.limite_superior*unit.commitment[idx_est]
            capacidade_instalada_minima += unit.limite_inferior*unit.commitment[idx_est]
        if(capacidade_instalada_maxima >=  sistema.demanda[idx_est] and capacidade_instalada_minima <= sistema.demanda[idx_est] ):
            lista_inviavel[idx_est] = False
        #else:
            #print("capacidade_instalada_maxima: ", capacidade_instalada_maxima)
            #print("capacidade_instalada_minima: ", capacidade_instalada_minima)
    #print("lista_inviavel: ", lista_inviavel)
    if(sum(lista_inviavel) == 0):
        return True
    else:
        return False

def seleciona_usinas_alternar_estados_periodo(sistema, grau):
    for iter in range(grau):
        t = random.choice(sistema.estagios)-1
        lista_usinas_ligadas_periodo, lista_usinas_desligadas_periodo  = seleciona_usinas(sistema, t)
        capacidade_instalada_periodo = 0
        for unit in lista_usinas_ligadas_periodo:
            unidade = sistema.getUsina(unit)
            capacidade_instalada_periodo += unidade.limite_superior
        if(len(lista_usinas_ligadas_periodo) != 0 and len(lista_usinas_desligadas_periodo) != 0):
            lista_unidades_a_serem_desligadas= []
            unit_a_ser_desligada = random.choice(lista_usinas_ligadas_periodo)
            lista_unidades_a_serem_desligadas.append(unit_a_ser_desligada)
            capacidade_instalada_periodo -= sistema.getUsina(unit_a_ser_desligada).limite_superior
            aux_usinas_desligadas_periodo = lista_usinas_desligadas_periodo.copy()
            #print(aux_usinas_desligadas_periodo, "capacidade_instalada_periodo: ", capacidade_instalada_periodo, " sistema.demanda[t]: ", sistema.demanda[t])
            lista_unidades_a_serem_ligadas = []
            while capacidade_instalada_periodo < sistema.demanda[t]:
                if(len(aux_usinas_desligadas_periodo) == 0):
                    break
                if(capacidade_instalada_periodo >=  sistema.demanda[t]):
                    break
                unit_a_ser_ligada = random.choice(aux_usinas_desligadas_periodo)
                lista_unidades_a_serem_ligadas.append(unit_a_ser_ligada)
                aux_usinas_desligadas_periodo.remove(unit_a_ser_ligada)
                capacidade_instalada_periodo += sistema.getUsina(unit_a_ser_ligada).limite_superior
            #print("iter: ", iter, " grau: ", grau)
            for usi in lista_unidades_a_serem_desligadas:
                sistema.getUsina(usi).commitment[t] = 0
            for usi in lista_unidades_a_serem_ligadas:
                sistema.getUsina(usi).commitment[t] = 1
            
    return sistema


def swap_sensibilidade_units(sistema_neighbour, grau):
    viavel = False
    contador = 1
    while viavel == False:
        sistema_new = copy.deepcopy(sistema_neighbour)
        sistema_new = seleciona_usinas_alternar_estados_periodo(sistema_new, grau)
        viavel = verifica_viabilidade_sistema(sistema_new)  
        print("viavel: ", viavel)
        #gera_log_unitcommitment(sistema_new)
        if(viavel):      
            solution  = executa_solucao_pl(sistema_new)
            return solution
        contador += 1

def random_explorer(sistema_neighbour):
    contador = 0
    inviavel = True
    ordem_termos = sorted(sistema_neighbour.geradores, key=lambda u: u.custo)
    #gera_log_informacoes(sistema_neighbour)
    while inviavel == True:
        #random.shuffle(ordem_termos) ###### SOLUCAO INICIAL RANDOMICA
        lista_inviavel = [1]*sistema_neighbour.n_estagios
        sistema_neighbour.zera_geracoes_e_commitment()
        for idx_est in range(sistema_neighbour.n_estagios):
            capacidade_instalada_per = 0
            #for unit in sistema_neighbour.geradores:
            for unit in ordem_termos: ## ATIVA RANDOM EXPLORER POR ORDEM DE MÉRITO
                if(lista_inviavel[idx_est] == True):
                    if(unit.locked[idx_est] == False):
                        estado = randint(0,1)
                        if(estado == 1):
                            for i in range(unit.t_on):
                                if(idx_est + i < sistema_neighbour.n_estagios):
                                    unit.commitment[idx_est + i ] = estado
                                    unit.locked[idx_est + i ] = True
                        if(idx_est > 0):
                            
                            if(unit.commitment[idx_est-1] == 1 and estado == 0):
                                for i in range(unit.t_off):
                                    if(idx_est + i < sistema_neighbour.n_estagios):
                                        unit.commitment[idx_est + i ] = estado
                                        unit.locked[idx_est + i ] = True
                    capacidade_instalada_per += unit.limite_superior*unit.commitment[idx_est]
                    if capacidade_instalada_per > sistema_neighbour.demanda[idx_est]:
                        lista_inviavel[idx_est] = False
        if(sum(lista_inviavel) == 0):
            inviavel = False
        contador += 1
    solution  = executa_solucao_pl(sistema_neighbour)
    #gera_log_informacoes(solution)
    return solution




def busca_local_sensibilidades_unit(sistema_neighbour):
    # Cria cópias da solução atual
    #gera_log_informacoes(sistema_neighbour)
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
                while capacidade_instalada_periodo < sistema_neighbour.demanda[i]:
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


                if(capacidade_instalada_per - sistema_neighbour.demanda[periodo] < 0):
                    inviavel = True
                lista_inviavel.append(inviavel)
            valida_inviabilidades_unit_commitment = sum(lista_inviavel)
            if(valida_inviabilidades_unit_commitment == 0):
                solution  = executa_solucao_pl(sistema_new)
                return solution
            else:
                inviavel = True
            contador += 1






def selecao_aleatoria_de_estados(unit):
    for idx_est in range(len(unit.commitment)):
        capacidade_instalada_per = 0
        if(unit.locked[idx_est] == False):
            estado = randint(0,1)
            if(estado == 1):
                for i in range(unit.t_on):
                    if(idx_est + i < len(unit.commitment)):
                        unit.commitment[idx_est + i ] = estado
                        unit.locked[idx_est + i ] = True
            if(idx_est > 0):
                if(unit.commitment[idx_est-1] == 1 and estado == 0):
                    for i in range(unit.t_off):
                        if(idx_est + i < len(unit.commitment)):
                            unit.commitment[idx_est + i ] = estado
                            unit.locked[idx_est + i ] = True

def desliga_uma_liga_outras_sorteia_estados(sistema_neighbour):
    inviavel = True
    contador = 0
    while inviavel == True:
        sistema_new = copy.deepcopy(sistema_neighbour)
        sistema_new.zera_geracoes()
        t = random.choice(sistema_new.estagios)-1
        lista_usinas_ligadas_periodo = []
        lista_usinas_desligadas_periodo = []
        capacidade_instalada_maxima = 0
        capacidade_instalada_minima = 0
        for unit in sistema_new.geradores:
            if(unit.commitment[t] == 1):
                lista_usinas_ligadas_periodo.append(unit)
                capacidade_instalada_maxima += unit.limite_superior
                capacidade_instalada_minima += unit.limite_inferior
            else:
                lista_usinas_desligadas_periodo.append(unit)
        lista_unidades_com_novo_despacho = []
        unit_ligada = random.choice(lista_usinas_ligadas_periodo)
        lista_unidades_com_novo_despacho.append(unit_ligada)
        capacidade_instalada_maxima -= unit_ligada.limite_superior
        capacidade_instalada_minima -= unit_ligada.limite_inferior
        aux_usinas_desligadas_periodo = lista_usinas_desligadas_periodo.copy()
        while capacidade_instalada_maxima < sistema_neighbour.demanda[t]:
            if(len(aux_usinas_desligadas_periodo) == 0):
                break
            unit_a_ser_ligada = random.choice(aux_usinas_desligadas_periodo)
            lista_unidades_com_novo_despacho.append(unit_a_ser_ligada)
            aux_usinas_desligadas_periodo.remove(unit_a_ser_ligada)
            capacidade_instalada_maxima += unit_a_ser_ligada.limite_superior
            capacidade_instalada_minima += unit_a_ser_ligada.limite_inferior
        for unit in lista_unidades_com_novo_despacho:
            selecao_aleatoria_de_estados(unit)
        viavel = verifica_viabilidade_sistema(sistema_new)
        if(viavel):
            solution  = adequa_balanco_potencia_guloso(sistema_new)
            return solution
        contador += 1


