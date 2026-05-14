import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "chave_super_secreta_projeto"

# Caminho do arquivo JSON
DB_FILE = os.path.join(os.path.dirname(__file__), 'templates', 'database.json')

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_db():
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        default_data = {'clientes': [], 'produtos': [], 'servicos': [], 'vendas': [], 'grupos_acesso': [], 'usuarios': []}
        save_db(default_data)
        return default_data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_next_id(db, tabela):
    return max([item.get('id', 0) for item in db.get(tabela, [])], default=0) + 1

# Rota principal e index
@app.route('/')
@app.route('/index')
def index():
    if not session.get('logado'):
        return redirect(url_for('login'))
    return render_template('index.html')

# Rotas de Autenticação
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/ver_login', methods=['POST'])
def ver_login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    # Validação simples de login
    if usuario == 'admin' and senha == '1234':
        session['logado'] = True
        return redirect(url_for('index'))
    else:
        flash('Usuário ou senha inválidos!')
        return redirect(url_for('login'))

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

# Rotas de Clientes
@app.route('/cadastro_clientes')
def cadastro_clientes():
    if not session.get('logado'): return redirect(url_for('login'))
    db = load_db()
    return render_template('cadastro_clientes.html', rows=db['clientes'])

@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    if nome:
        db = load_db()
        db['clientes'].append({'id': get_next_id(db, 'clientes'), 'nome': nome, 'email': email, 'telefone': telefone})
        save_db(db)
        flash('Cliente cadastrado com sucesso!')
    return redirect(url_for('cadastro_clientes'))

@app.route('/dlt_cliente', methods=['POST'])
def dlt_cliente():
    id_cliente = request.form.get('id', type=int)
    db = load_db()
    db['clientes'] = [c for c in db['clientes'] if c['id'] != id_cliente]
    save_db(db)
    flash('Cliente excluído com sucesso!')
    return redirect(url_for('cadastro_clientes'))

# Rotas de Produtos
@app.route('/cadastro_produtos')
def cadastro_produtos():
    if not session.get('logado'): return redirect(url_for('login'))
    db = load_db()
    return render_template('cadastro_produtos.html', rows=db['produtos'])

@app.route('/add_produto', methods=['POST'])
def add_produto():
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    if nome and preco:
        db = load_db()
        db['produtos'].append({'id': get_next_id(db, 'produtos'), 'nome': nome, 'preco': preco})
        save_db(db)
        flash('Produto cadastrado com sucesso!')
    return redirect(url_for('cadastro_produtos'))

@app.route('/dlt_produto', methods=['POST'])
def dlt_produto():
    id_produto = request.form.get('id', type=int)
    db = load_db()
    db['produtos'] = [p for p in db['produtos'] if p['id'] != id_produto]
    save_db(db)
    flash('Produto excluído com sucesso!')
    return redirect(url_for('cadastro_produtos'))

# Rotas de Serviços
@app.route('/cadastro_servicos')
def cadastro_servicos():
    if not session.get('logado'): return redirect(url_for('login'))
    db = load_db()
    return render_template('cadastro_servicos.html', rows=db['servicos'])

@app.route('/add_servico', methods=['POST'])
def add_servico():
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    if nome and preco:
        db = load_db()
        db['servicos'].append({'id': get_next_id(db, 'servicos'), 'nome': nome, 'preco': preco})
        save_db(db)
        flash('Serviço cadastrado com sucesso!')
    return redirect(url_for('cadastro_servicos'))

@app.route('/dlt_servico', methods=['POST'])
def dlt_servico():
    id_servico = request.form.get('id', type=int)
    db = load_db()
    db['servicos'] = [s for s in db['servicos'] if s['id'] != id_servico]
    save_db(db)
    flash('Serviço excluído com sucesso!')
    return redirect(url_for('cadastro_servicos'))

# Rotas de Grupos de Acesso
@app.route('/grupos_acesso')
def grupos_acesso():
    if not session.get('logado'): return redirect(url_for('login'))
    db = load_db()
    return render_template('grupos_acesso.html', rows=db.get('grupos_acesso', []))

@app.route('/add_grupo_acesso', methods=['POST'])
def add_grupo_acesso():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    if nome:
        db = load_db()
        db.setdefault('grupos_acesso', []).append({'id': get_next_id(db, 'grupos_acesso'), 'nome': nome, 'descricao': descricao})
        save_db(db)
        flash('Grupo de Acesso cadastrado com sucesso!')
    return redirect(url_for('grupos_acesso'))

@app.route('/dlt_grupo_acesso', methods=['POST'])
def dlt_grupo_acesso():
    id_grupo = request.form.get('id', type=int)
    db = load_db()
    db['grupos_acesso'] = [g for g in db.get('grupos_acesso', []) if g.get('id') != id_grupo]
    save_db(db)
    flash('Grupo de Acesso excluído com sucesso!')
    return redirect(url_for('grupos_acesso'))

# Rotas de Usuários
@app.route('/usuarios')
def usuarios():
    if not session.get('logado'): return redirect(url_for('login'))
    db = load_db()
    return render_template('usuarios.html', rows=db.get('usuarios', []))

@app.route('/add_usuario', methods=['POST'])
def add_usuario():
    nome = request.form.get('nome')
    login_user = request.form.get('login')
    senha = request.form.get('senha')
    id_grupo_acesso = request.form.get('id_grupo_acesso', type=int)
    if nome and login_user and senha:
        db = load_db()
        db.setdefault('usuarios', []).append({'id': get_next_id(db, 'usuarios'), 'nome': nome, 'login': login_user, 'senha': senha, 'id_grupo_acesso': id_grupo_acesso})
        save_db(db)
        flash('Usuário cadastrado com sucesso!')
    return redirect(url_for('usuarios'))

@app.route('/dlt_usuario', methods=['POST'])
def dlt_usuario():
    id_usuario = request.form.get('id', type=int)
    db = load_db()
    db['usuarios'] = [u for u in db.get('usuarios', []) if u.get('id') != id_usuario]
    save_db(db)
    flash('Usuário excluído com sucesso!')
    return redirect(url_for('usuarios'))

# Rotas de Vendas e Carrinho
@app.route('/vendas')
def vendas():
    if not session.get('logado'): return redirect(url_for('login'))
    db = load_db()
    return render_template('vendas.html', clientes=db['clientes'], vendas=db['vendas'])

@app.route('/vendas/carrinho')
def carrinho():
    if not session.get('logado'): return redirect(url_for('login'))
    cli_nome = request.args.get('cli_nome', 'Cliente não informado')
    db = load_db()
    itens = db['produtos'] + db['servicos']
    return render_template('carrinho.html', cli_nome=cli_nome, rows=itens)

@app.route('/submit_carrinho', methods=['POST'])
def submit_carrinho():
    cli_nome = request.form.get('cli_nome', 'Desconhecido')
    total = request.form.get('total', '0.00')
    db = load_db()
    db['vendas'].append({'id': get_next_id(db, 'vendas'), 'cliente': cli_nome, 'total': total})
    save_db(db)
    flash(f'Venda para o cliente {cli_nome} finalizada!')
    return redirect(url_for('vendas'))

if __name__ == '__main__':
    # Executa o servidor Flask na porta 5000 com reinício automático
    app.run(debug=True)