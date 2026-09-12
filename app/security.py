from pwdlib import PasswordHash
from datetime import UTC, datetime, timedelta
import jwt
from app.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    payload = {
    "sub": str(user_id),
    "exp": datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)


def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
    except jwt.InvalidTokenError:
        return None
    return payload.get("sub")