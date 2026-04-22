from flask import Flask, render_template

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Define a rota para a página inicial (o domínio raiz "/")
@app.route("/")
def home():
    # O Flask vai procurar esse arquivo dentro da pasta 'templates'
    return render_template("interface.html")

# Inicia o servidor em modo de depuração (atualiza sozinho quando você salva o código)
if __name__ == "__main__":
    app.run(debug=True)


def verificar():
    valor = request.form.get('codigo_ferramenta')
    try:
        numero = int(valor)
        if numero >= 0:
            flash("Sucesso: Número positivo!", "success")
        else:
            flash("Aviso: O número digitado é negativo.", "danger")
    except ValueError:
        flash("Erro: Digite um número inteiro válido.", "error")
    
    return redirect('/')
