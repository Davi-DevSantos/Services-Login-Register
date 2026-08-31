from src.core.config import get_settings
from src.models.user import User
from src.repositories.UserRepository import UserRepository
from src.utils.security import get_password_hash


class UserService:
    def __init__(self, repo: UserRepository):
        self.user_repository = repo
        self.secret_key = get_settings().secret_key
        self.algorithm = get_settings().algorithm
        self.access_token_lifetime = get_settings().access_token_expire_minutes

    def create_user(self, username: str, email: str, password: str):
        user = User(username=username,
                    email=email, 
                    hashed_password=get_password_hash(password))
        self.user_repository.create_user(user)
        return user

    