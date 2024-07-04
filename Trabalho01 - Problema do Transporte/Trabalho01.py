# Modelagem, de forma genérica, do problema do transporte considerando os 3
# possíveis casos (balanceado e desbalanceado). No caso desbalanceado, têm-se 
# tanto produção > demanda e produção < demanda.

# Exemplo de entrada (arquivo no formato .txt):
# 3 2 // Número de origens e número de destinos
# 5 5 10 // Produção de cada origem
# 7 8 // Demanda de cada destino
# 14 7 // Custo do transporte por unidade da origem 1 aos destinos 1 e 2
# 8 12 // Custo do transporte por unidade da origem 2 aos destinos 1 e 2
# 5 9 // Custo do transporte por unidade da origem 3 aos destinos 1 e 2


from ortools.linear_solver import pywraplp

# Leitura do TXT
def ler_txt(arquivo):
    with open(arquivo, 'r') as arquivo:
        num_origens, num_destinos = map(int, arquivo.readline().split())
        producao = list(map(int, arquivo.readline().split()))
        demanda = list(map(int, arquivo.readline().split()))
        custos = []
        for _ in range(num_origens):
            custos.append(list(map(int, arquivo.readline().split())))
        if sum(demanda) > sum(producao):
            num_origens += 1
            diferenca = sum(demanda) - sum(producao)
            producao.append(diferenca)
            custos.append([0] * num_destinos)

        elif sum(demanda) < sum(producao):
            num_destinos += 1
            diferenca = sum(producao) - sum(demanda)
            for i in range(num_origens):
                custos[i].append(0)
            demanda.append(diferenca)
        print(num_origens)
        print(num_destinos)
        print(custos)
    return num_origens, num_destinos, producao, demanda, custos


def solucionar_problema(num_origens, num_destinos, producao, demanda, custos):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    infinity = solver.infinity()

    # Variáveis de decisão
    x = {}
    for i in range(num_origens):
        for j in range(num_destinos):
            x[i, j] = solver.IntVar(0, infinity, 'x['+str(i)+str(j)+']')

    # Função objetivo
    objetivo = solver.Objective()
    for i in range(num_origens):
        for j in range(num_destinos):
            objetivo.SetCoefficient(x[i, j], custos[i][j])
    objetivo.SetMinimization()

    # Restrição produção
    for i in range(num_origens): 
        restricao_1 = solver.RowConstraint(producao[i], producao[i], 'restricao produção '+ str(i)) 
        for j in range(num_destinos):
            restricao_1.SetCoefficient(x[i, j], 1)

    # Restrição demanda
    for i in range(num_destinos):
        restricao_2 = solver.RowConstraint(demanda[i], demanda[i], 'restricao demanda '+ str(i)) 
        for j in range(num_origens):
            restricao_2.SetCoefficient(x[j, i], 1)

    # Resolve o problema
    status = solver.Solve()

    # Verifica se a solução é ótima
    if status == pywraplp.Solver.OPTIMAL:
        solucao = {}
        for i in range(num_origens):
            for j in range(num_destinos):
                solucao[i, j] = x[i, j].solution_value()
        return solucao
    else:
        return None

# Mostra a solução
def exibir_solucao(solucao):
    if solucao is not None:
        print("Política de transporte:")
        for (i, j), value in solucao.items():
            if value > 0:
                print(f"Transporte de {int(value)} unidade(s) da origem {i+1} para o destino {j+1}.")
    else:
        print("Não foi possível encontrar uma solução ótima.")


nome_arquivo = "arquivo.txt"  
num_origens, num_destinos, producao, demanda, custos = ler_txt(nome_arquivo)
solucao = solucionar_problema(num_origens, num_destinos, producao, demanda, custos)
exibir_solucao(solucao)
