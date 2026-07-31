import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class DocumentoModel(Base):
    __tablename__ = "documento"

    entidade_tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    entidade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    tipo_documento: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(String(500), nullable=False)
    tamanho_bytes: Mapped[int | None] = mapped_column(Integer)
    mime_type: Mapped[str | None] = mapped_column(String(50))
    observacao: Mapped[str | None] = mapped_column(Text)

    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id")
    )

    usuario = relationship("UsuarioModel")
