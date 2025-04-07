from flask import Flask, redirect, url_for, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # permite que o frontend chame o backend, especialmente útil localmente

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/red_cadastros')
def mensagem():
    return render_template('cadastros.html')

if __name__ == '__main__':
    app.run(debug=True)