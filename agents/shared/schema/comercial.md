# Schema Comercial

## `cliente`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| tipo_pessoa | Enum(PF,PJ) | |
| nome_razao_social | VARCHAR(200) | Nome ou razão social |
| nome_fantasia | VARCHAR(200) | Nome fantasia |
| cpf_cnpj | VARCHAR(14) | CPF ou CNPJ (único) |
| email | VARCHAR(255) | |
| telefone | VARCHAR(20) | |
| celular | VARCHAR(20) | |
| limite_credito | DECIMAL(12,2) | |
| saldo_disponivel | DECIMAL(12,2) | |
| status | Enum(ativo,inativo,bloqueado) | |
| deleted_at | DateTime | Soft delete |
| endereco_id | UUID FK → endereco | |
| tabela_preco_id | UUID FK → tabela_preco | |

## `pedido`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| numero | VARCHAR(15) | Número do pedido (único) |
| data_emissao | Date | |
| data_entrega_prevista | Date | |
| data_entrega_real | Date | |
| status | Enum | rascunho, aguardando_aprovacao, aprovado, em_separacao, faturado, entregue, cancelado |
| subtotal | DECIMAL(12,2) | |
| desconto | DECIMAL(12,2) | |
| frete | DECIMAL(12,2) | |
| total | DECIMAL(12,2) | |
| cliente_id | UUID FK → cliente | |
| vendedor_id | UUID FK → funcionario | |
| condicao_pagamento_id | UUID FK → condicao_pagamento | |

## `item_pedido`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| quantidade | DECIMAL(10,3) | |
| preco_unitario | DECIMAL(12,4) | |
| desconto_percentual | DECIMAL(5,2) | |
| desconto_valor | DECIMAL(12,2) | |
| subtotal | DECIMAL(12,2) | |
| ordem | SMALLINT | |
| pedido_id | UUID FK → pedido | |
| produto_id | UUID FK → produto | |

## `meta_comercial`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| descricao | VARCHAR(300) | |
| periodo_inicio | Date | |
| periodo_fim | Date | |
| valor_meta | DECIMAL(12,2) | Valor alvo |
| valor_realizado | DECIMAL(12,2) | Valor realizado |
| comissao_percentual | DECIMAL(5,2) | % comissão |
| status | Enum | aberta, atingida, nao_atingida, cancelada |
| vendedor_id | UUID FK → funcionario | |
