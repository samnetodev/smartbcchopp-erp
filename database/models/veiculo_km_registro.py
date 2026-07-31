import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class KmRegistroModel(Base):
    __tablename__ = "veiculo_km_registro"

    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    km: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="leitura_manual | abastecimento | manutencao",
    )
    origem: Mapped[str | None] = mapped_column(String(100))
    observacao: Mapped[str | None] = mapped_column(Text)

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )

    veiculo = relationship("VeiculoModel", back_populates="km_registros")
