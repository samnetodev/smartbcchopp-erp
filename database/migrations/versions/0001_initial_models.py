"""initial_models

Revision ID: 0001
Revises:
Create Date: 2026-07-30 12:00:00.000000

"""
from alembic import op

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE alertanivel AS ENUM('info', 'warning', 'critical')")
    op.execute("CREATE TYPE auditoriaacao AS ENUM('C', 'U', 'D')")
    op.execute("CREATE TYPE baixatipo AS ENUM('recebimento', 'pagamento')")
    op.execute("CREATE TYPE boletostatus AS ENUM('gerado', 'registrado', 'vencido', 'pago', 'cancelado')")
    op.execute("CREATE TYPE categoriacnh AS ENUM('A', 'B', 'C', 'D', 'E', 'AB', 'AC', 'AD', 'AE')")
    op.execute("CREATE TYPE chopeirastatus AS ENUM('disponivel', 'instalada', 'manutencao', 'baixada')")
    op.execute("CREATE TYPE chopeiratipo AS ENUM('chopeira', 'torre', 'cooler', 'torneira')")
    op.execute("CREATE TYPE clientestatus AS ENUM('ativo', 'inativo', 'bloqueado')")
    op.execute("CREATE TYPE clientetipopessoa AS ENUM('PF', 'PJ')")
    op.execute("CREATE TYPE contastatus AS ENUM('aberto', 'parcial', 'pago', 'atrasado', 'cancelado')")
    op.execute("CREATE TYPE depositotipo AS ENUM('matriz', 'filial', 'deposito')")
    op.execute("CREATE TYPE entregastatus AS ENUM('pendente', 'em_rota', 'entregue', 'parcial', 'atrasado', 'cancelada')")
    op.execute("CREATE TYPE formapagamento AS ENUM('boleto', 'pix', 'credito', 'debito', 'dinheiro', 'cheque')")
    op.execute("CREATE TYPE fornecedorcategoria AS ENUM('chope', 'carvao', 'transporte', 'insumos', 'servicos', 'outros')")
    op.execute("CREATE TYPE fornecedorstatus AS ENUM('ativo', 'inativo', 'bloqueado')")
    op.execute("CREATE TYPE funcionariostatus AS ENUM('ativo', 'inativo', 'afastado')")
    op.execute("CREATE TYPE historicoevento AS ENUM('instalacao', 'desinstalacao', 'transferencia', 'manutencao', 'status_change', 'observacao')")
    op.execute("CREATE TYPE inventariostatus AS ENUM('aberto', 'fechado')")
    op.execute("CREATE TYPE lancamentotipo AS ENUM('entrada', 'saida')")
    op.execute("CREATE TYPE manutencaocategoria AS ENUM('oleo', 'pneus', 'freios', 'motor', 'suspensao', 'eletrica', 'arrefecimento', 'geral', 'outros')")
    op.execute("CREATE TYPE manutencaostatus AS ENUM('agendada', 'andamento', 'concluida', 'cancelada')")
    op.execute("CREATE TYPE manutencaotipo AS ENUM('preventiva', 'corretiva')")
    op.execute("CREATE TYPE metastatus AS ENUM('aberta', 'atingida', 'nao_atingida', 'cancelada')")
    op.execute("CREATE TYPE motoristastatus AS ENUM('disponivel', 'em_viagem', 'folga', 'afastado', 'inativo')")
    op.execute("CREATE TYPE movimentacaotipo AS ENUM('entrada', 'saida', 'ajuste', 'transferencia', 'devolucao', 'perda', 'reserva', 'cancelamento_reserva')")
    op.execute("CREATE TYPE multaresponsavel AS ENUM('motorista', 'empresa')")
    op.execute("CREATE TYPE multastatus AS ENUM('pendente', 'pago', 'recorrendo', 'cancelado')")
    op.execute("CREATE TYPE papelusuario AS ENUM('admin', 'financeiro', 'comercial', 'motorista', 'estoque')")
    op.execute("CREATE TYPE pedidocomprastatus AS ENUM('rascunho', 'cotacao', 'aguardando_aprovacao', 'aprovado', 'enviado', 'recebido_parcial', 'recebido', 'cancelado')")
    op.execute("CREATE TYPE pedidostatus AS ENUM('rascunho', 'aguardando_aprovacao', 'aprovado', 'em_separacao', 'faturado', 'entregue', 'cancelado')")
    op.execute("CREATE TYPE pixstatus AS ENUM('ativo', 'concluido', 'expirado', 'cancelado')")
    op.execute("CREATE TYPE pneumarca AS ENUM('pirelli', 'goodyear', 'bridgestone', 'michelin', 'continental', 'dunlop', 'outra')")
    op.execute("CREATE TYPE pneuposicao AS ENUM('dianteiro_e', 'dianteiro_d', 'traseiro_e', 'traseiro_d', 'tap_e', 'tap_d', 'reserva')")
    op.execute("CREATE TYPE pneustatus AS ENUM('ativo', 'trocado', 'descartado')")
    op.execute("CREATE TYPE produtocategoria AS ENUM('chope', 'carvao', 'transporte')")
    op.execute("CREATE TYPE seguroseguradora AS ENUM('porto_seguro', 'sulamerica', 'allianz', 'mapfre', 'tokio_marine', 'liberty', 'hdi', 'outra')")
    op.execute("CREATE TYPE segurostatus AS ENUM('ativo', 'vencido', 'cancelado')")
    op.execute("CREATE TYPE tipocombustivel AS ENUM('diesel_s10', 'diesel_s500', 'gasolina_aditivada', 'gasolina_comum', 'etanol', 'gnv')")
    op.execute("CREATE TYPE tipofrete AS ENUM('CIF', 'FOB')")
    op.execute("CREATE TYPE unidademedida AS ENUM('L', 'KG', 'UN', 'PCT', 'SACO')")
    op.execute("CREATE TYPE veiculocarroceria AS ENUM('bau', 'graneleiro', 'tanque', 'sider', 'aberta')")
    op.execute("CREATE TYPE veiculocategoria AS ENUM('leve', 'medio', 'pesado')")
    op.execute("CREATE TYPE veiculohistoricoevento AS ENUM('criacao', 'alteracao_status', 'manutencao', 'troca_oleo', 'troca_pneu', 'seguro', 'abastecimento', 'multa', 'km_atualizado', 'documento', 'observacao')")
    op.execute("CREATE TYPE veiculoproprietario AS ENUM('proprio', 'terceiro')")
    op.execute("CREATE TYPE veiculostatus AS ENUM('disponivel', 'em_rota', 'manutencao', 'inativo')")
    op.execute("CREATE TYPE veiculotipo AS ENUM('caminhao', 'van', 'carro', 'utilitario')")
    op.execute("CREATE TYPE whatsappconversastatus AS ENUM('ativa', 'pendente', 'encerrada')")

    op.execute('''
CREATE TABLE condicao_pagamento (
	nome VARCHAR(100) NOT NULL,
	numero_parcelas INTEGER NOT NULL,
	intervalo_dias INTEGER NOT NULL,
	entrada_percentual DECIMAL(5, 2) NOT NULL,
	ativo BOOLEAN NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
)

''')
    op.execute('''
CREATE TABLE endereco (
	logradouro VARCHAR(200) NOT NULL,
	numero VARCHAR(20) NOT NULL,
	complemento VARCHAR(100),
	bairro VARCHAR(100) NOT NULL,
	cidade VARCHAR(100) NOT NULL,
	estado VARCHAR(2) NOT NULL,
	cep VARCHAR(8) NOT NULL,
	latitude DECIMAL(10, 7),
	longitude DECIMAL(10, 7),
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
)

''')
    op.execute('''
CREATE TABLE familia_produto (
	codigo VARCHAR(10) NOT NULL,
	nome VARCHAR(100) NOT NULL,
	margem_padrao DECIMAL(5, 2),
	ativa BOOLEAN NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo)
)

''')
    op.execute('''
CREATE TABLE tabela_preco (
	nome VARCHAR(100) NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
)

''')
    op.execute('''
CREATE TABLE veiculo (
	placa VARCHAR(7) NOT NULL,
	renavam VARCHAR(20),
	chassi VARCHAR(20),
	marca VARCHAR(50) NOT NULL,
	modelo VARCHAR(50) NOT NULL,
	ano_fabricacao SMALLINT,
	ano_modelo SMALLINT,
	cor VARCHAR(30),
	tipo veiculotipo NOT NULL,
	categoria veiculocategoria,
	capacidade_carga_kg DECIMAL(8, 2),
	capacidade_volume_m3 DECIMAL(8, 2),
	tipo_carroceria veiculocarroceria,
	consumo_medio_km_l DECIMAL(5, 2),
	tanque_capacidade_l DECIMAL(7, 2),
	status veiculostatus NOT NULL,
	km_atual INTEGER NOT NULL,
	km_proxima_troca_oleo INTEGER,
	proprietario veiculoproprietario NOT NULL,
	terceiro_nome VARCHAR(200),
	terceiro_cpf_cnpj VARCHAR(14),
	data_aquisicao DATE,
	data_vencimento_seguro DATE,
	ativo BOOLEAN NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (placa),
	UNIQUE (renavam),
	UNIQUE (chassi)
)

''')
    op.execute('''
CREATE TABLE cliente (
	tipo_pessoa clientetipopessoa NOT NULL,
	nome_razao_social VARCHAR(200) NOT NULL,
	nome_fantasia VARCHAR(200),
	cpf_cnpj VARCHAR(14) NOT NULL,
	rg_ie VARCHAR(20),
	email VARCHAR(255),
	telefone VARCHAR(20),
	celular VARCHAR(20),
	limite_credito DECIMAL(12, 2) NOT NULL,
	saldo_disponivel DECIMAL(12, 2) NOT NULL,
	status clientestatus NOT NULL,
	observacao TEXT,
	deleted_at TIMESTAMP WITH TIME ZONE,
	endereco_id UUID,
	tabela_preco_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (cpf_cnpj),
	FOREIGN KEY(endereco_id) REFERENCES endereco (id),
	FOREIGN KEY(tabela_preco_id) REFERENCES tabela_preco (id)
)

''')
    op.execute('''
CREATE TABLE deposito (
	codigo VARCHAR(10) NOT NULL,
	nome VARCHAR(100) NOT NULL,
	tipo depositotipo NOT NULL,
	telefone VARCHAR(20),
	ativo BOOLEAN NOT NULL,
	endereco_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo),
	FOREIGN KEY(endereco_id) REFERENCES endereco (id)
)

''')
    op.execute('''
CREATE TABLE fornecedor (
	tipo_pessoa VARCHAR(2) NOT NULL,
	nome_razao_social VARCHAR(200) NOT NULL,
	nome_fantasia VARCHAR(200),
	cpf_cnpj VARCHAR(14) NOT NULL,
	inscricao_estadual VARCHAR(20),
	inscricao_municipal VARCHAR(20),
	email VARCHAR(255),
	telefone VARCHAR(20),
	contato_nome VARCHAR(100),
	categoria fornecedorcategoria NOT NULL,
	prazo_medio_entrega_dias SMALLINT,
	avaliacao SMALLINT,
	status fornecedorstatus NOT NULL,
	observacao TEXT,
	endereco_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (cpf_cnpj),
	FOREIGN KEY(endereco_id) REFERENCES endereco (id)
)

''')
    op.execute('''
CREATE TABLE funcionario (
	matricula VARCHAR(20) NOT NULL,
	nome VARCHAR(150) NOT NULL,
	cpf VARCHAR(11) NOT NULL,
	rg VARCHAR(20),
	data_nascimento DATE NOT NULL,
	cargo VARCHAR(100) NOT NULL,
	departamento VARCHAR(100) NOT NULL,
	data_admissao DATE NOT NULL,
	data_demissao DATE,
	salario DECIMAL(12, 2),
	telefone VARCHAR(20),
	email_corporativo VARCHAR(255),
	tipo_sanguineo VARCHAR(5),
	status funcionariostatus NOT NULL,
	endereco_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (matricula),
	UNIQUE (cpf),
	UNIQUE (email_corporativo),
	FOREIGN KEY(endereco_id) REFERENCES endereco (id)
)

''')
    op.execute('''
CREATE TABLE manutencao (
	tipo manutencaotipo NOT NULL,
	categoria manutencaocategoria NOT NULL,
	data_agendamento DATE,
	data_inicio DATE,
	data_fim DATE,
	km_na_manutencao INTEGER,
	oficina_nome VARCHAR(150),
	oficina_cnpj VARCHAR(14),
	descricao TEXT NOT NULL,
	observacao TEXT,
	status manutencaostatus NOT NULL,
	valor_pecas DECIMAL(10, 2) NOT NULL,
	valor_servico DECIMAL(10, 2) NOT NULL,
	valor_total DECIMAL(10, 2) NOT NULL,
	nota_fiscal VARCHAR(50),
	veiculo_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id)
)

''')
    op.execute('''
CREATE TABLE produto (
	codigo VARCHAR(20) NOT NULL,
	codigo_barras VARCHAR(20),
	nome VARCHAR(200) NOT NULL,
	descricao TEXT,
	categoria produtocategoria NOT NULL,
	unidade_medida unidademedida NOT NULL,
	tipo_embalagem VARCHAR(50),
	peso_kg DECIMAL(10, 3),
	volume_l DECIMAL(10, 3),
	preco_custo DECIMAL(12, 4),
	preco_venda DECIMAL(12, 2) NOT NULL,
	ncm VARCHAR(8),
	cest VARCHAR(7),
	icms_aliquota DECIMAL(5, 2),
	icms_cst VARCHAR(3),
	ipi_aliquota DECIMAL(5, 2) NOT NULL,
	pis_cofins_cst VARCHAR(3),
	estoque_minimo DECIMAL(10, 3) NOT NULL,
	estoque_maximo DECIMAL(10, 3),
	lote_obrigatorio BOOLEAN NOT NULL,
	dias_validade INTEGER,
	controla_temperatura BOOLEAN NOT NULL,
	temperatura_min DECIMAL(5, 2),
	temperatura_max DECIMAL(5, 2),
	ativo BOOLEAN NOT NULL,
	familia_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo_barras),
	FOREIGN KEY(familia_id) REFERENCES familia_produto (id)
)

''')
    op.execute('''
CREATE TABLE veiculo_km_registro (
	data DATE NOT NULL,
	km INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	origem VARCHAR(100),
	observacao TEXT,
	veiculo_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id)
)

''')
    op.execute('''
CREATE TABLE veiculo_pneu (
	posicao pneuposicao NOT NULL,
	marca pneumarca NOT NULL,
	modelo VARCHAR(50) NOT NULL,
	medida VARCHAR(20) NOT NULL,
	numero_fogo VARCHAR(30),
	km_instalacao INTEGER NOT NULL,
	km_troca INTEGER,
	data_instalacao DATE NOT NULL,
	data_troca DATE,
	vida_util_km INTEGER,
	valor_unitario DECIMAL(10, 2),
	status pneustatus NOT NULL,
	observacao TEXT,
	veiculo_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id)
)

''')
    op.execute('''
CREATE TABLE veiculo_seguro (
	apolice VARCHAR(30) NOT NULL,
	seguradora seguroseguradora NOT NULL,
	data_inicio_vigencia DATE NOT NULL,
	data_fim_vigencia DATE NOT NULL,
	data_contratacao DATE,
	premio_total DECIMAL(10, 2) NOT NULL,
	premio_parcela DECIMAL(10, 2),
	numero_parcelas INTEGER,
	coberturas TEXT,
	valor_cobertura_terceiros DECIMAL(12, 2),
	valor_franquia DECIMAL(10, 2),
	status segurostatus NOT NULL,
	ativo BOOLEAN NOT NULL,
	observacao TEXT,
	veiculo_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id)
)

''')
    op.execute('''
CREATE TABLE veiculo_troca_oleo (
	data DATE NOT NULL,
	km_atual INTEGER NOT NULL,
	tipo_oleo VARCHAR(50) NOT NULL,
	quantidade_l DECIMAL(6, 2) NOT NULL,
	valor_oleo DECIMAL(10, 2) NOT NULL,
	valor_filtro DECIMAL(10, 2) NOT NULL,
	valor_servico DECIMAL(10, 2) NOT NULL,
	valor_total DECIMAL(10, 2) NOT NULL,
	oficina_nome VARCHAR(100),
	km_proxima_troca INTEGER,
	observacao TEXT,
	veiculo_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id)
)

''')
    op.execute('''
CREATE TABLE alerta (
	tipo VARCHAR(40) NOT NULL,
	entidade_tipo VARCHAR(30),
	entidade_id UUID,
	nivel alertanivel NOT NULL,
	titulo VARCHAR(200) NOT NULL,
	mensagem TEXT,
	lido BOOLEAN NOT NULL,
	data_lido TIMESTAMP WITH TIME ZONE,
	data_resolvido TIMESTAMP WITH TIME ZONE,
	usuario_responsavel_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(usuario_responsavel_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE auditoria (
	id BIGSERIAL NOT NULL,
	entidade_tipo VARCHAR(30) NOT NULL,
	entidade_id UUID NOT NULL,
	acao auditoriaacao NOT NULL,
	dados_anteriores JSONB,
	dados_novos JSONB,
	ip_origem VARCHAR(45),
	user_agent VARCHAR(255),
	usuario_id UUID,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(usuario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE chopeira (
	codigo_identificacao VARCHAR(50) NOT NULL,
	numero_serie VARCHAR(50),
	marca VARCHAR(50) NOT NULL,
	modelo VARCHAR(50) NOT NULL,
	tipo chopeiratipo NOT NULL,
	capacidade_l DECIMAL(6, 2),
	status chopeirastatus NOT NULL,
	ativo BOOLEAN NOT NULL,
	data_instalacao DATE,
	data_ultima_manutencao DATE,
	data_proxima_manutencao DATE,
	local_instalacao VARCHAR(200),
	latitude DECIMAL(10, 7),
	longitude DECIMAL(10, 7),
	observacao TEXT,
	cliente_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(cliente_id) REFERENCES cliente (id)
)

''')
    op.execute('''
CREATE TABLE documento (
	entidade_tipo VARCHAR(30) NOT NULL,
	entidade_id UUID NOT NULL,
	tipo_documento VARCHAR(30) NOT NULL,
	nome_original VARCHAR(255) NOT NULL,
	caminho_arquivo VARCHAR(500) NOT NULL,
	tamanho_bytes INTEGER,
	mime_type VARCHAR(50),
	observacao TEXT,
	usuario_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(usuario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE item_tabela_preco (
	preco DECIMAL(12, 2) NOT NULL,
	tabela_preco_id UUID NOT NULL,
	produto_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_tabela_produto UNIQUE (tabela_preco_id, produto_id),
	FOREIGN KEY(tabela_preco_id) REFERENCES tabela_preco (id),
	FOREIGN KEY(produto_id) REFERENCES produto (id)
)

''')
    op.execute('''
CREATE TABLE lote (
	codigo_lote VARCHAR(50) NOT NULL,
	data_fabricacao DATE,
	data_validade DATE NOT NULL,
	quantidade_inicial DECIMAL(10, 3) NOT NULL,
	produto_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(produto_id) REFERENCES produto (id)
)

''')
    op.execute('''
CREATE TABLE manutencao_item (
	descricao VARCHAR(200) NOT NULL,
	tipo VARCHAR(10) NOT NULL,
	quantidade DECIMAL(8, 2) NOT NULL,
	valor_unitario DECIMAL(10, 2) NOT NULL,
	valor_total DECIMAL(10, 2) NOT NULL,
	manutencao_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(manutencao_id) REFERENCES manutencao (id)
)

''')
    op.execute('''
CREATE TABLE meta_comercial (
	descricao VARCHAR(300) NOT NULL,
	periodo_inicio DATE NOT NULL,
	periodo_fim DATE NOT NULL,
	valor_meta DECIMAL(12, 2) NOT NULL,
	valor_realizado DECIMAL(12, 2) NOT NULL,
	comissao_percentual DECIMAL(5, 2) NOT NULL,
	status metastatus NOT NULL,
	vendedor_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(vendedor_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE motorista (
	numero_cnh VARCHAR(20) NOT NULL,
	categoria_cnh categoriacnh NOT NULL,
	data_validade_cnh DATE NOT NULL,
	data_primeira_cnh DATE,
	orgao_emissor_cnh VARCHAR(50),
	cnh_observacao VARCHAR(200),
	data_ultimo_exame_medico DATE,
	data_validade_exame_medico DATE,
	certificacoes VARCHAR,
	telefone VARCHAR(20),
	email VARCHAR(255),
	status motoristastatus NOT NULL,
	ativo BOOLEAN NOT NULL,
	funcionario_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (numero_cnh),
	UNIQUE (funcionario_id),
	FOREIGN KEY(funcionario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE pedido (
	numero VARCHAR(15) NOT NULL,
	data_emissao DATE NOT NULL,
	data_entrega_prevista DATE,
	data_entrega_real DATE,
	tipo_frete tipofrete,
	status pedidostatus NOT NULL,
	subtotal DECIMAL(12, 2) NOT NULL,
	desconto DECIMAL(12, 2) NOT NULL,
	frete DECIMAL(12, 2) NOT NULL,
	total DECIMAL(12, 2) NOT NULL,
	observacao TEXT,
	cliente_id UUID NOT NULL,
	vendedor_id UUID,
	condicao_pagamento_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(cliente_id) REFERENCES cliente (id),
	FOREIGN KEY(vendedor_id) REFERENCES funcionario (id),
	FOREIGN KEY(condicao_pagamento_id) REFERENCES condicao_pagamento (id)
)

''')
    op.execute('''
CREATE TABLE pedido_compra (
	numero VARCHAR(15) NOT NULL,
	data_emissao DATE NOT NULL,
	data_previsao_entrega DATE,
	data_entrega DATE,
	status pedidocomprastatus NOT NULL,
	subtotal DECIMAL(12, 2),
	frete DECIMAL(10, 2) NOT NULL,
	desconto DECIMAL(10, 2) NOT NULL,
	total DECIMAL(12, 2),
	observacao TEXT,
	fornecedor_id UUID NOT NULL,
	usuario_solicitante_id UUID,
	usuario_aprovador_id UUID,
	condicao_pagamento_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (numero),
	FOREIGN KEY(fornecedor_id) REFERENCES fornecedor (id),
	FOREIGN KEY(usuario_solicitante_id) REFERENCES funcionario (id),
	FOREIGN KEY(usuario_aprovador_id) REFERENCES funcionario (id),
	FOREIGN KEY(condicao_pagamento_id) REFERENCES condicao_pagamento (id)
)

''')
    op.execute('''
CREATE TABLE usuario (
	username VARCHAR(50) NOT NULL,
	email VARCHAR(255) NOT NULL,
	password_hash VARCHAR(255) NOT NULL,
	papel papelusuario NOT NULL,
	ativo BOOLEAN NOT NULL,
	ultimo_login TIMESTAMP WITH TIME ZONE,
	refresh_token VARCHAR(500),
	funcionario_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (username),
	UNIQUE (email),
	UNIQUE (funcionario_id),
	FOREIGN KEY(funcionario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE veiculo_historico (
	evento veiculohistoricoevento NOT NULL,
	data_evento DATE NOT NULL,
	descricao TEXT NOT NULL,
	detalhes VARCHAR(500),
	veiculo_id UUID NOT NULL,
	usuario_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id),
	FOREIGN KEY(usuario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE whatsapp_conversa (
	telefone VARCHAR(20) NOT NULL,
	nome_contato VARCHAR(200),
	status whatsappconversastatus NOT NULL,
	ultima_mensagem TEXT,
	ultima_data TIMESTAMP WITH TIME ZONE,
	contexto JSON,
	agente_ativo VARCHAR(30),
	cliente_id UUID,
	pedido_ctx JSON,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(cliente_id) REFERENCES cliente (id)
)

''')
    op.execute('''
CREATE TABLE abastecimento (
	data TIMESTAMP WITH TIME ZONE NOT NULL,
	km_atual INTEGER NOT NULL,
	tipo_combustivel tipocombustivel NOT NULL,
	litros DECIMAL(8, 3) NOT NULL,
	valor_litro DECIMAL(8, 4) NOT NULL,
	valor_total DECIMAL(10, 2) NOT NULL,
	posto_nome VARCHAR(100),
	posto_cnpj VARCHAR(14),
	completo BOOLEAN NOT NULL,
	nota_fiscal VARCHAR(50),
	veiculo_id UUID NOT NULL,
	motorista_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id),
	FOREIGN KEY(motorista_id) REFERENCES motorista (id)
)

''')
    op.execute('''
CREATE TABLE chopeira_historico (
	evento historicoevento NOT NULL,
	data_evento DATE NOT NULL,
	descricao TEXT,
	detalhes VARCHAR(500),
	chopeira_id UUID NOT NULL,
	cliente_id UUID,
	usuario_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(chopeira_id) REFERENCES chopeira (id),
	FOREIGN KEY(cliente_id) REFERENCES cliente (id),
	FOREIGN KEY(usuario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE chopeira_manutencao (
	tipo manutencaotipo NOT NULL,
	status manutencaostatus NOT NULL,
	data_solicitacao DATE NOT NULL,
	data_inicio DATE,
	data_fim DATE,
	descricao_problema TEXT,
	descricao_servico TEXT,
	tecnico_responsavel VARCHAR(100),
	custo_pecas DECIMAL(10, 2) NOT NULL,
	custo_servico DECIMAL(10, 2) NOT NULL,
	chopeira_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(chopeira_id) REFERENCES chopeira (id)
)

''')
    op.execute('''
CREATE TABLE conta_pagar (
	parcela SMALLINT NOT NULL,
	numero_documento VARCHAR(50) NOT NULL,
	data_emissao DATE NOT NULL,
	data_vencimento DATE NOT NULL,
	data_pagamento DATE,
	valor_original DECIMAL(12, 2) NOT NULL,
	valor_pago DECIMAL(12, 2) NOT NULL,
	desconto DECIMAL(10, 2) NOT NULL,
	juros DECIMAL(10, 2) NOT NULL,
	multa DECIMAL(10, 2) NOT NULL,
	categoria VARCHAR(50),
	status contastatus NOT NULL,
	fornecedor_id UUID,
	pedido_compra_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(fornecedor_id) REFERENCES fornecedor (id),
	FOREIGN KEY(pedido_compra_id) REFERENCES pedido_compra (id)
)

''')
    op.execute('''
CREATE TABLE conta_receber (
	parcela SMALLINT NOT NULL,
	numero_documento VARCHAR(50) NOT NULL,
	data_emissao DATE NOT NULL,
	data_vencimento DATE NOT NULL,
	data_pagamento DATE,
	valor_original DECIMAL(12, 2) NOT NULL,
	valor_pago DECIMAL(12, 2) NOT NULL,
	desconto DECIMAL(10, 2) NOT NULL,
	juros DECIMAL(10, 2) NOT NULL,
	multa DECIMAL(10, 2) NOT NULL,
	status contastatus NOT NULL,
	forma_pagamento formapagamento,
	nosso_numero VARCHAR(50),
	pix_charge_id VARCHAR(100),
	pedido_id UUID,
	cliente_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(pedido_id) REFERENCES pedido (id),
	FOREIGN KEY(cliente_id) REFERENCES cliente (id)
)

''')
    op.execute('''
CREATE TABLE entrega (
	rota VARCHAR(100),
	sequencia SMALLINT,
	data_saida TIMESTAMP WITH TIME ZONE,
	data_chegada TIMESTAMP WITH TIME ZONE,
	data_entrega TIMESTAMP WITH TIME ZONE,
	km_saida INTEGER,
	km_chegada INTEGER,
	km_rota INTEGER,
	status entregastatus NOT NULL,
	assinatura_recebedor VARCHAR(100),
	observacao TEXT,
	pedido_id UUID NOT NULL,
	veiculo_id UUID NOT NULL,
	motorista_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(pedido_id) REFERENCES pedido (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id),
	FOREIGN KEY(motorista_id) REFERENCES motorista (id)
)

''')
    op.execute('''
CREATE TABLE estoque (
	quantidade_atual DECIMAL(10, 3) NOT NULL,
	quantidade_reservada DECIMAL(10, 3) NOT NULL,
	localizacao VARCHAR(50),
	versao INTEGER NOT NULL,
	produto_id UUID NOT NULL,
	deposito_id UUID NOT NULL,
	lote_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_estoque_produto_deposito_lote UNIQUE (produto_id, deposito_id, lote_id),
	FOREIGN KEY(produto_id) REFERENCES produto (id),
	FOREIGN KEY(deposito_id) REFERENCES deposito (id),
	FOREIGN KEY(lote_id) REFERENCES lote (id)
)

''')
    op.execute('''
CREATE TABLE inventario (
	status inventariostatus NOT NULL,
	data_contagem DATE DEFAULT CURRENT_DATE NOT NULL,
	quantidade_sistema DECIMAL(10, 3) NOT NULL,
	quantidade_contada DECIMAL(10, 3) NOT NULL,
	diferenca DECIMAL(10, 3) NOT NULL,
	observacao TEXT,
	produto_id UUID NOT NULL,
	deposito_id UUID NOT NULL,
	lote_id UUID,
	usuario_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(produto_id) REFERENCES produto (id),
	FOREIGN KEY(deposito_id) REFERENCES deposito (id),
	FOREIGN KEY(lote_id) REFERENCES lote (id),
	FOREIGN KEY(usuario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE item_pedido (
	quantidade DECIMAL(10, 3) NOT NULL,
	preco_unitario DECIMAL(12, 4) NOT NULL,
	desconto_percentual DECIMAL(5, 2) NOT NULL,
	desconto_valor DECIMAL(12, 2) NOT NULL,
	subtotal DECIMAL(12, 2) NOT NULL,
	ordem SMALLINT NOT NULL,
	pedido_id UUID NOT NULL,
	produto_id UUID NOT NULL,
	lote_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(pedido_id) REFERENCES pedido (id),
	FOREIGN KEY(produto_id) REFERENCES produto (id),
	FOREIGN KEY(lote_id) REFERENCES lote (id)
)

''')
    op.execute('''
CREATE TABLE item_pedido_compra (
	quantidade DECIMAL(10, 3) NOT NULL,
	quantidade_recebida DECIMAL(10, 3) NOT NULL,
	preco_unitario DECIMAL(12, 4) NOT NULL,
	subtotal DECIMAL(12, 2) NOT NULL,
	pedido_compra_id UUID NOT NULL,
	produto_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(pedido_compra_id) REFERENCES pedido_compra (id),
	FOREIGN KEY(produto_id) REFERENCES produto (id)
)

''')
    op.execute('''
CREATE TABLE movimentacao (
	tipo movimentacaotipo NOT NULL,
	quantidade DECIMAL(10, 3) NOT NULL,
	documento_tipo VARCHAR(20),
	documento_numero VARCHAR(50),
	documento_id UUID,
	observacao TEXT,
	motivo_perda VARCHAR(100),
	produto_id UUID NOT NULL,
	deposito_id_origem UUID NOT NULL,
	deposito_id_destino UUID,
	lote_id UUID,
	pedido_id UUID,
	pedido_compra_id UUID,
	usuario_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(produto_id) REFERENCES produto (id),
	FOREIGN KEY(deposito_id_origem) REFERENCES deposito (id),
	FOREIGN KEY(deposito_id_destino) REFERENCES deposito (id),
	FOREIGN KEY(lote_id) REFERENCES lote (id),
	FOREIGN KEY(pedido_id) REFERENCES pedido (id),
	FOREIGN KEY(pedido_compra_id) REFERENCES pedido_compra (id),
	FOREIGN KEY(usuario_id) REFERENCES funcionario (id)
)

''')
    op.execute('''
CREATE TABLE multa (
	data_infracao DATE NOT NULL,
	data_notificacao DATE,
	data_vencimento DATE,
	data_pagamento DATE,
	orgao_autuador VARCHAR(50) NOT NULL,
	descricao VARCHAR(300) NOT NULL,
	artigo_ctb VARCHAR(20),
	pontuacao SMALLINT,
	valor_original DECIMAL(10, 2) NOT NULL,
	valor_pago DECIMAL(10, 2),
	desconto DECIMAL(10, 2) NOT NULL,
	status multastatus NOT NULL,
	responsavel multaresponsavel NOT NULL,
	veiculo_id UUID NOT NULL,
	motorista_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id),
	FOREIGN KEY(motorista_id) REFERENCES motorista (id)
)

''')
    op.execute('''
CREATE TABLE whatsapp_mensagem (
	remetente VARCHAR(20) NOT NULL,
	conteudo TEXT NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	direcao VARCHAR(10) NOT NULL,
	lida BOOLEAN NOT NULL,
	data_recebida TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	meta_dados JSON,
	conversa_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conversa_id) REFERENCES whatsapp_conversa (id)
)

''')
    op.execute('''
CREATE TABLE boleto (
	nosso_numero VARCHAR(50) NOT NULL,
	linha_digitavel VARCHAR(100),
	codigo_barras VARCHAR(60),
	qr_code TEXT,
	data_emissao DATE NOT NULL,
	data_vencimento DATE NOT NULL,
	data_pagamento DATE,
	valor_nominal FLOAT NOT NULL,
	valor_pago FLOAT,
	status boletostatus NOT NULL,
	arquivo_pdf VARCHAR(500),
	arquivo_remessa VARCHAR(500),
	observacao TEXT,
	conta_receber_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conta_receber_id) REFERENCES conta_receber (id)
)

''')
    op.execute('''
CREATE TABLE financeiro_baixa (
	tipo baixatipo NOT NULL,
	data_baixa DATE NOT NULL,
	valor FLOAT NOT NULL,
	forma_pagamento formapagamento,
	observacao VARCHAR(200),
	conta_receber_id UUID,
	conta_pagar_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conta_receber_id) REFERENCES conta_receber (id),
	FOREIGN KEY(conta_pagar_id) REFERENCES conta_pagar (id)
)

''')
    op.execute('''
CREATE TABLE lancamento (
	data DATE NOT NULL,
	tipo lancamentotipo NOT NULL,
	valor DECIMAL(12, 2) NOT NULL,
	categoria VARCHAR(50) NOT NULL,
	descricao VARCHAR(200) NOT NULL,
	conciliado BOOLEAN NOT NULL,
	data_conciliacao DATE,
	conta_receber_id UUID,
	conta_pagar_id UUID,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conta_receber_id) REFERENCES conta_receber (id),
	FOREIGN KEY(conta_pagar_id) REFERENCES conta_pagar (id)
)

''')
    op.execute('''
CREATE TABLE pix_cobranca (
	txid VARCHAR(50) NOT NULL,
	charge_id VARCHAR(100),
	payload_base64 TEXT,
	qr_code_url VARCHAR(500),
	pix_copia_cola TEXT,
	valor FLOAT NOT NULL,
	status pixstatus NOT NULL,
	data_expiracao TIMESTAMP WITH TIME ZONE,
	data_pagamento TIMESTAMP WITH TIME ZONE,
	end_to_end_id VARCHAR(50),
	observacao TEXT,
	conta_receber_id UUID NOT NULL,
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conta_receber_id) REFERENCES conta_receber (id)
)

''')

    op.execute('''CREATE INDEX ix_endereco_cep ON endereco (cep)''')
    op.execute('''CREATE INDEX ix_veiculo_data_vencimento_seguro ON veiculo (data_vencimento_seguro)''')
    op.execute('''CREATE INDEX ix_veiculo_status ON veiculo (status)''')
    op.execute('''CREATE INDEX ix_cliente_status ON cliente (status)''')
    op.execute('''CREATE INDEX ix_cliente_nome_razao_social ON cliente (nome_razao_social)''')
    op.execute('''CREATE INDEX ix_fornecedor_status ON fornecedor (status)''')
    op.execute('''CREATE INDEX ix_fornecedor_categoria ON fornecedor (categoria)''')
    op.execute('''CREATE INDEX ix_funcionario_status ON funcionario (status)''')
    op.execute('''CREATE INDEX ix_funcionario_departamento ON funcionario (departamento)''')
    op.execute('''CREATE INDEX ix_manutencao_data_inicio ON manutencao (data_inicio)''')
    op.execute('''CREATE INDEX ix_manutencao_veiculo_id ON manutencao (veiculo_id)''')
    op.execute('''CREATE INDEX ix_manutencao_status ON manutencao (status)''')
    op.execute('''CREATE INDEX ix_produto_categoria ON produto (categoria)''')
    op.execute('''CREATE UNIQUE INDEX ix_produto_codigo ON produto (codigo)''')
    op.execute('''CREATE INDEX ix_veiculo_km_registro_veiculo_id ON veiculo_km_registro (veiculo_id)''')
    op.execute('''CREATE INDEX ix_veiculo_km_registro_data ON veiculo_km_registro (data)''')
    op.execute('''CREATE INDEX ix_veiculo_pneu_veiculo_id ON veiculo_pneu (veiculo_id)''')
    op.execute('''CREATE INDEX ix_veiculo_pneu_status ON veiculo_pneu (status)''')
    op.execute('''CREATE INDEX ix_veiculo_seguro_status ON veiculo_seguro (status)''')
    op.execute('''CREATE INDEX ix_veiculo_seguro_veiculo_id ON veiculo_seguro (veiculo_id)''')
    op.execute('''CREATE INDEX ix_veiculo_seguro_data_fim_vigencia ON veiculo_seguro (data_fim_vigencia)''')
    op.execute('''CREATE INDEX ix_veiculo_troca_oleo_data ON veiculo_troca_oleo (data)''')
    op.execute('''CREATE INDEX ix_veiculo_troca_oleo_veiculo_id ON veiculo_troca_oleo (veiculo_id)''')
    op.execute('''CREATE INDEX ix_alerta_tipo ON alerta (tipo)''')
    op.execute('''CREATE INDEX ix_alerta_entidade_tipo ON alerta (entidade_tipo)''')
    op.execute('''CREATE INDEX ix_alerta_lido ON alerta (lido)''')
    op.execute('''CREATE INDEX ix_auditoria_entidade_id ON auditoria (entidade_id)''')
    op.execute('''CREATE INDEX ix_auditoria_entidade_tipo ON auditoria (entidade_tipo)''')
    op.execute('''CREATE INDEX ix_chopeira_cliente_id ON chopeira (cliente_id)''')
    op.execute('''CREATE UNIQUE INDEX ix_chopeira_codigo_identificacao ON chopeira (codigo_identificacao)''')
    op.execute('''CREATE INDEX ix_chopeira_status ON chopeira (status)''')
    op.execute('''CREATE INDEX ix_chopeira_data_proxima_manutencao ON chopeira (data_proxima_manutencao)''')
    op.execute('''CREATE INDEX ix_meta_comercial_periodo_inicio ON meta_comercial (periodo_inicio)''')
    op.execute('''CREATE INDEX ix_meta_comercial_vendedor_id ON meta_comercial (vendedor_id)''')
    op.execute('''CREATE INDEX ix_meta_comercial_status ON meta_comercial (status)''')
    op.execute('''CREATE INDEX ix_documento_entidade_tipo ON documento (entidade_tipo)''')
    op.execute('''CREATE INDEX ix_documento_entidade_id ON documento (entidade_id)''')
    op.execute('''CREATE INDEX ix_documento_tipo_documento ON documento (tipo_documento)''')
    op.execute('''CREATE INDEX ix_motorista_data_validade_cnh ON motorista (data_validade_cnh)''')
    op.execute('''CREATE INDEX ix_motorista_status ON motorista (status)''')
    op.execute('''CREATE INDEX ix_pedido_data_entrega_prevista ON pedido (data_entrega_prevista)''')
    op.execute('''CREATE UNIQUE INDEX ix_pedido_numero ON pedido (numero)''')
    op.execute('''CREATE INDEX ix_pedido_status ON pedido (status)''')
    op.execute('''CREATE INDEX ix_pedido_cliente_id ON pedido (cliente_id)''')
    op.execute('''CREATE INDEX ix_pedido_compra_status ON pedido_compra (status)''')
    op.execute('''CREATE INDEX ix_veiculo_historico_veiculo_id ON veiculo_historico (veiculo_id)''')
    op.execute('''CREATE INDEX ix_veiculo_historico_evento ON veiculo_historico (evento)''')
    op.execute('''CREATE UNIQUE INDEX ix_whatsapp_conversa_telefone ON whatsapp_conversa (telefone)''')
    op.execute('''CREATE INDEX ix_abastecimento_data ON abastecimento (data)''')
    op.execute('''CREATE INDEX ix_abastecimento_veiculo_id ON abastecimento (veiculo_id)''')
    op.execute('''CREATE INDEX ix_chopeira_historico_chopeira_id ON chopeira_historico (chopeira_id)''')
    op.execute('''CREATE INDEX ix_chopeira_historico_evento ON chopeira_historico (evento)''')
    op.execute('''CREATE INDEX ix_chopeira_manutencao_chopeira_id ON chopeira_manutencao (chopeira_id)''')
    op.execute('''CREATE INDEX ix_chopeira_manutencao_status ON chopeira_manutencao (status)''')
    op.execute('''CREATE INDEX ix_conta_receber_status ON conta_receber (status)''')
    op.execute('''CREATE INDEX ix_conta_receber_data_vencimento ON conta_receber (data_vencimento)''')
    op.execute('''CREATE INDEX ix_conta_receber_cliente_id ON conta_receber (cliente_id)''')
    op.execute('''CREATE INDEX ix_conta_pagar_categoria ON conta_pagar (categoria)''')
    op.execute('''CREATE INDEX ix_conta_pagar_status ON conta_pagar (status)''')
    op.execute('''CREATE INDEX ix_conta_pagar_data_vencimento ON conta_pagar (data_vencimento)''')
    op.execute('''CREATE INDEX ix_entrega_pedido_id ON entrega (pedido_id)''')
    op.execute('''CREATE INDEX ix_entrega_status ON entrega (status)''')
    op.execute('''CREATE INDEX ix_estoque_produto_id ON estoque (produto_id)''')
    op.execute('''CREATE INDEX ix_estoque_deposito_id ON estoque (deposito_id)''')
    op.execute('''CREATE INDEX ix_inventario_produto_id ON inventario (produto_id)''')
    op.execute('''CREATE INDEX ix_inventario_status ON inventario (status)''')
    op.execute('''CREATE INDEX ix_inventario_deposito_id ON inventario (deposito_id)''')
    op.execute('''CREATE INDEX ix_movimentacao_produto_id ON movimentacao (produto_id)''')
    op.execute('''CREATE INDEX ix_movimentacao_tipo ON movimentacao (tipo)''')
    op.execute('''CREATE INDEX ix_multa_status ON multa (status)''')
    op.execute('''CREATE INDEX ix_multa_veiculo_id ON multa (veiculo_id)''')
    op.execute('''CREATE INDEX ix_item_pedido_pedido_id ON item_pedido (pedido_id)''')
    op.execute('''CREATE INDEX ix_whatsapp_mensagem_remetente ON whatsapp_mensagem (remetente)''')
    op.execute('''CREATE INDEX ix_whatsapp_mensagem_conversa_id ON whatsapp_mensagem (conversa_id)''')
    op.execute('''CREATE INDEX ix_boleto_conta_receber_id ON boleto (conta_receber_id)''')
    op.execute('''CREATE INDEX ix_boleto_data_vencimento ON boleto (data_vencimento)''')
    op.execute('''CREATE UNIQUE INDEX ix_boleto_nosso_numero ON boleto (nosso_numero)''')
    op.execute('''CREATE INDEX ix_boleto_status ON boleto (status)''')
    op.execute('''CREATE INDEX ix_financeiro_baixa_data_baixa ON financeiro_baixa (data_baixa)''')
    op.execute('''CREATE INDEX ix_financeiro_baixa_tipo ON financeiro_baixa (tipo)''')
    op.execute('''CREATE INDEX ix_financeiro_baixa_conta_pagar_id ON financeiro_baixa (conta_pagar_id)''')
    op.execute('''CREATE INDEX ix_financeiro_baixa_conta_receber_id ON financeiro_baixa (conta_receber_id)''')
    op.execute('''CREATE INDEX ix_lancamento_data ON lancamento (data)''')
    op.execute('''CREATE INDEX ix_lancamento_categoria ON lancamento (categoria)''')
    op.execute('''CREATE UNIQUE INDEX ix_pix_cobranca_txid ON pix_cobranca (txid)''')
    op.execute('''CREATE INDEX ix_pix_cobranca_conta_receber_id ON pix_cobranca (conta_receber_id)''')
    op.execute('''CREATE INDEX ix_pix_cobranca_status ON pix_cobranca (status)''')

def downgrade() -> None:
    op.drop_index('ix_pix_cobranca_status', table_name='pix_cobranca')
    op.drop_index('ix_pix_cobranca_conta_receber_id', table_name='pix_cobranca')
    op.drop_index('ix_pix_cobranca_txid', table_name='pix_cobranca')
    op.drop_index('ix_lancamento_categoria', table_name='lancamento')
    op.drop_index('ix_lancamento_data', table_name='lancamento')
    op.drop_index('ix_financeiro_baixa_conta_receber_id', table_name='financeiro_baixa')
    op.drop_index('ix_financeiro_baixa_conta_pagar_id', table_name='financeiro_baixa')
    op.drop_index('ix_financeiro_baixa_tipo', table_name='financeiro_baixa')
    op.drop_index('ix_financeiro_baixa_data_baixa', table_name='financeiro_baixa')
    op.drop_index('ix_boleto_status', table_name='boleto')
    op.drop_index('ix_boleto_nosso_numero', table_name='boleto')
    op.drop_index('ix_boleto_data_vencimento', table_name='boleto')
    op.drop_index('ix_boleto_conta_receber_id', table_name='boleto')
    op.drop_index('ix_whatsapp_mensagem_conversa_id', table_name='whatsapp_mensagem')
    op.drop_index('ix_whatsapp_mensagem_remetente', table_name='whatsapp_mensagem')
    op.drop_index('ix_item_pedido_pedido_id', table_name='item_pedido')
    op.drop_index('ix_multa_veiculo_id', table_name='multa')
    op.drop_index('ix_multa_status', table_name='multa')
    op.drop_index('ix_movimentacao_tipo', table_name='movimentacao')
    op.drop_index('ix_movimentacao_produto_id', table_name='movimentacao')
    op.drop_index('ix_inventario_deposito_id', table_name='inventario')
    op.drop_index('ix_inventario_status', table_name='inventario')
    op.drop_index('ix_inventario_produto_id', table_name='inventario')
    op.drop_index('ix_estoque_deposito_id', table_name='estoque')
    op.drop_index('ix_estoque_produto_id', table_name='estoque')
    op.drop_index('ix_entrega_status', table_name='entrega')
    op.drop_index('ix_entrega_pedido_id', table_name='entrega')
    op.drop_index('ix_conta_pagar_data_vencimento', table_name='conta_pagar')
    op.drop_index('ix_conta_pagar_status', table_name='conta_pagar')
    op.drop_index('ix_conta_pagar_categoria', table_name='conta_pagar')
    op.drop_index('ix_conta_receber_cliente_id', table_name='conta_receber')
    op.drop_index('ix_conta_receber_data_vencimento', table_name='conta_receber')
    op.drop_index('ix_conta_receber_status', table_name='conta_receber')
    op.drop_index('ix_chopeira_manutencao_status', table_name='chopeira_manutencao')
    op.drop_index('ix_chopeira_manutencao_chopeira_id', table_name='chopeira_manutencao')
    op.drop_index('ix_chopeira_historico_evento', table_name='chopeira_historico')
    op.drop_index('ix_chopeira_historico_chopeira_id', table_name='chopeira_historico')
    op.drop_index('ix_abastecimento_veiculo_id', table_name='abastecimento')
    op.drop_index('ix_abastecimento_data', table_name='abastecimento')
    op.drop_index('ix_whatsapp_conversa_telefone', table_name='whatsapp_conversa')
    op.drop_index('ix_veiculo_historico_evento', table_name='veiculo_historico')
    op.drop_index('ix_veiculo_historico_veiculo_id', table_name='veiculo_historico')
    op.drop_index('ix_pedido_compra_status', table_name='pedido_compra')
    op.drop_index('ix_pedido_cliente_id', table_name='pedido')
    op.drop_index('ix_pedido_status', table_name='pedido')
    op.drop_index('ix_pedido_numero', table_name='pedido')
    op.drop_index('ix_pedido_data_entrega_prevista', table_name='pedido')
    op.drop_index('ix_motorista_status', table_name='motorista')
    op.drop_index('ix_motorista_data_validade_cnh', table_name='motorista')
    op.drop_index('ix_documento_tipo_documento', table_name='documento')
    op.drop_index('ix_documento_entidade_id', table_name='documento')
    op.drop_index('ix_documento_entidade_tipo', table_name='documento')
    op.drop_index('ix_meta_comercial_status', table_name='meta_comercial')
    op.drop_index('ix_meta_comercial_vendedor_id', table_name='meta_comercial')
    op.drop_index('ix_meta_comercial_periodo_inicio', table_name='meta_comercial')
    op.drop_index('ix_chopeira_data_proxima_manutencao', table_name='chopeira')
    op.drop_index('ix_chopeira_status', table_name='chopeira')
    op.drop_index('ix_chopeira_codigo_identificacao', table_name='chopeira')
    op.drop_index('ix_chopeira_cliente_id', table_name='chopeira')
    op.drop_index('ix_auditoria_entidade_tipo', table_name='auditoria')
    op.drop_index('ix_auditoria_entidade_id', table_name='auditoria')
    op.drop_index('ix_alerta_lido', table_name='alerta')
    op.drop_index('ix_alerta_entidade_tipo', table_name='alerta')
    op.drop_index('ix_alerta_tipo', table_name='alerta')
    op.drop_index('ix_veiculo_troca_oleo_veiculo_id', table_name='veiculo_troca_oleo')
    op.drop_index('ix_veiculo_troca_oleo_data', table_name='veiculo_troca_oleo')
    op.drop_index('ix_veiculo_seguro_data_fim_vigencia', table_name='veiculo_seguro')
    op.drop_index('ix_veiculo_seguro_veiculo_id', table_name='veiculo_seguro')
    op.drop_index('ix_veiculo_seguro_status', table_name='veiculo_seguro')
    op.drop_index('ix_veiculo_pneu_status', table_name='veiculo_pneu')
    op.drop_index('ix_veiculo_pneu_veiculo_id', table_name='veiculo_pneu')
    op.drop_index('ix_veiculo_km_registro_data', table_name='veiculo_km_registro')
    op.drop_index('ix_veiculo_km_registro_veiculo_id', table_name='veiculo_km_registro')
    op.drop_index('ix_produto_codigo', table_name='produto')
    op.drop_index('ix_produto_categoria', table_name='produto')
    op.drop_index('ix_manutencao_status', table_name='manutencao')
    op.drop_index('ix_manutencao_veiculo_id', table_name='manutencao')
    op.drop_index('ix_manutencao_data_inicio', table_name='manutencao')
    op.drop_index('ix_funcionario_departamento', table_name='funcionario')
    op.drop_index('ix_funcionario_status', table_name='funcionario')
    op.drop_index('ix_fornecedor_categoria', table_name='fornecedor')
    op.drop_index('ix_fornecedor_status', table_name='fornecedor')
    op.drop_index('ix_cliente_nome_razao_social', table_name='cliente')
    op.drop_index('ix_cliente_status', table_name='cliente')
    op.drop_index('ix_veiculo_status', table_name='veiculo')
    op.drop_index('ix_veiculo_data_vencimento_seguro', table_name='veiculo')
    op.drop_index('ix_endereco_cep', table_name='endereco')
    op.drop_table('pix_cobranca')
    op.drop_table('lancamento')
    op.drop_table('financeiro_baixa')
    op.drop_table('boleto')
    op.drop_table('whatsapp_mensagem')
    op.drop_table('multa')
    op.drop_table('movimentacao')
    op.drop_table('item_pedido_compra')
    op.drop_table('item_pedido')
    op.drop_table('inventario')
    op.drop_table('estoque')
    op.drop_table('entrega')
    op.drop_table('conta_receber')
    op.drop_table('conta_pagar')
    op.drop_table('chopeira_manutencao')
    op.drop_table('chopeira_historico')
    op.drop_table('abastecimento')
    op.drop_table('whatsapp_conversa')
    op.drop_table('veiculo_historico')
    op.drop_table('usuario')
    op.drop_table('pedido_compra')
    op.drop_table('pedido')
    op.drop_table('motorista')
    op.drop_table('meta_comercial')
    op.drop_table('manutencao_item')
    op.drop_table('lote')
    op.drop_table('item_tabela_preco')
    op.drop_table('documento')
    op.drop_table('chopeira')
    op.drop_table('auditoria')
    op.drop_table('alerta')
    op.drop_table('veiculo_troca_oleo')
    op.drop_table('veiculo_seguro')
    op.drop_table('veiculo_pneu')
    op.drop_table('veiculo_km_registro')
    op.drop_table('produto')
    op.drop_table('manutencao')
    op.drop_table('funcionario')
    op.drop_table('fornecedor')
    op.drop_table('deposito')
    op.drop_table('cliente')
    op.drop_table('veiculo')
    op.drop_table('tabela_preco')
    op.drop_table('familia_produto')
    op.drop_table('endereco')
    op.drop_table('condicao_pagamento')
    op.execute('DROP TYPE IF EXISTS whatsappconversastatus')
    op.execute('DROP TYPE IF EXISTS veiculotipo')
    op.execute('DROP TYPE IF EXISTS veiculostatus')
    op.execute('DROP TYPE IF EXISTS veiculoproprietario')
    op.execute('DROP TYPE IF EXISTS veiculohistoricoevento')
    op.execute('DROP TYPE IF EXISTS veiculocategoria')
    op.execute('DROP TYPE IF EXISTS veiculocarroceria')
    op.execute('DROP TYPE IF EXISTS unidademedida')
    op.execute('DROP TYPE IF EXISTS tipofrete')
    op.execute('DROP TYPE IF EXISTS tipocombustivel')
    op.execute('DROP TYPE IF EXISTS segurostatus')
    op.execute('DROP TYPE IF EXISTS seguroseguradora')
    op.execute('DROP TYPE IF EXISTS produtocategoria')
    op.execute('DROP TYPE IF EXISTS pneustatus')
    op.execute('DROP TYPE IF EXISTS pneuposicao')
    op.execute('DROP TYPE IF EXISTS pneumarca')
    op.execute('DROP TYPE IF EXISTS pixstatus')
    op.execute('DROP TYPE IF EXISTS pedidostatus')
    op.execute('DROP TYPE IF EXISTS pedidocomprastatus')
    op.execute('DROP TYPE IF EXISTS papelusuario')
    op.execute('DROP TYPE IF EXISTS multastatus')
    op.execute('DROP TYPE IF EXISTS multaresponsavel')
    op.execute('DROP TYPE IF EXISTS movimentacaotipo')
    op.execute('DROP TYPE IF EXISTS motoristastatus')
    op.execute('DROP TYPE IF EXISTS metastatus')
    op.execute('DROP TYPE IF EXISTS manutencaotipo')
    op.execute('DROP TYPE IF EXISTS manutencaostatus')
    op.execute('DROP TYPE IF EXISTS manutencaocategoria')
    op.execute('DROP TYPE IF EXISTS lancamentotipo')
    op.execute('DROP TYPE IF EXISTS inventariostatus')
    op.execute('DROP TYPE IF EXISTS historicoevento')
    op.execute('DROP TYPE IF EXISTS funcionariostatus')
    op.execute('DROP TYPE IF EXISTS fornecedorstatus')
    op.execute('DROP TYPE IF EXISTS fornecedorcategoria')
    op.execute('DROP TYPE IF EXISTS formapagamento')
    op.execute('DROP TYPE IF EXISTS entregastatus')
    op.execute('DROP TYPE IF EXISTS depositotipo')
    op.execute('DROP TYPE IF EXISTS contastatus')
    op.execute('DROP TYPE IF EXISTS clientetipopessoa')
    op.execute('DROP TYPE IF EXISTS clientestatus')
    op.execute('DROP TYPE IF EXISTS chopeiratipo')
    op.execute('DROP TYPE IF EXISTS chopeirastatus')
    op.execute('DROP TYPE IF EXISTS categoriacnh')
    op.execute('DROP TYPE IF EXISTS boletostatus')
    op.execute('DROP TYPE IF EXISTS baixatipo')
    op.execute('DROP TYPE IF EXISTS auditoriaacao')
    op.execute('DROP TYPE IF EXISTS alertanivel')
