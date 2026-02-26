from flask import Flask, render_template
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
def folha_rastreamento():
    cliente = '5'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT rastreio.id AS id_atendimento, clientes.nome AS nome_cliente, atividade, tempo, humor, autonomia, observacoes, data FROM  rastreio INNER JOIN clientes on rastreio.id_cliente = clientes.id WHERE clientes.id = %s;
        """,
        (cliente)
    )
    rastreio = cursor.fetchall()
    cursor.close()
    conn.close()
    print(rastreio)
    return render_template('rastreio_atendimento.html', atividades=rastreio)

if __name__ == '__main__':
    app.run(debug=True)