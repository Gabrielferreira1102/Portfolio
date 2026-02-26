from flask import Flask, jsonify, request, session
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import date, time

#conecta ao banco
def get_db_connection():
    # Conexão ao banco de dados
    conn = psycopg2.connect(
        host="localhost",
        dbname="clinica",
        user="postgres",
        password="Pink@2004"
    )
    return conn

app = Flask(__name__)
app.secret_key = 'supersecreto'  # Para uso de sessões


# Rota de teste (GET)
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})


#cria atendimento
@app.route('/api/atendimento', methods=['POST'])
def criar_atendimento():
    dados = request.get_json()

    id_cliente = dados.get('id_cliente')
    id_terapeuta = dados.get('id_terapeuta')
    dia_semana = dados.get('dia_semana')
    horario = dados.get('horario')

    if not (id_cliente and id_terapeuta and dia_semana and horario):
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Comando SQL para inserir um novo atendimento
        insert_query = """
        INSERT INTO Atendimento (id_cliente, id_terapeuta, dia_semana, horario)
        VALUES (%s, %s, %s, %s)
        RETURNING id_atendimento;
        """
        cursor.execute(insert_query, (id_cliente, id_terapeuta, dia_semana, horario))
        atendimento_id = cursor.fetchone()['id_atendimento']

        conn.commit()
        return jsonify({"mensagem": "Atendimento criado com sucesso", "id_atendimento": atendimento_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Rota para inserir um cliente
@app.route('/api/cliente', methods=['POST'])
def criar_cliente():
    dados = request.get_json()

    # Dados obrigatórios
    cpf = dados.get('cpf')
    usuario = dados.get('usuario')
    senha = dados.get('senha')  # A senha deve ser armazenada com hash (não feito aqui por simplicidade)
    nome = dados.get('nome')

    # Dados opcionais
    responsavel = dados.get('responsavel')
    telefone = dados.get('telefone')
    email = dados.get('email')
    data_nascimento = dados.get('data_nascimento')

    # Verificação de dados obrigatórios
    if not (cpf and usuario and senha and nome):
        return jsonify({"erro": "CPF, usuário, senha e nome são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Comando SQL para inserir o cliente com novos campos
        insert_query = """
        INSERT INTO Clientes (cpf, usuario, senha, nome, responsavel, telefone, email, data_nascimento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_cliente;
        """
        cursor.execute(insert_query, (cpf, usuario, senha, nome, responsavel, telefone, email, data_nascimento))
        cliente_id = cursor.fetchone()['id']

        conn.commit()
        return jsonify({"mensagem": "Cliente criado com sucesso", "id": cliente_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Rota para inserir um cliente
@app.route('/api/terapeuta', methods=['POST'])
def criar_terapeuta():
    dados = request.get_json()
    cpf = dados.get('cpf')
    usuario = dados.get('usuario')
    senha = dados.get('senha')
    nome = dados.get('nome')
    telefone = dados.get('telefone')
    email = dados.get('email')
    data_nascimento = dados.get('data_nascimento')

    if not (cpf and usuario and senha and nome):
        return jsonify({"erro": "CPF, usuário, senha e nome são obrigatórios"}), 400

    #senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        insert_query = """
        INSERT INTO Terapeutas (cpf, usuario, senha, nome, telefone, email, data_nascimento)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_terapeuta;
        """
        cursor.execute(insert_query, (cpf, usuario, senha, nome, telefone, email, data_nascimento))
        terapeuta_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"mensagem": "Terapeuta criado com sucesso", "id_terapeuta": terapeuta_id}), 201

    except Exception as e:
        conn.rollback()
        print("Erro ao inserir terapeuta:", e)  # Essa linha ajuda a identificar o campo exato
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# Rota para login 
@app.route('/api/login', methods=['POST'])
def login():
    # Verifique se os dados estão no formato JSON
    data = request.form()
    usuario = data.get('usuario')
    senha = data.get('senha')

    if not usuario or not senha:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM clientes WHERE usuario = %s AND senha = %s",
            (usuario, senha)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['usuario'] = usuario
            return jsonify({'message': 'Login successful', 'user': usuario}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        # Erro ao conectar ou executar a consulta no banco de dados
        return jsonify({'error': str(e)}), 500


# Rota de logout 
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    return jsonify({'message': 'Logged out successfully'})


if __name__ == '__main__':
    app.run(debug=True)
