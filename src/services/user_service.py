from sqlalchemy.exc import IntegrityError

from src.core.exceptions import UserAlreadyExistsError
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.utils.security import get_password_hash


class UserService:
    def __init__(self, repo: UserRepository):
        self.user_repository = repo

    def create_user(self, username: str, email: str, password: str) -> User:
        existing = self.user_repository.get_user_by_email_or_username(email, username)
        if existing:
            if existing.email == email:
                raise UserAlreadyExistsError("Email already registered")
            raise UserAlreadyExistsError("Username already taken")

        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
        )
        try:
            return self.user_repository.create_user(user)
        except IntegrityError as exc:
            raise UserAlreadyExistsError("User already exists") from exc

    