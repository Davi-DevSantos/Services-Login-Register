import bcrypt

# bcrypt 4+ raises ValueError for passwords >72 bytes.
# Truncamos de forma compatível com passlib (que fazia isso silenciosamente).
_BCRYPT_MAX = 72


def _norm(password: str) -> bytes:
    return password[:_BCRYPT_MAX].encode("utf-8")


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(_norm(password), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_norm(plain_password), hashed_password.encode("utf-8"))
    except Exception:
        return False


# Compatibilidade: mantém pwd_context para código legado que importe
try:
    from passlib.context import CryptContext  # type: ignore

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:  # pragma: no cover
    pwd_context = None  # type: ignore

