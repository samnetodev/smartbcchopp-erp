from database.models.abastecimento import AbastecimentoModel
from database.models.alerta import AlertaModel
from database.models.auditoria import AuditoriaModel
from database.models.base import Base
from database.models.boleto import BoletoModel, BoletoStatus
from database.models.chopeira import ChopeiraModel, ChopeiraStatus, ChopeiraTipo
from database.models.chopeira_historico import ChopeiraHistoricoModel, HistoricoEvento
from database.models.chopeira_manutencao import (
    ChopeiraManutencaoModel,
    ManutencaoStatus,
    ManutencaoTipo,
)
from database.models.cliente import ClienteModel
from database.models.comercial import MetaModel, MetaStatus
from database.models.condicao_pagamento import CondicaoPagamentoModel
from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel
from database.models.deposito import DepositoModel
from database.models.documento import DocumentoModel
from database.models.endereco import EnderecoModel
from database.models.entrega import EntregaModel
from database.models.estoque import EstoqueModel
from database.models.familia_produto import FamiliaProdutoModel
from database.models.financeiro_baixa import BaixaModel
from database.models.fornecedor import FornecedorModel
from database.models.funcionario import FuncionarioModel
from database.models.inventario import InventarioModel, InventarioStatus
from database.models.lancamento import LancamentoModel
from database.models.lote import LoteModel
from database.models.manutencao import ManutencaoItemModel, ManutencaoModel
from database.models.motorista import MotoristaModel
from database.models.movimentacao import MovimentacaoModel
from database.models.multa import MultaModel
from database.models.pedido import ItemPedidoModel, PedidoModel
from database.models.pedido_compra import ItemPedidoCompraModel, PedidoCompraModel
from database.models.pix_cobranca import PixCobrancaModel
from database.models.produto import ProdutoModel
from database.models.tabela_preco import ItemTabelaPrecoModel, TabelaPrecoModel
from database.models.usuario import UsuarioModel
from database.models.veiculo import VeiculoModel, VeiculoStatus, VeiculoTipo
from database.models.veiculo_historico import VeiculoHistoricoEvento, VeiculoHistoricoModel
from database.models.veiculo_km_registro import KmRegistroModel
from database.models.veiculo_pneu import PneuModel
from database.models.veiculo_seguro import SeguroModel
from database.models.veiculo_troca_oleo import TrocaOleoModel
from database.models.whatsapp_conversa import (
    WhatsappConversaModel,
    WhatsappConversaStatus,
    WhatsappMensagemModel,
)

__all__ = [
    "Base",
    "EnderecoModel",
    "FuncionarioModel",
    "UsuarioModel",
    "DepositoModel",
    "FamiliaProdutoModel",
    "ProdutoModel",
    "LoteModel",
    "EstoqueModel",
    "InventarioModel",
    "InventarioStatus",
    "MovimentacaoModel",
    "CondicaoPagamentoModel",
    "MetaModel",
    "MetaStatus",
    "PedidoModel",
    "ItemPedidoModel",
    "ClienteModel",
    "TabelaPrecoModel",
    "ItemTabelaPrecoModel",
    "VeiculoModel",
    "MotoristaModel",
    "EntregaModel",
    "ChopeiraModel",
    "ManutencaoModel",
    "ManutencaoItemModel",
    "AbastecimentoModel",
    "MultaModel",
    "FornecedorModel",
    "PedidoCompraModel",
    "ItemPedidoCompraModel",
    "ContaReceberModel",
    "ContaPagarModel",
    "LancamentoModel",
    "DocumentoModel",
    "AlertaModel",
    "AuditoriaModel",
    "BaixaModel",
    "BoletoModel",
    "BoletoStatus",
    "ChopeiraStatus",
    "ChopeiraTipo",
    "ChopeiraHistoricoModel",
    "HistoricoEvento",
    "ChopeiraManutencaoModel",
    "ManutencaoStatus",
    "ManutencaoTipo",
    "VeiculoStatus",
    "VeiculoTipo",
    "VeiculoHistoricoModel",
    "VeiculoHistoricoEvento",
    "KmRegistroModel",
    "PneuModel",
    "PixCobrancaModel",
    "SeguroModel",
    "TrocaOleoModel",
    "WhatsappConversaModel",
    "WhatsappConversaStatus",
    "WhatsappMensagemModel",
]
