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
#pesos = np.random.randint(2, 15, size=n)
#valores = np.random.randint(5, 30, size=n)
#capacidade = int(np.sum(pesos) - max(pesos)*0.01) 

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

x = solucao_inicial_aleatoria()
print(x)
melhor_sol = x.copy()

def calcula(sol):
    peso_total = np.sum(sol * pesos)
    if peso_total > capacidade:
        return 0  # penalizar excesso de peso
    return np.sum(sol * valores)

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