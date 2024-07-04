# “Considere o problema de corte unidimensional onde barras de ferro de 150m
# são utilizadas para produzir demandas de barras menores nos tamanhos de
# 80m, 60m e 50m. A produção de cada um dos tipos de barra de ferro da
# demanda deve ser de 70, 100, e 120 unidades respectivamente. Escreva um
# modelo que minimize o desperdício na produção da demanda desejada.”

# O programa recebe como entrada o tamanho da barra sobre a qual as demandas
# serão cortadas (no caso acima: 150). Em seguida, o programa recebe a quantidade
# de tipos de itens que a demanda possui (no caso acima: 3). Aém disso, o programa
# recebe o tamanho de cada tipo de item (no caso acima: 80, 60 e 50) e a quantidade a
# ser atendida de cada um (no caso acima: 70, 100 e 120). Além disso, o problema 
# foi modelado de forma a minimizar o desperdício para satisfazer a demanda. 


from ortools.linear_solver import pywraplp

class PadraoCorte:
    def __init__(self, pecas, desperdicio):
        self.arrayPecas = pecas
        self.desperdicio = desperdicio

class Maquina:
    def __init__(self, dados):
        self.barra = int(dados[0][0])
        self.num_de_pecas = int(dados[0][1])
        self.pecas_e_quantidade = []
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.infinity = self.solver.Infinity()
        self.objetivo = self.solver.Objective()
        self.x = []

        for i in range(self.num_de_pecas):
            self.pecas_e_quantidade.append((int(dados[i + 1][0]), int(dados[i + 1][1])))

    def gerar_padroes_de_corte(self):
        self.padroes_de_corte = []
        padrao_atual = []

        def gerar_padroes_de_corte_recursivo(index, multiplicador):
            if index == self.num_de_pecas:
                total = sum(padrao_atual)
                desperdicio = self.barra - total
                self.padroes_de_corte.append(PadraoCorte(padrao_atual[:], desperdicio))
                return
            for i in range(self.pecas_e_quantidade[index][1] * multiplicador + 1):
                if sum(padrao_atual) + i * self.pecas_e_quantidade[index][0] <= self.barra:
                    for j in range(i):
                        padrao_atual.append(self.pecas_e_quantidade[index][0])
                    gerar_padroes_de_corte_recursivo(index + 1, multiplicador)
                    for j in range(i):
                        padrao_atual.pop()

        gerar_padroes_de_corte_recursivo(0, 1)

        a_remover = self.filtrar_padroes_de_corte()

        for combinacao in a_remover:
            self.padroes_de_corte.remove(combinacao)

        return self.padroes_de_corte

    def filtrar_padroes_de_corte(self):
        menor_peca = min(self.pecas_e_quantidade)[0]
        a_remover = []

        for padrao in self.padroes_de_corte:
            if padrao.desperdicio >= menor_peca:
                a_remover.append(padrao)

        return a_remover

    def definir_variaveis_de_decisao(self):
        self.gerar_padroes_de_corte()
        for i, padrao in enumerate(self.padroes_de_corte):
            self.x.append(self.solver.NumVar(0, self.infinity, f'padrao_{i}'))

    def definir_restricoes(self):
        for indice_peca, (comprimento_peca, quantidade_peca) in enumerate(self.pecas_e_quantidade):
            restricao = self.solver.RowConstraint(quantidade_peca, self.infinity, f'peca_{indice_peca}')
            for i, padrao in enumerate(self.padroes_de_corte):
                if comprimento_peca in padrao.arrayPecas:
                    restricao.SetCoefficient(self.x[i], padrao.arrayPecas.count(comprimento_peca))

    def definir_objetivo(self):
        for i in range(len(self.padroes_de_corte)):
            self.objetivo.SetCoefficient(self.x[i], self.padroes_de_corte[i].desperdicio)

        self.objetivo.SetMinimization()

    def imprimir_solucao_otima(self):
        if self.solver.Solve() == pywraplp.Solver.OPTIMAL:
            print('Padroes de corte:\n')
            for i in range(len(self.x)):
                padrao = ' + '.join(map(str, self.padroes_de_corte[i].arrayPecas))
                print(
                    f'Corte: {padrao}\nDesperdicio: {self.padroes_de_corte[i].desperdicio}\nQuantidade: {int(self.x[i].solution_value())}\n')

            print(f'\nDesperdicio total: {int(self.solver.Objective().Value())}')
        else:
            print('Solucao otima nao encontrada')


# Funcao para ler a entrada do arquivo
def ler_entrada(arquivo):
    with open(arquivo, 'r') as f:
        linhas = [linha.split('#')[0].strip().split() for linha in f if linha.strip() and not linha.startswith('#')]
    return linhas


# Leitura da entrada e resolucao do problema
if __name__ == '__main__':
    arquivo_entrada = 'arquivo.txt'
    dados = ler_entrada(arquivo_entrada)
    maquina = Maquina(dados)
    maquina.definir_variaveis_de_decisao()
    maquina.definir_restricoes()
    maquina.definir_objetivo()
    maquina.imprimir_solucao_otima()
