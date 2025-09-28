import numpy as np

# Exemplo de uso
pesos= np.array([4, 3 , 7, 5, 3, 2, 3])   # valores dos itens
valores = np.array([12, 8, 17, 11, 6, 2, 2])       # pesos dos itens

densidade_de_valor = np.around(valores/pesos,2)
print(densidade_de_valor)
# Usando dict comprehension
dicionario = {i: v for i, v in enumerate(densidade_de_valor)}
invertido = {v: k for k, v in dicionario.items()}

print(dicionario)
ordenado = sorted(densidade_de_valor, reverse=True)
print(ordenado)
capacidade = 9

selecao = []
for item in ordenado:
    peso_item = pesos[invertido[item]]
    valor_item = valores[invertido[item]]
    print("densidade: ", item, " peso: ", peso_item, " valor: ", valor_item)
    if((capacidade >= 0) and (capacidade - peso_item >= 0)):
        selecao.append(invertido[item])
        capacidade = capacidade - peso_item
    print("CAPACIDADE: ", capacidade)
    print(selecao)