"""token persistence and refresh for whoop authentication."""
from __future__ import annotations
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

TOKEN_DIR = Path.home() / ".whoop"
TOKEN_FILE = TOKEN_DIR / "tokens.json"


@dataclass
class StoredTokens:
    access_token: str
    refresh_token: str
    expires_at: float


def save_tokens(tokens: StoredTokens) -> None:
    """persist tokens to ~/.whoop/tokens.json"""
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(asdict(tokens)))
    TOKEN_FILE.chmod(0o600)
    logger.info("tokens saved to %s", TOKEN_FILE)


def load_tokens() -> StoredTokens | None:
    """load tokens from disk, return None if not found."""
    if not TOKEN_FILE.exists():
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text())
        return StoredTokens(**data)
    except (json.JSONDecodeError, KeyError, TypeError):
        logger.warning("corrupt token file, removing")
        TOKEN_FILE.unlink(missing_ok=True)
        return None


def clear_tokens() -> None:
    """remove stored tokens."""
    TOKEN_FILE.unlink(missing_ok=True)


def tokens_expired(tokens: StoredTokens) -> bool:
    """check if access token is expired (with 60s buffer)."""
    return time.time() > (tokens.expires_at - 60)


async def login(email: str, password: str) -> StoredTokens:
    """authenticate with whoop and persist tokens."""
    from whoop import CognitoAuth
    auth = CognitoAuth()
    token_set = await auth.login(email, password)
    stored = StoredTokens(
        access_token=token_set.access_token,
        refresh_token=token_set.refresh_token,
        expires_at=token_set.expires_at,
    )
    save_tokens(stored)
    return stored


async def get_fresh_tokens() -> StoredTokens:
    """load tokens and refresh if expired."""
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("not logged in — run: whoop-mcp login")
    if not tokens_expired(tokens):
        return tokens
    # refresh
    from whoop import CognitoAuth
    auth = CognitoAuth()
    token_set = await auth.refresh(tokens.refresh_token)
    refreshed = StoredTokens(
        access_token=token_set.access_token,
        refresh_token=token_set.refresh_token,
        expires_at=token_set.expires_at,
    )
    save_tokens(refreshed)
    return refreshed


async def get_whoop_client():
    """create an authenticated whoop client."""
    from whoop import WhoopClient, TokenSet
    tokens = await get_fresh_tokens()
    token_set = TokenSet(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_at=tokens.expires_at,
    )

    def on_refresh(new_tokens):
        save_tokens(StoredTokens(
            access_token=new_tokens.access_token,
            refresh_token=new_tokens.refresh_token,
            expires_at=new_tokens.expires_at,
        ))

    return WhoopClient(token_set=token_set, on_token_refresh=on_refresh)
