from flask import Flask, render_template, request, flash, session, url_for, redirect, jsonify, Response
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
import matplotlib.pyplot as plt
import io
from dateutil.relativedelta import relativedelta
import pandas as pd
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)

def get_db_connection():
    conexao = psycopg2.connect(
    #aqui é só prencher com o seu banco
    host="",
    dbname="",
    user="",
    password=""
    )
    return conexao

app = Flask(__name__)
app.secret_key = 'supersecreto'  # Necessário para usar mensagens flash e sessão

busca_cliente = {"nome": "", "resultados": []}
busca_terapeuta = {"nome": "", "resultados": []}

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Define a rota de login padrão

def get_consultas():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT dia_semana FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') and dia_semana = 'Segunda'")
    dados_segunda  = cursor.fetchall()
    cursor.execute("SELECT dia_semana FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') and dia_semana = 'Terça'")
    dados_terca  = cursor.fetchall()
    cursor.execute("SELECT dia_semana FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') and dia_semana = 'Quarta'")
    dados_quarta  = cursor.fetchall()
    cursor.execute("SELECT dia_semana FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') and dia_semana = 'Quinta'")
    dados_quinta  = cursor.fetchall()
    cursor.execute("SELECT dia_semana FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') and dia_semana = 'Sexta'")
    dados_sexta  = cursor.fetchall()
    cursor.close()
    conn.close()

    segunda = len(dados_segunda)
    terca = len(dados_terca)
    quarta = len(dados_quarta)
    quinta = len(dados_quinta)
    sexta = len(dados_sexta)
    data = {
        "dia": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
        "consultas": [segunda, terca, quarta, quinta, sexta]  # Quantidade de consultas por dia
    }
    return pd.DataFrame(data)


class User(UserMixin):
    def __init__(self, user_id, role):
        self.id = user_id   # Atributo usado pelo Flask-Login (string ou int)
        self.role = role    # 'paciente', 'terapeuta', 'secretaria', 'adm'

@login_manager.user_loader
def load_user(user_id):
    """
    O Flask-Login chama esta função para recarregar o usuário a cada requisição,
    usando o 'user_id' armazenado na sessão (que vem de User.id).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Busca o usuário pelo ID na tabela funcionarios
        cursor.execute("SELECT id, funcao FROM funcionarios WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            # row[0] = id, row[1] = funcao
            return User(user_id=str(row[0]), role=row[1])
        else:
            return None
    except:
        return None


def dados_gragico_defaut():

    conn = get_db_connection()
    cursor = conn.cursor()
    # Buscar dados do paciente
    cursor.execute("SELECT * FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM');")
    dados = cursor.fetchall()

    cursor.close()
    conn.close()
    return dados


@app.route("/")
def index():
    return render_template("index.html")


#parte dedicada para o login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se for GET, apenas renderiza a página de login
    if request.method == 'GET':
        return render_template('login.html')
    """
    - GET: Renderiza o template de login.
    - POST: Verifica email/senha no banco de dados e, se válido,
      faz o login do usuário (login_user) e redireciona para o dashboard
      específico de acordo com a função (role).
    """
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            flash("Preencha todos os campos!")
            return render_template('login.html')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verifica na tabela funcionarios
            cursor.execute("""
                SELECT id, funcao
                FROM funcionarios
                WHERE email = %s AND senha = %s
            """, (email, senha))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            if row:
                user_id = str(row[0])
                user_funcao = row[1]  # 'paciente', 'terapeuta', 'secretaria', 'adm'
                print(user_id )
                print(user_funcao )
                # Instancia o usuário
                user_instance = User(user_id=user_id, role=user_funcao)
                # Registra o usuário na sessão
                login_user(user_instance)

                # Redireciona de acordo com a função
                if user_funcao == 'paciente':
                    return redirect(url_for('dashboard_paciente'))
                elif user_funcao == 'terapeuta':
                    return redirect(url_for('menu_adm'))
                elif user_funcao == 'secretario':
                    return redirect(url_for('menu_adm'))
                elif user_funcao == 'adm':
                    return redirect(url_for('menu_adm'))
                else:
                    flash("Função de usuário desconhecida.")
                    return render_template('login.html')
            else:
                flash("Credenciais inválidas.")
                return render_template('login.html')

        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            flash("Erro no servidor. Tente novamente mais tarde.")
            return render_template('login.html')

    

#parte dedicada para as paginar do paciente
@app.route('/paciente/<int:id_cliente>')
def paciente(id_cliente):
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('login'))
    try:
        # Abrir conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta para buscar horários do cliente
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
            WHERE clientes.id = %s;
            """,
            (id_cliente,)  # Passando id_cliente como uma tupla
        )
        resultados = cursor.fetchall()
        # Formatar resultados para exibição
        horarios_paciente = [
            resultado[:5] + (resultado[5].strftime("%d/%m/%Y") if resultado[5] else None,) + resultado[6:]
            for resultado in resultados
        ]

        # Fechar conexão com o banco
        cursor.close()
        conn.close()

        # Renderizar a página com os dados do cliente
        return render_template('paciente.html', horarios_paciente=horarios_paciente)

    except Exception as e:
        print(f"Erro ao buscar dados do paciente: {e}")
        flash("Erro ao carregar dados do paciente.")
        return redirect(url_for('index'))


#tela inicial de adm com todas as opçoes
@app.route('/menu_adm')
def menu_adm():
    # Verifica se o usuário está autenticado
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('login'))
    
    return render_template('menu_adm.html')




@app.route('/criar_horario', methods=['GET', 'POST'])
def criar_horario():
    """
    Página para criar um novo horário de atendimento.
    """
    if request.method == 'GET':
        # Garante que `busca_cliente` e `busca_terapeuta` sejam passados mesmo se vazios
        busca_cliente = {"nome": "", "resultados": []}
        busca_terapeuta = {"nome": "", "resultados": []}
        return render_template('criar_horario.html', busca_cliente=busca_cliente, busca_terapeuta=busca_terapeuta)

    if request.method == 'POST':
        try:
            # Obtendo os dados do formulário
            paciente = request.form.get('paciente')
            terapeuta = request.form.get('terapeuta')
            dia_semana = request.form.get('dia_semana')
            horario = request.form.get('horario')
            data = request.form.get('data')
            descricao = request.form.get('descricao')
            sala = request.form.get('sala')
            presenca = request.form.get('presenca')

            # Convertendo presença para booleano
            presenca = True if presenca == "on" else False

            # Verifica se todos os campos foram preenchidos
            if not all([paciente, terapeuta, dia_semana, horario, data, descricao, sala]):
                flash("Erro: Todos os campos são obrigatórios!", "error")
                return redirect(url_for('criar_horario'))

            conn = get_db_connection()
            cursor = conn.cursor()

            # Verifica se o paciente e terapeuta existem no banco de dados
            cursor.execute("SELECT id FROM clientes WHERE nome = %s", (paciente,))
            paciente_id = cursor.fetchone()
            cursor.execute("SELECT id FROM funcionarios WHERE nome = %s", (terapeuta,))
            terapeuta_id = cursor.fetchone()

            if not paciente_id or not terapeuta_id:
                flash("Erro: Paciente ou terapeuta não encontrado!", "error")
                return redirect(url_for('criar_horario'))

            # Inserindo o novo atendimento no banco
            query = """
                INSERT INTO atendimento (id_cliente, id_terapeuta, dia_semana, horario, data, descricao, sala, presenca)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (paciente_id[0], terapeuta_id[0], dia_semana, horario, data, descricao, sala, presenca))
            conn.commit()

            cursor.close()
            conn.close()

            flash("Horário criado com sucesso!", "success")
            return redirect(url_for('ver_horarios'))

        except Exception as e:
            print(f"Erro ao criar atendimento: {e}")
            flash("Erro ao criar atendimento.", "error")
            return redirect(url_for('criar_horario'))


@app.route('/ver_horarios_terapeuta')
def buscar_horario_terapeuta():
    """
    Busca os horários agendados no banco de dados.
    Permite filtrar pelo nome do paciente ou terapeuta.
    """
    usuario_id = current_user.id 
    conn = get_db_connection()
    cursor = conn.cursor()
    print(usuario_id)
    query = """
        SELECT * 
        FROM atendimento 
        JOIN clientes ON atendimento.id_cliente = clientes.id
        where id_terapeuta = %s and DATE(data_consulta) >= CURRENT_DATE - INTERVAL '1 day';

    """

    cursor.execute(query, (usuario_id))
    horarios = cursor.fetchall()
    print(horarios)
    cursor.close()
    conn.close()

    return render_template('ver_horarios_terapeuta.html', horarios=horarios)


@app.route('/ver_horarios')
def buscar_horario():
    """
    Busca os horários agendados no banco de dados.
    Permite filtrar pelo nome do paciente ou terapeuta.
    """
    termo_busca = request.args.get('search', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            a.id, c.nome AS paciente, f.nome AS terapeuta, 
            a.dia_semana, a.horario, a.data_consulta, a.descricao, a.sala, a.presenca
        FROM atendimento a
        JOIN clientes c ON a.id_cliente = c.id
        JOIN funcionarios f ON a.id_terapeuta = f.id
        WHERE c.nome ILIKE %s OR f.nome ILIKE %s
        ORDER BY a.data_consulta, a.horario;
    """

    cursor.execute(query, (f"%{termo_busca}%", f"%{termo_busca}%"))
    horarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('ver_horarios.html', horarios=horarios, termo_busca=termo_busca)


@app.route('/alterar_horario', methods=['POST'])
def alterar_horario():
    """
    Atualiza um atendimento existente no banco de dados.
    """
    try:
        # Obtendo os dados do formulário
        id_atendimento = request.form.get('id')
        paciente = request.form.get('paciente')
        terapeuta = request.form.get('terapeuta')
        dia_semana = request.form.get('dia_semana')
        horario = request.form.get('horario')
        data = request.form.get('data')
        descricao = request.form.get('descricao')
        sala = request.form.get('sala')
        presenca = request.form.get('presenca')

        # Convertendo presença para booleano
        presenca = True if presenca == "on" else False

        # Validação dos dados recebidos
        if not all([id_atendimento, paciente, terapeuta, dia_semana, horario, data, descricao, sala]):
            flash("Erro: Todos os campos são obrigatórios.", "error")
            return redirect(url_for('buscar_horario'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query SQL para atualizar o atendimento
        query = """
            UPDATE atendimento
            SET id_cliente = (SELECT id FROM clientes WHERE nome = %s),
                id_terapeuta = (SELECT id FROM funcionarios WHERE nome = %s),
                dia_semana = %s,
                horario = %s,
                data = %s,
                descricao = %s,
                sala = %s,
                presenca = %s
            WHERE id = %s;
        """

        cursor.execute(query, (paciente, terapeuta, dia_semana, horario, data, descricao, sala, presenca, id_atendimento))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Horário atualizado com sucesso!", "success")
        return redirect(url_for('buscar_horario'))

    except Exception as e:
        print(f"Erro ao atualizar atendimento: {e}")
        flash("Erro ao atualizar atendimento.", "error")
        return redirect(url_for('buscar_horario'))

    
# 🔹 ROTA PARA VER PACIENTES
@app.route('/ver_pacientes')
def ver_pacientes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome ASC")
        pacientes = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar pacientes: {e}")
        flash("Erro ao carregar a lista de pacientes.", "error")
        pacientes = []

    return render_template('ver_paciente.html', pacientes=pacientes)

# 🔹 ROTA PARA CADASTRAR PACIENTE
@app.route('/cadastrar_paciente', methods=['GET', 'POST'])
def cadastrar_paciente():
    if request.method == 'POST':
        try:
            usuario = request.form['usuario']
            nome = request.form['nome']
            cpf = request.form['cpf']
            email = request.form['email']
            telefone = request.form['telefone']
            responsavel = request.form.get('responsavel', '')
            senha = request.form['senha']
            confirma_senha = request.form['confirma_senha']
            data_nascimento = request.form['data_nascimento']

            if not all([nome,usuario, cpf, email, telefone, senha, confirma_senha, data_nascimento]):
                flash("Preencha todos os campos obrigatórios!", "error")
                return redirect(url_for('cadastrar_paciente'))

            if senha != confirma_senha:
                flash("As senhas não coincidem!", "error")
                return redirect(url_for('cadastrar_paciente'))

            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            INSERT INTO clientes (cpf, usuario, senha, nome, responsavel, telefone, email, data_nascimento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (cpf, usuario, senha, nome, responsavel, telefone, email, data_nascimento))
            conn.commit()
            cursor.close()
            conn.close()

            flash("Paciente cadastrado com sucesso!", "success")
            return redirect(url_for('ver_pacientes'))

        except Exception as e:
            print(f"Erro ao cadastrar paciente: {e}")
            flash("Erro ao cadastrar paciente. Tente novamente.", "error")
            return redirect(url_for('cadastrar_paciente'))

    return render_template('cadastrar_paciente.html')

# 🔹 ROTA PARA ALTERAR PACIENTE
@app.route('/alterar_paciente', methods=['POST'])
def alterar_paciente():
    try:
        paciente_id = request.form['id']
        nome = request.form['nome']
        responsavel = request.form['responsavel']
        telefone = request.form['telefone']
        email = request.form['email']
        data_nascimento = request.form['data_nascimento']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE clientes
            SET usuario = %s, responsavel = %s, telefone = %s, email = %s, data_nascimento = %s
            WHERE id = %s;
        """
        cursor.execute(query, (nome, responsavel, telefone, email, data_nascimento, paciente_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Paciente atualizado com sucesso!", "success")
        return redirect(url_for('ver_pacientes'))

    except Exception as e:
        print(f"Erro ao atualizar paciente: {e}")
        flash("Erro ao atualizar paciente.", "error")
        return redirect(url_for('ver_pacientes'))

#cadastrar cliente
@app.route('/cadastrar_funcionario', methods=['GET', 'POST'])
def cadastrar_funcionario():
    if request.method == 'GET':
        # Renderiza a página com o formulário para criar cliente
        return render_template('cadastrar_funcionario.html')

    if request.method == 'POST':
        try:
            # Obter os dados da requisição
            dados = request.get_json()

            # Dados obrigatórios
            cpf = dados.get('cpf')
            email = dados.get('email')
            senha = dados.get('senha')
            nome = dados.get('nome')

            # Dados opcionais
            telefone = dados.get('telefone', None)
            data_nascimento = dados.get('data_nascimento', None)
            funcao = dados.get('funcao', None)


            # Verificação de dados obrigatórios
            if not all([cpf, email, senha, nome]):
                flash("CPF, usuário, senha e nome são obrigatórios!")
                return render_template('criar_cliente.html'), 400

            # Conexão com o banco de dados
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Inserir dados no banco de dados
            insert_query = """
            INSERT INTO funcionarios (cpf, senha, nome, telefone, email, data_nascimento, funcao)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            cursor.execute(insert_query, (cpf, senha, nome, telefone, email, data_nascimento, funcao))
            cliente_id = cursor.fetchone()['id']

            conn.commit()

            # Retorno de sucesso
            flash("Cliente criado com sucesso!")
            return redirect(url_for('index'))

        except Exception as e:
            # Em caso de erro, rollback e retorno de erro
            print(f"Erro ao criar cliente: {e}")
            conn.rollback()
            flash("Erro ao criar cliente. Por favor, tente novamente.")
            return render_template('criar_cliente.html'), 500

        finally:
            # Fechar conexão com o banco de dados
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


#tela para ver todos horarios
@app.route('/ver_funcionarios')
def ver_funcionarios():
    # Verifica se o usuário está autenticado
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('login'))
    
    # Abrir conexão com o banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta para buscar funcionários
    cursor.execute("SELECT * FROM funcionarios")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Formatar as datas no índice 6
    funcionarios = [
        list(funcionario[:6]) + 
        [funcionario[6].strftime('%d/%m/%Y') if funcionario[6] else "Data inválida"] + 
        list(funcionario[7:])
        for funcionario in resultados
    ]
    
    return render_template('ver_funcionarios.html', funcionarios=funcionarios)


@app.route('/alterar_funcionario', methods=['POST'])
def alterar_funcionario():
    """
    Atualiza os dados de um funcionário no banco de dados.
    """
    try:
        funcionario_id = request.form.get('id')
        nome = request.form.get('nome')
        funcao = request.form.get('funcao')
        telefone = request.form.get('telefone')
        cpf = request.form.get('cpf')
        email = request.form.get('email')
        data_nascimento = request.form.get('data_nascimento')

        # Verificar se todos os campos foram preenchidos
        if not all([funcionario_id, nome, funcao, telefone, cpf, email, data_nascimento]):
            flash("Erro: Todos os campos obrigatórios devem ser preenchidos!", "error")
            return redirect(url_for('ver_funcionarios'))  # Redireciona de volta para a lista

        # Conectar ao banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        # Atualizar os dados do funcionário
        query = """
            UPDATE funcionarios
            SET nome = %s,
                funcao = %s,
                telefone = %s,
                cpf = %s,
                email = %s,
                data_nascimento = %s
            WHERE id = %s;
        """
        cursor.execute(query, (nome, funcao, telefone, cpf, email, data_nascimento, funcionario_id))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Funcionário atualizado com sucesso!", "success")
        return redirect(url_for('ver_funcionarios'))  # Volta para a página de funcionários

    except Exception as e:
        print(f"Erro ao atualizar funcionário: {e}")
        flash("Erro ao atualizar funcionário.", "error")
        return redirect(url_for('ver_funcionarios'))


# Criar rastreamento para um paciente específico
@app.route('/criar_rastreio/<int:id_cliente>', methods=['GET', 'POST'])
def criar_rastreio(id_cliente):
    """
    Página para criação de um rastreamento de um paciente específico.
    """
    if request.method == 'POST':
        try:
            atividade = request.form.get('atividade')
            tempo = request.form.get('tempo')
            humor = request.form.get('humor')
            autonomia = request.form.get('autonomia')
            observacoes = request.form.get('observacoes')
            data = request.form.get('data')

            if not all([atividade, tempo, humor, autonomia, data]):
                flash("Preencha todos os campos obrigatórios!", "error")
                return redirect(url_for('criar_rastreio', id_cliente=id_cliente))

            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO rastreio (id_cliente, atividade, tempo, humor, autonomia, observacoes, data)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (id_cliente, atividade, tempo, humor, autonomia, observacoes, data))
            conn.commit()

            cursor.close()
            conn.close()

            flash("Rastreamento cadastrado com sucesso!", "success")
            return redirect(url_for('rastreio', id_cliente=id_cliente))

        except Exception as e:
            print(f"Erro ao cadastrar rastreamento: {e}")
            flash("Erro ao cadastrar rastreamento.", "error")
            return redirect(url_for('criar_rastreio', id_cliente=id_cliente))

    return render_template('criar_rastreio.html', id_cliente=id_cliente)


@app.route('/rastreio/<int:id_cliente>')
def rastreio(id_cliente):
    """
    Exibe o rastreio de um paciente com base no ID do cliente.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rastreio WHERE id_cliente = %s ORDER BY data DESC", (id_cliente,))
        rastreios = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar rastreio: {e}")
        flash("Erro ao carregar os dados de rastreio.", "error")
        rastreios = []

    return render_template('rastreio.html', rastreios=rastreios, id_cliente=id_cliente)


@app.route('/criar_planejamento/<int:id_cliente>', methods=['GET', 'POST'])
def criar_planejamento(id_cliente):
    """
    Página para adicionar um novo planejamento para um paciente específico.
    """
    if request.method == 'POST':
        try:
            area = request.form.get('area')
            momento_atual = request.form.get('momento_atual')
            objetivo = request.form.get('objetivo')
            estrategia = request.form.get('estrategia')
            data = request.form.get('data')

            if not all([area, momento_atual, objetivo, estrategia, data]):
                flash("Preencha todos os campos obrigatórios!", "error")
                return redirect(url_for('criar_planejamento', id_cliente=id_cliente))

            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO planejamento (id_cliente, area, momento_atual, objetivo, estrategia, data)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (id_cliente, area, momento_atual, objetivo, estrategia, data))
            conn.commit()

            cursor.close()
            conn.close()

            flash("Planejamento cadastrado com sucesso!", "success")
            return redirect(url_for('planejamento', id_cliente=id_cliente))

        except Exception as e:
            print(f"Erro ao cadastrar planejamento: {e}")
            flash("Erro ao cadastrar planejamento.", "error")
            return redirect(url_for('criar_planejamento', id_cliente=id_cliente))

    return render_template('criar_planejamento.html', id_cliente=id_cliente)


@app.route('/planejamento/<int:id_cliente>')
def planejamento(id_cliente):
    """
    Página que exibe os planejamentos de um paciente específico.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Buscar os planejamentos do paciente
        query = """
        SELECT area, momento_atual, objetivo, estrategia, data
        FROM planejamento WHERE id_cliente = %s ORDER BY data DESC;
        """
        cursor.execute(query, (id_cliente,))
        planejamentos = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('planejamento.html', planejamentos=planejamentos, id_cliente=id_cliente)

    except Exception as e:
        print(f"Erro ao carregar planejamentos: {e}")
        return "Erro ao carregar planejamentos.", 500


@app.route('/relatorio')
def relatorio():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM')")
    dados_total_consultas  = cursor.fetchall()
    cursor.execute("SELECT presenca FROM atendimento WHERE TO_CHAR(data, 'YYYY-MM') = TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') and presenca = 'false'")
    dados_falso_consultas  = cursor.fetchall()
    cursor.execute("SELECT TO_CHAR(CURRENT_DATE - INTERVAL '1 MONTH', 'YYYY-MM') AS mes_anterior")
    mes  = cursor.fetchone()
    
    print(mes)
    cursor.close()
    conn.close()
    total_consultas = len(dados_total_consultas)
    falso_consultas = len(dados_falso_consultas)
    return render_template('relatorio.html', total_consultas = total_consultas, falso_consultas = falso_consultas, mes = mes)


# Rota para gerar o gráfico
@app.route("/grafico.png")
def grafico():
    df = get_consultas()  # Obtém os dados
# Criando o gráfico
    # Criando o gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Criando as barras com a cor verde fluorescente
    ax.bar(df["dia"], df["consultas"], color="#6a11cb", edgecolor="black")

    # Configuração do gráfico
    ax.set_ylim(0, max(df["consultas"]) + 5)  # Ajuste para melhor visualização
    ax.set_title("Consultas por Dia da Semana", fontsize=14, fontweight="bold", loc="left")

    # Removendo bordas superiores e laterais para um visual mais limpo
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Adicionando grid apenas no eixo Y
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Ajustando espaçamento para melhor visualização
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Salvando o gráfico como imagem na memória
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return Response(img.getvalue(), mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
