from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    # Criando a tabela de usuários (Corrigido o NOT EXISTS)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    
    # Inserindo usuário padrão para teste
    cursor.execute("INSERT OR IGNORE INTO usuarios (nome, senha) VALUES (?, ?)", ("Felipe", "1234"))
    
    conn.commit()
    conn.close()

# Rodar a inicialização uma única vez
inicializar_banco()

# --- ROTAS ---

@app.route('/')
def index():
    return render_template('interface.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.json
    novo_usuario = dados.get('usuario')
    nova_senha = dados.get('senha')

    if not novo_usuario or not nova_senha:
        return jsonify({"sucesso": False, "mensagem": "Preencha todos os campos!"}), 400

    try:
        conn = sqlite3.connect('almoxerifado.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (novo_usuario, nova_senha))
        conn.commit()
        conn.close()
        return jsonify({"sucesso": True, "mensagem": "Usuário cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"sucesso": False, "mensagem": "Este usuário já existe!"}), 400

@app.route('/autenticar', methods=['POST'])
def autenticar():
    dados = request.json
    usuario_form = dados.get('usuario')
    senha_form = dados.get('senha')

    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome, senha FROM usuarios WHERE nome = ?", (usuario_form,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado[1] == senha_form:
        return jsonify({"sucesso": True, "nome": resultado[0]}), 200
    else:
        return jsonify({"sucesso": False, "mensagem": "Usuário ou senha incorretos"}), 401

if __name__ == '__main__':
    app.run(debug=True)