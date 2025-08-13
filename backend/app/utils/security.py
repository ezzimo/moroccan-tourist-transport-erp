# --- top of file (add imports) ---
import secrets
from jose import jwt as jose_jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import string
from schemas.auth import TokenData
from config import settings
from passlib.context import CryptContext
from utils.redis_compat import r_exists, r_setex


# One global context for hashing/verification
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,          # tune for your infra
)

ISSUER = "auth-service"  # consider settings.service_name
AUDIENCE = "tourist-erp"  # set from settings in real use
CLOCK_SKEW_SECONDS = 15


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def generate_random_password(length: int = 12) -> str:
    """Generate a secure random password"""
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"

    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))

    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def create_access_token(
    *,
    data: dict | None = None,
    sub: uuid.UUID | str | None = None,
    email: str | None = None,
    scopes: Optional[list[str]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Backward-compatible token creator.
    - If `data` is provided, it should contain 'sub' and 'email'.
    - Otherwise use explicit `sub` and `email`.
    """
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
        expires_delta or timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "jti": jti,
        "sub": str(sub),
        "email": email,
        "scopes": scopes or [],
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": int(iat.timestamp()),
        "nbf": int(nbf.timestamp()),
        "exp": int(exp.timestamp()),
        "typ": "access",
        "alg": settings.algorithm,
    }
    return jose_jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def _decode_token_raw(token: str) -> dict:
    return jose_jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
        audience=AUDIENCE,
        issuer=ISSUER,
        options={
            "verify_signature": True,
            "verify_aud": True,
            "verify_iss": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "require": ["exp", "iat", "nbf", "sub", "jti"],
        },
        leeway=CLOCK_SKEW_SECONDS,
    )


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT, returning TokenData or None."""
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
        # Any decode/validation error => treat as invalid
        return None


def _get_jti_loose(token: str) -> str | None:
    try:
        return _decode_token_raw(token).get("jti")  # strict path
    except Exception:
        pass
    try:
        claims = jose_jwt.get_unverified_claims(token)  # lenient path
        return claims.get("jti")
    except Exception:
        return None


async def blacklist_token(
    token_or_jti: str,
    redis_client,
    *,
    expires_in_seconds: int,
) -> None:
    """
    Blacklist a token in Redis using both JTI and raw-token keys.
    Works with sync fakeredis and redis.asyncio transparently.
    """
    ttl = int(expires_in_seconds)

    # If you already extract JTI elsewhere, keep that logic; otherwise
    # use raw token as a fallback key too.
    jti_key = f"blacklist:jti:{token_or_jti}"
    raw_key = f"blacklist:raw:{token_or_jti}"

    # Set both keys with TTL
    await r_setex(redis_client, jti_key, ttl, "1")
    await r_setex(redis_client, raw_key, ttl, "1")


async def is_token_blacklisted(token_or_jti: str, redis_client) -> bool:
    """
    True if token (or its JTI) is blacklisted.
    Uses compat helpers so it works for sync/async Redis clients.
    """
    jti_key = f"blacklist:jti:{token_or_jti}"
    raw_key = f"blacklist:raw:{token_or_jti}"

    if await r_exists(redis_client, jti_key):
        return True
    if await r_exists(redis_client, raw_key):
        return True
    return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password; return False on malformed hash instead of raising."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
