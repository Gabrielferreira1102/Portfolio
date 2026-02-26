from flask import Flask, render_template
import pandas as pd
import psycopg2

def get_db_connection():
    conexao = psycopg2.connect(
        host="localhost",
        dbname="clinica",
        user="postgres",
        password="Pink@2004"
    )
    return conexao

app = Flask(__name__)

@app.route('/')
def mostrar_planilha():
    # Exemplo de DataFrame
    dados = {
        'segunda': [None]*12,
        'terça': [None]*12,
        'quarta': [None]*12,
        'quinta': [None]*12,
        'sexta': [None]*12,
    }
    indices = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00']
    df = pd.DataFrame(dados, index=indices)
    df_formatado = df.fillna('')

    cliente = 6  # ID do cliente a ser pesquisado
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            clientes.nome AS nome_cliente, 
            terapeutas.nome AS nome_terapeuta, 
            atendimento.dia_semana, 
            atendimento.horario 
        FROM atendimento 
        INNER JOIN clientes ON atendimento.id_cliente = clientes.id 
        INNER JOIN terapeutas ON atendimento.id_terapeuta = terapeutas.id 
        WHERE clientes.id = %s;
        """,
        (cliente,)
    )
    horarios = cursor.fetchall()
    cursor.close()
    conn.close()

    # Atualiza o DataFrame com os dados do banco
    for horario in horarios:
        nome_terapeuta = horario[1]
        dia_semana = horario[2].lower()
        hora = horario[3]
        if dia_semana in df_formatado.columns and hora in df_formatado.index:
            df_formatado.loc[hora, dia_semana] = nome_terapeuta

    # Converte o DataFrame para HTML sem classes automáticas
    tabela_html = df_formatado.to_html(border=0, index=True, header=True)

    return render_template('teste_tabela.html', tabela=tabela_html)

if __name__ == '__main__':
    app.run(debug=True)