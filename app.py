import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

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
        default_data = {
            'clientes': [], 
            'produtos': [], 
            'servicos': [], 
            'vendas': [], 
            'grupos_acesso': [{
                'GRP_CODIGO': '1', 
                'GRP_DESCRICAO': 'administrador', 
                'GRP_TIPOACESSO': '3',
                'D_E_L_E_T_':'',
                'R_E_C_N_O_':'1',
                'R_E_C_D_E_L_':'0'
            }], 
            'usuarios': [{
                'USR_CODIGO': 1, 
                'USR_NOME': 'admin', 
                'USR_EMAIL': 'admin@admin.com', 
                'USR_TELEFONE': '00000000000', 
                'USR_GRUPO': '1',
                'USR_SENHA': generate_password_hash('1234'),
                'D_E_L_E_T_':'',
                'R_E_C_N_O_':'1',
                'R_E_C_D_E_L_':'0'
            }]
        }
        save_db(default_data)
        return default_data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_next_id(db, tabela, id_field='id'):
    return max([int(item.get(id_field, 0) or 0) for item in db.get(tabela, [])], default=0) + 1

# Decorador para verificar se o usuário está logado e tem o nível de acesso necessário
def login_required(allowed_levels=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logado'):
                flash('Você precisa estar logado para acessar esta página.', 'warning')
                return redirect(url_for('login'))

            if allowed_levels:  # Se níveis de acesso específicos são necessários
                user_access_type = session.get('tipo_acesso')
                if user_access_type not in allowed_levels:
                    flash('Você não tem permissão para acessar esta página.', 'danger')
                    return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota principal e index
@app.route('/')
@app.route('/index')
@login_required()
def index():
    db = load_db()
    vendas = db.get('vendas', [])
    
    mes_filtro = request.args.get('mes', '')
    
    if mes_filtro:
        vendas = [v for v in vendas if str(v.get('data', '')).startswith(mes_filtro)]
        
    clientes = db.get('clientes', [])
    
    total_clientes = len(clientes)
    qtd_vendas = len(vendas)
    
    faturamento_total = 0.0
    faturamento_por_cliente = {}
    
    produtos_nomes = [p.get('nome') for p in db.get('produtos', [])]
    servicos_nomes = [s.get('nome') for s in db.get('servicos', [])]
    
    qtd_produtos = 0
    qtd_servicos = 0
    
    for v in vendas:
        try:
            total_venda = float(v.get('total', 0))
        except (ValueError, TypeError):
            total_venda = 0.0
            
        faturamento_total += total_venda
        cliente_nome = v.get('cliente', 'Desconhecido')
        faturamento_por_cliente[cliente_nome] = faturamento_por_cliente.get(cliente_nome, 0.0) + total_venda
        
        for item in v.get('itens', []):
            try:
                qtd = int(item.get('quantidade', 1))
            except (ValueError, TypeError):
                qtd = 1
            
            if item.get('nome') in produtos_nomes:
                qtd_produtos += qtd
            elif item.get('nome') in servicos_nomes:
                qtd_servicos += qtd
                
    labels_grafico = json.dumps(list(faturamento_por_cliente.keys()))
    valores_grafico = json.dumps(list(faturamento_por_cliente.values()))
    dados_prod_serv = json.dumps([qtd_produtos, qtd_servicos])

    return render_template('index.html', 
                           total_clientes=total_clientes, 
                           qtd_vendas=qtd_vendas, 
                           faturamento_total=faturamento_total,
                           labels_grafico=labels_grafico,
                           valores_grafico=valores_grafico,
                           dados_prod_serv=dados_prod_serv,
                           mes_filtro=mes_filtro)

# Rotas de Autenticação
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/ver_login', methods=['POST'])
def ver_login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    # Validação pela tabela de usuários no JSON
    db = load_db()
    for u in db.get('usuarios', []):
        if (u.get('USR_NOME') == usuario or u.get('USR_EMAIL') == usuario) and check_password_hash(str(u.get('USR_SENHA', '')), senha):
            session['logado'] = True
            session['usuario_logado'] = u.get('USR_NOME')
            grupo_usuario = next((g for g in db.get('grupos_acesso', []) if str(g.get('GRP_CODIGO')) == str(u.get('USR_GRUPO'))), {})
            session['tipo_acesso'] = str(grupo_usuario.get('GRP_TIPOACESSO', ''))
            session['grupo_acesso'] = str(grupo_usuario.get('GRP_DESCRICAO', '')).lower()
            return redirect(url_for('index'))
            
    flash('Usuário ou senha inválidos!')
    return redirect(url_for('login'))

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

# Rotas de Clientes
@app.route('/cadastro_clientes')
@login_required(allowed_levels=['2', '3'])
def cadastro_clientes():
    db = load_db()
    return render_template('cadastro_clientes.html', rows=db['clientes'])

@app.route('/add_cliente', methods=['POST'])
@login_required(allowed_levels=['2', '3'])
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
@login_required(allowed_levels=['2', '3'])
def dlt_cliente():
    id_cliente = request.form.get('id', type=int)
    db = load_db()
    db['clientes'] = [c for c in db['clientes'] if c['id'] != id_cliente]
    save_db(db)
    flash('Cliente excluído com sucesso!')
    return redirect(url_for('cadastro_clientes'))

# Rotas de Produtos
@app.route('/cadastro_produtos')
@login_required(allowed_levels=['2', '3'])
def cadastro_produtos():
    db = load_db()
    return render_template('cadastro_produtos.html', rows=db['produtos'])

@app.route('/add_produto', methods=['POST'])
@login_required(allowed_levels=['2', '3'])
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
@login_required(allowed_levels=['2', '3'])
def dlt_produto():
    id_produto = request.form.get('id', type=int)
    db = load_db()
    db['produtos'] = [p for p in db['produtos'] if p['id'] != id_produto]
    save_db(db)
    flash('Produto excluído com sucesso!')
    return redirect(url_for('cadastro_produtos'))

# Rotas de Serviços
@app.route('/cadastro_servicos')
@login_required(allowed_levels=['2', '3'])
def cadastro_servicos():
    db = load_db()
    return render_template('cadastro_servicos.html', rows=db['servicos'])

@app.route('/add_servico', methods=['POST'])
@login_required(allowed_levels=['2', '3'])
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
@login_required(allowed_levels=['2', '3'])
def dlt_servico():
    id_servico = request.form.get('id', type=int)
    db = load_db()
    db['servicos'] = [s for s in db['servicos'] if s['id'] != id_servico]
    save_db(db)
    flash('Serviço excluído com sucesso!')
    return redirect(url_for('cadastro_servicos'))

# Rotas de Grupos de Acesso
@app.route('/grupos_acesso')
@login_required(allowed_levels=['3'])
def grupos_acesso():
    db = load_db()
    return render_template('grupos_acesso.html', rows=db.get('grupos_acesso', []))

@app.route('/add_grupo_acesso', methods=['POST'])
@login_required(allowed_levels=['3'])
def add_grupo_acesso():
    descricao = request.form.get('descricao')
    tipo_acesso = request.form.get('tipo_acesso')
    if descricao and tipo_acesso:
        db = load_db()
        db.setdefault('grupos_acesso', []).append({
            'GRP_CODIGO': str(get_next_id(db, 'grupos_acesso', 'GRP_CODIGO')), 
            'GRP_DESCRICAO': descricao, 
            'GRP_TIPOACESSO': tipo_acesso
        })
        save_db(db)
        flash('Grupo de Acesso cadastrado com sucesso!')
    return redirect(url_for('grupos_acesso'))

@app.route('/dlt_grupo_acesso', methods=['POST'])
@login_required(allowed_levels=['3'])
def dlt_grupo_acesso():
    id_grupo = request.form.get('id')
    db = load_db()
    db['grupos_acesso'] = [g for g in db.get('grupos_acesso', []) if str(g.get('GRP_CODIGO')) != str(id_grupo)]
    save_db(db)
    flash('Grupo de Acesso excluído com sucesso!')
    return redirect(url_for('grupos_acesso'))

# Rotas de Usuários
@app.route('/usuarios')
@login_required(allowed_levels=['3'])
def usuarios():
    db = load_db()
    return render_template('usuarios.html', rows=db.get('usuarios', []))

@app.route('/add_usuario', methods=['POST'])
@login_required(allowed_levels=['3'])
def add_usuario():
    nome = request.form.get('usr_nome')
    email = request.form.get('usr_email')
    telefone = request.form.get('usr_telefone')
    grupo = request.form.get('usr_grupo')
    senha = request.form.get('usr_senha')
    if nome and email and telefone and grupo and senha:
        if nome == 'admin' and session.get('usuario_logado') != 'admin':
            flash('O usuário admin só pode ser alterado por ele mesmo!')
            return redirect(url_for('usuarios'))
            
        db = load_db()
        db.setdefault('usuarios', []).append({
            'USR_CODIGO': get_next_id(db, 'usuarios', 'USR_CODIGO'), 
            'USR_NOME': nome, 
            'USR_EMAIL': email, 
            'USR_TELEFONE': telefone, 
            'USR_GRUPO': grupo,
            'USR_SENHA': generate_password_hash(senha)
        })
        save_db(db)
        flash('Usuário cadastrado com sucesso!')
    return redirect(url_for('usuarios'))

@app.route('/dlt_usuario', methods=['POST'])
@login_required(allowed_levels=['3'])
def dlt_usuario():
    id_usuario = request.form.get('id', type=int)
    db = load_db()
    
    usuario_alvo = next((u for u in db.get('usuarios', []) if int(u.get('USR_CODIGO', 0)) == id_usuario), None)
    if usuario_alvo and usuario_alvo.get('USR_NOME') == 'admin':
        if session.get('usuario_logado') != 'admin':
            flash('O usuário admin só pode ser alterado por ele mesmo!')
            return redirect(url_for('usuarios'))
            
    db['usuarios'] = [u for u in db.get('usuarios', []) if int(u.get('USR_CODIGO', 0)) != id_usuario]
    save_db(db)
    flash('Usuário excluído com sucesso!')
    return redirect(url_for('usuarios'))

# Rotas de Vendas e Carrinho
@app.route('/vendas')
@login_required(allowed_levels=['2', '3'])
def vendas():
    db = load_db()
    vendas_list = db.get('vendas', [])
    busca = request.args.get('busca', '').strip().lower()
    
    if busca:
        vendas_list = [v for v in vendas_list if busca in str(v.get('cliente', '')).lower() or busca == str(v.get('id', ''))]
        
    return render_template('vendas.html', clientes=db['clientes'], vendas=vendas_list, busca=busca)

@app.route('/vendas/carrinho')
@login_required(allowed_levels=['2', '3'])
def carrinho():
    cli_nome = request.args.get('cli_nome', 'Cliente não informado')
    db = load_db()
    itens = db['produtos'] + db['servicos']
    return render_template('carrinho.html', cli_nome=cli_nome, rows=itens)

@app.route('/submit_carrinho', methods=['POST'])
@login_required(allowed_levels=['2', '3'])
def submit_carrinho():
    cli_nome = request.form.get('cli_nome', 'Desconhecido')
    total = request.form.get('total', '0.00')
    itens_json = request.form.get('itens', '[]')
    
    try:
        itens = json.loads(itens_json)
    except json.JSONDecodeError:
        itens = []

    db = load_db()
    data_venda = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db['vendas'].append({'id': get_next_id(db, 'vendas'), 'cliente': cli_nome, 'total': total, 'itens': itens, 'data': data_venda})
    save_db(db)
    flash(f'Venda para o cliente {cli_nome} finalizada!')
    return redirect(url_for('vendas'))

@app.route('/venda_detalhe/<int:id_venda>')
@login_required(allowed_levels=['2', '3'])
def venda_detalhe(id_venda):
    db = load_db()
    # Busca a venda pelo ID
    venda = next((v for v in db.get('vendas', []) if int(v.get('id', 0)) == id_venda), None)
    
    if not venda:
        flash('Venda não encontrada.', 'danger')
        return redirect(url_for('vendas'))
        
    return render_template('venda_detalhe.html', venda=venda)

@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required(allowed_levels=['3'])
def configuracoes():
    return render_template('configuracoes.html')

@app.route('/api/vendas')
@login_required(allowed_levels=['2', '3'])
def api_vendas():
    db = load_db()
    vendas_list = db.get('vendas', [])
    busca = request.args.get('busca', '').strip().lower()
    
    if busca:
        vendas_list = [v for v in vendas_list if busca in str(v.get('cliente', '')).lower() or busca == str(v.get('id', ''))]
        
    return jsonify(vendas_list)

if __name__ == '__main__':
    # Executa o servidor Flask na porta 5000 com reinício automático
    app.run(debug=True)