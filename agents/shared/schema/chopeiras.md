# Schema Chopeiras

## `chopeira`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| codigo_identificacao | VARCHAR(50) | (único) |
| numero_serie | VARCHAR(50) | |
| marca | VARCHAR(50) | |
| modelo | VARCHAR(50) | |
| tipo | Enum | chopeira, torre, cooler, torneira |
| capacidade_l | DECIMAL(6,2) | |
| status | Enum | disponivel, instalada, manutencao, baixada |
| ativo | Boolean | |
| data_instalacao | Date | |
| data_ultima_manutencao | Date | |
| data_proxima_manutencao | Date | |
| local_instalacao | VARCHAR(200) | |
| latitude | DECIMAL(10,7) | |
| longitude | DECIMAL(10,7) | |
| cliente_id | UUID FK → cliente | |

## `chopeira_historico`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| evento | Enum | instalada, removida, manutencao_iniciada, manutencao_concluida, status_alterado |
| descricao | Text | |
| data_evento | DateTime | |
| chopeira_id | UUID FK → chopeira | |

## `chopeira_manutencao`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| tipo | Enum | corretiva, preventiva, emergencial |
| descricao | Text | |
| data_inicio | DateTime | |
| data_fim | DateTime | |
| custo | DECIMAL(12,2) | |
| status | Enum | aberta, em_andamento, concluida |
| chopeira_id | UUID FK → chopeira | |
| responsavel_id | UUID FK → funcionario | |

## `alerta`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| tipo | VARCHAR(40) | estoque_baixo, manutencao_pendente, conta_vencida, etc. |
| entidade_tipo | VARCHAR(30) | |
| entidade_id | UUID | |
| nivel | Enum | info, warning, critical |
| titulo | VARCHAR(200) | |
| mensagem | Text | |
| lido | Boolean | |
| data_lido | DateTime | |
| data_resolvido | DateTime | |
| usuario_responsavel_id | UUID FK → funcionario | |
