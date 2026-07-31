# Schema Financeiro

## `conta_receber`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| parcela | SMALLINT | Número da parcela |
| numero_documento | VARCHAR(50) | |
| data_emissao | Date | |
| data_vencimento | Date | |
| data_pagamento | Date | |
| valor_original | DECIMAL(12,2) | |
| valor_pago | DECIMAL(12,2) | |
| desconto | DECIMAL(12,2) | |
| juros | DECIMAL(12,2) | |
| multa | DECIMAL(12,2) | |
| status | Enum | aberto, parcial, pago, atrasado, cancelado |
| forma_pagamento | Enum | boleto, pix, credito, debito, dinheiro, cheque |
| nosso_numero | VARCHAR(50) | Número do boleto |
| pix_charge_id | VARCHAR(100) | ID da cobrança PIX |
| cliente_id | UUID FK → cliente | |
| pedido_id | UUID FK → pedido | |

## `conta_pagar`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| parcela | SMALLINT | |
| numero_documento | VARCHAR(50) | |
| data_emissao | Date | |
| data_vencimento | Date | |
| data_pagamento | Date | |
| valor_original | DECIMAL(12,2) | |
| valor_pago | DECIMAL(12,2) | |
| desconto | DECIMAL(12,2) | |
| juros | DECIMAL(12,2) | |
| multa | DECIMAL(12,2) | |
| status | Enum | aberto, parcial, pago, atrasado, cancelado |
| categoria | VARCHAR(50) | |
| fornecedor_id | UUID FK → fornecedor | |
| pedido_compra_id | UUID FK → pedido_compra | |

## `lancamento`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| descricao | VARCHAR(255) | |
| tipo | Enum | receita, despesa |
| valor_receita | DECIMAL(12,2) | |
| valor_despesa | DECIMAL(12,2) | |
| data_competencia | Date | |
| data_baixa | Date | |
| categoria | VARCHAR(80) | |
| forma_pagamento | Enum | |
| conta_receber_id | UUID FK → conta_receber | |
| conta_pagar_id | UUID FK → conta_pagar | |

## `boleto`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| nosso_numero | VARCHAR(50) | Único |
| valor_nominal | DECIMAL(12,2) | |
| valor_pago | DECIMAL(12,2) | |
| data_emissao | Date | |
| data_vencimento | Date | |
| data_pagamento | Date | |
| status | Enum | gerado, registrado, vencido, pago, cancelado |
| conta_receber_id | UUID FK → conta_receber | |

## `pix_cobranca`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| txid | VARCHAR(50) | Identificador PIX (único) |
| valor | DECIMAL(12,2) | |
| status | Enum | ativo, concluido, expirado, cancelado |
| data_pagamento | DateTime | |
| conta_receber_id | UUID FK → conta_receber | |

## `baixa`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| tipo | Enum | recebimento, pagamento |
| data_baixa | Date | |
| valor | DECIMAL(12,2) | |
| forma_pagamento | Enum | |
| observacao | Text | |
| conta_receber_id | UUID FK → conta_receber | |
| conta_pagar_id | UUID FK → conta_pagar | |
