from flask import Flask, render_template, request, redirect, url_for
import qrcode
import sqlite3
import os

app = Flask(__name__)

# Garante que a pasta de imagens existe
if not os.path.exists('static/qrcodes'):
    os.makedirs('static/qrcodes')

def iniciar_banco():
    # Conecta no banco correto (com "e")
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    
    # Mantém a estrutura padronizada que criamos anteriormente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ferramentas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            quantidade_em_estoque INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ferramenta_id TEXT NOT NULL,
            quem_pegou TEXT NOT NULL,
            quem_autorizou TEXT NOT NULL,
            quantidade_retirada INTEGER NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ferramenta_id) REFERENCES ferramentas (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    # Busca as ferramentas no banco para mostrar no HTML
    conn = sqlite3.connect('almoxerifado.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ferramentas")
    lista_produtos = cursor.fetchall()
    conn.close()
    return render_template("interface.html", produtos=lista_produtos)

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get('nome_ferramenta')
    qtd = request.form.get('quantidade')
    
    if nome and qtd:
        conn = sqlite3.connect('almoxerifado.db')
        cursor = conn.cursor()
        
        # Cria o ID personalizado (ex: FER-005)
        cursor.execute("SELECT COUNT(id) FROM ferramentas")
        total = cursor.fetchone()[0] + 1
        novo_id = f"FER-{total:03d}"
        
        # Insere na tabela 'ferramentas'
        cursor.execute('INSERT INTO ferramentas (id, nome, quantidade_em_estoque) VALUES (?, ?, ?)', (novo_id, nome, qtd))
        
        # Gera o QR Code com o ID do banco em formato de texto
        img = qrcode.make(novo_id)
        img.save(f"static/qrcodes/qr_{novo_id}.png")
        
        conn.commit()
        conn.close()
        
    return redirect(url_for('home'))

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