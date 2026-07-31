from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from core.domain.auth.papeis import Acao, Modulo
from database.models.alerta import AlertaModel
from database.models.chopeira import ChopeiraModel, ChopeiraStatus
from database.models.cliente import ClienteModel, ClienteStatus
from database.models.estoque import EstoqueModel
from database.models.pedido import PedidoModel, PedidoStatus
from database.models.produto import ProdutoModel
from database.models.veiculo import VeiculoModel, VeiculoStatus

router = APIRouter()


@router.get("/master")
async def master_dashboard(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> dict[str, Any]:
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    ano_base = hoje.year - 1 if hoje.month < 7 else hoje.year
    mes_base = max(1, hoje.month - 5)
    seis_meses_atras = date(ano_base, mes_base, 1)
    if seis_meses_atras > hoje:
        seis_meses_atras = date(hoje.year - 1, 1, 1)

    # ── Clientes ──
    stmt_count = select(func.count()).select_from(ClienteModel)
    total_clientes = (await session.execute(stmt_count)).scalar_one()

    stmt_ativos = select(func.count()).select_from(ClienteModel).where(
        ClienteModel.deleted_at.is_(None), ClienteModel.status == ClienteStatus.ATIVO,
    )
    clientes_ativos = (await session.execute(stmt_ativos)).scalar_one()

    stmt_inativos = select(func.count()).select_from(ClienteModel).where(
        ClienteModel.deleted_at.is_(None), ClienteModel.status == ClienteStatus.INATIVO,
    )
    clientes_inativos = (await session.execute(stmt_inativos)).scalar_one()

    stmt_novos = select(func.count()).select_from(ClienteModel).where(
        ClienteModel.deleted_at.is_(None),
        func.date(ClienteModel.created_at) >= inicio_mes,
    )
    novos_clientes_mes = (await session.execute(stmt_novos)).scalar_one()

    # ── Veículos ──
    stmt_v_total = (
        select(func.count()).select_from(VeiculoModel).where(VeiculoModel.ativo.is_(True))
    )
    veiculos_ativos = (await session.execute(stmt_v_total)).scalar_one()

    stmt_v_manut = select(func.count()).select_from(VeiculoModel).where(
        VeiculoModel.ativo.is_(True), VeiculoModel.status == VeiculoStatus.MANUTENCAO,
    )
    veiculos_manutencao = (await session.execute(stmt_v_manut)).scalar_one()

    stmt_v_oleo = select(func.count()).select_from(VeiculoModel).where(
        VeiculoModel.ativo.is_(True),
        VeiculoModel.km_proxima_troca_oleo.isnot(None),
        VeiculoModel.km_atual >= VeiculoModel.km_proxima_troca_oleo,
    )
    veiculos_troca_oleo = (await session.execute(stmt_v_oleo)).scalar_one()

    # ── Chopeiras ──
    stmt_c_total = (
        select(func.count()).select_from(ChopeiraModel).where(ChopeiraModel.ativo.is_(True))
    )
    total_chopeiras = (await session.execute(stmt_c_total)).scalar_one()

    stmt_c_inst = select(func.count()).select_from(ChopeiraModel).where(
        ChopeiraModel.ativo.is_(True), ChopeiraModel.status == ChopeiraStatus.INSTALADA,
    )
    chopeiras_instaladas = (await session.execute(stmt_c_inst)).scalar_one()

    stmt_c_disp = select(func.count()).select_from(ChopeiraModel).where(
        ChopeiraModel.ativo.is_(True), ChopeiraModel.status == ChopeiraStatus.DISPONIVEL,
    )
    chopeiras_disponiveis = (await session.execute(stmt_c_disp)).scalar_one()

    stmt_c_manut = select(func.count()).select_from(ChopeiraModel).where(
        ChopeiraModel.ativo.is_(True), ChopeiraModel.status == ChopeiraStatus.MANUTENCAO,
    )
    chopeiras_manutencao = (await session.execute(stmt_c_manut)).scalar_one()

    manut_pendente_limite = hoje + timedelta(days=15)
    stmt_c_pend = select(func.count()).select_from(ChopeiraModel).where(
        ChopeiraModel.ativo.is_(True),
        ChopeiraModel.data_proxima_manutencao.isnot(None),
        ChopeiraModel.data_proxima_manutencao <= manut_pendente_limite,
    )
    chopeiras_manut_pendente = (await session.execute(stmt_c_pend)).scalar_one()

    # ── Financeiro ──
    from database.models.conta_pagar import ContaPagarModel
    from database.models.conta_pagar import ContaStatus as PagarStatus
    from database.models.conta_receber import ContaReceberModel
    from database.models.conta_receber import ContaStatus as ReceberStatus

    stmt_rec = select(func.coalesce(func.sum(ContaReceberModel.valor_original), 0)).where(
        ContaReceberModel.status.in_([ReceberStatus.ABERTO, ReceberStatus.PARCIAL]),
    )
    total_a_receber = float((await session.execute(stmt_rec)).scalar_one())

    stmt_pag = select(func.coalesce(func.sum(ContaPagarModel.valor_original), 0)).where(
        ContaPagarModel.status.in_([PagarStatus.ABERTO, PagarStatus.PARCIAL]),
    )
    total_a_pagar = float((await session.execute(stmt_pag)).scalar_one())

    stmt_rec_venc = select(func.coalesce(func.sum(ContaReceberModel.valor_original), 0)).where(
        ContaReceberModel.status.in_([ReceberStatus.ABERTO, ReceberStatus.PARCIAL]),
        ContaReceberModel.data_vencimento < hoje,
    )
    contas_receber_vencidas = float((await session.execute(stmt_rec_venc)).scalar_one())

    stmt_pag_venc = select(func.coalesce(func.sum(ContaPagarModel.valor_original), 0)).where(
        ContaPagarModel.status.in_([PagarStatus.ABERTO, PagarStatus.PARCIAL]),
        ContaPagarModel.data_vencimento < hoje,
    )
    contas_pagar_vencidas = float((await session.execute(stmt_pag_venc)).scalar_one())

    from database.models.lancamento import LancamentoModel, LancamentoTipo

    stmt_rec_mes = select(func.coalesce(func.sum(LancamentoModel.valor), 0)).where(
        LancamentoModel.tipo == LancamentoTipo.ENTRADA,
        LancamentoModel.data >= inicio_mes,
        LancamentoModel.data <= hoje,
    )
    recebido_mes = float((await session.execute(stmt_rec_mes)).scalar_one())

    stmt_pag_mes = select(func.coalesce(func.sum(LancamentoModel.valor), 0)).where(
        LancamentoModel.tipo == LancamentoTipo.SAIDA,
        LancamentoModel.data >= inicio_mes,
        LancamentoModel.data <= hoje,
    )
    pago_mes = float((await session.execute(stmt_pag_mes)).scalar_one())

    # ── Estoque ──
    stmt_prod = select(func.count()).select_from(ProdutoModel).where(ProdutoModel.ativo.is_(True))
    total_produtos = (await session.execute(stmt_prod)).scalar_one()

    stmt_estq = select(func.count()).select_from(EstoqueModel)
    total_itens_estoque = (await session.execute(stmt_estq)).scalar_one()

    stmt_estq_baixo = (
        select(func.count())
        .select_from(EstoqueModel)
        .join(ProdutoModel, ProdutoModel.id == EstoqueModel.produto_id)
        .where(
            EstoqueModel.quantidade_atual <= ProdutoModel.estoque_minimo,
            ProdutoModel.estoque_minimo > 0,
        )
    )
    estoque_baixo = (await session.execute(stmt_estq_baixo)).scalar_one()

    # ── Alertas ──
    stmt_alertas = (
        select(AlertaModel)
        .where(AlertaModel.lido.is_(False))
        .order_by(AlertaModel.created_at.desc())
        .limit(20)
    )
    alertas_raw = (await session.execute(stmt_alertas)).scalars().all()
    alertas = [
        {
            "id": str(a.id),
            "tipo": a.tipo,
            "nivel": a.nivel.value if hasattr(a.nivel, "value") else str(a.nivel),
            "titulo": a.titulo,
            "mensagem": a.mensagem,
            "lido": a.lido,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alertas_raw
    ]

    stmt_alertas_count = (
        select(func.count()).select_from(AlertaModel).where(AlertaModel.lido.is_(False))
    )
    alertas_pendentes = (await session.execute(stmt_alertas_count)).scalar_one()

    # ── Faturamento últimos meses ──
    meses_sql = func.date_trunc("month", PedidoModel.data_emissao)
    stmt_fat_meses = (
        select(
            meses_sql.label("mes"),
            func.coalesce(func.sum(PedidoModel.total), 0).label("receita"),
            func.count(PedidoModel.id).label("qtd_pedidos"),
        )
        .where(
            PedidoModel.data_emissao >= seis_meses_atras,
            PedidoModel.data_emissao <= hoje,
            PedidoModel.status.notin_([PedidoStatus.CANCELADO, PedidoStatus.RASCUNHO]),
        )
        .group_by(text("mes"))
        .order_by(text("mes"))
    )
    fat_meses_raw = (await session.execute(stmt_fat_meses)).all()
    faturamento_mensal = [
        {"mes": str(row.mes), "receita": float(row.receita), "qtd_pedidos": row.qtd_pedidos}
        for row in fat_meses_raw
    ]

    # ── Pedidos por status ──
    stmt_ped_status = (
        select(PedidoModel.status, func.count(PedidoModel.id))
        .group_by(PedidoModel.status)
    )
    ped_status_raw = (await session.execute(stmt_ped_status)).all()
    pedidos_por_status = {}
    for row in ped_status_raw:
        key = row[0].value if hasattr(row[0], "value") else str(row[0])
        pedidos_por_status[key] = row[1]

    return {
        "cards": {
            "clientes_ativos": clientes_ativos,
            "veiculos_ativos": veiculos_ativos,
            "chopeiras_instaladas": chopeiras_instaladas,
            "faturamento_mes": recebido_mes,
            "ticket_medio": round(
                recebido_mes / max(1, await _count_pedidos_periodo(session, inicio_mes, hoje)), 2
            ),
            "alertas_pendentes": alertas_pendentes,
        },
        "clientes": {
            "total": total_clientes,
            "ativos": clientes_ativos,
            "inativos": clientes_inativos,
            "novos_mes": novos_clientes_mes,
        },
        "veiculos": {
            "total": veiculos_ativos + veiculos_manutencao,
            "ativos": veiculos_ativos,
            "em_manutencao": veiculos_manutencao,
            "proxima_troca_oleo": veiculos_troca_oleo,
        },
        "chopeiras": {
            "total": total_chopeiras,
            "instaladas": chopeiras_instaladas,
            "disponiveis": chopeiras_disponiveis,
            "em_manutencao": chopeiras_manutencao,
            "manutencao_pendente": chopeiras_manut_pendente,
        },
        "financeiro": {
            "total_a_receber": total_a_receber,
            "total_a_pagar": total_a_pagar,
            "saldo_previsto": round(total_a_receber - total_a_pagar, 2),
            "contas_receber_vencidas": contas_receber_vencidas,
            "contas_pagar_vencidas": contas_pagar_vencidas,
            "recebido_mes": recebido_mes,
            "pago_mes": pago_mes,
        },
        "estoque": {
            "total_produtos": total_produtos,
            "total_itens_estoque": total_itens_estoque,
            "estoque_baixo": estoque_baixo,
        },
        "alertas": alertas,
        "faturamento_mensal": faturamento_mensal,
        "pedidos_por_status": pedidos_por_status,
    }


async def _count_pedidos_periodo(session: AsyncSession, inicio: date, fim: date) -> int:
    stmt = select(func.count()).select_from(PedidoModel).where(
        PedidoModel.data_emissao >= inicio,
        PedidoModel.data_emissao <= fim,
        PedidoModel.status.notin_([PedidoStatus.CANCELADO, PedidoStatus.RASCUNHO]),
    )
    result = await session.execute(stmt)
    return result.scalar_one()
