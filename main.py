from flask import Flask, request, redirect, url_for, jsonify, render_template
from flask_cors import CORS

produtos = []

app = Flask(__name__)
CORS(app)  # permite que o frontend chame o backend, especialmente útil localmente

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastros')
def mensagem():
    return render_template('cadastros.html')

@app.route('/cad_prod', methods=["POST"])
def cad_prod():
    nome = request.form.get('productName', '').strip()
    preco_raw = request.form.get('productPrice', '').strip()

    if not nome or not preco_raw:
        return "Dados incompletos", 400

    try:
        preco = float(preco_raw)
    except ValueError:
        return "Preço inválido", 400

    produtos.append([nome, preco])
    return "Produto adicionado com sucesso"

if __name__ == '__main__':
    app.run(debug=True)