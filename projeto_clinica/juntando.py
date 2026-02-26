from flask import Flask, render_template, request, flash, session, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurações do Banco de Dados
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="clinica",
        user="postgres",
        password="Pink@2004"
    )

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'supersecreto'

# Página Inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if not usuario or not senha:
            flash("Usuário e senha são obrigatórios.", "error")
            return redirect(url_for('login'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar se é um cliente
            cursor.execute(
                "SELECT id_cliente FROM clientes WHERE usuario = %s AND senha = %s",
                (usuario, senha)
            )
            cliente = cursor.fetchone()
            if cliente:
                session['user_id'] = cliente[0]
                session['tipo_usuario'] = 'cliente'
                return redirect(url_for('paciente', id_cliente=cliente[0]))

            # Verificar se é um terapeuta
            cursor.execute(
                "SELECT id_terapeuta FROM terapeutas WHERE usuario = %s AND senha = %s",
                (usuario, senha)
            )
            terapeuta = cursor.fetchone()
            if terapeuta:
                session['user_id'] = terapeuta[0]
                session['tipo_usuario'] = 'terapeuta'
                return redirect(url_for('index'))

            flash("Credenciais inválidas.", "error")
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Erro ao conectar ao banco de dados: {e}", "error")
            return redirect(url_for('login'))

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

# Rota para Visualizar Paciente
@app.route('/paciente/<int:id_cliente>')
def paciente(id_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                atendimento.id AS id_atendimento,
                terapeutas.nome AS nome_terapeuta,
                atendimento.dia_semana,
                atendimento.horario,
                atendimento.data,
                atendimento.descricao    
            FROM atendimento
            INNER JOIN terapeutas ON atendimento.id_terapeuta = terapeutas.id
            WHERE atendimento.id_cliente = %s;
        """, (id_cliente,))
        resultados = cursor.fetchall()
        horarios_paciente = [
            {
                'id_atendimento': r[0],
                'nome_terapeuta': r[1],
                'dia_semana': r[2],
                'horario': r[3],
                'data': r[4].strftime("%d/%m/%Y") if r[4] else None,
                'descricao': r[5]
            }
            for r in resultados
        ]
        return render_template('horario_paciente2.html', horarios_paciente=horarios_paciente)
    except Exception as e:
        flash(f"Erro ao buscar dados: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

# Rota para Criar Atendimento
@app.route('/atendimento', methods=['GET', 'POST'])
def criar_atendimento():
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        id_terapeuta = request.form.get('id_terapeuta')
        dia_semana = request.form.get('dia_semana')
        horario = request.form.get('horario')

        if not (id_cliente and id_terapeuta and dia_semana and horario):
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for('index'))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO atendimento (id_cliente, id_terapeuta, dia_semana, horario)
                VALUES (%s, %s, %s, %s);
            """, (id_cliente, id_terapeuta, dia_semana, horario))
            conn.commit()
            flash("Atendimento criado com sucesso!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao criar atendimento: {e}", "error")
            return redirect(url_for('index'))
        finally:
            cursor.close()
            conn.close()

    return render_template('criar_atendimento.html')

# Rota para Criar Cliente
@app.route('/criar_cliente', methods=['GET', 'POST'])
def criar_cliente():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        nome = request.form.get('nome')

        if not (cpf and usuario and senha and nome):
            flash("CPF, usuário, senha e nome são obrigatórios.", "error")
            return redirect(url_for('criar_cliente'))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO clientes (cpf, usuario, senha, nome)
                VALUES (%s, %s, %s, %s);
            """, (cpf, usuario, senha, nome))
            conn.commit()
            flash("Cliente criado com sucesso!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao criar cliente: {e}", "error")
            return redirect(url_for('criar_cliente'))
        finally:
            cursor.close()
            conn.close()

    return render_template('criar_cliente.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta.", "success")
    return redirect(url_for('login'))

# Início da Aplicação
if __name__ == "__main__":
    app.run(debug=True)
