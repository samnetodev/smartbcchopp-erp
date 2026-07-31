# Schema Frota

## `veiculo`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| placa | VARCHAR(10) | Placa do veículo (único) |
| renavam | VARCHAR(20) | |
| chassi | VARCHAR(30) | |
| marca | VARCHAR(50) | |
| modelo | VARCHAR(50) | |
| ano_fabricacao | INTEGER | |
| ano_modelo | INTEGER | |
| cor | VARCHAR(30) | |
| tipo | Enum | caminhao, van, utilitario, carro_passeio |
| capacidade_carga_kg | DECIMAL(8,2) | |
| tanque_litros | DECIMAL(8,2) | |
| km_atual | INTEGER | |
| km_troca_oleo | INTEGER | Km na última troca de óleo |
| proxima_troca_oleo | INTEGER | Km prevista para próxima troca |
| data_proxima_troca_oleo | Date | |
| data_ultima_troca_oleo | Date | |
| data_proxima_manutencao | Date | |
| status | Enum | ativo, inativo, manutencao, vendido, baixado |
| ativo | Boolean | |
| motorista_id | UUID FK → motorista | |

## `motorista`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| nome | VARCHAR(150) | |
| cpf | VARCHAR(11) | CPF (único) |
| cnh | VARCHAR(20) | Número da CNH (único) |
| categoria_cnh | VARCHAR(5) | A, B, C, D, E |
| data_validade_cnh | Date | |
| telefone | VARCHAR(20) | |
| status | Enum | ativo, inativo, afastado |
| ativo | Boolean | |

## `veiculo_km_registro`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| data_registro | Date | |
| km_atual | INTEGER | |
| km_percorrido | INTEGER | |
| tipo | Enum | entrada, saida, manual |
| observacao | Text | |
| veiculo_id | UUID FK → veiculo | |
| motorista_id | UUID FK → motorista | |

## `veiculo_troca_oleo`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| data_troca | Date | |
| km_atual | INTEGER | |
| tipo_oleo | VARCHAR(50) | |
| quantidade_l | DECIMAL(6,2) | |
| valor | DECIMAL(12,2) | |
| veiculo_id | UUID FK → veiculo | |

## `veiculo_pneu`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| posicao | VARCHAR(20) | Dianteiro E, Dianteiro D, Traseiro E, etc. |
| marca | VARCHAR(50) | |
| medida | VARCHAR(20) | |
| numero_fogo | VARCHAR(30) | |
| km_instalacao | INTEGER | |
| km_retirada | INTEGER | |
| data_instalacao | Date | |
| data_retirada | Date | |
| status | Enum | ativo, retirado, descartado |
| veiculo_id | UUID FK → veiculo | |

## `veiculo_seguro`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| seguradora | VARCHAR(100) | |
| apolice | VARCHAR(50) | |
| data_inicio | Date | |
| data_fim | Date | |
| valor_premio | DECIMAL(12,2) | |
| veiculo_id | UUID FK → veiculo | |

## `veiculo_historico`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| evento | Enum | criado, atualizado, km_atualizado, status_alterado, etc. |
| descricao | Text | |
| veiculo_id | UUID FK → veiculo | |
