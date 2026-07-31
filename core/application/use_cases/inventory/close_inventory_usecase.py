from uuid import UUID

from database.models.inventario import InventarioModel, InventarioStatus
from database.models.movimentacao import MovimentacaoModel, MovimentacaoTipo
from database.repositories.estoque_repository_impl import EstoqueRepositoryImpl
from database.repositories.inventario_repository_impl import InventarioRepositoryImpl
from database.repositories.movimentacao_repository_impl import MovimentacaoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


class CloseInventoryCountUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, inventario_id: UUID, usuario_id: UUID | None = None
    ) -> InventarioModel:
        inv_repo = InventarioRepositoryImpl(self._uow.session)
        estoque_repo = EstoqueRepositoryImpl(self._uow.session)
        mov_repo = MovimentacaoRepositoryImpl(self._uow.session)

        inventario = await inv_repo.find_by_id(inventario_id)
        if not inventario:
            raise ValueError("Inventário não encontrado")
        if inventario.status != InventarioStatus.ABERTO:
            raise ValueError("Inventário já está fechado")

        estoque = await estoque_repo.find_one_by_produto_deposito(
            inventario.produto_id, inventario.deposito_id, inventario.lote_id
        )

        diff = inventario.quantidade_contada - inventario.quantidade_sistema

        if estoque:
            estoque.quantidade_atual = inventario.quantidade_contada
        else:
            from database.models.estoque import EstoqueModel

            estoque = EstoqueModel(
                produto_id=inventario.produto_id,
                deposito_id=inventario.deposito_id,
                lote_id=inventario.lote_id,
                quantidade_atual=inventario.quantidade_contada,
            )
            await estoque_repo.save(estoque)

        movement = MovimentacaoModel(
            tipo=MovimentacaoTipo.AJUSTE,
            quantidade=abs(diff),
            observacao=f"Ajuste por inventário: {inventario.observacao or 'contagem física'}",
            produto_id=inventario.produto_id,
            deposito_id_origem=inventario.deposito_id,
            lote_id=inventario.lote_id,
            usuario_id=usuario_id,
        )
        await mov_repo.save(movement)

        inventario.status = InventarioStatus.FECHADO
        inventario.diferenca = diff
        await self._uow.commit()

        return inventario
