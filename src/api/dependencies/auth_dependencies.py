import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import get_settings
from src.core.exceptions import InvalidTokenError, TokenExpiredError, UnauthorizedError

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired") from None
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token") from None


def _require_type(payload: dict, expected: str, message: str) -> None:
    if payload.get("type") != expected:
        raise InvalidTokenError(message)


def _payload_subject(payload: dict) -> str:
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token: missing user ID")
    return user_id


def get_current_user(token: str) -> str:
    payload = decode_jwt_token(token)
    _require_type(payload, "access", "Invalid token: expected an access token")
    return _payload_subject(payload)


def get_refresh_user(token: str) -> str:
    payload = decode_jwt_token(token)
    _require_type(payload, "refresh", "Invalid token: expected a refresh token")
    return _payload_subject(payload)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:  # noqa: B008
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return get_current_user(token)
    except TokenExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except (InvalidTokenError, UnauthorizedError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def ensure_same_user(current_user: str, user_id: str) -> bool:
    if current_user != user_id:
        raise UnauthorizedError("User ID does not match the token's user ID")
    return True