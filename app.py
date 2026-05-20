import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv, set_key

app = Flask(__name__)
app.secret_key = "chave_super_secreta_projeto"

# Carrega as variáveis de ambiente do arquivo .env
ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_FILE)

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

def alertar_falha_banco_por_email(mensagem_erro):
    email_destino = os.getenv("ALERT_EMAIL")
    if not email_destino:
        print("[Alerta] E-mail de destino não configurado nas configurações.")
        return

    msg = EmailMessage()
    msg.set_content(f"Ocorreu uma falha crítica na sincronização com o Postgres:\n\n{mensagem_erro}")
    msg['Subject'] = "ALERTA: Falha de Banco de Dados - EstSys"
    msg['From'] = os.getenv("EMAIL_SENDER", "seu_email_remetente@gmail.com")
    msg['To'] = email_destino
    
    try:
        # Exemplo usando SMTP do Gmail (ajuste EMAIL_SENDER e EMAIL_PASSWORD no seu .env para contas reais)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv("EMAIL_SENDER", "seu_email_remetente@gmail.com"), os.getenv("EMAIL_PASSWORD", "senha_de_app"))
        server.send_message(msg)
        server.quit()
        print(f"[Alerta] E-mail enviado com sucesso para {email_destino}.")
    except Exception as e:
        print(f"[Alerta] Erro ao tentar enviar o alerta por e-mail: {e}")

# --- SISTEMA DE SINCRONIZAÇÃO ASSÍNCRONA ---
def sync_json_to_postgres():
    """
    Função executada em background periodicamente para enviar dados 
    do database.json (memória) para o banco PostgreSQL.
    """
    print("[Sync] Iniciando sincronização do JSON para o PostgreSQL...")
    try:
        # db = load_db()
        # conn = get_db_connection() # Requer a função definida em outro escopo
        # cur = conn.cursor()
        
        # Exemplo de lógica UPSERT (INSERT ON CONFLICT) para a tabela de clientes
        # for c in db.get('clientes', []):
        #     cur.execute("""
        #         INSERT INTO CLIENTE (CLI_CODIGO, CLI_NOME, CLI_DOC, CLI_TEL)
        #         VALUES (%s, %s, %s, %s)
        #         ON CONFLICT (CLI_CODIGO) DO UPDATE SET 
        #             CLI_NOME = EXCLUDED.CLI_NOME,
        #             CLI_DOC = EXCLUDED.CLI_DOC,
        #             CLI_TEL = EXCLUDED.CLI_TEL;
        #     """, (c.get('id'), c.get('nome'), c.get('email'), c.get('telefone')))
        
        # conn.commit()
        # cur.close()
        # conn.close()
        print("[Sync] Sincronização concluída com sucesso!")
    except Exception as e:
        print(f"[Sync] Erro na sincronização: {e}")
        alertar_falha_banco_por_email(str(e))

# Inicializa o Scheduler para rodar em segundo plano (ex: a cada 60 minutos)
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=sync_json_to_postgres, trigger="interval", minutes=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())  # Desliga o scheduler ao fechar a aplicação

# --- FILTROS CUSTOMIZADOS PARA TEMPLATES HTML (JINJA2) ---
@app.template_filter('formata_moeda')
def formata_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return valor

# Filtro para formatação de telefone (Ex: 11999998888 -> (11) 99999-8888)
@app.template_filter('formata_telefone')
def formata_telefone(valor):
    if not valor: return valor
    v = re.sub(r'\D', '', str(valor))
    if len(v) == 11:
        return f"({v[:2]}) {v[2:7]}-{v[7:]}"
    elif len(v) == 10:
        return f"({v[:2]}) {v[2:6]}-{v[6:]}"
    return valor

# Filtro para formatação de CPF (Ex: 12345678900 -> 123.456.789-00)
@app.template_filter('formata_cpf')
def formata_cpf(valor):
    if not valor: return valor
    v = re.sub(r'\D', '', str(valor))
    if len(v) == 11:
        return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    return valor

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
    global TipConDB
    success = False
    if request.method == 'POST':
        try:
            TipConDB = int(request.form.get('tipcondb'))
            
            db_host = request.form.get('db_host')
            db_port = request.form.get('db_port')
            db_user = request.form.get('db_user')
            db_pass = request.form.get('db_pass')
            alert_email = request.form.get('alert_email')
            
            if not os.path.exists(ENV_FILE):
                open(ENV_FILE, 'w').close()
                
            if db_host: set_key(ENV_FILE, "DB_HOST", db_host)
            if db_port: set_key(ENV_FILE, "DB_PORT", db_port)
            if db_user: set_key(ENV_FILE, "DB_USER", db_user)
            if db_pass: set_key(ENV_FILE, "DB_PASS", db_pass)
            if alert_email: set_key(ENV_FILE, "ALERT_EMAIL", alert_email)
            
            load_dotenv(ENV_FILE, override=True)
            success = True
            flash('Configurações atualizadas com sucesso!', 'success')
        except (ValueError, TypeError):
            flash('Erro ao atualizar configurações.', 'danger')
            
    return render_template('configuracoes.html', 
                           TipConDB=TipConDB, 
                           success=success,
                           db_host=os.getenv("DB_HOST", "localhost"),
                           db_port=os.getenv("DB_PORT", "5432"),
                           db_user=os.getenv("DB_USER", "estetsys"),
                           db_pass=os.getenv("DB_PASS", "estetsys"),
                           alert_email=os.getenv("ALERT_EMAIL", ""))

@app.route('/api/vendas')
@login_required(allowed_levels=['2', '3'])
def api_vendas():
    busca = request.args.get('busca', '').strip().lower()
    vendas_list = []
    
    if TipConDB == 1:
        db = load_db()
        vendas_list = db.get('vendas', [])
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT VND_CODIGO, VND_NOMECLI, VND_TOTAL, VND_NOMEPRD, VND_DATA FROM VENDAS WHERE D_E_L_E_T_ IS NULL")
        for r in cur.fetchall():
            try:
                itens = json.loads(r[3])
            except:
                itens = [{'nome': r[3], 'quantidade': 1}]
            vendas_list.append({'id': r[0], 'cliente': r[1], 'total': r[2], 'itens': itens, 'data': r[4]})
        cur.close()
        conn.close()
    
    if busca:
        vendas_list = [v for v in vendas_list if busca in str(v.get('cliente', '')).lower() or busca == str(v.get('id', ''))]
        
    return jsonify(vendas_list)

@app.route('/api/clientes')
@login_required(allowed_levels=['2', '3'])
def api_clientes():
    busca_id = request.args.get('clientID', '').strip()
    busca_nome = request.args.get('clientName', '').strip().lower()
    clientes_list = []
    
    try:
        _TipConDB = TipConDB
    except NameError:
        _TipConDB = 1
        
    if _TipConDB == 1:
        db = load_db()
        for c in db.get('clientes', []):
            if busca_id and str(c.get('id', '')) != busca_id: continue
            if busca_nome and busca_nome not in str(c.get('nome', '')).lower(): continue
            clientes_list.append(c)
    else:
        conn = get_db_connection() # Certifique-se que essa função existe no seu arquivo real
        cur = conn.cursor()
        src = "SELECT CLI_CODIGO, CLI_NOME, CLI_DOC, CLI_TEL FROM CLIENTE WHERE D_E_L_E_T_ IS NULL"
        params = []
        if busca_id:
            src += " AND CLI_CODIGO::text = %s"
            params.append(busca_id)
        if busca_nome:
            src += " AND CLI_NOME ILIKE %s"
            params.append(f"%{busca_nome}%")
        
        cur.execute(src, tuple(params))
        for r in cur.fetchall():
            clientes_list.append({'id': r[0], 'nome': r[1], 'email': r[2], 'telefone': r[3]})
        cur.close()
        conn.close()
        
    return jsonify(clientes_list)

@app.route('/api/produtos')
@login_required(allowed_levels=['2', '3'])
def api_produtos():
    busca_id = request.args.get('productID', '').strip()
    busca_nome = request.args.get('productName', '').strip().lower()
    produtos_list = []
    
    try:
        _TipConDB = TipConDB
    except NameError:
        _TipConDB = 1
        
    if _TipConDB == 1:
        db = load_db()
        for p in db.get('produtos', []):
            if busca_id and str(p.get('id', '')) != busca_id: continue
            if busca_nome and busca_nome not in str(p.get('nome', '')).lower(): continue
            produtos_list.append(p)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        src = "SELECT PRD_CODIGO, PRD_NOME, PRD_PRECO FROM PRODUTO WHERE D_E_L_E_T_ IS NULL"
        params = []
        if busca_id:
            src += " AND PRD_CODIGO::text = %s"
            params.append(busca_id)
        if busca_nome:
            src += " AND PRD_NOME ILIKE %s"
            params.append(f"%{busca_nome}%")
        
        cur.execute(src, tuple(params))
        for r in cur.fetchall():
            produtos_list.append({'id': r[0], 'nome': r[1], 'preco': r[2]})
        cur.close()
        conn.close()
        
    return jsonify(produtos_list)

@app.route('/api/servicos')
@login_required(allowed_levels=['2', '3'])
def api_servicos():
    busca_id = request.args.get('srvID', '').strip()
    busca_nome = request.args.get('serviceName', '').strip().lower()
    servicos_list = []
    
    try:
        _TipConDB = TipConDB
    except NameError:
        _TipConDB = 1
        
    if _TipConDB == 1:
        db = load_db()
        for s in db.get('servicos', []):
            if busca_id and str(s.get('id', '')) != busca_id: continue
            if busca_nome and busca_nome not in str(s.get('nome', '')).lower(): continue
            servicos_list.append(s)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        src = "SELECT SRV_CODIGO, SRV_NOME, SRV_PRECO FROM SERVICO WHERE D_E_L_E_T_ IS NULL"
        params = []
        if busca_id:
            src += " AND SRV_CODIGO::text = %s"
            params.append(busca_id)
        if busca_nome:
            src += " AND SRV_NOME ILIKE %s"
            params.append(f"%{busca_nome}%")
        
        cur.execute(src, tuple(params))
        for r in cur.fetchall():
            servicos_list.append({'id': r[0], 'nome': r[1], 'preco': r[2]})
        cur.close()
        conn.close()
        
    return jsonify(servicos_list)

@app.route('/update_cliente', methods=['POST'])
@login_required(allowed_levels=['2', '3'])
def update_cliente():
    id_cliente = request.form.get('id', type=int)
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    
    try:
        _TipConDB = TipConDB
    except NameError:
        _TipConDB = 1
        
    if _TipConDB == 1:
        db = load_db()
        for c in db.get('clientes', []):
            # Evitar erros caso 'id' venha sem tipo no DB local
            if int(c.get('id', 0)) == id_cliente:
                c['nome'] = nome
                c['email'] = email
                c['telefone'] = telefone
                break
        save_db(db)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        # Sincroniza a atualização no Postgre
        cur.execute("UPDATE CLIENTE SET CLI_NOME=%s, CLI_DOC=%s, CLI_TEL=%s WHERE CLI_CODIGO::text = %s", 
                    (nome, email, telefone, str(id_cliente)))
        conn.commit()
        cur.close()
        conn.close()
        
    flash('Cliente atualizado com sucesso!')
    return redirect(url_for('cadastro_clientes'))

@app.route('/proc_prd', methods=["GET"])
@login_required(allowed_levels=['2', '3'])
def proc_produto():
    data = request.args
    productID = data.get('productID', '').strip()
    productName = data.get('productName', '').strip()
    rows = []
    if TipConDB == 1:
        db = load_db()
        for p in db['produtos']:
            if productID and str(p.get('id', '')) != productID: continue
            if productName and productName.lower() not in str(p.get('nome', '')).lower(): continue
            rows.append(p)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        src = "SELECT PRD_CODIGO, PRD_NOME, PRD_PRECO FROM PRODUTO WHERE D_E_L_E_T_ IS NULL"
        params = []
        if productID:
            src += " AND PRD_CODIGO::text = %s"
            params.append(productID)
        if productName:
            src += " AND PRD_NOME ILIKE %s"
            params.append(f"%{productName}%")
        cur.execute(src, tuple(params))
        for r in cur.fetchall():
            rows.append({'id': r[0], 'nome': r[1], 'preco': r[2]})
        cur.close()
        conn.close()
    return render_template("cadastro_produtos.html", rows=rows, alert="Produtos filtrados!")

@app.route('/proc_cliente', methods=["GET"])
@login_required(allowed_levels=['2', '3'])
def proc_cliente():
    data = request.args
    clientID = data.get('clientID', '').strip()
    clientName = data.get('clientName', '').strip()
    rows = []
    if TipConDB == 1:
        db = load_db()
        for c in db['clientes']:
            if clientID and str(c.get('id', '')) != clientID: continue
            if clientName and clientName.lower() not in str(c.get('nome', '')).lower(): continue
            rows.append(c)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        src = "SELECT CLI_CODIGO, CLI_NOME, CLI_DOC, CLI_TEL FROM CLIENTE WHERE D_E_L_E_T_ IS NULL"
        params = []
        if clientID:
            src += " AND CLI_CODIGO::text = %s"
            params.append(clientID)
        if clientName:
            src += " AND CLI_NOME ILIKE %s"
            params.append(f"%{clientName}%")
        cur.execute(src, tuple(params))
        for r in cur.fetchall():
            rows.append({'id': r[0], 'nome': r[1], 'email': r[2], 'telefone': r[3]})
        cur.close()
        conn.close()
    return render_template("cadastro_clientes.html", rows=rows, alert="Clientes filtrados!")

@app.route('/proc_srv', methods=["GET"])
@login_required(allowed_levels=['2', '3'])
def proc_servico():
    data = request.args
    srvID = data.get('srvID', '').strip()
    srvName = data.get('serviceName', '').strip()
    rows = []
    if TipConDB == 1:
        db = load_db()
        for s in db['servicos']:
            if srvID and str(s.get('id', '')) != srvID: continue
            if srvName and srvName.lower() not in str(s.get('nome', '')).lower(): continue
            rows.append(s)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        src = "SELECT SRV_CODIGO, SRV_NOME, SRV_PRECO FROM SERVICO WHERE D_E_L_E_T_ IS NULL"
        params = []
        if srvID:
            src += " AND SRV_CODIGO::text = %s"
            params.append(srvID)
        if srvName:
            src += " AND SRV_NOME ILIKE %s"
            params.append(f"%{srvName}%")
        cur.execute(src, tuple(params))
        for r in cur.fetchall():
            rows.append({'id': r[0], 'nome': r[1], 'preco': r[2]})
        cur.close()
        conn.close()
    return render_template("cadastro_servicos.html", rows=rows, alert="Serviços filtrados!")

@app.route('/logs')
@login_required(allowed_levels=['3'])
def ver_logs_sistema():
    """ Rota restrita para o Admin (Nível 3) visualizar logs de erros """
    log_file = os.path.join(os.path.dirname(__file__), 'erros_sistema.log')
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        # Retorna o arquivo como texto puro para que o navegador não processe tags HTML que possam existir
        return Response(conteudo, mimetype='text/plain')
    else:
        return "Nenhum log de erros foi gerado pelo sistema ainda.", 404

@app.route('/limpar_logs', methods=['POST'])
@login_required(allowed_levels=['3'])
def limpar_logs():
    """ Rota para esvaziar o arquivo de logs através de um botão no HTML """
    log_file = os.path.join(os.path.dirname(__file__), 'erros_sistema.log')
    if os.path.exists(log_file):
        open(log_file, 'w').close() # Abre o arquivo em modo escrita e já o fecha, limpando seu conteúdo
        flash('Logs limpados com sucesso!', 'success')
    else:
        flash('Arquivo de log não encontrado.', 'warning')
    return redirect(url_for('configuracoes'))

if __name__ == '__main__':
    # Executa o servidor Flask na porta 5000 com reinício automático
    app.run(debug=True)