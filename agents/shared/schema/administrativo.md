# Schema Administrativo

## `funcionario`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| matricula | VARCHAR(20) | (único) |
| nome | VARCHAR(150) | |
| cpf | VARCHAR(11) | (único) |
| rg | VARCHAR(20) | |
| data_nascimento | Date | |
| cargo | VARCHAR(100) | |
| departamento | VARCHAR(100) | |
| data_admissao | Date | |
| data_demissao | Date | |
| salario | DECIMAL(12,2) | |
| telefone | VARCHAR(20) | |
| email_corporativo | VARCHAR(255) | |
| tipo_sanguineo | VARCHAR(5) | |
| status | Enum | ativo, inativo, afastado |
| endereco_id | UUID FK → endereco | |

## `usuario`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| username | VARCHAR(50) | (único) |
| email | VARCHAR(255) | (único) |
| senha_hash | VARCHAR(255) | |
| ativo | Boolean | |
| papel | Enum | admin, financeiro, comercial, motorista, estoque |
| funcionario_id | UUID FK → funcionario | |

## `fornecedor`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| nome_razao_social | VARCHAR(200) | |
| nome_fantasia | VARCHAR(200) | |
| cpf_cnpj | VARCHAR(14) | (único) |
| inscricao_estadual | VARCHAR(20) | |
| email | VARCHAR(255) | |
| telefone | VARCHAR(20) | |
| status | Enum | ativo, inativo, bloqueado |
| deleted_at | DateTime | |

## `pedido_compra`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| numero | VARCHAR(15) | (único) |
| data_emissao | Date | |
| data_entrega_prevista | Date | |
| status | Enum | rascunho, enviado, confirmado, recebido, cancelado |
| subtotal | DECIMAL(12,2) | |
| total | DECIMAL(12,2) | |
| fornecedor_id | UUID FK → fornecedor | |

## `item_pedido_compra`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| quantidade | DECIMAL(10,3) | |
| preco_unitario | DECIMAL(12,4) | |
| subtotal | DECIMAL(12,2) | |
| pedido_compra_id | UUID FK → pedido_compra | |
| produto_id | UUID FK → produto | |

## `endereco`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| logradouro | VARCHAR(200) | |
| numero | VARCHAR(20) | |
| complemento | VARCHAR(100) | |
| bairro | VARCHAR(100) | |
| cidade | VARCHAR(100) | |
| estado | VARCHAR(2) | |
| cep | VARCHAR(10) | |
| latitude | DECIMAL(10,7) | |
| longitude | DECIMAL(10,7) | |

## `auditoria`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| entidade_tipo | VARCHAR(30) | |
| entidade_id | UUID | |
| acao | VARCHAR(20) | criar, atualizar, deletar |
| valores_anteriores | JSONB | |
| valores_novos | JSONB | |
| usuario_id | UUID FK → usuario | |

## `documento`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| tipo | VARCHAR(30) | |
| nome_arquivo | VARCHAR(255) | |
| caminho | VARCHAR(500) | |
| entidade_tipo | VARCHAR(30) | |
| entidade_id | UUID | |
