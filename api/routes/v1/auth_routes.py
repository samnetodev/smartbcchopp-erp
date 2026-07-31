from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import get_current_user, requer_permissao
from api.serializers.auth_schema import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    MeResponse,
    RefreshRequest,
    RefreshResponse,
)
from config.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from core.domain.auth.papeis import Acao, Modulo
from database.repositories.usuario_repository_impl import UsuarioRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)) -> LoginResponse:
    repo = UsuarioRepositoryImpl(session)
    user = await repo.find_by_username(body.username)

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    if not user.ativo:
        raise HTTPException(status_code=401, detail="Usuário inativo")

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "username": user.username,
            "email": user.email,
            "papel": user.papel.value if hasattr(user.papel, "value") else user.papel,
        },
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    user.refresh_token = refresh_token
    user.ultimo_login = datetime.now(timezone.utc)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        email=user.email,
        papel=user.papel.value if hasattr(user.papel, "value") else user.papel,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> RefreshResponse:
    try:
        payload = decode_refresh_token(body.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    repo = UsuarioRepositoryImpl(session)
    user = await repo.find_by_id(payload["sub"])

    if not user or not user.ativo:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")

    if user.refresh_token != body.refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token não corresponde")

    new_access = create_access_token(
        subject=str(user.id),
        extra_claims={
            "username": user.username,
            "email": user.email,
            "papel": user.papel.value if hasattr(user.papel, "value") else user.papel,
        },
    )
    new_refresh = create_refresh_token(subject=str(user.id))
    user.refresh_token = new_refresh

    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return RefreshResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout")
async def logout(
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    repo = UsuarioRepositoryImpl(session)
    user = await repo.find_by_id(current_user["sub"])
    if user:
        user.refresh_token = None
        uow = AsyncUnitOfWork(session)
        await uow.commit()

    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=MeResponse)
async def me(current_user: dict[str, Any] = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=current_user["sub"],
        username=current_user.get("username", ""),
        email=current_user.get("email", ""),
        papel=current_user.get("papel", ""),
    )


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    repo = UsuarioRepositoryImpl(session)
    user = await repo.find_by_id(current_user["sub"])

    if not user or not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    user.password_hash = hash_password(body.new_password)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return {"message": "Senha alterada com sucesso"}


@router.get("/users", response_model=list[MeResponse])
async def list_users(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.USUARIOS, Acao.LER)),
) -> list[MeResponse]:
    repo = UsuarioRepositoryImpl(session)
    users = await repo.find_all()
    return [
        MeResponse(
            id=str(u.id),
            username=u.username,
            email=u.email,
            papel=u.papel.value if hasattr(u.papel, "value") else u.papel,
        )
        for u in users
    ]
