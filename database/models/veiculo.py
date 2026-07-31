import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Boolean, Date, Enum, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.veiculo_historico import VeiculoHistoricoModel
    from database.models.veiculo_km_registro import KmRegistroModel
    from database.models.veiculo_pneu import PneuModel
    from database.models.veiculo_seguro import SeguroModel
    from database.models.veiculo_troca_oleo import TrocaOleoModel


class VeiculoTipo(str, enum.Enum):  # noqa: UP042
    CAMINHAO = "caminhao"
    VAN = "van"
    CARRO = "carro"
    UTILITARIO = "utilitario"


class VeiculoCategoria(str, enum.Enum):  # noqa: UP042
    LEVE = "leve"
    MEDIO = "medio"
    PESADO = "pesado"


class VeiculoCarroceria(str, enum.Enum):  # noqa: UP042
    BAU = "bau"
    GRANELEIRO = "graneleiro"
    TANQUE = "tanque"
    SIDER = "sider"
    ABERTA = "aberta"


class VeiculoStatus(str, enum.Enum):  # noqa: UP042
    DISPONIVEL = "disponivel"
    EM_ROTA = "em_rota"
    MANUTENCAO = "manutencao"
    INATIVO = "inativo"


class VeiculoProprietario(str, enum.Enum):  # noqa: UP042
    PROPRIO = "proprio"
    TERCEIRO = "terceiro"


class VeiculoModel(Base):
    __tablename__ = "veiculo"

    placa: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)
    renavam: Mapped[str | None] = mapped_column(String(20), unique=True)
    chassi: Mapped[str | None] = mapped_column(String(20), unique=True)
    marca: Mapped[str] = mapped_column(String(50), nullable=False)
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    ano_fabricacao: Mapped[int | None] = mapped_column(SmallInteger)
    ano_modelo: Mapped[int | None] = mapped_column(SmallInteger)
    cor: Mapped[str | None] = mapped_column(String(30))
    tipo: Mapped[VeiculoTipo] = mapped_column(
        Enum(VeiculoTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    categoria: Mapped[VeiculoCategoria | None] = mapped_column(
        Enum(VeiculoCategoria, values_callable=lambda x: [e.value for e in x]),
    )
    capacidade_carga_kg: Mapped[float | None] = mapped_column(DECIMAL(8, 2))
    capacidade_volume_m3: Mapped[float | None] = mapped_column(DECIMAL(8, 2))
    tipo_carroceria: Mapped[VeiculoCarroceria | None] = mapped_column(
        Enum(VeiculoCarroceria, values_callable=lambda x: [e.value for e in x]),
    )
    consumo_medio_km_l: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    tanque_capacidade_l: Mapped[float | None] = mapped_column(DECIMAL(7, 2))
    status: Mapped[VeiculoStatus] = mapped_column(
        Enum(VeiculoStatus, values_callable=lambda x: [e.value for e in x]),
        default=VeiculoStatus.DISPONIVEL, nullable=False, index=True
    )
    km_atual: Mapped[int] = mapped_column(Integer, default=0)
    km_proxima_troca_oleo: Mapped[int | None] = mapped_column(Integer)
    proprietario: Mapped[VeiculoProprietario] = mapped_column(
        Enum(VeiculoProprietario, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    terceiro_nome: Mapped[str | None] = mapped_column(String(200))
    terceiro_cpf_cnpj: Mapped[str | None] = mapped_column(String(14))
    data_aquisicao: Mapped[date | None] = mapped_column(Date)
    data_vencimento_seguro: Mapped[date | None] = mapped_column(Date, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    seguros: Mapped[list["SeguroModel"]] = relationship(
        "SeguroModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    pneus: Mapped[list["PneuModel"]] = relationship(
        "PneuModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    trocas_oleo: Mapped[list["TrocaOleoModel"]] = relationship(
        "TrocaOleoModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    km_registros: Mapped[list["KmRegistroModel"]] = relationship(
        "KmRegistroModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    historico: Mapped[list["VeiculoHistoricoModel"]] = relationship(
        "VeiculoHistoricoModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    manutencoes = relationship(
        "ManutencaoModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    abastecimentos = relationship(
        "AbastecimentoModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
    multas = relationship(
        "MultaModel", back_populates="veiculo", cascade="all, delete-orphan"
    )
