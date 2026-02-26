import numpy as np

tabela2 = {
    1: "A", 8:"H",  15:"O", 22:"V",  
    2: "B", 9:"I",  16:"P", 23:"W",
    3: "C", 10:"J", 17:"Q", 24:"X",4:"D",
    11:"K", 18:"R", 25:"Y", 5:"E",            
    12:"L", 19:"S", 26:"Z", 6:"F", 13:"M",
    20:"T", 0 :"*", 7:"G",  14:"N",21:"U"}

lista_final = []
tabelado = []
lista_convertida = []

input_crip = input("Escreva uma matriz de 6 separando cada numero com virgula: ")
lista_crip = input_crip.split(",")
print()
def conversor2():
    for x in lista_final:
        tabelado.append(tabela2[x]) 

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

chave = np.array([[1,0,1,],
                  [1,1,1,],
                  [0, 2,-1,]])

invertido = np.linalg.inv(chave)



for x in lista_crip:
    lista_convertida.append(int(x))

matriz_crip = np.array([[lista_convertida[0], lista_convertida[1],],
                        [lista_convertida[2], lista_convertida[3],],
                        [lista_convertida[4], lista_convertida[5],]])



descriptografado = organiza(matriz_crip,invertido)
palavra_descrip = np.array([[descriptografado[0], descriptografado[1],],
                        [descriptografado[2], descriptografado[3],],
                        [descriptografado[4], descriptografado[5],]])
print("Palavra convertida:")
print(palavra_descrip)
print()
for x in descriptografado:
    lista_final.append(int(x))

conversor2()
palavra_organizada = tabelado[0],tabelado[2],tabelado[4],tabelado[1],tabelado[3],tabelado[5]
resultado = ''.join(palavra_organizada)
print("Palavra descriptografada:",resultado)