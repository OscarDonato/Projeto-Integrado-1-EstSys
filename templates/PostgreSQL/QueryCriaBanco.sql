--------------------------------------------------------------------------------------------------------
--								Banco de Dados EstetSys no PostgreSQL									--
--																										--
--	-------------------------------------------------------------------------------------------------	--
--																										--
--	Descrição:
--	Query para criação das tabelas, triggers e vinculos das tabelas do sistema de gerenciamento de 	--
--	salão "EstetSys".																					--
--																										--
--	Autor:	Oscar Donato																				--
--	Data:	10/04/2025																					--
--------------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------
-- Passo 1:																			--
--	Criação do usuario que vai administrar o banco e vai fazer integração com ele	--
-------------------------------------------------------------------------------------
Create Role estetsys With LOGIN Password 'estetsys' SUPERUSER;


-------------------------------------------------------------------------------------
-- Passo 2:																			--
--	Criação de dominios para facilitar a manutenção do tamanho de um campo, assim	--
--	caso precise alterar um campo fica mais facil.									--
-------------------------------------------------------------------------------------
Create Domain dm_nome Varchar(150)		Not Null	;
Create Domain dm_nmet Varchar(150)					;
Create Domain dm_ende Varchar(150)					;
Create Domain dm_tele Varchar(20)					;
Create Domain dm_docm Varchar(50)					;
Create Domain dm_comp Varchar(50)					;
Create Domain dm_cep  Varchar(50)					;
Create Domain dm_codi Numeric(10) 		Not Null	;
Create Domain dm_cdet Numeric(10) 					;
Create Domain dm_prec Numeric(10, 2)	Default 0	;
Create Domain dm_qtda Numeric(10) 		Default 0	;
Create Domain dm_obse Varchar(500)		Default ''	;
Create Domain dm_delt Varchar(1)					;
Create Domain dm_recn Bigint			Not Null	;
Create Domain dm_rcdl Bigint			Default 0	;
Create Domain dm_grap_codi Varchar(8)	Not Null	;
Create Domain dm_grap_desc Varchar(50)				;
Create Domain dm_grap_tipo Varchar(1)	Check (Value IN ('1', '2', '3'))	;
Create Domain dm_usur_codi Numeric(3)	Not Null	;
Create Domain dm_usur_nome Varchar(100)				;
Create Domain dm_usur_emai Varchar(50)				;


-------------------------------------------------------------------------------------
-- Passo 3:																			--
--	Criação da tabela de cadastro de cliente, de Triggers, Funções e Procedures	--
-------------------------------------------------------------------------------------

-----------
--	3.1 Cria Tabela Cliente
-----------
Create Table CLIENTE(
	CLI_CODIGO		dm_codi Unique,
	CLI_NOME		dm_nome,
	CLI_ENDERECO	dm_ende,
	CLI_COMPLEMENT	dm_comp,
	CLI_CEP			dm_cep ,
	CLI_TEL			dm_tele,
	CLI_DOC			dm_docm,
	CLI_OBSERVA 	dm_obse,
    D_E_L_E_T_		dm_delt,
    R_E_C_N_O_		dm_recn Unique,
    R_E_C_D_E_L_	dm_rcdl,
	
    Primary Key (CLI_CODIGO, R_E_C_N_O_)
);

-----------
--	3.2 Cria Trigger para autoimplementação do recno
-----------
Create Or Replace Function set_recno_client()
Returns Trigger As $$
Begin
    NEW.R_E_C_N_O_ := Coalesce( ( Select Max(R_E_C_N_O_) From CLIENTE ), 0) + 1;
    Return NEW;
End;
$$ Language plpgsql;

Create Trigger trg_set_recno_client
Before Insert On CLIENTE
For Each Row
Execute Function set_recno_client();

-----------
--	3.3 Cria Procedure para inclusão de dados na tabela de clientes
-----------
Create Or Replace Procedure add_cliente(
    ad_CLI_CODIGO		dm_codi,
	ad_CLI_NOME			dm_nome,
	ad_CLI_ENDERECO		dm_ende,
	ad_CLI_COMPLEMENT	dm_comp,
	ad_CLI_CEP			dm_cep ,
	ad_CLI_TEL			dm_tele,
	ad_CLI_DOC			dm_docm,
	ad_CLI_OBSERVA 		dm_obse
)
Language plpgsql As $$
Begin
    Insert Into CLIENTE ( CLI_CODIGO, CLI_NOME, CLI_ENDERECO, CLI_COMPLEMENT, CLI_CEP, CLI_TEL, CLI_DOC, CLI_OBSERVA )
    Values ( ad_CLI_CODIGO, ad_CLI_NOME, ad_CLI_ENDERECO, ad_CLI_COMPLEMENT, ad_CLI_CEP, ad_CLI_TEL, ad_CLI_DOC, ad_CLI_OBSERVA );
End;
$$;

-----------
--	3.4 Cria Procedure para alterar registro dos dados na tabela de clientes
-----------
Create Or Replace Procedure alte_cliente(
	alte_CLI_CODIGO		dm_codi,
	alte_CLI_ENDERECO	dm_ende,
	alte_CLI_COMPLEMENT	dm_comp,
	alte_CLI_CEP		dm_cep ,
	alte_CLI_TEL		dm_tele,
	alte_CLI_OBSERVA 	dm_obse
)
Language plpgsql As $$
Begin

	If IsNull( alte_CLI_ENDERECO, '' ) <> ''
		Then
        Update CLIENTE Set CLI_ENDERECO = alte_CLI_ENDERECO Where CLI_CODIGO = alte_CLI_CODIGO;
    End If;
	
	If IsNull( alte_CLI_COMPLEMENT, '' ) <> ''
		Then
        Update CLIENTE Set CLI_COMPLEMENT = alte_CLI_COMPLEMENT Where CLI_CODIGO = alte_CLI_CODIGO;
    End If;
	
	If IsNull( alte_CLI_CEP, '' ) <> ''
		Then
        Update CLIENTE Set CLI_CEP = alte_CLI_CEP Where CLI_CODIGO = alte_CLI_CODIGO;
    End If;
	
	If IsNull( alte_CLI_TEL, '' ) <> ''
		Then
        Update CLIENTE Set CLI_TEL = alte_CLI_TEL Where CLI_CODIGO = alte_CLI_CODIGO;
    End If;
	
	If IsNull( alte_CLI_OBSERVA, '' ) <> ''
		Then
        Update CLIENTE Set CLI_OBSERVA = alte_CLI_OBSERVA Where CLI_CODIGO = alte_CLI_CODIGO;
    End If;
	
End;
$$;


-----------
--	3.5 Cria Procedure para "deletar" registro dos dados na tabela de clientes
-----------
Create Or Replace Procedure dlt_cliente(
	dlt_CLI_CODIGO		dm_codi
)
Language plpgsql As $$
Begin
    Update CLIENTE Set D_E_L_E_T_ = '*', R_E_C_D_E_L_ = R_E_C_N_O_ Where CLI_CODIGO = dlt_CLI_CODIGO;
End;
$$;

------------------------------------------------------------------------------
--	Fim da parte de Cliente - Fim Passo 2	--
------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-- Passo 4:																			--
--	Criação da tabela de cadastro de produto, de Triggers, Funções e Procedures	--
-------------------------------------------------------------------------------------

-----------
--	4.1 Cria Tabela Produto
-----------
Create Table PRODUTO(
	PRD_CODIGO		dm_codi UNIQUE,
	PRD_NOME		dm_nome,
	PRD_PRECO		dm_prec,
	PRD_OBSERVA 	dm_obse,
    D_E_L_E_T_		dm_delt,
    R_E_C_N_O_		dm_recn UNIQUE,
    R_E_C_D_E_L_	dm_rcdl,
	
    Primary Key (PRD_CODIGO, R_E_C_N_O_)
);

-----------
--	4.2 Cria Trigger para autoimplementação do recno
-----------
Create Or Replace Function set_recno_prod()
Returns Trigger As $$
Begin
    NEW.R_E_C_N_O_ := Coalesce( ( Select Max(R_E_C_N_O_) From PRODUTO ), 0) + 1;
    Return NEW;
End;
$$ Language plpgsql;

Create Trigger trg_set_recno_prod
Before Insert On PRODUTO
For Each Row
Execute Function set_recno_prod();

-----------
--	4.3 Cria Procedure para inclusão de dados na tabela de Produto
-----------
Create Or Replace Procedure add_produto(
    ad_PRD_CODIGO	dm_codi,
	ad_PRD_NOME		dm_nome,
	ad_PRD_PRECO	dm_prec,
	ad_PRD_OBSERVA 	dm_obse
)
Language plpgsql As $$
Begin
    Insert Into PRODUTO ( PRD_CODIGO, PRD_NOME, PRD_PRECO, PRD_OBSERVA )
    Values ( ad_PRD_CODIGO, ad_PRD_NOME, ad_PRD_PRECO, ad_PRD_OBSERVA );
End
$$;

-----------
--	4.4 Cria Procedure para alterar registro dos dados na tabela de Produto
-----------
Create Or Replace Procedure alte_produto(
	alte_PRD_CODIGO		dm_codi,
	alte_PRD_PRECO		dm_prec,
	alte_PRD_OBSERVA 	dm_obse
)
Language plpgsql As $$
Begin

	If IsNull( alte_PRD_PRECO, '' ) <> ''
		Then
        Update PRODUTO Set PRD_PRECO = alte_PRD_PRECO Where PRD_CODIGO = alte_PRD_CODIGO;
    End If;
	
	If IsNull( alte_PRD_OBSERVA, '' ) <> ''
		Then
        Update PRODUTO Set PRD_OBSERVA = alte_PRD_OBSERVA Where PRD_CODIGO = alte_PRD_CODIGO;
    End If;
		
End
$$;


-----------
--	4.5 Cria Procedure para "deletar" registro dos dados na tabela de Produto
-----------
Create Or Replace Procedure dlt_produto(
	dlt_PRD_CODIGO		dm_codi
)
Language plpgsql As $$
Begin
    UPDATE PRODUTO
    SET D_E_L_E_T_ = '*',
        R_E_C_D_E_L_ = R_E_C_N_O_
    WHERE PRD_CODIGO = dlt_PRD_CODIGO;
End;
$$;

------------------------------------------------------------------------------
--	Fim da parte de Produto - Fim Passo 3	--
------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-- Passo 5:																			--
--	Criação da tabela de cadastro de produto, de Triggers, Funções e Procedures	--
-------------------------------------------------------------------------------------

-----------
--	5.1 Cria Tabela Servico
-----------
Create Table SERVICO(
	SRV_CODIGO		dm_codi UNIQUE,
	SRV_NOME		dm_nome,
	SRV_PRECO		dm_prec,
	SRV_OBSERVA 	dm_obse,
    D_E_L_E_T_		dm_delt,
    R_E_C_N_O_		dm_recn UNIQUE,
    R_E_C_D_E_L_	dm_rcdl,
	
    Primary Key (SRV_CODIGO, R_E_C_N_O_)
);

Create Or Replace Function set_recno_servico()
Returns Trigger As $$
Begin
    NEW.R_E_C_N_O_ := Coalesce( ( Select Max(R_E_C_N_O_) From SERVICO ), 0) + 1;
     Return NEW;
End;
$$ Language plpgsql;

Create Trigger trg_set_recno_servico
Before Insert On SERVICO
For Each Row
Execute Function set_recno_servico();


-----------
--	5.2 Cria Procedure para inclusão de dados na tabela de Servico
-----------
Create Or Replace Procedure add_servico(
    ad_SRV_CODIGO	dm_codi,
	ad_SRV_NOME		dm_nome,
	ad_SRV_PRECO	dm_prec,
	ad_SRV_OBSERVA 	dm_obse
)
Language plpgsql As $$
Begin
    Insert Into SERVICO ( SRV_CODIGO, SRV_NOME, SRV_PRECO, SRV_OBSERVA )
    Values ( ad_SRV_CODIGO, ad_SRV_NOME, ad_SRV_PRECO, ad_SRV_OBSERVA );
End
$$;

-----------
--	5.3 Cria Procedure para alterar registro dos dados na tabela de Servico
-----------
Create Or Replace Procedure alte_servico(
	alte_SRV_CODIGO		dm_codi,
	alte_SRV_PRECO		dm_prec,
	alte_SRV_OBSERVA 	dm_obse
)
Language plpgsql As $$
Begin

	If IsNull( alte_SRV_PRECO, '' ) <> ''
		Then
        Update SERVICO Set SRV_PRECO = alte_SRV_PRECO Where SRV_CODIGO = alte_SRV_CODIGO;
    End If;
	
	If IsNull( alte_SRV_OBSERVA, '' ) <> ''
		Then
        Update SERVICO Set SRV_OBSERVA = alte_SRV_OBSERVA Where SRV_CODIGO = alte_SRV_CODIGO;
    End If;
		
End;
$$;


-----------
--	5.4 Cria Procedure para "deletar" registro dos dados na tabela de Servico
-----------
Create Or Replace Procedure dlt_servico(
	dlt_SRV_CODIGO		dm_codi
)
Language plpgsql As $$
Begin
    Update SERVICO Set D_E_L_E_T_ = '*', R_E_C_D_E_L_ = R_E_C_N_O_ Where SRV_CODIGO = dlt_SRV_CODIGO;
End;
$$;

------------------------------------------------------------------------------
--	Fim da parte de Servico - Fim Passo 4	--
------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-- Passo 6:																			--
--	Criação da tabela de cadastro de Vendas e da trigger para vincular o recno	--
-------------------------------------------------------------------------------------

-----------
--	6.1 Cria Tabela Vendas
-----------
Create Table VENDAS(
	VND_CODIGO		dm_codi UNIQUE,
	
	VND_CLIENTE		dm_cdet,
	VND_NOMECLI		dm_nmet,
	VND_TEL			dm_tele,
	VND_DOC			dm_docm,
	
	VND_PRODUTO		dm_cdet,
	VND_NOMEPRD		dm_nmet,
	VND_PRECPRD		dm_prec,
	VND_QTDAPRD		dm_qtda,
	VND_TOTAPRD		dm_prec,
	
	VND_SERVICO		dm_cdet,
	VND_NOMESRV		dm_nmet,
	VND_PRECSRV		dm_prec,
	VND_QTDASRV		dm_qtda,
	VND_TOTASRV		dm_prec,

	VND_TOTAL		dm_prec,	
	VND_OBSERVA 	dm_obse,
	
    D_E_L_E_T_		dm_delt,
    R_E_C_N_O_		Bigserial UNIQUE Not Null,
    R_E_C_D_E_L_	dm_rcdl,
	
    Primary Key (VND_CODIGO, R_E_C_N_O_),
	Foreign Key (VND_CLIENTE) References CLIENTE(CLI_CODIGO),
	Foreign Key (VND_PRODUTO) References PRODUTO(PRD_CODIGO),
	Foreign Key (VND_SERVICO) References SERVICO(SRV_CODIGO)
);


-----------
--	6.2 Cria Procedure para inclusão de dados na tabela de Produto
-----------
Create Or Replace Procedure add_venda(
	ad_VND_CODIGO		dm_codi,
	ad_VND_CLIENTE		dm_cdet,
	ad_VND_NOMECLI		dm_nmet,
	ad_VND_TEL			dm_tele,
	ad_VND_DOC			dm_docm,
	ad_VND_PRODUTO		dm_cdet,
	ad_VND_NOMEPRD		dm_nmet,
	ad_VND_PRECPRD		dm_prec,
	ad_VND_QTDAPRD		dm_qtda,
	ad_VND_TOTAPRD		dm_prec,
	ad_VND_SERVICO		dm_cdet,
	ad_VND_NOMESRV		dm_nmet,
	ad_VND_PRECSRV		dm_prec,
	ad_VND_QTDASRV		dm_qtda,
	ad_VND_TOTASRV		dm_prec,
	ad_VND_TOTAL		dm_prec,	
	ad_VND_OBSERVA 	dm_obse
)
Language plpgsql As $$
Begin
    Insert Into VENDAS ( 
		VND_CODIGO,
		VND_CLIENTE,
		VND_NOMECLI,
		VND_TEL,
		VND_DOC,
		VND_PRODUTO,
		VND_NOMEPRD,
		VND_PRECPRD,
		VND_QTDAPRD,
		VND_TOTAPRD,
		VND_SERVICO,
		VND_NOMESRV,
		VND_PRECSRV,
		VND_QTDASRV,
		VND_TOTASRV,
		VND_TOTAL,	
		VND_OBSERVA 	
	)
    Values ( 
		ad_VND_CODIGO,
		ad_VND_CLIENTE,
		ad_VND_NOMECLI,
		ad_VND_TEL,
		ad_VND_DOC,
		ad_VND_PRODUTO,
		ad_VND_NOMEPRD,
		ad_VND_PRECPRD,
		ad_VND_QTDAPRD,
		ad_VND_TOTAPRD,
		ad_VND_SERVICO,
		ad_VND_NOMESRV,
		ad_VND_PRECSRV,
		ad_VND_QTDASRV,
		ad_VND_TOTASRV,
		ad_VND_TOTAL,	
		ad_VND_OBSERVA 	
	);
End;
$$;

-----------
--	6.3 Cria Procedure para alterar registro dos dados na tabela de Produto
-----------
Create Or Replace Procedure alte_venda(
	alte_VND_CODIGO		dm_codi,
	alte_VND_TEL		dm_tele,
	alte_VND_DOC		dm_docm,
	alte_VND_PRODUTO	dm_cdet,
	alte_VND_NOMEPRD	dm_nmet,
	alte_VND_PRECPRD	dm_prec,
	alte_VND_QTDAPRD	dm_qtda,
	alte_VND_TOTAPRD	dm_prec,
	alte_VND_SERVICO	dm_cdet,
	alte_VND_NOMESRV	dm_nmet,
	alte_VND_PRECSRV	dm_prec,
	alte_VND_QTDASRV	dm_qtda,
	alte_VND_TOTASRV	dm_prec,
	alte_VND_TOTAL		dm_prec,	
	alte_VND_OBSERVA 	dm_obse
	
)
Language plpgsql As $$
Begin
	
	If IsNull( alte_VND_TEL, '' ) <> ''
		Then
        Update VENDAS Set VND_TEL = alte_VND_TEL Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_DOC, '' ) <> ''
		Then
        Update VENDAS Set VND_DOC = alte_VND_DOC Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_PRODUTO, '' ) <> ''
		Then
        Update VENDAS Set VND_PRODUTO = alte_VND_PRODUTO Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_NOMEPRD, '' ) <> ''
		Then
        Update VENDAS Set VND_NOMEPRD = alte_VND_NOMEPRD Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_PRECPRD, '' ) <> ''
		Then
        Update VENDAS Set VND_PRECPRD = alte_VND_PRECPRD Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_QTDAPRD, '' ) <> ''
		Then
        Update VENDAS Set VND_QTDAPRD = alte_VND_QTDAPRD Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_TOTAPRD, '' ) <> ''
		Then
        Update VENDAS Set VND_TOTAPRD = alte_VND_TOTAPRD Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_SERVICO, '' ) <> ''
		Then
        Update VENDAS Set VND_SERVICO = alte_VND_SERVICO Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_NOMESRV, '' ) <> ''
		Then
        Update VENDAS Set VND_NOMESRV = alte_VND_NOMESRV Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_PRECSRV, '' ) <> ''
		Then
        Update VENDAS Set VND_PRECSRV = alte_VND_PRECSRV Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_QTDASRV, '' ) <> ''
		Then
        Update VENDAS Set VND_QTDASRV = alte_VND_QTDASRV Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_TOTASRV, '' ) <> ''
		Then
        Update VENDAS Set VND_TOTASRV = alte_VND_TOTASRV Where VND_CODIGO = alte_VND_CODIGO;
    End If;
	
	If IsNull( alte_VND_TOTAL, '' ) <> ''
		Then
        Update VENDAS Set VND_TOTAL = alte_VND_TOTAL Where VND_CODIGO = alte_VND_CODIGO;
    End If;
		
	If IsNull( alte_VND_OBSERVA, '' ) <> ''
		Then
        Update VENDAS Set VND_OBSERVA = alte_VND_OBSERVA Where VND_CODIGO = alte_VND_CODIGO;
    End If;
			
End;
$$;


-----------
--	6.4 Cria Procedure para "deletar" registro dos dados na tabela de Produto
-----------
Create Or Replace Procedure dlt_venda(
    dlt_VND_CODIGO		dm_codi
)
Language plpgsql As $$
Begin
    Update VENDAS Set D_E_L_E_T_ = '*', R_E_C_D_E_L_ = R_E_C_N_O_ Where VND_CODIGO = dlt_VND_CODIGO;
End;
$$;

------------------------------------------------------------------------------
--	Fim da parte de Produto - Fim Passo 5	--
------------------------------------------------------------------------------


-------------------------------------------------------------------------
-------------------------------------------------------------------------
-------------------------------------------------------------------------


-------------------------------------------------------------------------
-------------------------------------------------------------------------
-------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-- Passo 7:																			--
--	Criação da tabela de cadastro de grupo de acesso, de Triggers, Funções e Procedures	--
-------------------------------------------------------------------------------------

-----------
--	7.1 Cria Tabela GRUPO_ACESSO
-----------
Create Table GRUPO_ACESSO(
	GRP_CODIGO		dm_grap_codi Unique,
	GRP_DESCRICAO	dm_grap_desc,
	GRP_TIPOACESSO	dm_grap_tipo,
    D_E_L_E_T_		dm_delt,
    R_E_C_N_O_		dm_recn Unique,
    R_E_C_D_E_L_	dm_rcdl,
	
    Primary Key (GRP_CODIGO, R_E_C_N_O_)
);

-----------
--	7.2 Cria Trigger para autoimplementação do recno
-----------
Create Or Replace Function set_recno_grupo_acesso()
Returns Trigger As $$
Begin
    NEW.R_E_C_N_O_ := Coalesce( ( Select Max(R_E_C_N_O_) From GRUPO_ACESSO ), 0) + 1;
    Return NEW;
End;
$$ Language plpgsql;

Create Trigger trg_set_recno_grupo_acesso
Before Insert On GRUPO_ACESSO
For Each Row
Execute Function set_recno_grupo_acesso();

-----------
--	7.3 Cria Procedure para inclusão de dados na tabela de GRUPO_ACESSO
-----------
Create Or Replace Procedure add_grupo_acesso(
    ad_GRP_CODIGO		dm_grap_codi,
	ad_GRP_DESCRICAO	dm_grap_desc,
	ad_GRP_TIPOACESSO	dm_grap_tipo
)
Language plpgsql As $$
Begin
    Insert Into GRUPO_ACESSO ( GRP_CODIGO, GRP_DESCRICAO, GRP_TIPOACESSO )
    Values ( ad_GRP_CODIGO, ad_GRP_DESCRICAO, ad_GRP_TIPOACESSO );
End;
$$;

-----------
--	7.4 Cria Procedure para alterar registro dos dados na tabela de GRUPO_ACESSO
-----------
Create Or Replace Procedure alte_grupo_acesso(
	alte_GRP_CODIGO		dm_grap_codi,
	alte_GRP_DESCRICAO	dm_grap_desc,
	alte_GRP_TIPOACESSO	dm_grap_tipo
)
Language plpgsql As $$
Begin

	If IsNull( alte_GRP_DESCRICAO, '' ) <> ''
		Then
        Update GRUPO_ACESSO Set GRP_DESCRICAO = alte_GRP_DESCRICAO Where GRP_CODIGO = alte_GRP_CODIGO;
    End If;
	
	If IsNull( alte_GRP_TIPOACESSO, '' ) <> ''
		Then
        Update GRUPO_ACESSO Set GRP_TIPOACESSO = alte_GRP_TIPOACESSO Where GRP_CODIGO = alte_GRP_CODIGO;
    End If;
	
End;
$$;


-----------
--	7.5 Cria Procedure para "deletar" registro dos dados na tabela de GRUPO_ACESSO
-----------
Create Or Replace Procedure dlt_grupo_acesso(
	dlt_GRP_CODIGO		dm_grap_codi
)
Language plpgsql As $$
Begin
    Update GRUPO_ACESSO Set D_E_L_E_T_ = '*', R_E_C_D_E_L_ = R_E_C_N_O_ Where GRP_CODIGO = dlt_GRP_CODIGO;
End;
$$;

------------------------------------------------------------------------------
--	Fim da parte de GRUPO_ACESSO - Fim Passo 7	--
------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
-- Passo 8:																			--
--	Criação da tabela de cadastro de usuários, de Triggers, Funções e Procedures	--
-------------------------------------------------------------------------------------

-----------
--	8.1 Cria Tabela USUARIOS
-----------
Create Table USUARIOS(
	USR_CODIGO		dm_usur_codi Unique,
	USR_NOME		dm_usur_nome,
	USR_EMAIL		dm_usur_emai,
	USR_TELEFONE	dm_tele,
	USR_GRUPO		dm_grap_codi,
    D_E_L_E_T_		dm_delt,
    R_E_C_N_O_		dm_recn Unique,
    R_E_C_D_E_L_	dm_rcdl,
	
    Primary Key (USR_CODIGO, R_E_C_N_O_),
	Foreign Key (USR_GRUPO) References GRUPO_ACESSO(GRP_CODIGO)
);

-----------
--	8.2 Cria Trigger para autoimplementação do recno
-----------
Create Or Replace Function set_recno_usuarios()
Returns Trigger As $$
Begin
    NEW.R_E_C_N_O_ := Coalesce( ( Select Max(R_E_C_N_O_) From USUARIOS ), 0) + 1;
    Return NEW;
End;
$$ Language plpgsql;

Create Trigger trg_set_recno_usuarios
Before Insert On USUARIOS
For Each Row
Execute Function set_recno_usuarios();

-----------
--	8.3 Cria Procedure para inclusão de dados na tabela de USUARIOS
-----------
Create Or Replace Procedure add_usuario(
    ad_USR_CODIGO		dm_usur_codi,
	ad_USR_NOME			dm_usur_nome,
	ad_USR_EMAIL		dm_usur_emai,
	ad_USR_TELEFONE		dm_tele,
	ad_USR_GRUPO		dm_grap_codi
)
Language plpgsql As $$
Begin
    Insert Into USUARIOS ( USR_CODIGO, USR_NOME, USR_EMAIL, USR_TELEFONE, USR_GRUPO )
    Values ( ad_USR_CODIGO, ad_USR_NOME, ad_USR_EMAIL, ad_USR_TELEFONE, ad_USR_GRUPO );
End;
$$;

-----------
--	8.4 Cria Procedure para alterar registro dos dados na tabela de USUARIOS
-----------
Create Or Replace Procedure alte_usuario(
	alte_USR_CODIGO		dm_usur_codi,
	alte_USR_NOME		dm_usur_nome,
	alte_USR_EMAIL		dm_usur_emai,
	alte_USR_TELEFONE	dm_tele,
	alte_USR_GRUPO		dm_grap_codi
)
Language plpgsql As $$
Begin

	If IsNull( alte_USR_NOME, '' ) <> ''
		Then
        Update USUARIOS Set USR_NOME = alte_USR_NOME Where USR_CODIGO = alte_USR_CODIGO;
    End If;
	
	If IsNull( alte_USR_EMAIL, '' ) <> ''
		Then
        Update USUARIOS Set USR_EMAIL = alte_USR_EMAIL Where USR_CODIGO = alte_USR_CODIGO;
    End If;
	
	If IsNull( alte_USR_TELEFONE, '' ) <> ''
		Then
        Update USUARIOS Set USR_TELEFONE = alte_USR_TELEFONE Where USR_CODIGO = alte_USR_CODIGO;
    End If;
	
	If IsNull( alte_USR_GRUPO, '' ) <> ''
		Then
        Update USUARIOS Set USR_GRUPO = alte_USR_GRUPO Where USR_CODIGO = alte_USR_CODIGO;
    End If;
	
End;
$$;


-----------
--	8.5 Cria Procedure para "deletar" registro dos dados na tabela de USUARIOS
-----------
Create Or Replace Procedure dlt_usuario(
	dlt_USR_CODIGO		dm_usur_codi
)
Language plpgsql As $$
Begin
    Update USUARIOS Set D_E_L_E_T_ = '*', R_E_C_D_E_L_ = R_E_C_N_O_ Where USR_CODIGO = dlt_USR_CODIGO;
End;
$$;

------------------------------------------------------------------------------
--	Fim da parte de USUARIOS - Fim Passo 8	--
------------------------------------------------------------------------------


-------------------------------------------------------------------------
-------------------------------------------------------------------------
-------------------------------------------------------------------------


-------------------------------------------------------------------------
--- Exemplos															--
-------------------------------------------------------------------------
--	Select * From CLIENTE Where D_E_L_E_T_ = '';
--	Select * From PRODUTO Where D_E_L_E_T_ = '';
--	Select * From SERVICO Where D_E_L_E_T_ = '';
--	Select * From VENDAS  Where D_E_L_E_T_ = ''
--	Select * From GRUPO_ACESSO  Where D_E_L_E_T_ = ''
--	Select * From USUARIOS  Where D_E_L_E_T_ = ''
-------------------------------------------------------------------------
-------------------------------------------------------------------------
-------------------------------------------------------------------------
