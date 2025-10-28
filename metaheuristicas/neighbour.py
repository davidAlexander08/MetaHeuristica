

from modelo.classes import *
from utils.utils import *
from metaheuristicas.algoritmo_guloso import *
import pandas as pd
import copy
import random

# --------------------------
# Variação de solução (neighbor)
# --------------------------

def neighbor(sistema_neighbour):
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