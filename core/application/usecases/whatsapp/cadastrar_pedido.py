import uuid
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.shared.result import Failure, Success
from database.models.pedido import ItemPedidoModel, PedidoModel, PedidoStatus
from database.repositories.cliente_repository_impl import ClienteRepositoryImpl
from database.repositories.produto_repository_impl import ProdutoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


class CadastrarPedidoWhatsAppUseCase:
    """Cadastra pedido simplificado a partir de dados extraídos do WhatsApp."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cliente_repo = ClienteRepositoryImpl(session)
        self._produto_repo = ProdutoRepositoryImpl(session)

    async def executar(
        self,
        cliente_id: uuid.UUID,
        produto_nome: str,
        quantidade: float,
    ) -> Success[dict[str, Any]] | Failure[str]:
        try:
            cliente = await self._cliente_repo.find_by_id(cliente_id)
            if not cliente:
                return Failure("cliente_nao_encontrado")

            produtos = await self._produto_repo.search(produto_nome, limit=1)
            if not produtos:
                return Failure("produto_nao_encontrado")

            produto = produtos[0]
            preco = produto.preco_venda or 0
            subtotal = quantidade * preco
            numero = f"WA{date.today().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

            pedido = PedidoModel(
                numero=numero,
                cliente_id=cliente_id,
                status=PedidoStatus.RASCUNHO,
                subtotal=subtotal,
                total=subtotal,
                data_emissao=date.today(),
            )
            self._session.add(pedido)
            await self._session.flush()

            item = ItemPedidoModel(
                quantidade=quantidade,
                preco_unitario=preco,
                subtotal=subtotal,
                ordem=1,
                pedido_id=pedido.id,
                produto_id=produto.id,
            )
            self._session.add(item)

            uow = AsyncUnitOfWork(self._session)
            await uow.commit()

            return Success({
                "id": pedido.id,
                "numero": pedido.numero,
                "total": float(pedido.total),
                "status": pedido.status.value,
            })
        except Exception as e:
            await self._session.rollback()
            return Failure(str(e))
