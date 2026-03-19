"""CLI entry point for whoop-write-mcp."""
from __future__ import annotations
import asyncio
import sys


def main():
    """entry point for whoop-write-mcp command."""
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        _handle_login()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "logout":
        from whoop_write_mcp.auth import clear_tokens
        clear_tokens()
        print("Logged out. Tokens removed.")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        _handle_status()
        return
    from whoop_write_mcp.server import mcp
    mcp.run(transport="stdio")


def _handle_login():
    """interactive login flow."""
    import getpass
    email = input("Whoop email: ")
    password = getpass.getpass("Whoop password: ")
    try:
        tokens = asyncio.run(_do_login(email, password))
        print(f"Logged in. Token expires at {tokens.expires_at:.0f}")
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)


async def _do_login(email: str, password: str):
    from whoop_write_mcp.auth import login
    return await login(email, password)


def _handle_status():
    """check auth status."""
    from whoop_write_mcp.auth import load_tokens, tokens_expired
    tokens = load_tokens()
    if not tokens:
        print("Not logged in. Run: whoop-write-mcp login")
        return
    if tokens_expired(tokens):
        print("Token expired. Run: whoop-write-mcp login")
    else:
        import time
        remaining = int(tokens.expires_at - time.time())
        print(f"Authenticated. Token valid for {remaining // 60} minutes.")
