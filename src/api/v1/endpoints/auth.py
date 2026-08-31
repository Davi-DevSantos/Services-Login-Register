from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.dependencies.auth_dependencies import get_refresh_user
from src.core.ExceptionsError import InvalidCredentialsError, UserNotFoundError
from src.db.session import get_db
from src.repositories.UserRepository import UserRepository
from src.schemas.auth_schemas import LoginRequest, TokenPair, TokenRefresh
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:  # noqa: B008
    return AuthService(UserRepository(db))


@router.post("/login", response_model=TokenPair)
def login(
    body: LoginRequest, service: AuthService = Depends(get_auth_service)  # noqa: B008
) -> dict:
    try:
        return service.authenticate_user(body.email, body.password)
    except (UserNotFoundError, InvalidCredentialsError):
        raise HTTPException(status_code=401, detail="Invalid credentials") from None


@router.post("/refresh", response_model=TokenPair)
def refresh_token(
    body: TokenRefresh, service: AuthService = Depends(get_auth_service)  # noqa: B008
) -> dict:
    user_id = get_refresh_user(body.refresh_token)
    return service.create_token_pair(user_id)
