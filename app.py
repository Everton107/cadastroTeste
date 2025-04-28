import sqlite3
from flask import Flask, request, render_template, jsonify, g

app = Flask(__name__)
DATABASE = 'cadastro1.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        try:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")

@app.cli.command('initdb')
def init_db_command():
    """Inicializa o banco de dados."""
    init_db()
    print('Banco de dados inicializado.')

@app.route('/')
def exibir_cadastro():
    return render_template('cadastroTeste.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    endereco = request.form['endereco']
    telefone = request.form['telefone']
    data_nascimento = request.form['data_nascimento']
    cidade = request.form['cidade']
    db = get_db()
    error = None

    if not nome:
        error = 'Nome é obrigatório.'
    elif not email:
        error = 'Email é obrigatório.'
    elif not senha:
        error = 'Senha é obrigatória.'
    elif db.execute(
        'SELECT id FROM usuarios WHERE email = ?', (email,)
    ).fetchone() is not None:
        error = 'Email já cadastrado.'

    if error is None:
        try:
            db.execute(
                'INSERT INTO usuarios (nome, email, senha, endereco, telefone, data_nascimento, cidade) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (nome, email, senha, endereco, telefone, data_nascimento, cidade)
            )
            db.commit()
            return jsonify({'sucesso': True, 'mensagem': 'Usuário cadastrado com sucesso!'})
        except sqlite3.Error as e:
            db.rollback()
            return jsonify({'sucesso': False, 'mensagem': f'Erro ao cadastrar: {e}'})
    else:
        return jsonify({'sucesso': False, 'mensagem': error})

if __name__ == '__main__':
    app.run(debug=True)