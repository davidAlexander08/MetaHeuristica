import numpy as np

class Termica:
    def __init__(self):
        self.limite_superior = None
        self.limite_inferior = None
        self.custo = None
        self.t_on = None
        self.t_off = None
        self.nome = None
        self.geracoes = np.array([])
        self.commitment = np.array([])
        self.locked = np.array([])

class Sistema:
    def __init__(self):
        self.geradores = None
        self.estagios = None
        self.demanda = np.array([])
        self.deficit = None
        self.custo_deficit = None
        self.custo_total = None
    
    @property
    def n_estagios(self):
        if self.estagios is not None:
            return len(self.estagios)
        else:
            return 0  # or None, if you prefer

    @property
    def demanda_liquida(self):
        if(self.demanda is not None):
            geracao_total = np.array([0.0]*self.n_estagios)
            for estagio in range(self.n_estagios):
                for usina in self.geradores:
                    geracao_total[estagio] += usina.geracoes[estagio]
            return self.demanda - geracao_total


    def zera_geracoes(self):
        for gerador in self.geradores:
            if gerador.geracoes is not None:
                gerador.geracoes[:] = [0] * len(gerador.geracoes)  # set all periods to 0
                gerador.locked[:] = [False] * len(gerador.locked)  # set all periods to 0
            else:
                print("ERRO: Lista geradores é None, verifique dados de entrada")

    def zera_geracoes_e_commitment(self):
        for gerador in self.geradores:
            if gerador.geracoes is not None:
                gerador.geracoes[:] = [0] * len(gerador.geracoes)  # set all periods to 0
                gerador.commitment[:] = [0] * len(gerador.geracoes)  # set all periods to 0
                gerador.locked[:] = [False] * len(gerador.locked)  # set all periods to 0
            else:
                print("ERRO: Lista geradores é None, verifique dados de entrada")

    @property
    def total_cost(self):
        cost = sum(unit.custo*unit.geracoes[t] for unit in self.geradores for t in range(self.n_estagios))
        return cost