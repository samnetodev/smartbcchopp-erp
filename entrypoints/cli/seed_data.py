"""Seed data — cria admin + dados demo para o MVP.

Uso:
    python -m entrypoints.cli.seed_data
"""

import asyncio
import os
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from sqlalchemy import select

os.environ.setdefault("SECRET_KEY", "dev")
os.environ.setdefault("JWT_SECRET_KEY", "dev")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://smartbcchopp:MMFrduU2BUxjelhxXA44bg@localhost:55432/smartbcchopp"
)

from config.security import hash_password
from database.models.alerta import AlertaModel, AlertaNivel
from database.models.chopeira import ChopeiraModel, ChopeiraStatus, ChopeiraTipo
from database.models.cliente import ClienteModel, ClienteStatus, ClienteTipoPessoa
from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel
from database.models.deposito import DepositoModel, DepositoTipo
from database.models.endereco import EnderecoModel
from database.models.estoque import EstoqueModel
from database.models.familia_produto import FamiliaProdutoModel
from database.models.fornecedor import FornecedorCategoria, FornecedorModel
from database.models.lancamento import LancamentoModel, LancamentoTipo
from database.models.pedido import ItemPedidoModel, PedidoModel, PedidoStatus
from database.models.produto import ProdutoCategoria, ProdutoModel, UnidadeMedida
from database.models.usuario import PapelUsuario, UsuarioModel
from database.models.veiculo import (
    VeiculoModel,
    VeiculoProprietario,
    VeiculoStatus,
    VeiculoTipo,
)
from database.session import get_async_session_factory, get_engine

HOJE = date.today()
AGORA = datetime.now(timezone.utc)


async def seed() -> None:
    print("=== SmartBcChopp ERP — Seed ===")

    engine = get_engine()
    async with engine.begin() as conn:
        from database.models import Base
        await conn.run_sync(Base.metadata.create_all)

    factory = get_async_session_factory()

    async with factory() as session:
        # ── Admin ──
        existing = await session.execute(
            select(UsuarioModel).where(UsuarioModel.username == "admin")
        )
        if existing.scalar_one_or_none():
            print("[OK] Admin já existe")
        else:
            session.add(UsuarioModel(
                username="admin",
                email="admin@smartbcchopp.com",
                password_hash=hash_password("admin123"),
                papel=PapelUsuario.ADMIN,
                ativo=True,
            ))
            print("[OK] Admin criado (admin / admin123)")

        # ── Famílias ──
        fam_map = {}
        familia_defs = [
            ("CH", "Chope"),
            ("CV", "Carvão"),
            ("GA", "Gás"),
            ("DS", "Descartáveis"),
        ]
        for codigo, nome in familia_defs:
            f = FamiliaProdutoModel(codigo=codigo, nome=nome)
            session.add(f)
            await session.flush()
            fam_map[nome] = f.id

        # ── Fornecedores ──
        forn_ids = []
        for data in [
            {"nome": "Ambev S.A.", "cnpj": "07526557000100",
             "cat": FornecedorCategoria.CHOPE},
            {"nome": "Carvoeira do Brasil", "cnpj": "12345678000190",
             "cat": FornecedorCategoria.CARVAO},
            {"nome": "Ultragaz", "cnpj": "33597556000128",
             "cat": FornecedorCategoria.INSUMOS},
        ]:
            f = FornecedorModel(
                tipo_pessoa="PJ",
                nome_razao_social=data["nome"],
                cpf_cnpj=data["cnpj"],
                categoria=data["cat"],
            )
            session.add(f)
            await session.flush()
            forn_ids.append(f.id)

        # ── Endereço do depósito + Depósito ──
        dep_end = EnderecoModel(
            logradouro="Av. Principal",
            numero="1000",
            bairro="Centro",
            cidade="São Paulo",
            estado="SP",
            cep="01001000",
        )
        session.add(dep_end)
        await session.flush()

        dep = DepositoModel(
            codigo="DEP01",
            nome="Depósito Principal",
            tipo=DepositoTipo.DEPOSITO,
            endereco_id=dep_end.id,
        )
        session.add(dep)
        await session.flush()

        # ── Produtos + Estoque ──
        prods = []
        prod_data = [
            ("Chope Brahma 50L", "CH-BRA-50", ProdutoCategoria.CHOPE,
             UnidadeMedida.L, Decimal("289.90"), 45, 10, "Chope"),
            ("Chope Skol 50L", "CH-SKO-50", ProdutoCategoria.CHOPE,
             UnidadeMedida.L, Decimal("269.90"), 38, 10, "Chope"),
            ("Chope Antarctica 50L", "CH-ANT-50", ProdutoCategoria.CHOPE,
             UnidadeMedida.L, Decimal("275.00"), 52, 10, "Chope"),
            ("Chope Heineken 50L", "CH-HEI-50", ProdutoCategoria.CHOPE,
             UnidadeMedida.L, Decimal("359.90"), 28, 8, "Chope"),
            ("Carvão V8 10kg", "CV-V8-10", ProdutoCategoria.CARVAO,
             UnidadeMedida.SACO, Decimal("22.90"), 200, 50, "Carvão"),
            ("Carvão Minas Grill 5kg", "CV-MG-05", ProdutoCategoria.CARVAO,
             UnidadeMedida.SACO, Decimal("14.90"), 350, 100, "Carvão"),
            ("Carvão Reserva 25kg", "CV-RE-25", ProdutoCategoria.CARVAO,
             UnidadeMedida.SACO, Decimal("38.90"), 3, 20, "Carvão"),
            ("Gás P13", "GA-P13", ProdutoCategoria.TRANSPORTE,
             UnidadeMedida.UN, Decimal("105.00"), 80, 30, "Gás"),
            ("Gás P45", "GA-P45", ProdutoCategoria.TRANSPORTE,
             UnidadeMedida.UN, Decimal("245.00"), 2, 10, "Gás"),
            ("Copo Descartável 300ml", "DS-COP-300", ProdutoCategoria.TRANSPORTE,
             UnidadeMedida.UN, Decimal("12.90"), 500, 100, "Descartáveis"),
        ]
        for nome, codigo, cat, unid, preco, qtd, minimo, fam_nome in prod_data:
            p = ProdutoModel(
                codigo=codigo,
                nome=nome,
                categoria=cat,
                unidade_medida=unid,
                preco_venda=preco,
                estoque_minimo=minimo,
                familia_id=fam_map[fam_nome],
            )
            session.add(p)
            await session.flush()
            session.add(EstoqueModel(
                produto_id=p.id,
                deposito_id=dep.id,
                quantidade_atual=qtd,
            ))
            prods.append(p)

        # ── Clientes ──
        cli_data = [
            ("Bar do Zé", "Bar do Zé", "11222333000181",
             ClienteStatus.ATIVO, "São Paulo"),
            ("Choperia do João", "Choperia do João", "44555666000199",
             ClienteStatus.ATIVO, "Campinas"),
            ("Restaurante KiDelicia", "Restaurante KiDelicia", "77888999000155",
             ClienteStatus.ATIVO, "São Bernardo"),
            ("Padaria Pão Quente", "Padaria Pão Quente", "99888777000122",
             ClienteStatus.ATIVO, "Santo André"),
            ("Casa de Carnes Boi Nobre", "Casa de Carnes Boi Nobre",
             "33222111000144", ClienteStatus.ATIVO, "Osasco"),
            ("Mercado do Povo", "Mercado do Povo", "55444333000177",
             ClienteStatus.INATIVO, "São Paulo"),
            ("Clube Recreativo", "Clube Recreativo", "66555444000188",
             ClienteStatus.ATIVO, "Guarulhos"),
            ("Distribuidora JS", "Distribuidora JS", "77666555000199",
             ClienteStatus.ATIVO, "São Paulo"),
        ]
        clientes = []
        for nome_razao, nome_fant, doc, status, cidade in cli_data:
            ender = EnderecoModel(
                logradouro=f"Rua {nome_fant}",
                numero="100",
                bairro="Centro",
                cidade=cidade,
                estado="SP",
                cep="01001000",
            )
            session.add(ender)
            await session.flush()
            c = ClienteModel(
                tipo_pessoa=ClienteTipoPessoa.PJ,
                nome_razao_social=nome_razao,
                nome_fantasia=nome_fant,
                cpf_cnpj=doc,
                status=status,
                endereco_id=ender.id,
            )
            session.add(c)
            await session.flush()
            clientes.append(c)

            if status == ClienteStatus.ATIVO:
                for m in range(1, 4):
                    mes = HOJE.month - m
                    ano = HOJE.year
                    if mes <= 0:
                        mes += 12
                        ano -= 1
                    data = date(ano, mes, 20)
                    total = Decimal(
                        str(300 * (len(clientes) + 1) + m * 50)
                    )
                    ped = PedidoModel(
                        numero=f"PED-{len(clientes)}-{m}",
                        cliente_id=c.id,
                        data_emissao=data,
                        subtotal=total,
                        total=total,
                        status=PedidoStatus.APROVADO,
                    )
                    session.add(ped)
                    await session.flush()
                    qtd = m + 2
                    vu = prods[m % len(prods)].preco_venda
                    session.add(ItemPedidoModel(
                        pedido_id=ped.id,
                        produto_id=prods[m % len(prods)].id,
                        quantidade=qtd,
                        preco_unitario=vu,
                        subtotal=vu * qtd,
                        ordem=m,
                    ))
                    session.add(LancamentoModel(
                        tipo=LancamentoTipo.ENTRADA,
                        valor=total,
                        categoria="receita",
                        descricao=f"Pedido #{len(clientes)}-{m}",
                        data=data,
                    ))

        # ── Chopeiras ──
        chopeira_data = [
            ("CHP-001", "Brahma 2 Torres", ChopeiraStatus.INSTALADA, 0),
            ("CHP-002", "Skol 1 Torre", ChopeiraStatus.INSTALADA, 1),
            ("CHP-003", "Antarctica 2 Torres", ChopeiraStatus.INSTALADA, 2),
            ("CHP-004", "Heineken 3 Torres", ChopeiraStatus.INSTALADA, 3),
            ("CHP-005", "Brahma 1 Torre", ChopeiraStatus.INSTALADA, 6),
            ("CHP-006", "Skol 2 Torres", ChopeiraStatus.DISPONIVEL, None),
            ("CHP-007", "Ambev 2 Torres", ChopeiraStatus.DISPONIVEL, None),
            ("CHP-008", "Heineken 1 Torre", ChopeiraStatus.MANUTENCAO, None),
            ("CHP-009", "Brahma 2 Torres", ChopeiraStatus.MANUTENCAO, None),
            ("CHP-010", "Skol 1 Torre", ChopeiraStatus.INSTALADA, 7),
        ]
        for i, (cod, modelo, status, cli_idx) in enumerate(chopeira_data):
            session.add(ChopeiraModel(
                codigo_identificacao=cod,
                marca=modelo.split()[0],
                modelo=modelo,
                tipo=ChopeiraTipo.CHOPEIRA,
                status=status,
                capacidade_l=50,
                cliente_id=(
                    clientes[cli_idx].id if cli_idx is not None else None
                ),
                data_proxima_manutencao=HOJE + timedelta(days=60 - i * 5),
                ativo=True,
            ))

        # ── Veículos ──
        veic_data = [
            ("ABC1D23", "Fiat Fiorino 1.4", "Fiat", VeiculoTipo.UTILITARIO,
             VeiculoStatus.DISPONIVEL, 45230, 2021, 75230),
            ("DEF4G56", "VW Delivery Express", "Volkswagen",
             VeiculoTipo.UTILITARIO, VeiculoStatus.DISPONIVEL, 78210, 2022,
             108210),
            ("GHI7J89", "Mercedes Sprinter 416", "Mercedes-Benz",
             VeiculoTipo.VAN, VeiculoStatus.DISPONIVEL, 123450, 2020, 153450),
            ("JKL0M12", "Ford Transit 350", "Ford", VeiculoTipo.VAN,
             VeiculoStatus.MANUTENCAO, 89000, 2023, 119000),
            ("MNO3P45", "Iveco Daily 35S", "Iveco", VeiculoTipo.UTILITARIO,
             VeiculoStatus.DISPONIVEL, 34560, 2022, 64560),
            ("PQR6S78", "VW Delivery 11.180", "Volkswagen",
             VeiculoTipo.CAMINHAO, VeiculoStatus.DISPONIVEL, 56780, 2021,
             86780),
        ]
        for placa, modelo, marca, tipo, status, km, ano, km_troca in veic_data:
            session.add(VeiculoModel(
                placa=placa,
                marca=marca,
                modelo=modelo,
                tipo=tipo,
                ano_fabricacao=ano,
                status=status,
                km_atual=km,
                km_proxima_troca_oleo=km_troca,
                proprietario=VeiculoProprietario.PROPRIO,
                ativo=True,
            ))

        # ── Contas ──
        session.add(ContaReceberModel(
            cliente_id=clientes[0].id,
            numero_documento="FAT-001",
            data_emissao=HOJE - timedelta(days=30),
            valor_original=Decimal("5450.00"),
            data_vencimento=HOJE - timedelta(days=3),
        ))
        session.add(ContaReceberModel(
            cliente_id=clientes[1].id,
            numero_documento="FAT-002",
            data_emissao=HOJE - timedelta(days=20),
            valor_original=Decimal("3200.00"),
            data_vencimento=HOJE + timedelta(days=5),
        ))
        session.add(ContaPagarModel(
            fornecedor_id=forn_ids[0],
            numero_documento="NF-1024",
            data_emissao=HOJE - timedelta(days=5),
            valor_original=Decimal("12500.00"),
            data_vencimento=HOJE + timedelta(days=10),
            categoria="estoque",
        ))
        session.add(ContaPagarModel(
            fornecedor_id=forn_ids[1],
            numero_documento="NF-1025",
            data_emissao=HOJE - timedelta(days=3),
            valor_original=Decimal("3450.00"),
            data_vencimento=HOJE - timedelta(days=1),
            categoria="estoque",
        ))

        # ── Alertas ──
        alertas = [
            ("manutencao", AlertaNivel.CRITICAL,
             "Chopeira #142 sem manutenção há 45 dias",
             "Risco de falha iminente. Agendar manutenção urgente."),
            ("estoque", AlertaNivel.WARNING,
             "Estoque baixo: Carvão Reserva 25kg",
             "Restam 3 unidades. Mínimo é 20."),
            ("cliente", AlertaNivel.INFO,
             "Cliente João Barbosa completa 1 ano",
             "Considere enviar um brinde promocional."),
            ("veiculo", AlertaNivel.WARNING,
             "Troca de óleo: VW Delivery #003",
             "45.230 km rodados. Troca aos 50.000 km."),
            ("boleto", AlertaNivel.CRITICAL,
             "Boleto vencido: R$ 5.450,00",
             "Cliente: Bar do Zé. 3 dias em atraso."),
            ("veiculo", AlertaNivel.WARNING,
             "Seguro vencendo: Fiat Fiorino ABC1D23",
             "Vencimento em 15 dias."),
            ("estoque", AlertaNivel.WARNING,
             "Gás P45 crítico",
             "Restam 2 unidades. Repor urgentemente."),
            ("chopeira", AlertaNivel.WARNING,
             "CHP-008 em manutenção há 12 dias",
             "Tempo máximo: 7 dias."),
            ("financeiro", AlertaNivel.INFO,
             "Conta a pagar: R$ 12.500,00",
             "Fornecedor: Ambev. Vence amanhã."),
            ("documento", AlertaNivel.WARNING,
             "CRLV vencido: Mercedes Sprinter GHI7J89",
             "Venceu há 5 dias."),
            ("manutencao", AlertaNivel.INFO,
             "Manutenção preventiva: CHP-004",
             "Cliente: Padaria Pão Quente. Em 7 dias."),
            ("cliente", AlertaNivel.INFO,
             "Mercado do Povo inativo há 60+ dias",
             "Última compra: 27/05/2026."),
        ]
        for tipo, nivel, titulo, msg in alertas:
            session.add(AlertaModel(
                tipo=tipo, nivel=nivel, titulo=titulo, mensagem=msg,
            ))

        await session.commit()

    print(
        f"[OK] {len(cli_data)} clientes, {len(prod_data)} produtos, "
        f"{len(chopeira_data)} chopeiras, {len(veic_data)} veículos, "
        f"{len(alertas)} alertas"
    )
    print("Login: admin / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
