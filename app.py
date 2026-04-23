from flask import Flask, render_template, request, redirect, url_for
import qrcode
import sqlite3
import os

app = Flask(__name__)

# Garante que a pasta de imagens existe
if not os.path.exists('static/qrcodes'):
    os.makedirs('static/qrcodes')

def iniciar_banco():
    conn = sqlite3.connect('almoxarifado.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    # Vamos buscar os produtos no banco para mostrar no HTML
    conn = sqlite3.connect('almoxarifado.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    lista_produtos = cursor.fetchall()
    conn.close()
    return render_template("interface.html", produtos=lista_produtos)

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get('nome_ferramenta')
    qtd = request.form.get('quantidade')
    
    if nome and qtd:
        conn = sqlite3.connect('almoxarifado.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO produtos (nome, quantidade) VALUES (?, ?)', (nome, qtd))
        novo_id = cursor.lastrowid
        
        # Gera o QR Code com o ID do banco
        img = qrcode.make(f"{novo_id}")
        img.save(f"static/qrcodes/qr_{novo_id}.png")
        
        conn.commit()
        conn.close()
        
    return redirect(url_for('home'))

if __name__ == "__main__":
    iniciar_banco()
    app.run(debug=True)