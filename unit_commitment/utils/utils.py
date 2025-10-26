
def gera_log_informacoes(sistema):
    ## Print unit info
    for t in sistema.geradores:
        print(f"Nome: {t.nome}, LimSup: {t.limite_superior}, LimInf: {t.limite_inferior}, "
              f"Custo: {t.custo}, T_on: {t.t_on}, T_off: {t.t_off}")
    print("-"*80)

    if sistema.demanda is not None and len(sistema.demanda) > 0:
        demanda_str = " ".join(f"{int(x):>3}" for x in sistema.demanda)
        print(f"Demanda   : {demanda_str}")
        print("-"*80)

    # Print all Gerações
    print("Gerações:")
    for t in sistema.geradores:
        geracoes_str = " ".join(f"{int(x):>3}" for x in t.geracoes) if t.geracoes is not None else "-"
        print(f"{t.nome:<6}: {geracoes_str}")
    print("-"*80)

    # Print all Commitment
    print("Commitment:")
    for t in sistema.geradores:
        commit_str = " ".join(str(int(x)) for x in t.commitment) if t.commitment is not None else "-"
        print(f"{t.nome:<6}: {commit_str}")
    print("-"*80)

    ## Print all Locked
    #print("Locked:")
    #for t in sistema.geradores:
    #    locked_str = " ".join(str(int(x)) for x in t.locked) if t.locked is not None else "-"
    #    print(f"{t.nome:<6}: {locked_str}")
    #print("-"*80)
# Initialize containers
#UnitCommitment = {}



def consecutive_ones(v, pos):
    lista = []
    lista.append(pos)
    if v[pos] == 0:
        return 0

    count = 1
    # Left side
    i = pos - 1
    while i >= 0 and v[i] == 1:
        lista.append(i)
        count += 1
        i -= 1

    # Right side
    i = pos + 1
    while i < len(v) and v[i] == 1:
        lista.append(i)
        count += 1
        i += 1

    return count, lista