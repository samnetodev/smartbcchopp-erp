from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.security import decode_access_token
from core.domain.auth.papeis import Acao, Modulo, Papel, acao_permite

security = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> dict[str, Any]:
    credentials: HTTPAuthorizationCredentials | None = await security(request)
    if not credentials:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return payload


def requer_permissao(
    modulo: Modulo, acao: Acao
) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def dependency(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        papel_str = current_user.get("papel", "")
        try:
            papel = Papel(papel_str)
        except ValueError:
            raise HTTPException(status_code=403, detail="Papel inválido")

        if not acao_permite(papel, modulo, acao):
            raise HTTPException(
                status_code=403,
                detail=f"Acesso negado: {papel.value} não pode {acao.value} em {modulo.value}",
            )
        return current_user

    return dependency
