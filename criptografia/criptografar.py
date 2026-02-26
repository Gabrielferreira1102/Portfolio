import numpy as np

tabela = {
    "A":1, "H":8, "O":15, "V":22,
    "B":2, "I":9, "P":16, "W":23 ,
    "C":3, "J":10,"Q":17, "X":24 ,"D":4,
    "K":11,"R":18,"Y":25 ,"E":5,
    "L":12,"S":19,"Z":26, "F":6, "M":13,
    "T":20,"*":0 ,"G":7,  "N":14,"U":21}

lista_final = []
lista_convertida = []

palavra = input("Digite uma palavra de 6 digitos: ")
palavra_maiuscula = palavra.upper()
converte_matriz = list(palavra_maiuscula)
print("Sua palavra é:",palavra)
print()
def conversor():
    for x in converte_matriz:
        lista_convertida.append(tabela[x]) 

def organiza(matriz,chave):
    lista_soma = []
    lista_total = []
    linha_matriz = 0
    coluna_matriz = 0

    linha_chave = 0
    coluna_chave = 0

    while True:
        lista_soma.append(matriz[linha_matriz][coluna_matriz] * chave[linha_chave][coluna_chave])
        if linha_chave == 2 and coluna_chave ==2 and coluna_matriz == 1 and linha_matriz == 2:
            if len(lista_soma) != 0:
                lista_total.append(sum(lista_soma))
            return lista_total
        
        if len(lista_soma) == 3:
            lista_total.append(sum(lista_soma))
            lista_soma = []
            
        if coluna_matriz == 1 and linha_matriz == 2:
            coluna_matriz =0
            linha_matriz = 0
            linha_chave+=1
            coluna_chave =0

        elif linha_matriz == 2:
            coluna_chave = 0
            linha_matriz = 0
            coluna_matriz+=1
        else:
            coluna_chave+=1
            linha_matriz+=1

conversor()

matriz = np.array([[lista_convertida[0], lista_convertida[3],],
                   [lista_convertida[1], lista_convertida[4],],
                   [lista_convertida[2], lista_convertida[5],]])
print("Palavra convertida:")
print(matriz)
print()
chave = np.array([[1,0,1,],
                  [1,1,1,],
                  [0, 2,-1,]])

invertido = np.linalg.inv(chave)
matriz = organiza(matriz,chave)

matriz = np.array([[matriz[0], matriz[1],],
                   [matriz[2], matriz[3],],
                   [matriz[4], matriz[5],]])
print("Palavra criptografada: ")
print(matriz)
