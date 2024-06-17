import random
from inspect import signature, getfullargspec
import time
import math

#definir a função SUT do GA como no exemplo da triangle, retornando uma lista dos nós executados

def triangle(x: int,y: int,z: int):
    path = []
    if x != y and x != z and y != z:
        path.append(1)
        #print("scalene")
    else:
        if x == y and y == z:
            path.append(2)
            #print("equilateral")
        else:
            path.append(3)
            #print("isosceles")
    return path


#funções das etapas do GA

def InitializePopulation(_popsize, _numPaths, _numParams, _sut):
    _population = []

    for i in range(_popsize):
        t_i = []
        for i in range(_numPaths):
            aux = []
            for j in range(_numParams):
                if str(signature(_sut).parameters[getfullargspec(_sut).args[j]]).split(': ')[1] == 'list':
                    aux2 = []
                    num = random.randint(0,10)
                    for k in range(num):
                        aux2.append(random.randint(0,100))
                    aux.append(aux2)
                elif str(signature(_sut).parameters[getfullargspec(_sut).args[j]]).split(': ')[1] == 'str':
                    aux3 = ""
                    num = random.randint(0,10)
                    for k in range(num):
                        aux3 += chr(random.randint(32,126))
                    aux.append(aux3)
                else:
                    aux.append(random.randint(0,100))
            t_i.append(aux)
        _population.append(t_i)
    
    return _population

def EvaluatePopulation(_population, _sut, _cfg, _numPaths):
    _fitness = []

    for t in _population:
        paths = []
        for test in t:
            try:
                paths.append(set(_sut(*test)))
            except:
                paths.append(set([0]))
        num = 0
        for p in _cfg:
            if set(p) in paths:
                num += 1
        _fitness.append(num/_numPaths)
    
    return _fitness

def Recombination(_popsize, _population, _numPaths):
    available = [j for j in range(_popsize)]
    rnd = int(math.floor(random.randint(0,_popsize-1)/2))
    for i in range(rnd):
        pos1 = random.randint(0,len(available)-1)
        num1 = available[pos1]
        del available[pos1]
        pos2 = random.randint(0,len(available)-1)
        num2 = available[pos2]
        del available[pos2]
        
        rnd1 = random.randint(0,_numPaths-1)
        rnd2 = random.randint(0,_numPaths-1)

        aux = _population[num1][rnd1]
        
        _population[num1][rnd1] = _population[num2][rnd2]
        _population[num2][rnd2] = aux

def Mutation(_population, _mutation_probability, _numPaths, _numParams):
    for cromossome in _population:
        r = random.random()
        if r >= (1 - _mutation_probability):
            num = random.randint(0, _numPaths-1)
            param = random.randint(0, _numParams-1)
            if type(cromossome[num][param]) == type([]):
                aux = []
                rnd = random.randint(0,10)
                for i in range(rnd):
                    aux.append(random.randint(0,10))
                cromossome[num][param] = aux
            elif type(cromossome[num][param]) == type(""):
                aux = list(cromossome[num][param])
                if len(aux) > 0:
                    rnd = random.randint(0,len(aux)-1)
                    aux[rnd] = chr(random.randint(32,126))
                    aux = "".join(aux)
                    cromossome[num][param] = aux
            else:
                cromossome[num][param] = random.randint(0,10)

def AdditionalSearch(_popsize, _population):
    selected = []
    notSelected = []
    for t in _population:
        r = random.random()
        if r >= 1 - (_population.index(t)+1)/_popsize:
            selected.append(t)
        else:
            notSelected.append(t)

    return selected[len(selected)-1], selected

def Selection(_popsize, _selected, _numPaths, _numParams, _sut):
    _population = InitializePopulation(_popsize-len(_selected), _numPaths, _numParams, _sut)
    
    if(len(_selected)>0):
        for t in _selected:
            _population.append(t)
    return _population

#definir para a variável sut o nome da função alvo da geração de casos de teste
sut = triangle

start = time.time()

#definir para a variável cfg a lista de conjuntos de nós dos caminhos da CFG da SUT escolhida
cfg = [[1],[2],[3]]

#tamanho da população
popsize = 10

#limite de iterações realizadas para tentar obter um cromossomo com cobertura total
max_iterations = 100

#valor mínimo sorteado entre 0 e 1 para que um dos casos de teste redundantes de cada cromossomo sofra mutação
mutation_probability = 1.0

#define se todos os cojuntos de nós dos caminhos da CFG foram cobertos pelo melhor cromossomo
allPaths = False

#número de conjuntos de nós dos caminhos
numPaths = len(cfg)

#número de parâmetros de entrada da função testada
numParams = len(signature(sut).parameters)

iter = 0

#cria a população inicial onde os cromossomos possuem o mesmo número de elementos que a quantidade de conjuntos de nós dos caminhos
#da CFG e cada elemento possui um conjunto de valores aleatórios de entrada para serem testados na função em teste
population = InitializePopulation(popsize, numPaths, numParams, sut)

#enquanto um conjunto de nó de algum caminho da CFG não tiver sido coberto ainda pelo melhor cromossomo
#e o número limite de iterações não tiver sido realizado
while not allPaths and iter < max_iterations:

    #calcula o valor de aptidão de cada cromossomo, essa sendo o percentual de conjuntos de nós de caminhos da CFG cobertos por ele
    fitness = EvaluatePopulation(population, sut, cfg, numPaths)
    
    #ordena a população de acordo com a aptidão e de forma crescente
    [x for _, x in sorted(zip(fitness, population))]
    
    #escolhe um número aleatório de vezes um par de dois cromossomos aleatórios e substitui um caso de teste redundante de um
    #por um caso de teste não redundante do outro e vice-versa
    Recombination(popsize, population, numPaths)
    
    #cada cromossomo da população terá uma mesma probabilidade de ter os valores de um de seus casos de teste redundantes
    #alterado aleatoriamente
    Mutation(population, mutation_probability, numPaths, numParams)

    #guarda o valor de aptidão atual do cromossomo com maior aptidão inicial
    pathsBest = []
    for test in population[popsize-1]:
        try:
            pathsBest.append(set(sut(*test)))
        except:
            pathsBest.append(set([0]))
    num = 0
    for p in cfg:
        if set(p) in pathsBest:
            num += 1
    f_best = num/numPaths

    #seleciona quais cromossomos serão reaproveitados para a próxima geração
    #e substitui casos de teste redundantes do melhor cromossomo inicial por casos de teste de cromossomos não selecionados
    #que cobriam um conjunto de nós de um caminho não coberto por nenhum dos cromossomos selecionados
    searchList = AdditionalSearch(popsize, population)
    new_t = searchList[0]
    selected = searchList[1]
        
    #checa se o melhor cromossomo cobre todos os conjuntos de nós dos caminhos da CFG
    pathsT = []
    for test in new_t:
        try:
            path = set(sut(*test))
        except:
            path = set([0])
        if path not in pathsT and path != set([0]):
            pathsT.append(path)
    
    if len(pathsT) == numPaths:
        allPaths = True
        
    #gera a próxima geração a partir dos cromossomos selecionados da atual e novos cromossomos aleatórios
    population = Selection(popsize, selected, numPaths, numParams, sut)
    
    iter+=1

tempo = time.time()-start

print("Caso de teste obtido:", new_t)
print("Percentual de cobertura alcançada: ", len(pathsT)/numPaths)
print("Número de iterações realizadas:", iter)
print("Tempo total:", tempo, "segundos")
print("Média de tempo gasto por iteração:", tempo/iter, "segundos")
