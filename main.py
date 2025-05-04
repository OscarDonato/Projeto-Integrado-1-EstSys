from flask import Flask, request, redirect, url_for, jsonify, render_template
from flask_cors import CORS
import psycopg2
from psycopg2 import sql


produtos = [{'desc':"banana",'preco': 12.8, 'tipo':'fruta'},{'desc':"repolho",'preco': 12.8, 'tipo':'fruta'}]
#services = []

app = Flask(__name__)
CORS(app)  # permite que o frontend chame o backend, especialmente útil localmente

# Rotas das páginas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastros')
def dir_cadastros():
    return render_template('cadastros.html')

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

########################    Seção de Cliente   ########################

# Rota para adicionar um produto ao cadastro de produtos
@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    data = request.form
    ad_CLI_CODIGO   = data.get('clientCPF', '').strip()
    ad_CLI_NOME     = data.get('clientName', '').strip()
    ad_CLI_ENDERECO	= data.get('clientAddress', '').strip() + data.get('clientComplement', '').strip() + data.get('clientCEP', '').strip()
    ad_CLI_TEL      = data.get('clientPhone', '').strip()
    ad_CLI_DOC      = data.get('clientCPF', '').strip()
    ad_CLI_OBSERVA  = data.get('clientNote', '').strip()

    if not ad_CLI_CODIGO or not ad_CLI_NOME or not ad_CLI_ENDERECO or not ad_CLI_TEL or not ad_CLI_DOC:
        return "Dados incompletos", 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Chamando a procedure de inclusão de dados na tabela de cadastro de produtos
        cur.callproc( 'add_cliente', ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA ))
        conn.commit()
        response = {"message": "Cliente adicionado com sucesso!"}
    except Exception as e:
        response = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response)


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
    data = request.form
    CLI_CODIGO   = data.get('clientCPF', '').strip()
    CLI_NOME     = data.get('clientName', '').strip()
    CLI_TEL      = data.get('clientPhone', '').strip()
    
    # FORMATA PARA BUSCA PARCIAL
    src_cod = f"%{CLI_CODIGO}%"
    src_nome = f"%{CLI_NOME}%"
    src_tel = f"%{CLI_TEL}%"

    conn = get_db_connection()
    cur = conn.cursor()

    cliente_query = """
        SELECT * FROM CLIENTE 
        WHERE CLI_CODIGO LIKE %s OR CLI_NOME LIKE %s OR CLI_TEL LIKE %s;
    """

    cur.execute(cliente_query, (src_cod, src_nome, src_tel))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)


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
        WHERE PRD_CODIGO LIKE %s OR PRD_NOME LIKE %s OR PRD_OBSERVA LIKE %s;
    """

    cur.execute(produto_query, (src_cod, src_nome, src_obs))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)
 

@app.route('/proc_srv', methods=["GET"])
def proc_service():

    data = request.form
    SRV_CODIGO   = data.get('productID', '').strip()
    SRV_NOME     = data.get('productName', '').strip()
    SRV_OBSERVA      = data.get('productDesc', '').strip()
    
    # FORMATA PARA BUSCA PARCIAL
    src_cod = f"%{SRV_CODIGO}%"
    src_nome = f"%{SRV_NOME}%"
    src_obs = f"%{SRV_OBSERVA}%"

    conn = get_db_connection()
    cur = conn.cursor()

    servico_query = """
        SELECT * FROM SERVICO 
        WHERE SRV_CODIGO LIKE %s OR SRV_NOME LIKE %s OR SRV_OBSERVA LIKE %s;
    """

    cur.execute(servico_query, (src_cod, src_nome, src_obs))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)



if __name__ == '__main__':
    app.run(debug=True)