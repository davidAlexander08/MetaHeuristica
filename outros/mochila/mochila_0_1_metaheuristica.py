import numpy as np
seed = 0
n = 4
# Exemplo de uso
pesos= np.array([4, 3 , 7, 5, 3, 2, 3])   # valores dos itens
valores = np.array([12, 8, 17, 11, 6, 2, 2])       # pesos dos itens
capacidade = 9

pesos= np.array([4, 2 , 1, 3, 1])   # valores dos itens
valores = np.array([20, 5, 1, 8, 1])       # pesos dos itens
capacidade = 7

#pesos= np.array([2, 3 , 4, 5])   # valores dos itens
#valores = np.array([3,4, 5, 6])       # pesos dos itens
#capacidade = 5
n = len(pesos)
np.random.seed(seed)
# valores/pesos aleatórios
n = 20
pesos = np.random.randint(2, 15, size=n)
valores = np.random.randint(5, 30, size=n)
capacidade = int(np.sum(pesos) - max(pesos)*0.1) 

print("PESOS: ", pesos)
print("VALORES: ", valores)
print("CAPACIDADE INICIAL: ",  capacidade)

##Programação Dinâmica
dp = np.zeros((n+1, capacidade+1), dtype=int)

for linha in range(n):
    for cap_mom in range(1, capacidade+1):
        peso_item = pesos[linha]
        valor_item = valores[linha]
        valor = max(dp[linha][cap_mom], valor_item + dp[linha][cap_mom - peso_item]) if peso_item <= cap_mom else dp[linha][cap_mom]
        dp[linha+1][cap_mom] = valor

        #if peso_item <= cap_mom:
        #    if(linha == 1):
        #        print("Linha: ", linha, " cap_mom: ", cap_mom, " valor: ", dp[linha][cap_mom])
        #        print("Nao Adicionar: ", dp[linha][cap_mom])
        #        print("Adicionar: ", " valor_item: ", valor_item,  " dp[linha][cap_mom - peso_item]: ", dp[linha][cap_mom - peso_item], " cap_mom - peso_item ; ", cap_mom - peso_item)
        #        print(dp[linha][cap_mom])
        #        print(dp)

print(dp)
# Valor máximo
valor_max = dp[n][capacidade]
print("VALOR MÁXIMO:", valor_max)

# Reconstrução dos itens escolhidos
w = capacidade
itens_escolhidos = []
for i in range(n, 0, -1):
    if dp[i][w] != dp[i-1][w]:
        itens_escolhidos.append(i-1)
        w -= pesos[i-1]

itens_escolhidos = list(reversed(itens_escolhidos))
print("CAPACIDADE: ", w)
print("ITENS ESCOLHIDOS:", itens_escolhidos)
print("PESOS ESCOLHIDOS:", pesos[itens_escolhidos])
print("VALORES ESCOLHIDOS:", valores[itens_escolhidos])

print("#############################################################")
print("SIMULATED ANEEALING")

## SIMULATED ANNEALING S.A. (Usando algoritmo de Metropole)

# Parâmetros S.A.
T = 100.0
T_min = 0.1
alpha = 0.95
num_iter = 1000

# Solução inicial aleatória
def solucao_inicial_aleatoria():
    x = np.random.randint(0, 2, size=n)
    
    peso_total = np.sum(x * pesos)
    while peso_total > capacidade and peso_total != 0:
        x = np.random.randint(0, 2, size=n)
        print(x)
        peso_total = np.sum(x * pesos)
        print("capacidade: ", capacidade, " peso_total: ", peso_total)
    return x



def calcula(sol):
    peso_total = np.sum(sol * pesos)
    if peso_total > capacidade:
        return 0  # penalizar excesso de peso
    return np.sum(sol * valores)

x = solucao_inicial_aleatoria()
print(x)
melhor_sol = x.copy()
melhor_valor = calcula(x)

while T > T_min:
    for _ in range(num_iter):
        # Gerar vizinho: inverter um bit aleatório
        i = np.random.randint(0, n)
        x_novo = x.copy()
        x_novo[i] = 1 - x_novo[i]
        
        f_curr = calcula(x)
        f_new = calcula(x_novo)
        
        if f_new > f_curr:
            x = x_novo
            if f_new > melhor_valor:
                melhor_valor = f_new
                melhor_sol = x_novo
        else:
            # aceitar pior com probabilidade
            delta = f_curr - f_new
            if np.random.rand() < np.exp(-delta / T):
                x = x_novo
    T *= alpha

print("Melhor valor:", melhor_valor)
print("Itens selecionados:", melhor_sol)



#################################################
print("#############################################################")
print("SOLUCAO POR ILS")
x = solucao_inicial_aleatoria()
print(x)
melhor_sol = x.copy()
melhor_valor = calcula(x)

def local_search(x):
    """Busca local: troca de bits até não haver melhora"""
    melhorou = True
    melhor_sol = x.copy()
    melhor_val = calcula(melhor_sol)
    while melhorou:
        melhorou = False
        for i in range(n):
            vizinho = melhor_sol.copy()
            vizinho[i] = 1 - vizinho[i]
            if np.sum(vizinho * pesos) <= capacidade:
                val = calcula(vizinho)
                if val > melhor_val:
                    melhor_sol = vizinho
                    melhor_val = val
                    melhorou = True
                    break  # recomeça busca
    return melhor_sol, melhor_val

def perturba(x, intensidade=2):
    """Perturba a solução trocando 'intensidade' bits"""
    y = x.copy()
    indices = np.random.choice(n, intensidade, replace=False)
    for i in indices:
        y[i] = 1 - y[i]
    # Garante viabilidade
    while np.sum(y * pesos) > capacidade:
        idx = np.random.choice(np.where(y == 1)[0])
        y[idx] = 0
    return y


# --------- ILS principal ---------

max_iter = 100
x = solucao_inicial_aleatoria()
x, f = local_search(x)

melhor_sol = x.copy()
melhor_val = f

for it in range(max_iter):
    y = perturba(melhor_sol)
    y, f_y = local_search(y)
    if f_y > melhor_val:
        melhor_sol = y.copy()
        melhor_val = f_y
    # (opcional: critério de aceitação mais elaborado)
    #print(f"Iter {it}: melhor valor = {melhor_val}")

print("\n--- Resultado Final ---")
print("Melhor valor:", melhor_val)
print("Itens selecionados:", melhor_sol)
print("Peso total:", np.sum(melhor_sol * pesos))


##################################################
print("#############################################################")
print("SOLUCAO POR VNS")

def shake(x, k):
    """Gera vizinho aleatório na vizinhança de tamanho k"""
    y = x.copy()
    indices = np.random.choice(n, k, replace=False)
    for i in indices:
        y[i] = 1 - y[i]
    # Garante viabilidade
    while np.sum(y * pesos) > capacidade:
        idx = np.random.choice(np.where(y == 1)[0])
        y[idx] = 0
    return y

# ---------- VNS principal ----------

k_max = 3        # número máximo de vizinhanças
max_iter = 100   # número máximo de iterações

x = solucao_inicial_aleatoria()
x, f = local_search(x)
melhor_sol = x.copy()
melhor_val = f

for it in range(max_iter):
    k = 1
    while k <= k_max:
        y = shake(melhor_sol, k)
        y, f_y = local_search(y)

        if f_y > melhor_val:
            melhor_sol = y.copy()
            melhor_val = f_y
            k = 1  # volta à primeira vizinhança
        else:
            k += 1  # tenta próxima vizinhança
    #print(f"Iter {it}: melhor valor = {melhor_val}")

print("\n--- Resultado Final ---")
print("Melhor valor:", melhor_val)
print("Itens selecionados:", melhor_sol)
print("Peso total:", np.sum(melhor_sol * pesos))



##################################################
print("#############################################################")
print("VND")


# ---------- VND ----------

def vnd(x, k_max=3):
    melhor_sol = x.copy()
    melhor_val = calcula(melhor_sol)
    k = 1
    while k <= k_max:
        vizinho, val_viz = melhor_vizinho_k(melhor_sol, k)
        if val_viz > melhor_val:
            melhor_sol = vizinho
            melhor_val = val_viz
            k = 1  # volta à primeira vizinhança
        else:
            k += 1
    return melhor_sol, melhor_val

def melhor_vizinho_k(x, k):
    """Gera todos os vizinhos de tamanho k e retorna o melhor factível"""
    melhor_sol = x.copy()
    melhor_val = calcula(x)
    from itertools import combinations
    for indices in combinations(range(n), k):
        vizinho = x.copy()
        for i in indices:
            vizinho[i] = 1 - vizinho[i]  # flip k bits
        if np.sum(vizinho * pesos) <= capacidade:
            val = calcula(vizinho)
            if val > melhor_val:
                melhor_sol = vizinho
                melhor_val = val
    return melhor_sol, melhor_val

# ---------- Execução ----------

x0 = solucao_inicial_aleatoria()
melhor_sol, melhor_val = vnd(x0, k_max=3)

print("\n--- Resultado VND ---")
print("Melhor valor:", melhor_val)
print("Itens selecionados:", melhor_sol)
print("Peso total:", np.sum(melhor_sol * pesos))
##################################################
print("#############################################################")
print("SOLUCAO GULOSA")


## METODOLOGIA GULOSA
densidade_de_valor = np.around(valores/pesos,2)
dicionario = {i: v for i, v in enumerate(densidade_de_valor)}
invertido = {v: k for k, v in dicionario.items()}
ordenado = sorted(densidade_de_valor, reverse=True)
selecao = []
peso_escolhido = []
valor_escolhido = []
valor = 0
for item in ordenado:
    peso_item = pesos[invertido[item]]
    valor_item = valores[invertido[item]]
    if((capacidade >= 0) and (capacidade - peso_item >= 0)):
        selecao.append(invertido[item])
        capacidade = capacidade - peso_item
        #print("densidade: ", item, " peso: ", peso_item, " valor: ", valor_item, " capacidade: ", capacidade)
        valor += valor_item
        peso_escolhido.append(peso_item)
        valor_escolhido.append(valor_item)
print("CAPACIDADE: ", capacidade)
print("VALOR: ", valor)
print("ITENS ESCOLHIDOS: ", selecao)
peso_escolhido = [int(x) for x in peso_escolhido]
valor_escolhido = [int(x) for x in valor_escolhido]

print("PESOS ESCOLHIDOS: ", peso_escolhido)
print("VALORES ESCOLHIDOS: ", valor_escolhido)