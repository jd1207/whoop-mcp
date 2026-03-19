"""tests for token persistence."""
from whoop_mcp.auth import StoredTokens, save_tokens, load_tokens, clear_tokens, tokens_expired
import time


def test_save_and_load_tokens(tmp_path, monkeypatch):
    monkeypatch.setattr("whoop_mcp.auth.TOKEN_DIR", tmp_path)
    monkeypatch.setattr("whoop_mcp.auth.TOKEN_FILE", tmp_path / "tokens.json")

    tokens = StoredTokens(
        access_token="access-123",
        refresh_token="refresh-456",
        expires_at=time.time() + 3600,
    )
    save_tokens(tokens)

    loaded = load_tokens()
    assert loaded is not None
    assert loaded.access_token == "access-123"
    assert loaded.refresh_token == "refresh-456"


def test_load_tokens_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("whoop_mcp.auth.TOKEN_FILE", tmp_path / "nope.json")
    assert load_tokens() is None


def test_clear_tokens(tmp_path, monkeypatch):
    token_file = tmp_path / "tokens.json"
    monkeypatch.setattr("whoop_mcp.auth.TOKEN_FILE", token_file)
    token_file.write_text("{}")
    clear_tokens()
    assert not token_file.exists()


def test_tokens_expired():
    expired = StoredTokens("a", "b", time.time() - 100)
    assert tokens_expired(expired) is True

    fresh = StoredTokens("a", "b", time.time() + 3600)
    assert tokens_expired(fresh) is False
