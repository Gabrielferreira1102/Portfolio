from flask import Flask, render_template, request, redirect, url_for, session
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
app.secret_key = 'chave_secreta_para_sessao'  # Substitua por uma chave segura

@app.route('/buscar_horario', methods=['GET', 'POST'])
def buscar_horario():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        if 'buscar_cliente' in request.form:
            # Atualizar a busca por cliente
            nome_cliente = request.form.get('nome_cliente')
            session['busca_cliente_nome'] = nome_cliente
            cursor.execute(
                """
                SELECT 
                    atendimento.id AS id_atendimento,
                    clientes.nome AS nome_cliente,
                    funcionarios.nome AS nome_terapeuta,
                    atendimento.dia_semana,
                    atendimento.horario,
                    atendimento.data,
                    atendimento.descricao    
                FROM atendimento
                INNER JOIN clientes ON atendimento.id_cliente = clientes.id
                INNER JOIN funcionarios ON atendimento.id_terapeuta = funcionarios.id
                WHERE clientes.nome ILIKE %s;
                """,
                (f"%{nome_cliente}%",)
            )
            resultados_cliente = cursor.fetchall()
            session['busca_cliente_resultados'] = [
                resultado[:5] + (resultado[5].strftime("%d/%m/%Y") if resultado[5] else None,) + resultado[6:]
                for resultado in resultados_cliente
            ]

        if 'buscar_terapeuta' in request.form:
            # Atualizar a busca por terapeuta
            nome_terapeuta = request.form.get('nome_terapeuta')
            session['busca_terapeuta_nome'] = nome_terapeuta
            cursor.execute(
                """
                SELECT 
                    atendimento.id AS id_atendimento,
                    funcionarios.nome AS nome_terapeuta,
                    clientes.nome AS nome_cliente,
                    atendimento.dia_semana,
                    atendimento.horario,
                    atendimento.data,
                    atendimento.descricao    
                FROM atendimento
                INNER JOIN funcionarios ON atendimento.id_terapeuta = funcionarios.id
                INNER JOIN clientes ON atendimento.id_cliente = clientes.id
                WHERE funcionarios.nome ILIKE %s;
                """,
                (f"%{nome_terapeuta}%",)
            )
            resultados_terapeuta = cursor.fetchall()
            session['busca_terapeuta_resultados'] = [
                resultado[:5] + (resultado[5].strftime("%d/%m/%Y") if resultado[5] else None,) + resultado[6:]
                for resultado in resultados_terapeuta
            ]

        cursor.close()
        conn.close()

    # Recuperar os resultados da sessão
    busca_cliente = {
        "nome": session.get('busca_cliente_nome', ""),
        "resultados": session.get('busca_cliente_resultados', [])
    }
    busca_terapeuta = {
        "nome": session.get('busca_terapeuta_nome', ""),
        "resultados": session.get('busca_terapeuta_resultados', [])
    }

    return render_template('criar_horarios.html', 
                           busca_cliente=busca_cliente, 
                           busca_terapeuta=busca_terapeuta)

@app.route('/criar_horario', methods=['POST'])
def criar_horario():
    cliente = request.form.get('cliente')
    terapeuta = request.form.get('terapeuta')
    dia_semana = request.form.get('dia_semana')
    horario = request.form.get('horario')
    data = request.form.get('data')
    descricao = request.form.get('descricao')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO atendimento (id_cliente, id_terapeuta, dia_semana, horario, data, descricao)
        VALUES ((SELECT id FROM clientes WHERE nome = %s),
                (SELECT id FROM funcionarios WHERE nome = %s),
                %s, %s, %s, %s);
        """,
        (cliente, terapeuta, dia_semana, horario, data, descricao)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('buscar_horario'))

if __name__ == '__main__':
    app.run(debug=True)
