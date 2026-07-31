from enum import Enum


class Papel(str, Enum):  # noqa: UP042
    ADMIN = "admin"
    FINANCEIRO = "financeiro"
    COMERCIAL = "comercial"
    MOTORISTA = "motorista"
    ESTOQUE = "estoque"


class Acao(str, Enum):  # noqa: UP042
    CRIAR = "criar"
    LER = "ler"
    ATUALIZAR = "atualizar"
    DELETAR = "deletar"
    APROVAR = "aprovar"
    CANCELAR = "cancelar"


class Modulo(str, Enum):  # noqa: UP042
    PRODUTOS = "produtos"
    CLIENTES = "clientes"
    PEDIDOS = "pedidos"
    ESTOQUE = "estoque"
    FINANCEIRO = "financeiro"
    VEICULOS = "veiculos"
    FORNECEDORES = "fornecedores"
    USUARIOS = "usuarios"
    RELATORIOS = "relatorios"
    CHOPEIRAS = "chopeiras"
    COMERCIAL = "comercial"


PERMISSOES: dict[Papel, dict[Modulo, list[Acao]]] = {
    Papel.ADMIN: {
        mod: list(Acao) for mod in Modulo
    },
    Papel.FINANCEIRO: {
        Modulo.CLIENTES: [Acao.LER],
        Modulo.FINANCEIRO: [Acao.CRIAR, Acao.LER, Acao.ATUALIZAR],
        Modulo.PEDIDOS: [Acao.LER],
        Modulo.FORNECEDORES: [Acao.LER, Acao.ATUALIZAR],
        Modulo.RELATORIOS: [Acao.LER],
    },
    Papel.COMERCIAL: {
        Modulo.CLIENTES: [Acao.CRIAR, Acao.LER, Acao.ATUALIZAR],
        Modulo.PEDIDOS: [Acao.CRIAR, Acao.LER, Acao.ATUALIZAR, Acao.CANCELAR],
        Modulo.PRODUTOS: [Acao.LER],
        Modulo.RELATORIOS: [Acao.LER],
        Modulo.COMERCIAL: [Acao.CRIAR, Acao.LER, Acao.ATUALIZAR, Acao.DELETAR],
    },
    Papel.MOTORISTA: {
        Modulo.VEICULOS: [Acao.LER],
        Modulo.PEDIDOS: [Acao.LER],
    },
    Papel.ESTOQUE: {
        Modulo.ESTOQUE: [Acao.CRIAR, Acao.LER, Acao.ATUALIZAR],
        Modulo.PRODUTOS: [Acao.LER, Acao.ATUALIZAR],
        Modulo.PEDIDOS: [Acao.LER],
        Modulo.CHOPEIRAS: [Acao.CRIAR, Acao.LER, Acao.ATUALIZAR],
    },
}


def acao_permite(papel: Papel, modulo: Modulo, acao: Acao) -> bool:
    permissoes = PERMISSOES.get(papel, {})
    acoes = permissoes.get(modulo, [])
    return acao in acoes
