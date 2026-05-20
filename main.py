from flask import Flask, request, redirect, url_for, jsonify, render_template, session
from flask_cors import CORS
import psycopg2
import os
import json
from datetime import datetime
from dotenv import load_dotenv, set_key

app = Flask(__name__)
CORS(app)

app.secret_key = '19i320od$'
global login_key
login_key = 'G15estetsys'
global TipConDB
TipConDB = 2 # 1 = Aplicação/Memória, 2 = DB Postgre
# teste commit

DB_FILE = os.path.join(os.path.dirname(__file__), 'templates', 'database.json')

def save_json_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_json_db():
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        default_data = {'cliente': [], 'produto': [], 'servico': [], 'vendas': [], 'grupos_acesso': [], 'usuarios': []}
        save_json_db(default_data)
        return default_data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Rotas das páginas

ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_FILE)

# Função para conectar ao banco de dados do Estetsys
def get_db_connection():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "estetsys")
    db_user = os.getenv("DB_USER", "estetsys")
    db_pass = os.getenv("DB_PASS", "estetsys")
    conn = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass)
    return conn

def valid_login():
    global login_key
    senha = session.get('senha')
    if senha == login_key:
        return True
    else:
        return False

@app.route('/ver_login', methods = ['POST'])
def ver_login():
    data = request.form
    senha = data.get('senha')
    session['senha'] = senha
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        return redirect(url_for("index"))

@app.route('/')
def login():
    return render_template("login.html", alert = "VOCÊ PRECISA LOGAR COM A SENHA CORRETA!")

@app.route('/sair')
def sair():
    session.pop('senha', None)
    return redirect(url_for("login"))

@app.route('/index')
def index():
    session.pop('cliente', None)
    session.pop('carrinho', None)
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        return render_template('index.html')

@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    global TipConDB
    if valid_login() == False:
        return redirect(url_for("login"))
        
    success = False
    if request.method == 'POST':
        try:
            TipConDB = int(request.form.get('tipcondb'))
            
            db_host = request.form.get('db_host')
            db_port = request.form.get('db_port')
            db_user = request.form.get('db_user')
            db_pass = request.form.get('db_pass')
            
            if not os.path.exists(ENV_FILE):
                open(ENV_FILE, 'w').close()
                
            if db_host: set_key(ENV_FILE, "DB_HOST", db_host)
            if db_port: set_key(ENV_FILE, "DB_PORT", db_port)
            if db_user: set_key(ENV_FILE, "DB_USER", db_user)
            if db_pass: set_key(ENV_FILE, "DB_PASS", db_pass)
            
            load_dotenv(ENV_FILE, override=True) # Força a releitura das novas variáveis no SO
            success = True
        except (ValueError, TypeError):
            pass
            
    return render_template('configuracoes.html', 
                           TipConDB=TipConDB, 
                           success=success,
                           db_host=os.getenv("DB_HOST", "localhost"),
                           db_port=os.getenv("DB_PORT", "5432"),
                           db_user=os.getenv("DB_USER", "estetsys"),
                           db_pass=os.getenv("DB_PASS", "estetsys"))

def get_clientes_rows():
    rows = []
    if TipConDB == 1:
        db = load_json_db()
        for c in db.get('cliente', []):
            if c.get('D_E_L_E_T_') is None:
                rows.append((c.get('CLI_NOME'), c.get('CLI_DOC'), c.get('CLI_TEL'), c.get('CLI_OBSERVA')))
        rows.sort(key=lambda x: x[0] if x[0] else '')
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT CLI_NOME, CLI_DOC, CLI_TEL, CLI_OBSERVA FROM CLIENTE WHERE D_E_L_E_T_ IS NULL ORDER BY CLI_NOME ASC;")
            rows = cur.fetchall()
        except Exception as e:
            pass
        finally:
            cur.close()
            conn.close()
    return rows

@app.route('/cadastro_clientes')
def dir_cadastro_clientes():
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        alert = request.args.get('alert')
        return render_template('cadastro_clientes.html', rows=get_clientes_rows(), alert=alert)

def get_produtos_rows():
    rows = []
    if TipConDB == 1:
        db = load_json_db()
        for p in db.get('produto', []):
            if p.get('D_E_L_E_T_') is None:
                rows.append((p.get('PRD_CODIGO'), p.get('PRD_NOME'), p.get('PRD_PRECO'), p.get('PRD_OBSERVA')))
        rows.sort(key=lambda x: str(x[1]) if x[1] else '')
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT PRD_CODIGO, PRD_NOME, PRD_PRECO, PRD_OBSERVA FROM PRODUTO WHERE D_E_L_E_T_ IS NULL ORDER BY PRD_NOME ASC;")
            rows = cur.fetchall()
        except Exception as e:
            pass
        finally:
            cur.close()
            conn.close()
    return rows

@app.route('/cadastro_produtos')
def dir_cadastro_produtos():
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        alert = request.args.get('alert')
        return render_template('cadastro_produtos.html', rows=get_produtos_rows(), alert=alert)

def get_servicos_rows():
    rows = []
    if TipConDB == 1:
        db = load_json_db()
        for s in db.get('servico', []):
            if s.get('D_E_L_E_T_') is None:
                rows.append((s.get('SRV_CODIGO'), s.get('SRV_NOME'), s.get('SRV_PRECO'), s.get('SRV_OBSERVA')))
        rows.sort(key=lambda x: str(x[1]) if x[1] else '')
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT SRV_CODIGO, SRV_NOME, SRV_PRECO, SRV_OBSERVA FROM SERVICO WHERE D_E_L_E_T_ IS NULL ORDER BY SRV_NOME ASC;")
            rows = cur.fetchall()
        except Exception as e:
            pass
        finally:
            cur.close()
            conn.close()
    return rows

@app.route('/cadastro_servicos')
def dir_cadastro_servicos():
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        alert = request.args.get('alert')
        return render_template('cadastro_servicos.html', rows=get_servicos_rows(), alert=alert)

def get_grupos_acesso_rows():
    rows = []
    if TipConDB == 1:
        db = load_json_db()
        for g in db.get('grupos_acesso', []):
            if g.get('D_E_L_E_T_') is None:
                rows.append((g.get('GRP_CODIGO'), g.get('GRP_DESCRICAO'), g.get('GRP_TIPOACESSO')))
        rows.sort(key=lambda x: str(x[1]) if x[1] else '')
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT GRP_CODIGO, GRP_DESCRICAO, GRP_TIPOACESSO FROM GRUPO_ACESSO WHERE D_E_L_E_T_ IS NULL ORDER BY GRP_DESCRICAO ASC;")
            rows = cur.fetchall()
        except Exception as e:
            pass
        finally:
            cur.close()
            conn.close()
    return rows

@app.route('/grupos_acesso')
def dir_grupos_acesso():
    if valid_login() == False:
        return redirect(url_for("login"))
    alert = request.args.get('alert')
    return render_template('grupos_acesso.html', rows=get_grupos_acesso_rows(), alert=alert)

def get_usuarios_rows():
    rows = []
    if TipConDB == 1:
        db = load_json_db()
        for u in db.get('usuarios', []):
            if u.get('D_E_L_E_T_') is None:
                rows.append((u.get('USR_CODIGO'), u.get('USR_NOME'), u.get('USR_EMAIL'), u.get('USR_TELEFONE'), u.get('USR_GRUPO')))
        rows.sort(key=lambda x: str(x[1]) if x[1] else '')
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT USR_CODIGO, USR_NOME, USR_EMAIL, USR_TELEFONE, USR_GRUPO FROM USUARIOS WHERE D_E_L_E_T_ IS NULL ORDER BY USR_NOME ASC;")
            rows = cur.fetchall()
        except Exception as e:
            pass
        finally:
            cur.close()
            conn.close()
    return rows

@app.route('/usuarios')
def dir_usuarios():
    if valid_login() == False:
        return redirect(url_for("login"))
    alert = request.args.get('alert')
    return render_template('usuarios.html', rows=get_usuarios_rows(), alert=alert)

@app.route('/vendas')
def dir_vendas():
    busca = request.args.get('busca', '').strip()

    if TipConDB == 1:
        db = load_json_db()
        vendas = []
        for v in db.get('vendas', []):
            if v.get('D_E_L_E_T_') is None:
                match = True
                if busca and busca.lower() not in str(v.get('VND_NOMECLI', '')).lower() and busca.lower() not in str(v.get('VND_DOC', '')).lower() and busca.lower() not in str(v.get('VND_CODIGO', '')).lower():
                    match = False
                if match:
                    vendas.append((v.get('VND_CODIGO'), v.get('VND_NOMECLI'), v.get('VND_DOC'), v.get('VND_NOMEPRD'), v.get('VND_TOTAL'), v.get('VND_DATA', '')))
        vendas.sort(key=lambda x: x[5] if x[5] else '', reverse=True)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        src = "SELECT VND_CODIGO, VND_NOMECLI, VND_DOC, VND_NOMEPRD, VND_TOTAL, TO_CHAR(VND_DATA, 'YYYY-MM-DD HH24:MI') FROM VENDAS WHERE d_e_l_e_t_ IS NULL"
        params = []
        
        if busca:
            src += " AND (VND_NOMECLI ILIKE %s OR VND_DOC ILIKE %s OR VND_CODIGO::text ILIKE %s)"
            params.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%"])
            
        src += " ORDER BY VND_DATA DESC;"
        cur.execute(src, tuple(params))
        vendas = cur.fetchall()
    
        cur.close()
        conn.close()

    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        alert = request.args.get('alert')
        return render_template('vendas.html', rows=vendas, alert=alert)

##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
# Configurações do banco de dados



# Função para determinar o CLI_CODIGO MÁXIMO

def max_cli_cod():
    if TipConDB == 1:
        db = load_json_db()
        return max([item.get('CLI_CODIGO', 0) for item in db.get('cliente', [])], default=0)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(CLI_CODIGO) FROM CLIENTE;")
    last_cli_cod = cur.fetchall()[0][0]

    if not last_cli_cod:
        last_cli_cod = 0

    cur.close()
    conn.close()
    return last_cli_cod

########################   Seção de Cliente   ########################

# Rota para adicionar um produto ao cadastro de produtos
@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    data = request.form
    ad_CLI_CODIGO     = max_cli_cod() + 1
    ad_CLI_NOME       = data.get('clientName', '').strip()
    ad_CLI_ENDERECO	  = data.get('clientAddress', '').strip()
    ad_CLI_COMPLEMENT = data.get('clientComplement', '').strip()
    ad_CLI_CEP        = data.get('clientCEP', '').strip()
    ad_CLI_TEL        = data.get('clientPhone', '').strip()
    ad_CLI_DOC        = data.get('clientCPF', '').strip()
    ad_CLI_OBSERVA    = data.get('clientNote', '').strip()

    if not ad_CLI_NOME or not ad_CLI_ENDERECO or not ad_CLI_TEL or not ad_CLI_DOC:
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_clientes', alert="Dados incompletos"))
    
    if TipConDB == 1:
        db = load_json_db()
        novo_cliente = {
            'CLI_CODIGO': ad_CLI_CODIGO,
            'CLI_NOME': ad_CLI_NOME,
            'CLI_ENDERECO': ad_CLI_ENDERECO,
            'CLI_COMPLEMENT': ad_CLI_COMPLEMENT,
            'CLI_CEP': ad_CLI_CEP,
            'CLI_TEL': ad_CLI_TEL,
            'CLI_DOC': ad_CLI_DOC,
            'CLI_OBSERVA': ad_CLI_OBSERVA,
            'D_E_L_E_T_': None
        }
        db.setdefault('cliente', []).append(novo_cliente)
        save_json_db(db)
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_clientes', alert="Cliente adicionado com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute( "Insert Into CLIENTE ( CLI_CODIGO, CLI_NOME, CLI_ENDERECO, CLI_COMPLEMENT, CLI_CEP, CLI_TEL, CLI_DOC, CLI_OBSERVA, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, %s, %s, %s, %s, NULL, 1, NULL);", ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_COMPLEMENT, ad_CLI_CEP, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA ))
            conn.commit()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_clientes', alert="Cliente adicionado com sucesso!"))
        
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_clientes', alert=f"Erro ao cadastrar: {str(e)}"))
        finally:
            cur.close()
            conn.close()
    
    

# Rota para deletar um cadastro de um cliente
@app.route('/dlt_cliente', methods=['POST'])
def dlt_cliente():
    codigo = request.form.get('codigo')
    codigo = str(codigo)

    if TipConDB == 1:
        db = load_json_db()
        for c in db.get('cliente', []):
            if c.get('CLI_DOC') == codigo:
                c['D_E_L_E_T_'] = '*'
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_clientes', alert="Cliente excluído com sucesso"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute("UPDATE CLIENTE SET D_E_L_E_T_ = %s WHERE CLI_DOC = %s;", ('*', codigo))
            conn.commit()
    
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_clientes', alert="Cliente excluído com sucesso"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_clientes', alert=f"Erro ao excluir cliente: {e}"))
        finally:
            cur.close()
            conn.close()

########################    Seção de Produtos   ########################

def max_prd_cod():
    if TipConDB == 1:
        db = load_json_db()
        return max([item.get('PRD_CODIGO', 0) for item in db.get('produto', [])], default=0)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(PRD_CODIGO) FROM PRODUTO;")
    last_prd_cod = cur.fetchone()[0]

    if not last_prd_cod:
        last_prd_cod = 0

    cur.close()
    conn.close()
    return last_prd_cod


# Rota para adicionar um produto ao cadastro de produtos
@app.route('/add_produto', methods=['POST'])
def add_produto():
    data = request.form
    ad_PRD_CODIGO  = max_prd_cod() + 1
    ad_PRD_NOME    = data.get('productName', '').strip()
    ad_PRD_PRECO   = data.get('productPrice', '').strip()
    ad_PRD_OBSERVA = data.get('productDesc', '').strip()

    if not ad_PRD_NOME or not ad_PRD_PRECO or not ad_PRD_CODIGO or not ad_PRD_OBSERVA:
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_produtos', alert="Dados incompletos"))
    
    if TipConDB == 1:
        db = load_json_db()
        novo_produto = {
            'PRD_CODIGO': ad_PRD_CODIGO,
            'PRD_NOME': ad_PRD_NOME,
            'PRD_PRECO': ad_PRD_PRECO,
            'PRD_OBSERVA': ad_PRD_OBSERVA,
            'D_E_L_E_T_': None
        }
        db.setdefault('produto', []).append(novo_produto)
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_produtos', alert="Produto adicionado com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute( "Insert Into PRODUTO ( PRD_CODIGO, PRD_NOME, PRD_PRECO, PRD_OBSERVA, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, NULL, 1, NULL);", ( ad_PRD_CODIGO, ad_PRD_NOME, ad_PRD_PRECO, ad_PRD_OBSERVA))
            conn.commit()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_produtos', alert="Produto adicionado com sucesso!"))
    
        except Exception as e:
            conn.rollback()
            return redirect(url_for('dir_cadastro_produtos', alert=f"Erro ao cadastrar: {str(e)}"))
        
        finally:
            cur.close()
            conn.close()
    
    

# Rota para deletar um cadastro de um produto
@app.route('/dlt_produto', methods=['POST'])
def dlt_produto():
    codigo = request.form.get('codigo')

    if TipConDB == 1:
        db = load_json_db()
        for p in db.get('produto', []):
            if str(p.get('PRD_CODIGO')) == str(codigo):
                p['D_E_L_E_T_'] = '*'
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_produtos', alert="Produto excluído com sucesso"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute("UPDATE PRODUTO SET D_E_L_E_T_ = %s WHERE PRD_CODIGO = %s;", ('*', codigo))
            conn.commit()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_produtos', alert="Produto excluído com sucesso"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_produtos', alert=f"Erro ao excluir produto: {e}"))
        
        finally:
            cur.close()
            conn.close()

########################    Seção de Serviços   ########################

def max_srv_cod():
    if TipConDB == 1:
        db = load_json_db()
        return max([item.get('SRV_CODIGO', 0) for item in db.get('servico', [])], default=0)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT MAX(SRV_CODIGO) FROM SERVICO")
    last_srv_cod = cur.fetchall()[0][0]
    if not last_srv_cod:
        last_srv_cod = 0

    cur.close()
    conn.close()

    return last_srv_cod

# Rota para adicionar um produto ao cadastro de produtos
@app.route('/add_servico', methods=['POST'])
def add_servico():
    data = request.form
    ad_SRV_CODIGO  = max_srv_cod() + 1
    ad_SRV_NOME    = data.get('serviceName', '').strip()
    ad_SRV_PRECO   = data.get('servicePrice', '').strip()
    ad_SRV_OBSERVA = data.get('serviceDesc', '').strip()

    if not ad_SRV_NOME or not ad_SRV_PRECO or not ad_SRV_OBSERVA:
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_servicos', alert="Dados incompletos"))
    
    if TipConDB == 1:
        db = load_json_db()
        novo_servico = {
            'SRV_CODIGO': ad_SRV_CODIGO,
            'SRV_NOME': ad_SRV_NOME,
            'SRV_PRECO': ad_SRV_PRECO,
            'SRV_OBSERVA': ad_SRV_OBSERVA,
            'D_E_L_E_T_': None
        }
        db.setdefault('servico', []).append(novo_servico)
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_servicos', alert="Serviço adicionado com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute( "Insert Into SERVICO ( SRV_CODIGO, SRV_NOME, SRV_PRECO, SRV_OBSERVA, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, NULL, 1, NULL);", ( ad_SRV_CODIGO, ad_SRV_NOME, ad_SRV_PRECO, ad_SRV_OBSERVA))
            conn.commit()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_servicos', alert="Serviço adicionado com sucesso!"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_servicos', alert=f"Erro ao cadastrar: {str(e)}"))
        
        finally:
            cur.close()
            conn.close()

@app.route('/dlt_servico', methods=['POST'])
def dlt_servico():
    codigo = request.form.get('codigo')

    if TipConDB == 1:
        db = load_json_db()
        for s in db.get('servico', []):
            if str(s.get('SRV_CODIGO')) == str(codigo):
                s['D_E_L_E_T_'] = '*'
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_cadastro_servicos', alert="Servico excluído com sucesso"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute("UPDATE SERVICO SET D_E_L_E_T_ = %s WHERE SRV_CODIGO = %s;", ('*', codigo))
            conn.commit()
    
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_servicos', alert="Servico excluído com sucesso"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_servicos', alert=f"Erro ao excluir produto: {e}"))
        
        finally:
            cur.close()
            conn.close()

########################    Seção de Grupos de Acesso   ########################

def max_grp_cod():
    if TipConDB == 1:
        db = load_json_db()
        return max([item.get('GRP_CODIGO', 0) for item in db.get('grupos_acesso', [])], default=0)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(GRP_CODIGO) FROM GRUPO_ACESSO;")
    last_grp_cod = cur.fetchone()[0]

    if not last_grp_cod:
        last_grp_cod = 0

    cur.close()
    conn.close()
    return last_grp_cod

@app.route('/add_grupo_acesso', methods=['POST'])
def add_grupo_acesso():
    data = request.form
    ad_GRP_CODIGO    = max_grp_cod() + 1
    ad_GRP_TIPOACESSO = data.get('grpTipoAcesso', '').strip()
    ad_GRP_DESCRICAO = data.get('grpDescricao', '').strip()

    if not ad_GRP_DESCRICAO or not ad_GRP_TIPOACESSO:
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_grupos_acesso', alert="Dados incompletos"))
    
    if TipConDB == 1:
        db = load_json_db()
        novo_grupo = {
            'GRP_CODIGO': ad_GRP_CODIGO,
            'GRP_DESCRICAO': ad_GRP_DESCRICAO,
            'GRP_TIPOACESSO': ad_GRP_TIPOACESSO,
            'D_E_L_E_T_': None
        }
        db.setdefault('grupos_acesso', []).append(novo_grupo)
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_grupos_acesso', alert="Grupo adicionado com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute( "Insert Into GRUPO_ACESSO ( GRP_CODIGO, GRP_DESCRICAO, GRP_TIPOACESSO, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, NULL, 1, NULL);", ( ad_GRP_CODIGO, ad_GRP_DESCRICAO, ad_GRP_TIPOACESSO))
            conn.commit()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_grupos_acesso', alert="Grupo adicionado com sucesso!"))
    
        except Exception as e:
            conn.rollback()
            return redirect(url_for('dir_grupos_acesso', alert=f"Erro ao cadastrar: {str(e)}"))
        
        finally:
            cur.close()
            conn.close()

@app.route('/dlt_grupo_acesso', methods=['POST'])
def dlt_grupo_acesso():
    codigo = request.form.get('codigo')

    if TipConDB == 1:
        db = load_json_db()
        for g in db.get('grupos_acesso', []):
            if str(g.get('GRP_CODIGO')) == str(codigo):
                g['D_E_L_E_T_'] = '*'
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_grupos_acesso', alert="Grupo excluído com sucesso"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute("UPDATE GRUPO_ACESSO SET D_E_L_E_T_ = %s WHERE GRP_CODIGO = %s;", ('*', codigo))
            conn.commit()
    
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_grupos_acesso', alert="Grupo excluído com sucesso"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_grupos_acesso', alert=f"Erro ao excluir grupo: {e}"))
        finally:
            cur.close()
            conn.close()

########################    Seção de Usuários   ########################

def max_usr_cod():
    if TipConDB == 1:
        db = load_json_db()
        return max([item.get('USR_CODIGO', 0) for item in db.get('usuarios', [])], default=0)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(USR_CODIGO) FROM USUARIOS;")
    last_usr_cod = cur.fetchone()[0]

    if not last_usr_cod:
        last_usr_cod = 0

    cur.close()
    conn.close()
    return last_usr_cod

@app.route('/add_usuario', methods=['POST'])
def add_usuario():
    data = request.form
    ad_USR_CODIGO    = max_usr_cod() + 1
    ad_USR_NOME      = data.get('usrNome', '').strip()
    ad_USR_EMAIL     = data.get('usrEmail', '').strip()
    ad_USR_TELEFONE  = data.get('usrTelefone', '').strip()
    ad_USR_GRPCOD    = data.get('usrGrpCod', '').strip()

    if not ad_USR_NOME or not ad_USR_EMAIL or not ad_USR_TELEFONE or not ad_USR_GRPCOD:
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_usuarios', alert="Dados incompletos"))
    
    if TipConDB == 1:
        db = load_json_db()
        novo_usuario = {
            'USR_CODIGO': ad_USR_CODIGO,
            'USR_NOME': ad_USR_NOME,
            'USR_EMAIL': ad_USR_EMAIL,
            'USR_TELEFONE': ad_USR_TELEFONE,
            'USR_GRUPO': ad_USR_GRPCOD,
            'D_E_L_E_T_': None
        }
        db.setdefault('usuarios', []).append(novo_usuario)
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_usuarios', alert="Usuário adicionado com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute( "Insert Into USUARIOS ( USR_CODIGO, USR_NOME, USR_EMAIL, USR_TELEFONE, USR_GRUPO, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, %s, NULL, 1, NULL);", ( ad_USR_CODIGO, ad_USR_NOME, ad_USR_EMAIL, ad_USR_TELEFONE, ad_USR_GRPCOD))
            conn.commit()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_usuarios', alert="Usuário adicionado com sucesso!"))
    
        except Exception as e:
            conn.rollback()
            return redirect(url_for('dir_usuarios', alert=f"Erro ao cadastrar: {str(e)}"))
        
        finally:
            cur.close()
            conn.close()

@app.route('/dlt_usuario', methods=['POST'])
def dlt_usuario():
    codigo = request.form.get('codigo')

    if TipConDB == 1:
        db = load_json_db()
        for u in db.get('usuarios', []):
            if str(u.get('USR_CODIGO')) == str(codigo):
                u['D_E_L_E_T_'] = '*'
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for('dir_usuarios', alert="Usuário excluído com sucesso"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute("UPDATE USUARIOS SET D_E_L_E_T_ = %s WHERE USR_CODIGO = %s;", ('*', codigo))
            conn.commit()
    
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_usuarios', alert="Usuário excluído com sucesso"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_usuarios', alert=f"Erro ao excluir usuário: {e}"))
        finally:
            cur.close()
            conn.close()
        
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################

#################################################################
###################     Consulta de dados       #################

@app.route('/proc_cliente', methods=["GET"])
def proc_cliente():
    data = request.args
    DOC   = data.get('clientCPF', '').strip()
    NOME     = data.get('clientName', '').strip()
    TEL      = data.get('clientPhone', '').strip()
    
    if TipConDB == 1:
        db = load_json_db()
        rows = []
        for c in db.get('cliente', []):
            if c.get('D_E_L_E_T_') is None:
                match = True
                if DOC and DOC.lower() not in c.get('CLI_DOC', '').lower(): match = False
                if NOME and NOME.lower() not in c.get('CLI_NOME', '').lower(): match = False
                if TEL and TEL.lower() not in c.get('CLI_TEL', '').lower(): match = False
                if match:
                    rows.append((c.get('CLI_NOME'), c.get('CLI_DOC'), c.get('CLI_TEL'), c.get('CLI_OBSERVA')))
        rows.sort(key=lambda x: x[0] if x[0] else '')
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_clientes.html", rows=rows, alert = "Clientes encontrados!")
    else:
        src = "SELECT CLI_NOME AS NOME, CLI_DOC AS DOCUMENTO, CLI_TEL AS TELEFONE, CLI_OBSERVA AS OBSERVAÇÕES FROM CLIENTE WHERE D_E_L_E_T_ IS NULL"
        params = []
    
        if DOC:
            src += " AND CLI_DOC ILIKE %s"
            params.append(f"%{DOC}%")
        
        if NOME:
            src += " AND CLI_NOME ILIKE %s"
            params.append(f"%{NOME}%")
        
        if TEL:
            src += " AND CLI_TEL ILIKE %s"
            params.append(f"%{TEL}%")
        
        src += ' ORDER BY CLI_NOME ASC;'
    
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute(src, tuple(params))
            rows = cur.fetchall()
    
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return render_template("cadastro_clientes.html", rows=rows, alert = "Clientes encontrados!")
        
        except:
            mensagem = 'Cliente não encontrado!'
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_clientes'))
    
        finally:
            cur.close()
            conn.close()

@app.route('/proc_prd', methods=["GET"])
def proc_produto():
    data = request.args
    CODIGO   = data.get('productID', '').strip()
    NOME     = data.get('productName', '').strip()
    OBSERVA  = data.get('productDesc', '').strip()

    if TipConDB == 1:
        db = load_json_db()
        rows = []
        for p in db.get('produto', []):
            if p.get('D_E_L_E_T_') is None:
                match = True
                if CODIGO and str(p.get('PRD_CODIGO', '')) != CODIGO: match = False
                if NOME and NOME.lower() not in str(p.get('PRD_NOME', '')).lower(): match = False
                if OBSERVA and OBSERVA.lower() not in str(p.get('PRD_OBSERVA', '')).lower(): match = False
                if match:
                    rows.append((p.get('PRD_CODIGO'), p.get('PRD_NOME'), p.get('PRD_PRECO'), p.get('PRD_OBSERVA')))
        rows.sort(key=lambda x: str(x[1]) if x[1] else '')
        return render_template("cadastro_produtos.html", rows=rows)
    else:
        src = 'SELECT PRD_CODIGO AS Código, PRD_NOME AS Nome, PRD_PRECO AS Preço, PRD_OBSERVA AS DESCRIÇÃO FROM PRODUTO WHERE D_E_L_E_T_ IS NULL'
        params = []
    
        # FORMATA PARA BUSCA PARCIAL
        if CODIGO:
            src += " AND PRD_CODIGO::text ILIKE %s"
            params.append(f"%{CODIGO}%")
        
        if NOME:
            src += " AND PRD_NOME ILIKE %s"
            params.append(f"%{NOME}%")
        
        if OBSERVA:
            src += " AND PRD_OBSERVA ILIKE %s"
            params.append(f"%{OBSERVA}%")
    
        src += ' ORDER BY PRD_NOME ASC;'
    
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute(src, tuple(params))
            rows = cur.fetchall()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return render_template("cadastro_produtos.html", rows=rows, alert="Produtos encontrados!")
        except:
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_produtos', alert='Produto não encontrado!'))
        finally:
            cur.close()
            conn.close()
 
@app.route('/proc_srv', methods=["GET"])
def proc_service():

    data = request.args
    SRV_CODIGO   = data.get('srvID', '').strip()
    SRV_NOME     = data.get('serviceName', '').strip()
    SRV_OBSERVA      = data.get('serviceDesc', '').strip()
    
    if TipConDB == 1:
        db = load_json_db()
        rows = []
        for s in db.get('servico', []):
            if s.get('D_E_L_E_T_') is None:
                match = True
                if SRV_CODIGO and str(s.get('SRV_CODIGO', '')) != SRV_CODIGO: match = False
                if SRV_NOME and SRV_NOME.lower() not in str(s.get('SRV_NOME', '')).lower(): match = False
                if SRV_OBSERVA and SRV_OBSERVA.lower() not in str(s.get('SRV_OBSERVA', '')).lower(): match = False
                if match:
                    rows.append((s.get('SRV_CODIGO'), s.get('SRV_NOME'), s.get('SRV_PRECO'), s.get('SRV_OBSERVA')))
        rows.sort(key=lambda x: str(x[1]) if x[1] else '')
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html", rows = rows, alert="Serviços encontrados!")
    else:
        # FORMATA PARA BUSCA PARCIAL
        src = "SELECT SRV_CODIGO, SRV_NOME, SRV_PRECO, SRV_OBSERVA FROM SERVICO WHERE D_E_L_E_T_ IS NULL"
        params = []
    
        if SRV_CODIGO:
            src += " AND SRV_CODIGO::text ILIKE %s"
            params.append(f"%{SRV_CODIGO}%")
    
        if SRV_NOME:
            src += " AND SRV_NOME ILIKE %s"
            params.append(f"%{SRV_NOME}%")
        
        if SRV_OBSERVA:
            src += " AND SRV_OBSERVA ILIKE %s"
            params.append(f"%{SRV_OBSERVA}%")
        
        src += " ORDER BY SRV_NOME ASC"
    
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute(src, tuple(params))
            rows = cur.fetchall()
    
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return render_template("cadastro_servicos.html", rows = rows, alert="Serviços encontrados!")
    
        except Exception as e:
            conn.rollback()
            
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for('dir_cadastro_servicos', alert=f"Erro ao buscar serviço: {e}"))
                
        finally:
            cur.close()
            conn.close()

####################################################################
############################# ROTAS PARA VENDA #####################

@app.route("/buscar_cliente")
def buscar_cliente():
    cpf = request.args.get("cpf", "").strip()

    if TipConDB == 1:
        db = load_json_db()
        resultado = None
        for c in db.get('cliente', []):
            if c.get('D_E_L_E_T_') is None and cpf.lower() in str(c.get('CLI_DOC', '')).lower():
                resultado = (c.get('CLI_DOC'), c.get('CLI_NOME'), c.get('CLI_TEL'), c.get('CLI_CODIGO'))
                break
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        cur.execute("SELECT CLI_DOC, CLI_NOME, CLI_TEL, CLI_CODIGO FROM CLIENTE WHERE D_E_L_E_T_ IS NULL AND CLI_DOC ILIKE %s LIMIT 1", (f"%{cpf}%",))
        resultado = cur.fetchone()
        
        cur.close()
        conn.close()

    if resultado:
        doc   = resultado[0]
        nome  = resultado[1]
        tel   = resultado[2]
        cod   = resultado[3]
        cliente = [doc,nome,tel,cod]
        session['cliente'] = cliente

        print(session['cliente'])
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return jsonify({"nome": nome, "telefone": tel, "doc": doc})
    
    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return jsonify({"erro": "Cliente não encontrado"}), 404

@app.route('/buscar-item', methods=['GET'])
def buscar_item():
    tipo = request.args.get('tipo')
    termo = request.args.get('texto')

    if tipo not in ['produto', 'servico']:
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return jsonify({'erro': 'Tipo inválido'}), 400

    if TipConDB == 1:
        db = load_json_db()
        dados = []
        if tipo == 'produto':
            for p in db.get('produto', []):
                if p.get('D_E_L_E_T_') is None:
                    if termo.lower() in str(p.get('PRD_NOME', '')).lower() or termo.lower() in str(p.get('PRD_CODIGO', '')).lower():
                        dados.append({
                            'id': p.get('PRD_CODIGO'),
                            'nome': p.get('PRD_NOME'),
                            'observa': p.get('PRD_OBSERVA'),
                            'preco': p.get('PRD_PRECO')
                        })
        else:
            for s in db.get('servico', []):
                if s.get('D_E_L_E_T_') is None:
                    if termo.lower() in str(s.get('SRV_NOME', '')).lower() or termo.lower() in str(s.get('SRV_CODIGO', '')).lower():
                        dados.append({
                            'id': s.get('SRV_CODIGO'),
                            'nome': s.get('SRV_NOME'),
                            'observa': s.get('SRV_OBSERVA'),
                            'preco': s.get('SRV_PRECO')
                        })
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        if tipo == 'produto':
            cur.execute("SELECT PRD_CODIGO AS id, PRD_NOME AS nome, PRD_OBSERVA AS observa, PRD_PRECO AS preco FROM produto WHERE D_E_L_E_T_ IS NULL AND (PRD_NOME ILIKE %s OR PRD_CODIGO::text ILIKE %s)",
                        (f"%{termo}%", f"%{termo}%"))
        else:
            cur.execute("SELECT SRV_CODIGO AS id, SRV_NOME AS nome, SRV_OBSERVA AS observa, SRV_PRECO AS preco FROM servico WHERE D_E_L_E_T_ IS NULL AND (SRV_NOME ILIKE %s OR SRV_CODIGO::text ILIKE %s)",
                        (f"%{termo}%", f"%{termo}%"))
    
        resultados = cur.fetchall()
        cur.close()
        conn.close()
    
        colnames = [desc[0] for desc in cur.description]
        dados = [dict(zip(colnames, row)) for row in resultados]

    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return jsonify(dados)

@app.route("/vendas/carrinho")
def init_carrinho():
    # global cliente
    # global carrinho

    doc = session['cliente'][0]
    nome = session['cliente'][1]

    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return render_template("carrinho.html", cli_doc = doc, cli_nome = nome )

@app.route('/montar_cart')
def montar_cart():
    # global cliente
    carrinho = session.get('carrinho',[])

    cli_nome = session['cliente'][1]
    cli_doc = session['cliente'][0]

    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return render_template("carrinho.html", rows = carrinho, cli_nome = cli_nome, cli_doc = cli_doc)

@app.route('/add_item_cart', methods=['GET'])
def add_item_cart():
    # global carrinho
    carrinho = session.get('carrinho',[])
    
    data = request.args
    id_item = data.get('id')
    nome = data.get('itemnome')
    desc = data.get('descricao')
    preco = float(data.get('preco'))

    newitemCart = [id_item,nome,desc,preco]

    if newitemCart:
        carrinho.append(newitemCart)
        session['carrinho'] = carrinho
    else:
        print(newitemCart)

    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return redirect(url_for('montar_cart'))

@app.route('/dlt_item_cart', methods=['POST'])
def dlt_item_cart():
    data = request.form
    item = data.get('nome')

    carrinho = session['carrinho']

    for i in carrinho:
        if i[1] == str(item):
            inx = carrinho.index(i)
            carrinho.pop(inx)
            session['carrinho'] = carrinho
            break
    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return redirect(url_for('montar_cart'))

@app.route('/get_qts',methods=['GET'])
def get_qts():
    carrinho = session['carrinho']
    if valid_login() == False:
            return redirect(url_for("login"))
    else:
        return jsonify(carrinho)

def get_max_vndcod():
    if TipConDB == 1:
        db = load_json_db()
        return max([item.get('VND_CODIGO', 0) for item in db.get('vendas', [])], default=0)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT MAX(VND_CODIGO) FROM VENDAS')
    last_vndcod = cur.fetchone()[0]
    if not last_vndcod:
        last_vndcod = 0

    conn.close()
    cur.close()
    return last_vndcod

@app.route('/dlt_venda', methods=['POST'])
def dlt_venda():
    codigo = request.form.get('codigo')

    if TipConDB == 1:
        db = load_json_db()
        for v in db.get('vendas', []):
            if str(v.get('VND_CODIGO')) == str(codigo):
                v['D_E_L_E_T_'] = '*'
        save_json_db(db)
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("dir_vendas", alert="Venda excluída com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
        try:
            cur.execute("UPDATE VENDAS SET D_E_L_E_T_ = %s WHERE VND_CODIGO = %s;", ('*', codigo))
            conn.commit()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for("dir_vendas", alert="Venda excluída com sucesso!"))
    
        except Exception as e:
            conn.rollback()
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return redirect(url_for("dir_vendas", alert=f"Erro ao excluir venda: {e}"))
        
        finally:
            cur.close()
            conn.close()

@app.route('/submit_carrinho', methods = ['POST'])
def submit_carrinho():
    valor_total = 0
    cliente = session['cliente'] 
    carrinho = session['carrinho']
    
    # cliente é [doc,nome,tel,cod]
    # item é [id_item,nome,desc,preco]
    LsCart = [] # cada item é um str 'nome | preço | quantidade'

    for i in carrinho:
        LsCart.append(i[1] + ' | '+str(i[3])+' | ')

        # Pega o nome substituído no carrinho.js para poder recuperar a informação do form com os input hidden que contém as quantidades
        nome = i[1].replace(' ', '_') + '_qt'
        qt = request.form.get(nome)
        LsCart[-1]+=str(qt) # concatena qt à string do item em LsCart
        valor_total += float(i[3])*float(qt)

    bigStrCart = ', '.join(LsCart) # para ficar ["nome1 | preço1 | quantidade1","nome2 | preço2 | quantidade2" .... ]

    ad_vnd_cod = get_max_vndcod()+1
    vnd_cliente = cliente[3]
    vnd_nomecli = cliente[1]
    vnd_tel = cliente[2]
    vnd_doc = cliente[0]

    if TipConDB == 1:
        db = load_json_db()
        nova_venda = {
            'VND_CODIGO': ad_vnd_cod,
            'VND_CLIENTE': vnd_cliente,
            'VND_NOMECLI': vnd_nomecli,
            'VND_TEL': str(vnd_tel),
            'VND_DOC': vnd_doc,
            'VND_NOMEPRD': bigStrCart,
            'VND_TOTAL': valor_total,
            'VND_DATA': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'D_E_L_E_T_': None
        }
        db.setdefault('vendas', []).append(nova_venda)
        save_json_db(db)
        
        session.pop('cliente', None)
        session.pop('carrinho', None)
        return redirect(url_for("dir_vendas", alert="Venda finalizada com sucesso!"))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
    
    # Precisa fazer na query um ALTER TABLE VENDAS ADD VND_DATA DATE
    # Formato da data: YYYY-MM-DD hh:mm:ss
        try:
            cur.execute("""INSERT INTO VENDAS (VND_CODIGO, VND_CLIENTE, VND_NOMECLI, VND_TEL, VND_DOC,
                        VND_NOMEPRD, VND_TOTAL, VND_DATA, D_E_L_E_T_, R_E_C_N_O_, 
                        R_E_C_D_E_L_) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, NULL, 1, NULL);
                        """,(ad_vnd_cod, vnd_cliente, vnd_nomecli, str(vnd_tel), vnd_doc, bigStrCart, valor_total, datetime.now().strftime('%Y-%m-%d %H:%M')))
            conn.commit()
            return redirect(url_for("dir_vendas", alert="Venda finalizada com sucesso!"))
    
        except Exception as e:
            conn.rollback()
            print("Erro ao inserir venda:", e)
            if valid_login() == False:
                return redirect(url_for("login"))
            else:
                return jsonify({"Erro": str(e)})
    
        finally:
            conn.close()
            cur.close()
            session.pop('cliente', None)
            session.pop('carrinho', None)


if __name__ == '__main__':
    app.run(debug=True)