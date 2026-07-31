# Schema do Banco de Dados — SmartBcChopp ERP

## Convenções

- Todas as tabelas usam `UUID` como chave primária (`id`).
- Todas as tabelas herdam de `Base` e possuem `id`, `created_at`, `updated_at`.
- Relacionamentos são feitos via `ForeignKey` com `UUID`.
- Valores monetários são `DECIMAL(12,2)`.
- Enums são salvos como `VARCHAR` via `Enum` do SQLAlchemy.
- Soft delete é feito com `deleted_at` (timestamp) ou `ativo` (boolean).

## Modelo Relacional (Entidades Principais)

### Vendas / Comercial
- `cliente` — clientes (PF/PJ)
- `pedido` — pedidos de venda
- `item_pedido` — itens do pedido
- `meta_comercial` — metas de vendas por vendedor/período

### Financeiro
- `conta_receber` — contas a receber
- `conta_pagar` — contas a pagar
- `lancamento` — lançamentos contábeis (receitas/despesas)
- `boleto` — boletos gerados
- `pix_cobranca` — cobranças PIX
- `baixa` — baixas/transações

### Frota
- `veiculo` — veículos da frota
- `motorista` — motoristas
- `veiculo_km_registro` — registro de quilometragem
- `veiculo_troca_oleo` — trocas de óleo
- `veiculo_pneu` — pneus
- `veiculo_seguro` — seguros
- `veiculo_historico` — histórico do veículo

### Chopeiras
- `chopeira` — equipamentos (chopeiras, torres, coolers)
- `chopeira_historico` — histórico de eventos
- `chopeira_manutencao` — manutenções
- `alerta` — alertas do sistema

### Estoque
- `produto` — produtos
- `familia_produto` — famílias de produtos
- `deposito` — depósitos/almoxarifados
- `estoque` — saldo por produto/depósito/lote
- `movimentacao` — movimentações (entrada/saída/transferência/perda)
- `inventario` — contagens de inventário
- `lote` — lotes

### Administrativo
- `funcionario` — funcionários
- `usuario` — usuários do sistema
- `fornecedor` — fornecedores
- `pedido_compra` — pedidos de compra
- `item_pedido_compra` — itens do pedido de compra
- `endereco` — endereços
- `auditoria` — log de auditoria
- `documento` — documentos anexados
