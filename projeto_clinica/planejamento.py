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
        SELECT 
            planejamento.id,
            clientes.nome AS nome_cliente,
            area,
            momento_atual,
            objetivo,
            estrategia,
            data
        FROM 
            planejamento
        INNER JOIN 
            clientes on planejamento.id_cliente = clientes.id
        WHERE 
            clientes.id = %s;
        """,
        (cliente)
    )
    planejamentos = cursor.fetchall()
    cursor.close()
    conn.close()
    print(planejamentos)
    return render_template('planejamento.html', planejamentos=planejamentos)

if __name__ == '__main__':
    app.run(debug=True)