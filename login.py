import sqlite3

def criar_banco():
    # Cria a conexão (se o arquivo não existir, ele será criado)
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()

    # Cria a tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Insere o usuário Felipe para teste (se ele não existir)
    cursor.execute("INSERT OR IGNORE INTO usuarios (nome, senha) VALUES (?, ?)", ("Felipe", "1234"))
    
    conn.commit()
    conn.close()

# Chame esta função uma vez para preparar tudo
criar_banco()

@app.route('/autenticar', methods=['POST'])
def autenticar():
    dados = request.json
    usuario_form = dados.get('usuario')
    senha_form = dados.get('senha')

    # 1. Conecta ao banco de dados
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()

    # 2. Busca o usuário pelo nome
    cursor.execute("SELECT nome, senha FROM usuarios WHERE nome = ?", (usuario_form,))
    resultado = cursor.fetchone() # Retorna (nome, senha) ou None
    conn.close()

    # 3. Verifica se encontrou e se a senha bate
    if resultado and resultado[1] == senha_form:
        return jsonify({
            "sucesso": True, 
            "nome": resultado[0]
        }), 200
    else:
        return jsonify({
            "sucesso": False, 
            "mensagem": "Usuário ou senha incorretos"
        }), 401