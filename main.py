from flask import Flask, request, redirect, url_for, jsonify, render_template, session
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

app.secret_key = '19i320od$'
global login_key
login_key = 'G15estetsys'
# teste commit
# Rotas das páginas

DB_HOST = "localhost"
DB_NAME = "estetsys"
DB_USER = "estetsys"
DB_PASS = "estetsys"

# Função para conectar ao banco de dados do Estetsys como 
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
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

@app.route('/cadastro_clientes')
def dir_cadastro_clientes():
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        return render_template('cadastro_clientes.html')

@app.route('/cadastro_produtos')
def dir_cadastro_produtos():
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        return render_template('cadastro_produtos.html')

@app.route('/cadastro_servicos')
def dir_cadastro_servicos():
    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        return render_template('cadastro_servicos.html')

@app.route('/vendas')
def dir_vendas():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT VND_CODIGO, VND_NOMECLI, VND_DOC, VND_NOMEPRD, VND_TOTAL, TO_CHAR(VND_DATA, 'YYYY-MM-DD HH24:MI') FROM VENDAS WHERE d_e_l_e_t_ IS NULL ORDER BY VND_DATA DESC;")
    vendas = cur.fetchall()

    cur.close()
    conn.close()

    if valid_login() == False:
        return redirect(url_for("login"))
    else:
        return render_template('vendas.html', rows=vendas)

##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
# Configurações do banco de dados



# Função para determinar o CLI_CODIGO MÁXIMO

def max_cli_cod():
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
            return render_template("cadastro_clientes.html", alert="Dados incompletos", rows=[])
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de inclusão de dados na tabela de cadastro de produtos
        # cur.callproc( 'add_cliente', ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA ))
        
        # Utilizar o comando abaixo enquanto a procedure não é consertada
        cur.execute( "Insert Into CLIENTE ( CLI_CODIGO, CLI_NOME, CLI_ENDERECO, CLI_COMPLEMENT, CLI_CEP, CLI_TEL, CLI_DOC, CLI_OBSERVA, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, %s, %s, %s, %s, NULL, 1, NULL);", ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_COMPLEMENT, ad_CLI_CEP, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA ))
        conn.commit()
        rows = [(ad_CLI_NOME, ad_CLI_DOC, ad_CLI_TEL, ad_CLI_OBSERVA)]
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_clientes.html", alert=f"Cliente adicionado com sucesso!",rows=rows)
    
    except Exception as e:
        conn.rollback()

        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_clientes.html", alert=f"Erro ao cadastrar: {str(e)}")
    finally:
        cur.close()
        conn.close()
    
    

# Rota para deletar um cadastro de um cliente
@app.route('/dlt_cliente', methods=['POST'])
def dlt_cliente():
    codigo = request.form.get('codigo')
    codigo = str(codigo)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE CLIENTE SET D_E_L_E_T_ = %s WHERE CLI_DOC = %s;", ('*', codigo))
        conn.commit()

        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_clientes.html", alert = "Cliente excluído com sucesso")

    except Exception as e:
        conn.rollback()
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_clientes.html",alert = f"Erro ao excluir cliente: {e}")
    finally:
        cur.close()
        conn.close()

########################    Seção de Produtos   ########################

def max_prd_cod():
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
            return render_template("cadastro_produtos.html", alert="Dados incompletos", rows=[])
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de inclusão de dados na tabela de cadastro de produtos
        # cur.callproc( 'add_cliente', ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA ))
        
        # Utilizar o comando abaixo enquanto a procedure não é consertada
        cur.execute( "Insert Into PRODUTO ( PRD_CODIGO, PRD_NOME, PRD_PRECO, PRD_OBSERVA, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, NULL, 1, NULL);", ( ad_PRD_CODIGO, ad_PRD_NOME, ad_PRD_PRECO, ad_PRD_OBSERVA))
        conn.commit()
        rows = [(ad_PRD_CODIGO, ad_PRD_NOME, ad_PRD_PRECO, ad_PRD_OBSERVA)]
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_produtos.html", alert="Produto adicionado com sucesso!", rows=rows)

    except Exception as e:
        conn.rollback()
        render_template("cadastro_produtos.html", alert=f"Erro ao cadastrar: {str(e)}")
    
    finally:
        cur.close()
        conn.close()
    
    

# Rota para deletar um cadastro de um produto
@app.route('/dlt_produto', methods=['POST'])
def dlt_produto():
    codigo = request.form.get('codigo')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE PRODUTO SET D_E_L_E_T_ = %s WHERE PRD_CODIGO = %s;", ('*', codigo))
        conn.commit()
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_produtos.html", alert = "Produto excluído com sucesso")

    except Exception as e:
        conn.rollback()
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_produtos.html",alert = f"Erro ao excluir produto: {e}")
    
    finally:
        cur.close()
        conn.close()

########################    Seção de Serviços   ########################

def max_srv_cod():
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
            return render_template("cadastro_servicos.html", alert="Dados incompletos", rows=[])
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de inclusão de dados na tabela de cadastro de produtos
        # cur.callproc( 'add_cliente', ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA ))
        
        # Utilizar o comando abaixo enquanto a procedure não é consertada
        cur.execute( "Insert Into SERVICO ( SRV_CODIGO, SRV_NOME, SRV_PRECO, SRV_OBSERVA, D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) Values ( %s, %s, %s, %s, NULL, 1, NULL);", ( ad_SRV_CODIGO, ad_SRV_NOME, ad_SRV_PRECO, ad_SRV_OBSERVA))
        conn.commit()
        rows = [(ad_SRV_CODIGO, ad_SRV_NOME, ad_SRV_PRECO, ad_SRV_OBSERVA)]
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html", alert="Serviço adicionado com sucesso!", rows=rows)

    except Exception as e:
        conn.rollback()
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html", alert=f"Erro ao cadastrar: {str(e)}")
    
    finally:
        cur.close()
        conn.close()

@app.route('/dlt_servico', methods=['POST'])
def dlt_servico():
    codigo = request.form.get('codigo')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE SERVICO SET D_E_L_E_T_ = %s WHERE SRV_CODIGO = %s;", ('*', codigo))
        conn.commit()

        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html", alert = "Servico excluído com sucesso")

    except Exception as e:
        conn.rollback()
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html",alert = f"Erro ao excluir produto: {e}")
    
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
    src = 'SELECT CLI_NOME AS NOME, CLI_DOC AS DOCUMENTO, CLI_TEL AS TELEFONE, CLI_OBSERVA AS OBSERVAÇÕES FROM CLIENTE WHERE D_E_L_E_T_ IS NULL'
    # FORMATA PARA BUSCA PARCIAL

    if DOC:
        src += f" AND CLI_DOC ILIKE \'%{DOC}%\'"
    
    if NOME:
        src += f" AND CLI_NOME ILIKE \'%{NOME}%\'"
    
    if TEL:
        src += f" AND CLI_TEL ILIKE \'%{TEL}%\'"
    
    src += ' ORDER BY CLI_NOME ASC;'

    conn = get_db_connection()
    cur = conn.cursor()


    try:
        cur.execute(src)
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
            return redirect(url_for(dir_cadastro_clientes))

    finally:
        cur.close()
        conn.close()

@app.route('/proc_prd', methods=["GET"])
def proc_produto():
    data = request.args
    CODIGO   = data.get('productID', '').strip()
    NOME     = data.get('productName', '').strip()
    OBSERVA  = data.get('productDesc', '').strip()
    src = 'SELECT PRD_CODIGO AS Código, PRD_NOME AS Nome, PRD_PRECO AS Preço, PRD_OBSERVA AS DESCRIÇÃO FROM PRODUTO WHERE D_E_L_E_T_ IS NULL'

    # FORMATA PARA BUSCA PARCIAL
    if CODIGO:
        src += f" AND PRD_CODIGO = {CODIGO}"
    
    if NOME:
        src += f" AND PRD_NOME ILIKE \'%{NOME}%\'"
    
    if OBSERVA:
        src += f" AND PRD_OBSERVA ILIKE \'%{OBSERVA}%\'"

    src += ' ORDER BY PRD_NOME ASC;'


    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(src)
        rows = cur.fetchall()

    except:
        mensagem = 'Produto não encontrado!'
        return redirect(url_for(dir_cadastro_produtos))

    cur.close()
    conn.close()

    return render_template("cadastro_produtos.html", rows=rows)
 
@app.route('/proc_srv', methods=["GET"])
def proc_service():

    data = request.args
    SRV_CODIGO   = data.get('srvID', '').strip()
    SRV_NOME     = data.get('serviceName', '').strip()
    SRV_OBSERVA      = data.get('serviceDesc', '').strip()
    
    # FORMATA PARA BUSCA PARCIAL
    src = "SELECT SRV_CODIGO, SRV_NOME, SRV_PRECO, SRV_OBSERVA FROM SERVICO WHERE D_E_L_E_T_ IS NULL"

    if SRV_CODIGO:
        src += f" AND SRV_CODIGO = {SRV_CODIGO}"

    if SRV_NOME:
        src += f" AND SRV_NOME ILIKE \'{SRV_NOME}\'"
    
    if SRV_OBSERVA:
        src += f" AND SRV_OBSERVA ILIKE \'{SRV_OBSERVA}\'"
    
    src += " ORDER BY SRV_NOME ASC"

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(src)
        rows = cur.fetchall()

        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html", rows = rows)

    except Exception as e:
        conn.rollback()
        
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("cadastro_servicos.html", alert = f"Erro ao buscar serviço: {e}")
            
    finally:
        cur.close()
        conn.close()

####################################################################
############################# ROTAS PARA VENDA #####################

@app.route("/buscar_cliente")
def buscar_cliente():
    cpf = request.args.get("cpf", "").strip()

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

    conn = get_db_connection()
    cur = conn.cursor()

    if tipo == 'produto':
        cur.execute("SELECT PRD_CODIGO AS id, PRD_NOME AS nome, PRD_OBSERVA AS observa, PRD_PRECO AS preco FROM produto WHERE PRD_NOME ILIKE %s OR PRD_CODIGO::text ILIKE %s",
                    (f"%{termo}%", f"%{termo}%"))
    else:
        cur.execute("SELECT SRV_CODIGO AS id, SRV_NOME AS nome, SRV_OBSERVA AS observa, SRV_PRECO AS preco FROM servico WHERE SRV_NOME ILIKE %s OR SRV_CODIGO::text ILIKE %s",
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

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE VENDAS SET D_E_L_E_T_ = %s WHERE VND_CODIGO = %s;", ('*', codigo))
        conn.commit()
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("dir_vendas"))

    except Exception as e:
        conn.rollback()
        if valid_login() == False:
            return redirect(url_for("login"))
        else:
            return render_template("vendas.html",alert = f"Erro ao excluir produto: {e}")
    
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

    conn = get_db_connection()
    cur = conn.cursor()

# Precisa fazer na query um ALTER TABLE VENDAS ADD VND_DATA DATE
# Formato da data: YYYY-MM-DD hh:mm:ss
    try:
        cur.execute("""INSERT INTO VENDAS (VND_CODIGO, VND_CLIENTE, VND_NOMECLI, VND_TEL, VND_DOC,
                    VND_NOMEPRD, VND_TOTAL, D_E_L_E_T_, R_E_C_N_O_, 
                    R_E_C_D_E_L_) VALUES ( %s, %s, %s, %s, %s, %s, %s, NULL, 1, NULL);
                    """,(ad_vnd_cod, vnd_cliente, vnd_nomecli, str(vnd_tel), vnd_doc, bigStrCart, valor_total))
        conn.commit()
        return redirect(url_for("dir_vendas"))

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