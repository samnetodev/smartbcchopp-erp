from dataclasses import dataclass

from config.security import create_access_token, verify_password
from database.repositories.usuario_repository_impl import UsuarioRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


@dataclass
class LoginResult:
    access_token: str
    token_type: str = "bearer"
    username: str = ""
    email: str = ""


class LoginUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, username: str, password: str) -> LoginResult:
        repo = UsuarioRepositoryImpl(self._uow.session)
        user = await repo.find_by_username(username)

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Usuário ou senha inválidos")

        if not user.ativo:
            raise ValueError("Usuário inativo")

        token = create_access_token(
            subject=str(user.id),
            extra_claims={"username": user.username, "email": user.email},
        )

        return LoginResult(
            access_token=token,
            username=user.username,
            email=user.email,
        )
