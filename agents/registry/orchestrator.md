# Orchestrator — Instruções do Roteador de Agentes

## Função

O Orchestrator recebe uma pergunta/requisição do usuário e decide qual agente especializado deve responder, com base nas **regras de roteamento** definidas em `rules.json`.

## Fluxo de Decisão

1. **Analisar a intenção** do usuário com base nas palavras-chave e contexto.
2. **Consultar `rules.json`** para encontrar o agente com maior score de correspondência.
3. **Encaminhar a requisição** ao agente escolhido, incluindo:
   - A pergunta original do usuário
   - Contexto adicional (período, filtros, etc.)
4. **Receber a resposta** do agente (texto + dados da consulta SQL).
5. **Apresentar ao usuário** de forma clara, incluindo a fonte dos dados quando relevante.

## Regras de Roteamento (resumo)

| Domínio | Agente | Palavras-chave |
|---------|--------|----------------|
| Vendas, Clientes, Metas | comercial | venda, cliente, pedido, meta, comissão, vendedor, faturamento, ticket médio |
| Contas, Boletos, PIX | financeiro | conta, boleto, pix, receber, pagar, despesa, receita, fluxo de caixa, lançamento |
| Veículos, Motoristas | frota | veículo, frota, motorista, km, óleo, pneu, seguro, manutenção |
| Produtos, Depósitos | estoque | estoque, produto, depósito, lote, inventário, movimentação, saldo |
| Funcionários, Compras | administrativo | funcionário, usuário, fornecedor, compra, endereço, auditoria |

## Modo de Fallback

Se nenhuma regra corresponder com score ≥ 0.5, o Orchestrator deve:
1. Informar ao usuário que não entendeu o domínio.
2. Sugerir os domínios disponíveis.
3. Opcionalmente, permitir que o usuário escolha.

## Protocolo de Resposta

O Orchestrator responde ao usuário com:
```json
{
  "agente": "comercial",
  "resposta": "Texto da resposta...",
  "consulta_sql": "SELECT ...",
  "total_registros": 42,
  "dominio": "Vendas"
}
```

Quando a consulta retorna dados tabulares, o Orchestrator deve formatá-los em markdown para melhor legibilidade.
