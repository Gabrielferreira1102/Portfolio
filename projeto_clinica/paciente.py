from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from datetime import datetime

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
def horarios_paciente():
    horarios_paciente = []
    nome_cliente = "5"
    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta para buscar horários do cliente
    cursor.execute(
        """
        SELECT 
            atendimento.id AS id_atendimento,
            clientes.nome AS nome_cliente,
            terapeutas.nome AS nome_terapeuta,
            atendimento.dia_semana,
            atendimento.horario,
            atendimento.data,
            atendimento.descricao    
        FROM atendimento
        INNER JOIN clientes ON atendimento.id_cliente = clientes.id
        INNER JOIN terapeutas ON atendimento.id_terapeuta = terapeutas.id
        WHERE clientes.id = %s;
        """,
        (nome_cliente)
    )
    resultados = cursor.fetchall()
    horarios_paciente = [
        resultado[:5] + (resultado[5].strftime("%d/%m/%Y") if resultado[5] else None,) + resultado[6:]
        for resultado in resultados
    ]

    cursor.close()
    conn.close()

    return render_template('horario_paciente2.html', nome_cliente=nome_cliente, horarios_paciente=horarios_paciente)

if __name__ == '__main__':
    app.run(debug=True)
