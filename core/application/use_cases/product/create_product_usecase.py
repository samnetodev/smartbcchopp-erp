from dataclasses import dataclass
from typing import Any

from database.repositories.produto_repository_impl import ProdutoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


@dataclass
class CreateProductInput:
    codigo: str
    nome: str
    categoria: str
    unidade_medida: str
    preco_venda: float
    preco_custo: float | None = None
    familia_id: str | None = None
    ncm: str | None = None
    codigo_barras: str | None = None
    estoque_minimo: float = 0
    lote_obrigatorio: bool = False


class CreateProductUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, input_data: CreateProductInput) -> dict[str, Any]:
        from database.models.produto import ProdutoModel

        repo = ProdutoRepositoryImpl(self._uow.session)

        existing = await repo.find_by_codigo(input_data.codigo)
        if existing:
            raise ValueError(f"Produto com código '{input_data.codigo}' já existe")

        if input_data.codigo_barras:
            existing_barcode = await repo.find_by_codigo_barras(input_data.codigo_barras)
            if existing_barcode:
                raise ValueError(f"Código de barras '{input_data.codigo_barras}' já cadastrado")

        product = ProdutoModel(
            codigo=input_data.codigo,
            nome=input_data.nome,
            categoria=input_data.categoria,
            unidade_medida=input_data.unidade_medida,
            preco_venda=input_data.preco_venda,
            preco_custo=input_data.preco_custo or 0,
            ncm=input_data.ncm,
            estoque_minimo=input_data.estoque_minimo,
            lote_obrigatorio=input_data.lote_obrigatorio,
        )

        await repo.save(product)
        await self._uow.commit()

        return {
            "id": str(product.id),
            "codigo": product.codigo,
            "nome": product.nome,
            "categoria": product.categoria,
            "preco_venda": product.preco_venda,
        }
