from flask import Flask, flash, request, redirect, url_for, jsonify, render_template
from flask_cors import CORS
import psycopg2
from psycopg2 import sql


app = Flask(__name__)
CORS(app)  # permite que o frontend chame o backend, especialmente útil localmente

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
        response = {"message": "Cliente adicionado com sucesso!"}
        rows = [(ad_CLI_NOME, ad_CLI_DOC, ad_CLI_TEL, ad_CLI_OBSERVA)]
    except Exception as e:
        conn.rollback()
        render_template("cadastro_clientes.html", alert=f"Erro ao cadastrar: {str(e)}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("cadastro_clientes.html", rows=rows)


# Rota para alterar um cadastro de um cliente
@app.route('/alte_cliente', methods=['POST'])
def alte_cliente():
    data = request.form
    alte_CLI_CODIGO   = data.get('clientCPF', '').strip()
    alte_CLI_ENDERECO = data.get('clientAddress', '').strip() + data.get('clientComplement', '').strip() + data.get('clientCEP', '').strip()
    alte_CLI_TEL      = data.get('clientPhone', '').strip()
    alte_CLI_OBSERVA  = data.get('clientNote', '').strip()

    if not alte_CLI_CODIGO or ( not alte_CLI_ENDERECO and not alte_CLI_TEL ):
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de alteração de dados na tabela de cadastro de produtos
        cur.callproc( 'alte_cliente', (alte_CLI_CODIGO, alte_CLI_ENDERECO, alte_CLI_TEL, alte_CLI_OBSERVA ) )
        conn.commit()
        response = {"message": "Cliente alterados com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


# Rota para deletar um cadastro de um produto
@app.route('/dlt_cliente', methods=['POST'])
def dlt_cliente():
    data = request.form
    dlt_CLI_CODIGO  = data.get('clientCPF', '').strip()

    if not dlt_CLI_CODIGO:
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de "deleção" de dados na tabela de cadastro de produtos
        cur.callproc( 'dlt_cliente', (dlt_CLI_CODIGO ) )
        conn.commit()
        response = {"message": "Cliente deletado com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)

########################    Seção de Produtos   ########################

# Rota para adicionar um produto ao cadastro de produtos
@app.route('/add_produto', methods=['POST'])
def add_produto():
    data = request.form
    ad_PRD_CODIGO  = data.get('productName', '').strip()
    ad_PRD_NOME    = data.get('productName', '').strip()
    ad_PRD_PRECO   = float( data.get('productPrice', '').strip() )
    ad_PRD_OBSERVA = data.get('productName', '').strip()

    if not ad_PRD_NOME or not ad_PRD_PRECO:
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de inclusão de dados na tabela de cadastro de produtos
        cur.callproc('add_produto', (ad_PRD_CODIGO, ad_PRD_NOME, ad_PRD_PRECO, ad_PRD_OBSERVA))
        conn.commit()
        response = {"message": "Produto adicionado com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


# Rota para alterar um cadastro de um produto
@app.route('/alte_produto', methods=['POST'])
def alte_produto():
    data = request.form
    alt_PRD_CODIGO  = data.get('productName', '').strip()
    alt_PRD_PRECO   = float( data.get('productPrice', '').strip() )
    alt_PRD_OBSERVA = data.get('productName', '').strip()

    if not alt_PRD_CODIGO or ( not alt_PRD_PRECO and not alt_PRD_OBSERVA ):
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de alteração de dados na tabela de cadastro de produtos
        cur.callproc( 'alte_produto', (alt_PRD_CODIGO, alt_PRD_PRECO, alt_PRD_OBSERVA ) )
        conn.commit()
        response = {"message": "Produto alterados com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


# Rota para deletar um cadastro de um produto
@app.route('/dlt_produto', methods=['POST'])
def dlt_produto():
    data = request.form
    dlt_PRD_CODIGO  = data.get('productName', '').strip()

    if not dlt_PRD_CODIGO:
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de "deleção" de dados na tabela de cadastro de produtos
        cur.callproc( 'dlt_produto', (dlt_PRD_CODIGO ) )
        conn.commit()
        response = {"message": "Produto deletado com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)

########################    Seção de Serviços   ########################

# Rota para adicionar um produto ao cadastro de produtos
@app.route('/add_servico', methods=['POST'])
def add_servico():
    data = request.form
    ad_SRV_CODIGO  = data.get('serviceName', '').strip()
    ad_SRV_NOME    = data.get('serviceName', '').strip()
    ad_SRV_PRECO   = float( data.get('servicePrice', '').strip() )
    ad_SRV_OBSERVA = data.get('serviceName', '').strip()

    if not ad_SRV_NOME or not ad_SRV_PRECO:
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de inclusão de dados na tabela de cadastro de produtos
        cur.callproc('add_servico', (ad_SRV_CODIGO, ad_SRV_NOME, ad_SRV_PRECO, ad_SRV_OBSERVA))
        conn.commit()
        response = {"message": "Serviço adicionado com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


# Rota para alterar um cadastro de um produto
@app.route('/alte_servico', methods=['POST'])
def alte_servico():
    data = request.form
    alte_SRV_CODIGO  = data.get('serviceName', '').strip()
    alte_SRV_PRECO   = float( data.get('servicePrice', '').strip() )
    alte_SRV_OBSERVA = data.get('serviceName', '').strip()

    if not alte_SRV_CODIGO or ( not alte_SRV_PRECO and not alte_SRV_OBSERVA ):
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de alteração de dados na tabela de cadastro de produtos
        cur.callproc( 'alte_servico', (alte_SRV_CODIGO, alte_SRV_PRECO, alte_SRV_OBSERVA ) )
        conn.commit()
        response = {"message": "Serviço alterados com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


# Rota para deletar um cadastro de um produto
@app.route('/dlt_servico', methods=['POST'])
def dlt_servico():
    data = request.form
    dlt_SRV_CODIGO  = data.get('serviceName', '').strip()

    if not dlt_SRV_CODIGO:
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de "deleção" de dados na tabela de cadastro de produtos
        cur.callproc( 'dlt_servico', (dlt_SRV_CODIGO ) )
        conn.commit()
        response = {"message": "Serviço deletado com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################


@app.route('/cad_prod', methods=["POST"])
def cad_prod():

    data = request.form

    nome = data.get('productName', '').strip()
    preco_raw = data.get('productPrice', '').strip()

    if not nome or not preco_raw:
        return "Dados incompletos", 400

    try:
        preco = float(preco_raw)
    except ValueError:
        return "Preço inválido", 400

    return "Produto adicionado com sucesso"

@app.route('/cad_serv', methods=["POST"])
def cad_serv():
    nome = request.form.get('serviceName','').strip()
    preco_raw = request.form.get('servicePrice', '').strip()

    if not nome or not preco_raw:
        return "\nDados incompletos", 400

    try:
        preco = float(preco_raw)
    except ValueError:
        return "Preço inválido", 400

    # services.append([nome, preco])
    return "Serviço adicionado com sucesso"

#################################################################
###################     Consulta de dados       #################

@app.route('/proc_cliente', methods=["GET"])
def proc_cliente():
    data = request.args
    DOC   = data.get('clientCPF', '').strip()
    NOME     = data.get('clientName', '').strip()
    TEL      = data.get('clientPhone', '').strip()
    src = 'SELECT CLI_NOME AS NOME, CLI_DOC AS DOCUMENTO, CLI_TEL AS TELEFONE, CLI_OBSERVA AS OBSERVAÇÕES FROM CLIENTE WHERE D_E_L_E_T_ IS NULL'
    print(NOME)
    # FORMATA PARA BUSCA PARCIAL

    if DOC:
        src += f" AND CLI_DOC ILIKE \'%{DOC}%\'"
    
    if NOME:
        src += f" AND CLI_NOME ILIKE \'%{NOME}%\'"
    
    if TEL:
        src += f" AND CLI_TEL ILIKE \'%{TEL}%\'"
    
    src += ';'

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

    data = request.form
    PRD_CODIGO   = data.get('productID', '').strip()
    PRD_NOME     = data.get('productName', '').strip()
    PRD_OBSERVA      = data.get('productDesc', '').strip()
    
    # FORMATA PARA BUSCA PARCIAL
    src_cod = f"%{PRD_CODIGO}%"
    src_nome = f"%{PRD_NOME}%"
    src_obs = f"%{PRD_OBSERVA}%"

    conn = get_db_connection()
    cur = conn.cursor()

    produto_query = """
        SELECT * FROM PRODUTO 
        WHERE (PRD_CODIGO LIKE %s OR PRD_NOME LIKE %s OR PRD_OBSERVA LIKE %s) AND D_E_L_E_T_ = '';
    """

    cur.execute(produto_query, (src_cod, src_nome, src_obs))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
 

@app.route('/proc_srv', methods=["GET"])
def proc_service():

    data = request.form
    SRV_CODIGO   = data.get('srvID', '').strip()
    SRV_NOME     = data.get('srvName', '').strip()
    SRV_OBSERVA      = data.get('srvDesc', '').strip()
    
    # FORMATA PARA BUSCA PARCIAL
    src_cod = f"%{SRV_CODIGO}%"
    src_nome = f"%{SRV_NOME}%"
    src_obs = f"%{SRV_OBSERVA}%"

    conn = get_db_connection()
    cur = conn.cursor()

    servico_query = """
        SELECT * FROM SERVICO 
        WHERE (SRV_CODIGO LIKE %s OR SRV_NOME LIKE %s OR SRV_OBSERVA LIKE %s) AND D_E_L_E_T_ = '';
    """

    cur.execute(servico_query, (src_cod, src_nome, src_obs))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows



if __name__ == '__main__':
    app.run(debug=True)