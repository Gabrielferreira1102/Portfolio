#Dado um array de inteiros nums e um número inteiro alvo‚retorno índices dos dois números tais que somam alvo.O.

#Você pode supor que cada entrada teria exatamente uma solução, e você não pode usar o mesmo elemento duas vezes.

#Pode retornar a resposta em qualquer ordem.

#para testar no site apague "nums = [0,4,3,0]" e "target = 0" o site vai te passar os valores
nums = [0,4,3,0]
target = 0

i = 0
contador1 = 0
contador2 = 1
total = 0
limite = len(nums)- 1

while i < 10:
    total = nums[contador1] + nums[contador2]
    if total == target:
        break
    elif contador2 == limite:
        contador1 += 1
        contador2 = contador1 + 1
    else:
        contador2 += 1
print(contador1,contador2)
#adicione "return" no lugar do print para testar no site
