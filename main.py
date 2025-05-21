from flask import Flask, flash, request, redirect, url_for, jsonify, render_template
from flask_cors import CORS
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
CORS(app)  # permite que o frontend chame o backend, especialmente útil localmente
# teste commit
# Rotas das páginas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro_clientes')
def dir_cadastro_clientes():
    return render_template('cadastro_clientes.html')

@app.route('/cadastro_produtos')
def dir_cadastro_produtos():
    return render_template('cadastro_produtos.html')

@app.route('/cadastro_servicos')
def dir_cadastro_servicos():
    return render_template('cadastro_servicos.html')

@app.route('/vendas')
def dir_vendas():
    return render_template('vendas.html')


##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
# Configurações do banco de dados

DB_HOST = "localhost"
DB_NAME = "estetsys"
DB_USER = "estetsys"
DB_PASS = "estetsys"

# Função para conectar ao banco de dados do Estetsys como 
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

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
    except Exception as e:
        conn.rollback()
        render_template("cadastro_clientes.html", alert=f"Erro ao cadastrar: {str(e)}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("cadastro_clientes.html", alert=f"Cliente adicionado com sucesso!",rows=rows)

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
        return render_template("cadastro_clientes.html", alert = "Cliente excluído com sucesso")

    except Exception as e:
        conn.rollback()
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

    except Exception as e:
        conn.rollback()
        render_template("cadastro_produtos.html", alert=f"Erro ao cadastrar: {str(e)}")
    
    finally:
        cur.close()
        conn.close()
    
    return render_template("cadastro_produtos.html", alert="Produto adicionado com sucesso!", rows=rows)

# Rota para deletar um cadastro de um produto
@app.route('/dlt_produto', methods=['POST'])
def dlt_produto():
    codigo = request.form.get('codigo')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE PRODUTO SET D_E_L_E_T_ = %s WHERE PRD_CODIGO = %s;", ('*', codigo))
        conn.commit()
        return render_template("cadastro_produtos.html", alert = "Produto excluído com sucesso")

    except Exception as e:
        conn.rollback()
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
        
        return render_template("cadastro_servicos.html", alert="Serviço adicionado com sucesso!", rows=rows)

    except Exception as e:
        conn.rollback()
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
        return render_template("cadastro_servicos.html", alert = "Servico excluído com sucesso")

    except Exception as e:
        conn.rollback()
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
    
    except:
        mensagem = 'Cliente não encontrado!'
        return redirect(url_for(dir_cadastro_clientes))

    cur.close()
    conn.close()

    return render_template("cadastro_clientes.html", rows=rows)


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
        return render_template("cadastro_servicos.html", rows = rows)

    except Exception as e:
        conn.rollback()
        return render_template("cadastro_servicos.html", alert = f"Erro ao buscar serviço: {e}")
            
    finally:
        cur.close()
        conn.close()

############################# ROTAS PARA VENDA #####################

@app.route("/buscar_cliente")
def buscar_cliente():
    cpf = request.args.get("cpf", "").strip()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT CLI_DOC, CLI_NOME, CLI_TEL FROM CLIENTE WHERE D_E_L_E_T_ IS NULL AND CLI_DOC ILIKE %s LIMIT 1", (f"%{cpf}%",))
    resultado = cur.fetchone()
    
    cur.close()
    conn.close()

    if resultado:
        doc   = resultado[0]
        nome  = resultado[1]
        tel   = resultado[2]
        return jsonify({"nome": nome, "telefone": tel, "doc": doc})
    return jsonify({"erro": "Cliente não encontrado"}), 404

@app.route("/vendas/carrinho")
def init_carrinho():
    nome = request.args.get('cli_nome')
    doc = request.args.get('cli_doc')

    return render_template("carrinho.html", cli_doc = doc, cli_nome = nome )

if __name__ == '__main__':
    app.run(debug=True)