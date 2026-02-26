import psycopg2

#aqui é só prencher com o seu banco
conexao = psycopg2.connect(
    host="",
    dbname="",
    user="",
    password="",
    port=1111, #numero ficticio para o exemplo
    
)

#conexao.autocommit = True
#numero = input("id: ")
#nome_2 = input("diga seu nome: ")
#servicos = input("diga quantidade de servicos: ")
#cursos = conexao.cursor()

#comando = f""" INSERT INTO pessoa(id, nome, servico)
            #values ({numero},'{nome_2}',{servicos})"""

#cursos.execute(comando)
