from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClienteResponse(BaseModel):
    id: UUID
    nome_razao_social: str
    cpf_cnpj: str
    telefone: str | None = None
    celular: str | None = None
    email: str | None = None
    status: str


class ProdutoEstoqueResponse(BaseModel):
    codigo: str
    nome: str
    quantidade_atual: float
    deposito: str
    estoque_minimo: float | None = None


class ChopeiraResponse(BaseModel):
    codigo_identificacao: str
    marca: str
    modelo: str
    tipo: str
    status: str
    local_instalacao: str | None = None


class DocumentoResponse(BaseModel):
    id: UUID
    tipo_documento: str
    nome_original: str
    entidade_tipo: str


class PedidoCriadoResponse(BaseModel):
    id: UUID
    numero: str
    total: float
    status: str
    mensagem: str = "Pedido cadastrado com sucesso!"


class MensagemResponse(BaseModel):
    mensagem_id: UUID
    conversa_id: UUID
    resposta: str


class WebhookReceber(BaseModel):
    telefone: str = Field(..., description="Número do remetente")
    mensagem: str = Field(..., description="Conteúdo da mensagem")
    nome_contato: str | None = Field(None, description="Nome do contato")
    mensagem_id: str | None = Field(None, description="ID da mensagem no provedor")


class MensagemEnviar(BaseModel):
    conversa_id: UUID | None = None
    telefone: str
    mensagem: str


class MensagemSaida(BaseModel):
    id: UUID
    telefone: str
    conteudo: str
    data_envio: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class MensagemEntrada(BaseModel):
    id: UUID
    telefone: str
    conteudo: str
    tipo: str
    data_recebida: datetime
    lida: bool

    model_config = ConfigDict(from_attributes=True)


class ConversaResponse(BaseModel):
    id: UUID
    telefone: str
    nome_contato: str | None = None
    status: str
    ultima_mensagem: str | None = None
    ultima_data: datetime | None = None
    agente_ativo: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversaDetalhadaResponse(ConversaResponse):
    mensagens: list[MensagemEntrada | MensagemSaida] = []
