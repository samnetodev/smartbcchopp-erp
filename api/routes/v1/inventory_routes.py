from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import get_current_user, requer_permissao
from api.serializers.inventory_schema import (
    AdjustmentCreate,
    DepositoResponse,
    EntryCreate,
    ExitCreate,
    InventoryCountCreate,
    InventoryCountListResponse,
    InventoryCountResponse,
    LossCreate,
    LowStockReportItem,
    MovementListResponse,
    MovementResponse,
    StockListResponse,
    StockResponse,
    StockValueReportItem,
    TransferCreate,
)
from core.application.use_cases.inventory.close_inventory_usecase import CloseInventoryCountUseCase
from core.application.use_cases.inventory.create_movement_usecase import (
    CreateMovementUseCase,
    MovementInput,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.deposito import DepositoModel
from database.models.estoque import EstoqueModel
from database.models.inventario import InventarioModel
from database.models.produto import ProdutoModel
from database.repositories.estoque_repository_impl import EstoqueRepositoryImpl
from database.repositories.inventario_repository_impl import InventarioRepositoryImpl
from database.repositories.movimentacao_repository_impl import MovimentacaoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


# ─── Depósitos ──────────────────────────────────────────────────────────────────


@router.get("/depositos", response_model=list[DepositoResponse])
async def list_depositos(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> list[DepositoResponse]:
    result = await session.execute(
        select(DepositoModel).where(DepositoModel.ativo.is_(True)).order_by(DepositoModel.nome)
    )
    return [DepositoResponse.model_validate(d) for d in result.scalars().all()]


# ─── Saldo (Stock Balance) ─────────────────────────────────────────────────────


@router.get("/stock", response_model=StockListResponse)
async def list_stock(
    deposito_id: UUID | None = None,
    produto_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> StockListResponse:
    repo = EstoqueRepositoryImpl(session)

    if deposito_id:
        items = await repo.find_by_deposito(deposito_id)
    elif produto_id:
        items = await repo.find_by_produto(produto_id)
    else:
        items = await repo.find_all(skip=skip, limit=limit)

    total = len(items) if (deposito_id or produto_id) else await repo.count()

    return StockListResponse(
        items=[StockResponse.model_validate(s) for s in items],
        total=total,
    )


@router.get("/stock/{produto_id}", response_model=list[StockResponse])
async def get_product_stock(
    produto_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> list[StockResponse]:
    repo = EstoqueRepositoryImpl(session)
    items = await repo.find_by_produto(produto_id)
    return [StockResponse.model_validate(s) for s in items]


@router.get("/stock/{produto_id}/{deposito_id}", response_model=StockResponse)
async def get_product_stock_at_deposito(
    produto_id: UUID,
    deposito_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> StockResponse:
    repo = EstoqueRepositoryImpl(session)
    saldo = await repo.find_one_by_produto_deposito(produto_id, deposito_id)
    if not saldo:
        msg = "Estoque não encontrado para este produto/depósito"
        raise HTTPException(status_code=404, detail=msg)
    return StockResponse.model_validate(saldo)


# ─── Movimentações (Movements — unified) ────────────────────────────────────────


@router.get("/movements", response_model=MovementListResponse)
async def list_movements(
    tipo: str | None = None,
    produto_id: UUID | None = None,
    deposito_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> MovementListResponse:
    repo = MovimentacaoRepositoryImpl(session)
    from database.models.movimentacao import MovimentacaoTipo

    tipo_enum = MovimentacaoTipo(tipo) if tipo else None
    items = await repo.find_all_filtered(
        tipo=tipo_enum, produto_id=produto_id, deposito_id=deposito_id, skip=skip, limit=limit
    )
    total = await repo.count_filtered(
        tipo=tipo_enum, produto_id=produto_id, deposito_id=deposito_id
    )

    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


# ─── Entradas ────────────────────────────────────────────────────────────────────


@router.post("/entries", response_model=MovementResponse, status_code=201)
async def create_entry(
    body: EntryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.CRIAR)),
) -> MovementResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CreateMovementUseCase(uow)
    movement = await use_case.execute(
        MovementInput(
            tipo="entrada",
            produto_id=body.produto_id,
            quantidade=float(body.quantidade),
            deposito_id_origem=body.deposito_id,
            lote_id=body.lote_id,
            documento_tipo=body.documento_tipo,
            documento_numero=body.documento_numero,
            documento_id=body.documento_id,
            observacao=body.observacao,
        )
    )
    return MovementResponse.model_validate(movement)


@router.get("/entries", response_model=MovementListResponse)
async def list_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> MovementListResponse:
    from database.models.movimentacao import MovimentacaoTipo

    repo = MovimentacaoRepositoryImpl(session)
    items = await repo.find_by_tipo(MovimentacaoTipo.ENTRADA, skip=skip, limit=limit)
    total = await repo.count_by_tipo(MovimentacaoTipo.ENTRADA)
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


# ─── Saídas ──────────────────────────────────────────────────────────────────────


@router.post("/exits", response_model=MovementResponse, status_code=201)
async def create_exit(
    body: ExitCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.CRIAR)),
) -> MovementResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CreateMovementUseCase(uow)
    try:
        movement = await use_case.execute(
            MovementInput(
                tipo="saida",
                produto_id=body.produto_id,
                quantidade=float(body.quantidade),
                deposito_id_origem=body.deposito_id,
                lote_id=body.lote_id,
                documento_tipo=body.documento_tipo,
                documento_numero=body.documento_numero,
                documento_id=body.documento_id,
                observacao=body.observacao,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MovementResponse.model_validate(movement)


@router.get("/exits", response_model=MovementListResponse)
async def list_exits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> MovementListResponse:
    from database.models.movimentacao import MovimentacaoTipo

    repo = MovimentacaoRepositoryImpl(session)
    items = await repo.find_by_tipo(MovimentacaoTipo.SAIDA, skip=skip, limit=limit)
    total = await repo.count_by_tipo(MovimentacaoTipo.SAIDA)
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


# ─── Transferências ─────────────────────────────────────────────────────────────


@router.post("/transfers", response_model=MovementResponse, status_code=201)
async def create_transfer(
    body: TransferCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.CRIAR)),
) -> MovementResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CreateMovementUseCase(uow)
    try:
        movement = await use_case.execute(
            MovementInput(
                tipo="transferencia",
                produto_id=body.produto_id,
                quantidade=float(body.quantidade),
                deposito_id_origem=body.deposito_id_origem,
                deposito_id_destino=body.deposito_id_destino,
                lote_id=body.lote_id,
                observacao=body.observacao,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MovementResponse.model_validate(movement)


@router.get("/transfers", response_model=MovementListResponse)
async def list_transfers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> MovementListResponse:
    from database.models.movimentacao import MovimentacaoTipo

    repo = MovimentacaoRepositoryImpl(session)
    items = await repo.find_by_tipo(MovimentacaoTipo.TRANSFERENCIA, skip=skip, limit=limit)
    total = await repo.count_by_tipo(MovimentacaoTipo.TRANSFERENCIA)
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


# ─── Perdas ─────────────────────────────────────────────────────────────────────


@router.post("/losses", response_model=MovementResponse, status_code=201)
async def create_loss(
    body: LossCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.CRIAR)),
) -> MovementResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CreateMovementUseCase(uow)
    try:
        movement = await use_case.execute(
            MovementInput(
                tipo="perda",
                produto_id=body.produto_id,
                quantidade=float(body.quantidade),
                deposito_id_origem=body.deposito_id,
                lote_id=body.lote_id,
                motivo_perda=body.motivo,
                observacao=body.observacao,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MovementResponse.model_validate(movement)


@router.get("/losses", response_model=MovementListResponse)
async def list_losses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> MovementListResponse:
    from database.models.movimentacao import MovimentacaoTipo

    repo = MovimentacaoRepositoryImpl(session)
    items = await repo.find_by_tipo(MovimentacaoTipo.PERDA, skip=skip, limit=limit)
    total = await repo.count_by_tipo(MovimentacaoTipo.PERDA)
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


# ─── Ajustes ────────────────────────────────────────────────────────────────────


@router.post("/adjustments", response_model=MovementResponse, status_code=201)
async def create_adjustment(
    body: AdjustmentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.CRIAR)),
) -> MovementResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CreateMovementUseCase(uow)
    movement = await use_case.execute(
        MovementInput(
            tipo="ajuste",
            produto_id=body.produto_id,
            quantidade=float(body.quantidade_nova),
            deposito_id_origem=body.deposito_id,
            lote_id=body.lote_id,
            observacao=body.observacao,
        )
    )
    return MovementResponse.model_validate(movement)


@router.get("/adjustments", response_model=MovementListResponse)
async def list_adjustments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> MovementListResponse:
    from database.models.movimentacao import MovimentacaoTipo

    repo = MovimentacaoRepositoryImpl(session)
    items = await repo.find_by_tipo(MovimentacaoTipo.AJUSTE, skip=skip, limit=limit)
    total = await repo.count_by_tipo(MovimentacaoTipo.AJUSTE)
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


# ─── Inventário Físico (Inventory Count) ────────────────────────────────────────


@router.post("/inventory-count", response_model=InventoryCountResponse, status_code=201)
async def create_inventory_count(
    body: InventoryCountCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.CRIAR)),
) -> InventoryCountResponse:
    repo = EstoqueRepositoryImpl(session)
    inv_repo = InventarioRepositoryImpl(session)

    saldo = await repo.find_one_by_produto_deposito(
        body.produto_id, body.deposito_id, body.lote_id
    )
    qtd_sistema = float(saldo.quantidade_atual) if saldo else 0

    inventario = InventarioModel(
        status="aberto",
        produto_id=body.produto_id,
        deposito_id=body.deposito_id,
        lote_id=body.lote_id,
        quantidade_sistema=qtd_sistema,
        quantidade_contada=float(body.quantidade_contada),
        diferenca=float(body.quantidade_contada) - qtd_sistema,
        observacao=body.observacao,
        usuario_id=UUID(current_user["sub"]),
    )
    await inv_repo.save(inventario)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return InventoryCountResponse.model_validate(inventario)


@router.get("/inventory-count", response_model=InventoryCountListResponse)
async def list_inventory_counts(
    deposito_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> InventoryCountListResponse:
    inv_repo = InventarioRepositoryImpl(session)

    if deposito_id:
        items = await inv_repo.find_by_deposito(deposito_id, skip=skip, limit=limit)
        total = len(items)
    else:
        items = await inv_repo.find_all(skip=skip, limit=limit)
        total = await inv_repo.count()

    return InventoryCountListResponse(
        items=[InventoryCountResponse.model_validate(i) for i in items],
        total=total,
    )


@router.post("/inventory-count/{inventario_id}/close", response_model=InventoryCountResponse)
async def close_inventory_count(
    inventario_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.ATUALIZAR)),
) -> InventoryCountResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CloseInventoryCountUseCase(uow)
    try:
        inventario = await use_case.execute(inventario_id, usuario_id=UUID(current_user["sub"]))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return InventoryCountResponse.model_validate(inventario)


# ─── Relatórios ─────────────────────────────────────────────────────────────────


@router.get("/reports/low-stock", response_model=list[LowStockReportItem])
async def low_stock_report(
    deposito_id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> list[LowStockReportItem]:
    repo = EstoqueRepositoryImpl(session)
    items = await repo.find_estoque_critico(deposito_id)

    result: list[LowStockReportItem] = []
    for item in items:
        produto = await session.get(ProdutoModel, item.produto_id)
        deposito = await session.get(DepositoModel, item.deposito_id)
        result.append(
            LowStockReportItem(
                produto_id=item.produto_id,
                produto_codigo=produto.codigo if produto else "",
                produto_nome=produto.nome if produto else "",
                deposito_id=item.deposito_id,
                deposito_nome=deposito.nome if deposito else "",
                quantidade_atual=Decimal(str(item.quantidade_atual)),
                estoque_minimo=Decimal(str(produto.estoque_minimo if produto else 0)),
            )
        )
    return result


@router.get("/reports/stock-value", response_model=list[StockValueReportItem])
async def stock_value_report(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.ESTOQUE, Acao.LER)),
) -> list[StockValueReportItem]:
    from sqlalchemy import select as sa_select

    stmt = sa_select(
        EstoqueModel.produto_id,
        func.sum(EstoqueModel.quantidade_atual).label("quantidade_total"),
        func.avg(ProdutoModel.preco_custo).label("preco_custo_medio"),
        func.sum(
            EstoqueModel.quantidade_atual * literal_column("produto.preco_custo")
        ).label("valor_total"),
    ).join(
        ProdutoModel, EstoqueModel.produto_id == ProdutoModel.id
    ).group_by(EstoqueModel.produto_id)

    rows = (await session.execute(stmt)).all()

    result: list[StockValueReportItem] = []
    for row in rows:
        produto = await session.get(ProdutoModel, row.produto_id)
        result.append(
            StockValueReportItem(
                produto_id=row.produto_id,
                produto_codigo=produto.codigo if produto else "",
                produto_nome=produto.nome if produto else "",
                quantidade_total=Decimal(str(row.quantidade_total or 0)),
                preco_custo_medio=Decimal(str(row.preco_custo_medio or 0)),
                valor_total=Decimal(str(row.valor_total or 0)),
            )
        )
    return result
