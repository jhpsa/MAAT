import random
from inspect import signature, getfullargspec
import time
import math
import copy

#definir a função SUT do MAAT como no exemplo da triangle, retornando uma lista dos nós executados

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
    #return x, y, z
    return path


#funções das etapas do MAAT

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

def GetDuplicates(_population, num, _sut):
    duplicates = []
    tDup = []
    notDup = []
    tNotDup = []
    for test in _population[num]:
        try:
            path = set(_sut(*test))
        except:
            path = set([0])
        if path not in notDup and path != set([0]):
            notDup.append(path)
            tNotDup.append(test)
        else:
            duplicates.append(path)
            tDup.append(test)
    
    return [duplicates, tDup, notDup, tNotDup]

def Recombination(_popsize, _population, _sut):
    available = [j for j in range(_popsize)]
    rnd = int(math.floor(random.randint(0,_popsize-1)/2))
    for i in range(rnd):
        pos1 = random.randint(0,len(available)-1)
        num1 = available[pos1]
        del available[pos1]
        pos2 = random.randint(0,len(available)-1)
        num2 = available[pos2]
        del available[pos2]

        dupList1 = GetDuplicates(_population, num1, _sut)
        duplicates1 = dupList1[0]
        tDup1 = dupList1[1]
        tNotDup1 = dupList1[3]

        dupList2 = GetDuplicates(_population, num2, _sut)
        duplicates2 = dupList2[0]
        tDup2 = dupList2[1]
        tNotDup2 = dupList2[3]
        
        if len(duplicates1) > 0 and len(duplicates2) > 0:
            _population[num1][_population[num1].index(tDup1[0])] = tNotDup2[0]
            _population[num2][_population[num2].index(tDup2[0])] = tNotDup1[0]

def Mutation(_population, _mutation_probability, _sut, _numParams):
    for cromossome in _population:
        dupList = GetDuplicates(_population, _population.index(cromossome), _sut)
        tDups = dupList[1]

        r = random.random()
        if r >= (1 - _mutation_probability) and len(tDups) > 0:
            num = random.randint(0,len(tDups)-1)
            param = random.randint(0, _numParams-1)
            if type(tDups[num][param]) == type([]):
                aux = []
                rnd = random.randint(0,10)
                for i in range(rnd):
                    aux.append(random.randint(0,100))
                cromossome[cromossome.index(tDups[num])][param] = aux
            elif type(tDups[num][param]) == type(""):
                if len(tDups[num][param]) > 0:
                    aux = list(tDups[num][param])
                    rnd = random.randint(0,len(aux)-1)
                    aux[rnd] = chr(random.randint(32,126))
                    aux = "".join(aux)
                    cromossome[cromossome.index(tDups[num])][param] = aux
            else:
                cromossome[cromossome.index(tDups[num])][param] = random.randint(0,100)

def MemeticPreprocess(_t_best, _sut, _cfg):
    paths = []
    for test in _t_best:
        try:
            paths.append(set(_sut(*test)))
        except:
            paths.append(set([0]))
    uncovered = []
    for p in _cfg:
        if set(p) not in paths:
            uncovered.append(p)
    if len(uncovered) > 0:
        r = random.randint(0,len(uncovered)-1)
        p_wanted = uncovered[r]
        jac = []
        for p in paths:
            inter = 0
            uni = 0
            for num in p_wanted:
                if num in p:
                    inter += 1
                    uni -= 1
            uni += len(p) + len(p_wanted)
            jac.append(inter/uni)
        h = t_best[jac.index(max(jac))]

        return [h, jac, p_wanted]
    else:
        return [None, None, None]

def q_learning(_jac, _numParams, _h, _sut, _p_wanted, _population, _popsize, _t_best):

    #guarda o conjunto de entrada atual
    current = copy.deepcopy(_h)

    #guarda a proximidade de seu caminho executado em relação ao ainda não coberto
    c_jac = max(_jac)

    #existirá um estado para cada valor de entrada do conjunto
    states = _numParams

    #guarda o estado atual
    state = 0

    i = 0

    #define se o caminho que ainda não tinha sido coberto já está coberto pelo conjunto de entrada
    isCovered = False

    maxI = 100

    #enquanto o caminho ainda não for coberto e o número máximo de iterações for realizado
    while not(isCovered) and i < maxI and [] not in current:

        #escolhe-se aleatoriamente uma ação para ser realizada no valor de entrada relativo ao estado atual
        aux = random.randint(0,7)
        
        if aux == 0:
            if type(current[state]) == type([]):
                if len(current[state]) > 1:
                    current[state][random.randint(0,len(current[state])-1)] -= 1
                else:
                    current[state][0] -= 1
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    string[rnd] = chr((ord(string[rnd])-1-26+107)%107+26)
                    string = "".join(string)
                    current[state] = string
            else:
                current[state] -= 1
        elif aux == 1:
            if type(current[state]) == type([]):
                if len(current[state]) > 1:
                    current[state][random.randint(0,len(current[state])-1)] += 1
                else:
                    current[state][0] += 1
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    string[rnd] = chr((ord(string[rnd])+1-26)%107+26)
                    string = "".join(string)
                    current[state] = string
            else:
                current[state] += 1
        elif aux == 2:
            if type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    string.insert(rnd, chr(random.randint(26,132)))
                    string = "".join(string)
                    current[state] = string
                else:
                    current[state] += chr(random.randint(26,132))
                    
            else:
                pass
        elif aux == 3:
            if type(current[state]) == type([]):
                if len(current[state]) > 1:
                    rnd = random.randint(0, len(current[state])-1)
                    current[state][rnd] = current[state][(rnd+1)%len(current[state])]
                else:
                    pass
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    string[rnd] = string[(rnd+1)%len(string)]
                    string = "".join(string)
                    current[state] = string
                else:
                    current[state] += chr(random.randint(26,132))
            else:
                if type(current[(state+1)%states]) == type([]):
                    if len(current[(state+1)%states]) > 1:
                        current[state] = current[(state+1)%states][random.randint(0,len(current[(state+1)%states])-1)]
                    else:
                        pass
                elif type(current[(state+1)%states]) == type(""):
                    if len(current[(state+1)%states]) > 0:
                        string = list(current[(state+1)%states])
                        current[state] = ord(string[random.randint(0,len(string)-1)])
                    else:
                        current[state] = 0
                else:
                    current[state] = current[(state+1)%states]
        elif aux == 4:
            if type(current[state]) == type([]):
                if len(current[state]) > 1:
                    rnd = random.randint(0, len(current[state])-1)
                    current[state][rnd] = current[state][(rnd-1+len(current[state]))%len(current[state])]
                else:
                    pass
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    string[rnd] = string[(rnd-1+len(string))%len(string)]
                    string = "".join(string)
                    current[state] = string
                else:
                    current[state] += chr(random.randint(26,132))
            else:
                if type(current[(state-1+states)%states]) == type([]):
                    if len(current[(state-1+states)%states]) > 1:
                        current[state] = current[(state-1+states)%states][random.randint(0,len(current[(state-1+states)%states])-1)]
                    else:
                        pass
                elif type(current[(state-1+states)%states]) == type(""):
                    if len(current[(state-1+states)%states]) > 0:
                        string = list(current[(state-1+states)%states])
                        current[state] = ord(string[random.randint(0,len(string)-1)])
                    else:
                        current[state] = 0
                else:
                    current[state] = current[(state-1+states)%states]
        elif aux == 5:
            if type(current[state]) == type([]):
                current[state] = []
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    del string[random.randint(0,len(string)-1)]
                    string = "".join(string)
                    current[state] = string
            else:
                current[state] = 0
        elif aux == 6:
            if type(current[state]) == type([]):
                if len(current[state]) > 1:
                    rnd = random.randint(0, len(current[state])-1)
                    num = current[state][rnd]
                    current[state][rnd] = current[state][(rnd+1)%len(current[state])]
                    current[state][(rnd+1)%len(current[state])] = num
                else:
                    pass
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    char = string[rnd]
                    string[rnd] = string[(rnd+1)%len(string)]
                    string[(rnd+1)%len(string)] = char
                    string = "".join(string)
                    current[state] = string
                else:
                    current[state] += chr(random.randint(26,132))
            else:
                if type(current[(state+1)%states]) == type([]):
                    if len(current[(state+1)%states]) > 1:
                        rnd = random.randint(0,len(current[(state+1)%states])-1)
                        num = current[state]
                        current[state] = current[(state+1)%states][rnd]
                        current[(state+1)%states][rnd] = num
                    else:
                        pass
                elif type(current[(state+1)%states]) == type(""):
                    if len(current[(state+1)%states]) > 0:
                        string = list(current[(state+1)%states])
                        rnd = random.randint(0,len(string)-1)
                        num = current[state]
                        current[state] = ord(string[rnd])
                        string[rnd] = chr(num%107+26)
                        string = "".join(string)
                        current[(state+1)%states] = string
                    else:
                        current[state] = 0
                        current[(state+1)%states] += chr(random.randint(26,132))
                else:
                    num = current[state]
                    current[state] = current[(state+1)%states]
                    current[(state+1)%states] = num
        else:
            if type(current[state]) == type([]):
                if len(current[state]) > 1:
                    rnd = random.randint(0, len(current[state])-1)
                    num = current[state][rnd]
                    current[state][rnd] = current[state][(rnd-1+len(current[state]))%len(current[state])]
                    current[state][(rnd-1+len(current[state]))%len(current[state])] = num
                else:
                    pass
            elif type(current[state]) == type(""):
                if len(current[state]) > 0:
                    string = list(current[state])
                    rnd = random.randint(0,len(string)-1)
                    char = string[rnd]
                    string[rnd] = string[(rnd-1+len(string))%len(string)]
                    string[(rnd-1+len(string))%len(string)] = char
                    string = "".join(string)
                    current[state] = string
                else:
                    current[state] += chr(random.randint(26,132))
            else:
                if type(current[(state-1+states)%states]) == type([]):
                    if len(current[(state-1+states)%states]) > 1:
                        rnd = random.randint(0,len(current[(state-1+states)%states])-1)
                        num = current[state]
                        current[state] = current[(state-1+states)%states][rnd]
                        current[(state-1+states)%states][rnd] = num
                    else:
                        pass
                elif type(current[(state-1+states)%states]) == type(""):
                    if len(current[(state-1+states)%states]) > 0:
                        string = list(current[(state-1+states)%states])
                        rnd = random.randint(0,len(string)-1)
                        num = current[state]
                        current[state] = ord(string[rnd])
                        string[rnd] = chr(num%107+26)
                        string = "".join(string)
                        current[(state-1+states)%states] = string
                    else:
                        current[state] = 0
                        current[(state-1+states)%states] += chr(random.randint(26,132))
                else:
                    num = current[state]
                    current[state] = current[(state-1+states)%states]
                    current[(state-1+states)%states] = num
        
        #checa se o caminho foi coberto após realizada a ação no conjunto de entrada
        try:
            path = _sut(*current)
        except:
            path = [0]
        if set(path) == set(_p_wanted):
            isCovered = True
        
        #calcula-se a proximidade do conjunto após realizada a ação, se for maior do que anteriormente o conjunto é atualizado
        inter = 0
        uni = 0
        for num in _p_wanted:
            if num in path:
                inter += 1
                uni -= 1
        uni += len(path) + len(_p_wanted)
        if inter/uni > c_jac:
            _h = current
            c_jac = inter/uni
        
        #escolhe-se aleatoriamente o próximo estado, ou seja, em qual valor de entrada a próxima ação será realizada
        state = random.randint(0,states-1)

        i += 1
    
    #substitui o conjunto de entrada resultante por um dos conjuntos que executam um caminho redundante no melhor cromossomo
    dupList = GetDuplicates(_population, _popsize-1, _sut)
    tDups = dupList[1]
    
    if len(tDups) > 1:
        dup = tDups[random.randint(0,len(tDups)-1)]
    else:
        dup = tDups[0]
    _t_best[_t_best.index(dup)] = _h
    _population[_popsize-1] = _t_best

def AdditionalSearch(_popsize, _population, _sut, _numPaths):
    selected = []
    notSelected = []
    for t in _population:
        r = random.random()
        if r >= 1 - (_population.index(t)+1)/_popsize:
            selected.append(t)
        else:
            notSelected.append(t)
    
    pathsS = []
    tS = []
    for t in selected:
        for test in t:
            try:
                p = set(_sut(*test))
            except:
                p = set([0])
            if p not in pathsS:
                pathsS.append(p)
                tS.append(test)
    pathsN = []
    tN = []
    for t in notSelected:
        for test in t:
            try:
                p = set(_sut(*test))
            except:
                p = set([0])
            if p not in pathsN and p not in pathsS:
                pathsN.append(p)
                tN.append(test)
    
    dupList = GetDuplicates(selected, len(selected)-1, _sut)

    tDup = dupList[1]
    tNotDup = dupList[3]

    if len(tN) + len(tNotDup) > _numPaths:

        new_t = []
        for test in tDup:
            new_t.append(tN[0])
            tN.pop(0)
        for test in tNotDup:
            new_t.append(test)
        
        selected[len(selected)-1] = new_t

        return new_t, selected
    
    else:
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

#valor mínimo de fitness para o cromossomo com maior fitness passar pela etapa memética
memetic_threshold = 0.0

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
    Recombination(popsize, population, sut)
    
    #cada cromossomo da população terá uma mesma probabilidade de ter os valores de um de seus casos de teste redundantes
    #alterado aleatoriamente
    Mutation(population, mutation_probability, sut, numParams)

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
    
    #se o valor de aptidão do melhor cromossomo inicial for maior que o valor limiar e ele ainda não possuir cobertura total
    if f_best >= memetic_threshold and f_best < 1:

        #guarda o cromossomo inicialmente com maior aptidão
        t_best = copy.deepcopy(population[popsize-1])

        #procura-se um conjunto de nós de um caminho da CFG que ainda não esteja sendo coberto pelo melhor cromossomo
        #e calcula-se o caso de teste que cobre o conjunto de nós do caminho mais próximo do ainda não coberto escolhido
        memeticList = MemeticPreprocess(t_best, sut, cfg)
        h = memeticList[0]
        jac = memeticList[1]
        p_wanted = memeticList[2]

        if h:
            
            #tentativa de alterar o caso de teste escolhido para que ele passe a cobrir o conjunto de nós ainda não coberto
            q_learning(jac, numParams, h, sut, p_wanted, population, popsize, t_best)

    #seleciona quais cromossomos serão reaproveitados para a próxima geração
    #e substitui casos de teste redundantes do melhor cromossomo inicial por casos de teste de cromossomos não selecionados
    #que cobriam um conjunto de nós de um caminho não coberto por nenhum dos cromossomos selecionados
    searchList = AdditionalSearch(popsize, population, sut, numPaths)
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
