
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide
from jose import jwt, JWTError

from app.v1_0.schemas.user_schema import UserRegisterDTO
from app.v1_0.services.user_service import UserService
from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.utils.security import (
    create_access_token,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=None,
    summary="Registrar un nuevo usuario"
)
@inject
async def register_user(
    request: UserRegisterDTO,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(
        Provide[ApplicationContainer.api_container.user_service]
    )
):
    await user_service.register_user(
        username=request.username,
        plain_password=request.password,
        db=db
    )
    return {"msg": "Usuario registrado exitosamente"}


@router.post(
    "/token",
    summary="Obtener token de acceso",
    responses={401: {"description": "Credenciales inválidas"}}
)
@inject
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(
        Provide[ApplicationContainer.api_container.user_service]
    )
):
    user = await user_service.authenticate(
        username=form_data.username,
        password=form_data.password,
        db=db
    )
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    summary="Obtener datos del usuario autenticado",
    responses={401: {"description": "Token inválido o expirado"}}
)
async def read_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"username": username}
