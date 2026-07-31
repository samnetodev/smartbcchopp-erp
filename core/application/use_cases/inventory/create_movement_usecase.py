from dataclasses import dataclass
from uuid import UUID

from database.models.estoque import EstoqueModel
from database.models.movimentacao import MovimentacaoModel, MovimentacaoTipo
from database.repositories.estoque_repository_impl import EstoqueRepositoryImpl
from database.repositories.movimentacao_repository_impl import MovimentacaoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


@dataclass
class MovementInput:
    tipo: str
    produto_id: UUID
    quantidade: float
    deposito_id_origem: UUID
    deposito_id_destino: UUID | None = None
    lote_id: UUID | None = None
    motivo_perda: str | None = None
    documento_tipo: str | None = None
    documento_numero: str | None = None
    documento_id: UUID | None = None
    pedido_id: UUID | None = None
    pedido_compra_id: UUID | None = None
    usuario_id: UUID | None = None
    observacao: str | None = None


class CreateMovementUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, input_data: MovementInput) -> MovimentacaoModel:
        estoque_repo = EstoqueRepositoryImpl(self._uow.session)
        mov_repo = MovimentacaoRepositoryImpl(self._uow.session)

        tipo = MovimentacaoTipo(input_data.tipo)

        if tipo == MovimentacaoTipo.SAIDA or tipo == MovimentacaoTipo.PERDA:
            saldo = await estoque_repo.find_one_by_produto_deposito(
                input_data.produto_id, input_data.deposito_id_origem, input_data.lote_id
            )
            if not saldo or saldo.quantidade_atual < input_data.quantidade:
                raise ValueError("Estoque insuficiente")

        movement = MovimentacaoModel(
            tipo=tipo,
            quantidade=input_data.quantidade,
            motivo_perda=input_data.motivo_perda if tipo == MovimentacaoTipo.PERDA else None,
            documento_tipo=input_data.documento_tipo,
            documento_numero=input_data.documento_numero,
            documento_id=input_data.documento_id,
            observacao=input_data.observacao,
            produto_id=input_data.produto_id,
            deposito_id_origem=input_data.deposito_id_origem,
            deposito_id_destino=(
                input_data.deposito_id_destino if tipo == MovimentacaoTipo.TRANSFERENCIA else None
            ),
            lote_id=input_data.lote_id,
            pedido_id=input_data.pedido_id,
            pedido_compra_id=input_data.pedido_compra_id,
            usuario_id=input_data.usuario_id,
        )
        await mov_repo.save(movement)

        if tipo in (MovimentacaoTipo.ENTRADA, MovimentacaoTipo.DEVOLUCAO):
            await self._ajustar_saldo(estoque_repo, input_data, +input_data.quantidade)

        elif tipo in (MovimentacaoTipo.SAIDA, MovimentacaoTipo.PERDA):
            await self._ajustar_saldo(estoque_repo, input_data, -input_data.quantidade)

        elif tipo == MovimentacaoTipo.AJUSTE:
            saldo = await estoque_repo.find_one_by_produto_deposito(
                input_data.produto_id, input_data.deposito_id_origem, input_data.lote_id
            )
            if saldo:
                diff = input_data.quantidade - float(saldo.quantidade_atual)
                saldo.quantidade_atual = float(saldo.quantidade_atual) + diff
            else:
                estoque = EstoqueModel(
                    produto_id=input_data.produto_id,
                    deposito_id=input_data.deposito_id_origem,
                    lote_id=input_data.lote_id,
                    quantidade_atual=input_data.quantidade,
                )
                await estoque_repo.save(estoque)

        elif tipo == MovimentacaoTipo.TRANSFERENCIA:
            if not input_data.deposito_id_destino:
                raise ValueError("Depósito destino é obrigatório para transferência")
            await self._ajustar_saldo(estoque_repo, input_data, -input_data.quantidade)
            dest_input = MovementInput(
                tipo="entrada",
                produto_id=input_data.produto_id,
                quantidade=input_data.quantidade,
                deposito_id_origem=input_data.deposito_id_destino,
                lote_id=input_data.lote_id,
            )
            await self._ajustar_saldo(estoque_repo, dest_input, +input_data.quantidade)

        await self._uow.commit()
        return movement

    async def _ajustar_saldo(
        self, repo: EstoqueRepositoryImpl, input_data: MovementInput, delta: float
    ) -> None:
        saldo = await repo.find_one_by_produto_deposito(
            input_data.produto_id, input_data.deposito_id_origem, input_data.lote_id
        )
        if saldo:
            saldo.quantidade_atual = float(saldo.quantidade_atual) + delta
        elif delta > 0:
            estoque = EstoqueModel(
                produto_id=input_data.produto_id,
                deposito_id=input_data.deposito_id_origem,
                lote_id=input_data.lote_id,
                quantidade_atual=delta,
            )
            await repo.save(estoque)
