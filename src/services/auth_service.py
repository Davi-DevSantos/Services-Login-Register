from datetime import datetime, timedelta, timezone

import jwt

from src.core.config import get_settings
from src.core.exceptions import InvalidCredentialsError, UnauthorizedError, UserNotFoundError
from src.repositories.user_repository import UserRepository
from src.utils.security import verify_password

settings = get_settings()


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_lifetime = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def authenticate_user(self, email: str, password: str) -> dict[str, str]:
        user = self.repo.get_user_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")
        if not user.is_active:
            raise UnauthorizedError("User is inactive")
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid credentials")

        return self.create_token_pair(str(user.id))

    def create_token(self, user_id: str) -> str:
        token = jwt.encode(
            {
                "sub": str(user_id),
                "type": "access",
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int(
                    (
                        datetime.now(timezone.utc)
                        + timedelta(minutes=self.access_token_lifetime)
                    ).timestamp()
                ),
            },
            self.secret_key,
            self.algorithm,
        )
        return token

    def create_refresh_token(self, user_id: str) -> str:
        token = jwt.encode(
            {
                "sub": str(user_id),
                "type": "refresh",
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int(
                    (
                        datetime.now(timezone.utc)
                        + timedelta(days=self.refresh_token_expire_days)
                    ).timestamp()
                ),
            },
            self.secret_key,
            self.algorithm,
        )
        return token

    def create_token_pair(self, user_id: str) -> dict:
        return {
            "access_token": self.create_token(user_id),
            "refresh_token": self.create_refresh_token(user_id),
            "token_type": "bearer",
        }