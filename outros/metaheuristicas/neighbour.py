

from modelo.classes import *
from utils.utils import *
from metaheuristicas.algoritmo_guloso import *
import pandas as pd
import copy
from random import randint

# --------------------------
# Variação de solução (neighbor)
# --------------------------
def neighbor(sistema_neighbour):
    sistema_neighbour = busca_local_desliga_usina_periodo(sistema_neighbour)
    return sistema_neighbour

def seleciona_usinas(sistema_new, estagio):
    lista_usinas_ligadas_periodo = []
    lista_usinas_desligadas_periodo = []
    for unit in sistema_new.geradores:
        if(unit.commitment[estagio-1] == 1):
            lista_usinas_ligadas_periodo.append(unit)
        else:
            lista_usinas_desligadas_periodo.append(unit)
    
    return lista_usinas_ligadas_periodo, lista_usinas_desligadas_periodo

def busca_local_desliga_usina_periodo(sistema_neighbour):
    #gera_log_informacoes(sistema_neighbour)
    inviavel = True
    contador = 0
    #gera_log_informacoes(sistema_neighbour)
    while inviavel == True:
        sistema_new = copy.deepcopy(sistema_neighbour)
        t = random.choice(sistema_new.estagios)
        
        escolha = randint(0,1)
        lista_usinas_ligadas_periodo, lista_usinas_desligadas_periodo = seleciona_usinas(sistema_new, t)
        if(escolha == 1 or len(lista_usinas_desligadas_periodo) == 0 ):
            unit_a_ser_desligada = random.choice(lista_usinas_ligadas_periodo)
            sistema_new.zera_geracoes_e_commitment()
            unit_a_ser_desligada.locked[t-1] = True
        else:
            unit_a_ser_ligada = random.choice(lista_usinas_desligadas_periodo)
            sistema_new.zera_geracoes_e_commitment()
            for i in range(unit_a_ser_ligada.t_on):
                indice = min(t-1 +i, sistema_new.n_estagios-1)
                unit_a_ser_ligada.locked[indice] = True
                unit_a_ser_ligada.commitment[indice] = 1
                unit_a_ser_ligada.geracoes[indice] = unit_a_ser_ligada.limite_inferior


        #print("INFORMACOES ANTES: ")
        #gera_log_informacoes(sistema_new)
        #print("unit_a_ser_ligada: ", unit_a_ser_ligada.nome, " t: ", t)
        #print("unit_a_ser_desligada: ", unit_a_ser_desligada.nome, " t: ", t)


        solution  = nova_solucao_gulosa(sistema_new)
        #print("INFORMACOES DEPOIS: ")
        #gera_log_unitcommitment(solution)
        #exit(1)

        #if(solution.total_cost < 7540):
        #    exit(1)
        return solution


def busca_local(sistema_neighbour):
    # Cria cópias da solução atual
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
            gera_log_informacoes(solution)
            return solution
        contador += 1


def verifica_viabilidade_sistema(sistema):
    lista_inviavel = [True]*sistema.n_estagios
    for idx_est in range(sistema.n_estagios):
        capacidade_instalada_maxima = 0
        capacidade_instalada_minima = 0
        for unit in sistema.geradores:
            capacidade_instalada_maxima += unit.limite_superior*unit.commitment[idx_est]
            capacidade_instalada_minima += unit.limite_inferior*unit.commitment[idx_est]

        if(capacidade_instalada_maxima >  sistema.demanda[idx_est] and capacidade_instalada_minima < sistema.demanda[idx_est]):
            lista_inviavel[idx_est] = False

    if(sum(lista_inviavel) == 0):
        return True
    else:
        return False

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

def random_explorer(sistema_neighbour):
    contador = 0
    inviavel = True
    ordem_termos = sorted(sistema_neighbour.geradores, key=lambda u: u.custo)
    gera_log_informacoes(sistema_neighbour)
    exit(1)
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

    solution  = adequa_balanco_potencia_guloso(sistema_neighbour)
    gera_log_informacoes(solution)
    return solution



def neighbor_old(sistema_neighbour):
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

                solution  = adequa_balanco_potencia_guloso(sistema_new)
                return solution
            else:
                inviavel = True
            contador += 1