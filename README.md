# whoop-mcp

MCP server for [Whoop](https://www.whoop.com/) — read biometrics, log activities, and manage your Whoop band from Claude.

Built on [whoop-write-api](https://github.com/jd1207/whoop-write-api) and the [Model Context Protocol](https://modelcontextprotocol.io/).

## Tools

| Tool | Description |
|------|-------------|
| `get_recovery` | Recovery score, HRV, resting HR |
| `get_sleep` | Sleep score and hours |
| `get_strain` | Daily strain from cycles |
| `create_activity` | Log sauna, meditation, yoga, running, etc. |
| `delete_activity` | Remove an activity by ID |
| `list_activities` | List recent activities |
| `update_weight` | Update body weight (lbs, converted to kg) |
| `set_alarm` | Set or disable Whoop alarm |

## Quick Start

### 1. Install

```bash
pip install whoop-mcp
```

Or from source:

```bash
git clone https://github.com/jd1207/whoop-mcp.git
cd whoop-mcp
pip install -e .
```

### 2. Add to Claude Code

Add to `~/.claude/settings.json` with your Whoop credentials as env vars:

```json
{
  "mcpServers": {
    "whoop": {
      "command": "whoop-mcp",
      "env": {
        "WHOOP_EMAIL": "your-whoop-email@example.com",
        "WHOOP_PASSWORD": "your-whoop-password"
      }
    }
  }
}
```

That's it. The server auto-authenticates on first use, caches tokens at `~/.whoop/tokens.json`, and refreshes automatically. Your password is only used once to get tokens, then the server uses refresh tokens going forward.

### 3. Use

Ask Claude things like:
- "What's my recovery today?"
- "Log a 20-minute sauna session"
- "Set my alarm for 7:30 AM"
- "How did I sleep last night?"
- "Update my weight to 255 lbs"

## Alternative: CLI Login

If you prefer not to put credentials in the config file:

```bash
whoop-mcp login      # interactive prompt for email/password
whoop-mcp status     # check auth state
whoop-mcp logout     # remove stored tokens
```

Then use a simpler config without env vars:

```json
{
  "mcpServers": {
    "whoop": {
      "command": "whoop-mcp"
    }
  }
}
```

## How Auth Works

1. On first tool call, the server checks for cached tokens at `~/.whoop/tokens.json`
2. If no tokens: auto-authenticates using `WHOOP_EMAIL`/`WHOOP_PASSWORD` env vars (or fails with a helpful error if not set)
3. Tokens are cached with `0600` permissions and auto-refresh when expired
4. Your password is never stored — only the OAuth-like refresh token

## Architecture

```
Claude Code  <--stdio-->  whoop-mcp  <--https-->  Whoop API
                              |
                        ~/.whoop/tokens.json
```

- **Transport:** stdio (Claude Code launches the server as a subprocess)
- **Auth:** File-based token persistence with auto-refresh, auto-login from env vars
- **API:** [whoop-write-api](https://github.com/jd1207/whoop-write-api) v0.4+ for all Whoop operations

## Development

```bash
git clone https://github.com/jd1207/whoop-mcp.git
cd whoop-mcp
pip install -e ".[dev]"
pytest
```

## License

MIT
