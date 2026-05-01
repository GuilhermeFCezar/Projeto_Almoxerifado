
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from werkzeug.utils import secure_filename
import qrcode
import sqlite3
import os

app = Flask(__name__)


app.secret_key = 'elsoyelllobo'

# Define o caminho da pasta de imagens
UPLOAD_FOLDER = 'static/Imagens'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cria a pasta caso ela não exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Garante que a pasta de imagens existe
if not os.path.exists('static/qrcodes'):
    os.makedirs('static/qrcodes')

def iniciar_banco():
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    # ... (suas tabelas ferramentas e movimentacoes continuam iguais aqui) ...
    
    # ADICIONE A TABELA DE USUÁRIOS AQUI:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO usuarios (nome, senha) VALUES (?, ?)", ("Felipe", "1234"))
    
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ferramentas")
    lista_produtos = cursor.fetchall()
    conn.close()
    
    # Pega o nome do usuário logado (se não tiver, vira 'Visitante')
    nome_atual = session.get('usuario_nome', 'Visitante')
    
    # Passa as DUAS coisas para o HTML: produtos e nome
    return render_template("interface.html", produtos=lista_produtos, nome=nome_atual)

#sistemas de usuarios

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar():
    dados = request.json
    novo_usuario = dados.get('usuario')
    nova_senha = dados.get('senha')

    if not novo_usuario or not nova_senha:
        return jsonify({"sucesso": False, "mensagem": "Preencha todos os campos!"}), 400

    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (novo_usuario, nova_senha))
        conn.commit()
        return jsonify({"sucesso": True, "mensagem": "Usuário cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"sucesso": False, "mensagem": "Este usuário já existe!"}), 400
    finally:
        # A MÁGICA ESTÁ AQUI! O 'finally' roda não importa o que aconteça lá em cima.
        # Assim o banco NUNCA vai ficar trancado (locked).
        conn.close()

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
        session['usuario_nome'] = resultado[0] 
        return jsonify({"sucesso": True, "nome": resultado[0]}), 200
    else:
        return jsonify({"sucesso": False, "mensagem": "Usuário ou senha incorretos"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route("/inventario")
def inventario():
    # Proteção de acesso: se não estiver logado, manda pro inicio
    if 'usuario_nome' not in session:
        return redirect(url_for('home'))

    nome_do_logado = session['usuario_nome']

    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM ferramentas")
    lista_ferramentas = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM ferramentas")
    total_real = cursor.fetchone()[0] 
    
    conn.close()
    
    # Adicionamos a variável nome aqui no final
    return render_template("inventario.html", ferramentas=lista_ferramentas, total=total_real, nome=nome_do_logado)

#Rota da busca do inventario
@app.route("/buscar_ferramentas")
def buscar_ferramentas():
    # Pega o que o usuário digitou na URL (ex: ?q=fura)
    termo = request.args.get('q', '') 
    
    # Adiciona o '%' para o comando LIKE do SQL entender que pode ter texto antes ou depois
    termo_sql = f"%{termo}%" 

    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    # Busca no banco filtrando por nome OU id
    cursor.execute("SELECT * FROM ferramentas WHERE nome LIKE ? OR id LIKE ?", (termo_sql, termo_sql))
    resultados = cursor.fetchall()
    conn.close()
    
    # Vamos transformar o resultado do banco em um formato de "dicionário" 
    # para o JavaScript conseguir ler facilmente as colunas
    ferramentas_json = []
    for item in resultados:
        ferramentas_json.append({
            'id': item[0],
            'nome': item[1],
            'quantidade': item[2],
            'imagem': item[3]
        })
        
    return jsonify(ferramentas_json)

@app.route("/editar_ferramenta", methods=['POST'])
def editar_ferramenta():
    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json()
    
    id_ferramenta = dados.get('id')
    nome = dados.get('nome')
    quantidade = dados.get('quantidade')
    imagem = dados.get('imagem')

    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    try:
        # Comando SQL para atualizar os dados baseados no ID
        cursor.execute('''
            UPDATE ferramentas 
            SET nome = ?, quantidade_em_estoque = ?, imagem = ?
            WHERE id = ?
        ''', (nome, quantidade, imagem, id_ferramenta))
        
        conn.commit()
        mensagem = "Sucesso"
    except Exception as e:
        mensagem = str(e)
    finally:
        conn.close()
    
    return jsonify({"status": mensagem})

@app.route("/excluir_ferramenta", methods=['DELETE'])
def excluir_ferramenta():
    # Recebe o ID no formato JSON (enviado pelo Front-end)
    dados = request.get_json()
    id_ferramenta = dados.get('id')
    
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()

    try:
        # Comando SQL corrigido com o FROM e a vírgula (id_ferramenta,)
        cursor.execute('''
            DELETE FROM ferramentas 
            WHERE id = ?
        ''', (id_ferramenta,))
        
        conn.commit()
        mensagem = "Sucesso"
    except Exception as e:
        mensagem = str(e)
    finally:
        conn.close()
        
    # Devolve a resposta para o navegador
    return jsonify({"status": mensagem})
     



@app.route("/adicionar_ferramenta", methods=['POST'])
def adicionar_ferramenta():
    # Pega os textos do formulário
    id_ferramenta = request.form.get('id')
    nome = request.form.get('nome')
    quantidade = request.form.get('quantidade')
    
    # Pega o arquivo enviado
    arquivo = request.files.get('imagem')

    if not arquivo or int(quantidade) < 0:
        return jsonify({"status": "Dados inválidos ou imagem ausente!"})

    # Limpa o nome do arquivo para evitar erros de segurança (ex: furadeira de impacto.png -> furadeira_de_impacto.png)
    nome_arquivo = secure_filename(arquivo.filename)
    
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()

    try:
        # 1. Salva a imagem na pasta static/Imagens/
        caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        arquivo.save(caminho_completo)

        # 2. Salva os dados no banco (usamos o nome_arquivo limpo)
        cursor.execute('''
            INSERT INTO ferramentas (id, nome, quantidade_em_estoque, imagem)
            VALUES (?, ?, ?, ?)
        ''', (id_ferramenta, nome, quantidade, nome_arquivo))
        
        # 3. Gera o QR Code
        img_qr = qrcode.make(id_ferramenta)
        if not os.path.exists("static/qrcodes"):
            os.makedirs("static/qrcodes")
        img_qr.save(f"static/qrcodes/qr_{id_ferramenta}.png")
        
        conn.commit()
        mensagem = "Sucesso"
        
    except Exception as e:
        mensagem = str(e)
    finally:
        conn.close()
        
    return jsonify({"status": mensagem})

@app.route("/ferramenta/<id_ferramenta>")
def segunda_tela(id_ferramenta):
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    # Busca a ferramenta específica pelo ID escaneado
    cursor.execute("SELECT * FROM ferramentas WHERE id = ?", (id_ferramenta,))
    ferramenta_escolhida = cursor.fetchone()
    conn.close()
    
    # Se a ferramenta existir, manda os dados para o HTML
    if ferramenta_escolhida:
        return render_template("Segunda_tela.html", ferramenta=ferramenta_escolhida)
    else:
        return "Ferramenta não encontrada no sistema!", 404

if __name__ == "__main__":
    iniciar_banco()
    app.run(debug=True)




#login

