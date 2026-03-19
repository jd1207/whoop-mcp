"""token persistence and refresh for whoop authentication."""
from __future__ import annotations
import json
import os
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


async def _auto_login_from_env() -> StoredTokens:
    """auto-login using WHOOP_EMAIL and WHOOP_PASSWORD env vars."""
    email = os.environ.get("WHOOP_EMAIL", "")
    password = os.environ.get("WHOOP_PASSWORD", "")
    if not email or not password:
        raise RuntimeError(
            "Whoop not connected. Run this in your terminal:\n\n"
            "  whoop-write-mcp login\n\n"
            "Or pass credentials via env vars when adding the server:\n"
            "  claude mcp add -e WHOOP_EMAIL=... -e WHOOP_PASSWORD=... -s user whoop -- uvx whoop-write-mcp"
        )
    logger.info("auto-login from env vars")
    return await login(email, password)


async def get_fresh_tokens() -> StoredTokens:
    """load tokens, refresh if expired, auto-login from env if no tokens."""
    tokens = load_tokens()

    # no tokens on disk — try auto-login from env
    if not tokens:
        return await _auto_login_from_env()

    # tokens valid — use them
    if not tokens_expired(tokens):
        return tokens

    # expired — try refresh first
    try:
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
    except Exception:
        logger.info("refresh failed, attempting re-login from env")
        return await _auto_login_from_env()


async def get_whoop_client():
    """create an authenticated whoop client."""
    from whoop import WhoopClient, TokenSet
    tokens = await get_fresh_tokens()
    token_set = TokenSet(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_at=tokens.expires_at,
    )

    async def on_refresh(new_tokens):
        save_tokens(StoredTokens(
            access_token=new_tokens.access_token,
            refresh_token=new_tokens.refresh_token,
            expires_at=new_tokens.expires_at,
        ))

    return WhoopClient(token_set=token_set, on_token_refresh=on_refresh)
