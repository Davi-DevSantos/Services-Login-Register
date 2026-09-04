from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies.auth_dependencies import get_refresh_user
from src.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UnauthorizedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.db.session import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.auth_schemas import LoginRequest, TokenPair, TokenRefresh
from src.schemas.user_schemas import UserCreate, UserResponse
from src.services.auth_service import AuthService
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:  # noqa: B008
    return AuthService(UserRepository(db))


def get_user_service(db: Session = Depends(get_db)) -> UserService:  # noqa: B008
    return UserService(UserRepository(db))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: UserCreate, service: UserService = Depends(get_user_service)  # noqa: B008
) -> UserResponse:
    try:
        user = service.create_user(body.username, body.email, body.password)
        return user
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenPair)
def login(
    body: LoginRequest, service: AuthService = Depends(get_auth_service)  # noqa: B008
) -> dict:
    try:
        return service.authenticate_user(body.email, body.password)
    except (UserNotFoundError, InvalidCredentialsError, UnauthorizedError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc


@router.post("/refresh", response_model=TokenPair)
def refresh_token(
    body: TokenRefresh, service: AuthService = Depends(get_auth_service)  # noqa: B008
) -> dict:
    try:
        user_id = get_refresh_user(body.refresh_token)
        return service.create_token_pair(user_id)
    except TokenExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
