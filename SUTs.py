#códigos utilizados como SUT nos experimentos modificados para retornarem o conjunto de nós executados
#e suas respectivas listas de conjuntos de nós dos caminhos da CFG 

def triangle(x: int,y: int,z: int):
    path = []
    path.append(3)
    if x != y and x != z and y != z:
        path.append(4)
        #print("scalene")
    else:
        path.append(6)
        if x == y and y == z:
            path.append(7)
            #print("equilateral")
        else:
            path.append(9)
            #print("isosceles")
    path.append(5)
    return path

cfg = [[3,4,5],[3,5,6,7],[3,5,6,9]]


def multiplos(l: list,n: int):
    path = []
    i=0
    divn=[]
    while i<len(l):
        if l[i]%n==0:
            divn.append(l[i])
            path.append(1)
        else:
            path.append(2)
        i+=1
    path.append(3)
    #return divn
    return path

cfg = [[1,3],[2,3],[3],[1,2,3]]


def qtd_divisores(n: int):
    path = []
    total = 0
    path.append(1)
    for contador in range(1,n+1):
        path.append(2)
        if n%contador == 0:
            total += 1
            path.append(3)
        else:
            path.append(4)
    path.append(5)
    #return total
    return path

cfg = [[1,5],[1,2,3,5],[1,2,3,4,5]]


def primo(n: int):
    path =[]
    if n<=1:
        path.append(1)
        #return False
        return path
    elif n==2:
        path.append(2)
        #return True
        return path
    for contador in range(2,n):
        if n%contador == 0:
            path.append(3)
            #return False
            return path
        else:
            path.append(4)
    return path
    #return True

cfg = [[1], [2], [3], [4], [3,4]]


def repetidos(l: list):
    path = []
    i=1
    cont=0
    path.append(1)
    while i<len(l):
        path.append(2)
        if l[i]==l[i-1]:
            cont+=1
            path.append(3)
        else:
            path.append(4)
        i+=1
    path.append(5)
    return path
    #return cont

cfg = [[1,5], [1,2,3,5], [1,2,4,5], [1,2,3,4,5]]   


def faltante1(pecas: list):
    path = []
    lp = pecas[:]
    lp.sort()
    contador = 0
    peca = -1
    path.append(1)
    while (contador < len(lp)):
        path.append(2)
        if (lp[contador] == (contador + 1)):
            contador = contador + 1
            path.append(3)
        else:
            peca = contador + 1
            contador = len(lp)
            path.append(4)
    if (peca == -1):
        peca = len(lp) + 1
        path.append(5)
    else:
        path.append(6)
    path.append(7)
    return path
    #return peca

cfg = [[1,5,7], [1,2,3,5,7], [1,2,4,6,7], [1,2,3,4,6,7]]


def uppCons(frase: str):
    path = []
    frase_tratada = ""
    i=0
    path.append(1)
    while i<len(frase):
        caractere=frase[i]
        if caractere in "bcdfghjklmnpqrstwxyzç":
            caractere = str.upper(caractere)
            path.append(2)
        frase_tratada = frase_tratada + caractere
        i=i+1
        path.append(3)
    return path
    #return frase_tratada

cfg = [[1], [1,3], [1,2,3]]


def freq_palavras(frase: str):
    path = []
    dic = {}
    lista = frase.split()
    path.append(1)
    for palavra in lista:
        if palavra in dic:
            dic[palavra] += 1
            path.append(2)
        else:
            dic[palavra] = 1
            path.append(3)
    #return dic
    return path

cfg = [[1],[1,3],[1,2,3]]
