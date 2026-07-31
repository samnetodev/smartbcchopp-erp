# Schema Estoque

## `produto`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| codigo | VARCHAR(30) | Código interno (único) |
| codigo_barras | VARCHAR(20) | EAN |
| nome | VARCHAR(200) | |
| descricao | Text | |
| unidade_medida | VARCHAR(10) | UN, KG, LT, CX, etc. |
| preco_custo | DECIMAL(12,4) | |
| preco_venda | DECIMAL(12,4) | |
| ncm | VARCHAR(10) | |
| cest | VARCHAR(10) | |
| origem | Enum | nacional, importado |
| tipo | Enum | produto, insumo, embalagem, bonificacao |
| ativo | Boolean | |
| familia_id | UUID FK → familia_produto | |

## `familia_produto`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| codigo | VARCHAR(20) | |
| nome | VARCHAR(100) | |
| descricao | Text | |
| ativo | Boolean | |

## `deposito`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| codigo | VARCHAR(20) | |
| nome | VARCHAR(100) | |
| tipo | Enum | matriz, filial, centro_distribuicao |
| ativo | Boolean | |

## `estoque`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| quantidade_atual | DECIMAL(12,4) | Saldo atual |
| quantidade_reservada | DECIMAL(12,4) | |
| estoque_minimo | DECIMAL(12,4) | |
| estoque_maximo | DECIMAL(12,4) | |
| produto_id | UUID FK → produto | |
| deposito_id | UUID FK → deposito | |
| lote_id | UUID FK → lote | |

## `movimentacao`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| tipo | Enum | entrada, saida, transferencia, perda, ajuste |
| quantidade | DECIMAL(12,4) | |
| data_movimentacao | DateTime | |
| motivo | VARCHAR(200) | |
| observacao | Text | |
| produto_id | UUID FK → produto | |
| deposito_id_origem | UUID FK → deposito | |
| deposito_id_destino | UUID FK → deposito | |
| lote_id | UUID FK → lote | |
| pedido_id | UUID FK → pedido | |

## `lote`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| codigo | VARCHAR(50) | |
| data_fabricacao | Date | |
| data_validade | Date | |
| produto_id | UUID FK → produto | |

## `inventario`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| data_contagem | Date | |
| quantidade_contada | DECIMAL(12,4) | |
| quantidade_sistema | DECIMAL(12,4) | |
| diferenca | DECIMAL(12,4) | |
| status | Enum | aberto, finalizado, ajustado |
| produto_id | UUID FK → produto | |
| deposito_id | UUID FK → deposito | |
