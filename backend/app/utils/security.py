import secrets
from jose import jwt as jose_jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import string
from passlib.context import CryptContext

from schemas.auth import TokenData
from config import settings
from utils.redis_compat import r_exists, r_setex

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

ISSUER = "auth-service"
AUDIENCE = "tourist-erp"
CLOCK_SKEW_SECONDS = 15


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def generate_random_password(length: int = 12) -> str:
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars),
    ]
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def create_access_token(
    *,
    data: dict | None = None,
    sub: uuid.UUID | str | None = None,
    email: str | None = None,
    scopes: Optional[list[str]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if data:
        sub = data.get("sub") or data.get("user_id") or sub
        email = data.get("email") or email
        scopes = data.get("scopes", scopes)
    if sub is None or email is None:
        raise ValueError("create_access_token requires sub and email")

    jti = str(uuid.uuid4())
    iat = _now_utc()
    nbf = iat - timedelta(seconds=1)
    exp = iat + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        "jti": jti,
        "sub": str(sub),
        "email": email,
        "scopes": scopes or [],
        "iss": ISSUER,
        "aud": settings.jwt_audience,
        "iat": int(iat.timestamp()),
        "nbf": int(nbf.timestamp()),
        "exp": int(exp.timestamp()),
        "typ": "access",
        "alg": settings.algorithm,
    }
    return jose_jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jose_jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_aud": False},
        )
        if payload.get("typ") != "access":
            return None
        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or not email:
            return None
        return TokenData(
            user_id=uuid.UUID(sub),
            email=email,
            exp=payload.get("exp"),
            jti=payload.get("jti"),
            scopes=payload.get("scopes", []),
        )
    except Exception:
        return None


# -------------------
# Redis blacklist API
# -------------------


# Async variants (used inside app code)
async def blacklist_token_async(
    token_or_jti: str, redis_client, *, expires_in_seconds: int
) -> None:
    ttl = int(expires_in_seconds)
    # We store both jti-like and raw-token keys (we treat token_or_jti as identifier)
    await r_setex(redis_client, f"blacklist:jti:{token_or_jti}", ttl, "1")
    await r_setex(redis_client, f"blacklist:raw:{token_or_jti}", ttl, "1")


async def is_token_blacklisted_async(token_or_jti: str, redis_client) -> bool:
    if await r_exists(redis_client, f"blacklist:jti:{token_or_jti}"):
        return True
    if await r_exists(redis_client, f"blacklist:raw:{token_or_jti}"):
        return True
    return False


# Sync variants (kept for tests that call this synchronously)
def blacklist_token(
    token_or_jti: str, redis_client, expires_in_seconds: int | None = None
) -> None:
    ttl = int(expires_in_seconds or settings.access_token_expire_minutes * 60)
    try:
        redis_client.setex(f"blacklist:jti:{token_or_jti}", ttl, "1")
        redis_client.setex(f"blacklist:raw:{token_or_jti}", ttl, "1")
    except Exception:
        # last-ditch attempt (works for fakeredis as well)
        try:
            redis_client.setex(f"blacklist:raw:{token_or_jti}", ttl, "1")
        except Exception:
            pass


def is_token_blacklisted(token_or_jti: str, redis_client) -> bool:
    try:
        if redis_client.exists(f"blacklist:jti:{token_or_jti}"):
            return True
    except Exception:
        pass
    try:
        if redis_client.exists(f"blacklist:raw:{token_or_jti}"):
            return True
    except Exception:
        pass
    return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
