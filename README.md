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

## Setup

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

### 2. Login

```bash
whoop-mcp login
```

Enter your Whoop email and password. Credentials are used once to authenticate, then discarded. Tokens are stored at `~/.whoop/tokens.json` (file permissions `600`).

### 3. Add to Claude Code

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "whoop": {
      "command": "whoop-mcp"
    }
  }
}
```

Or project-level `.claude/settings.json`:

```json
{
  "mcpServers": {
    "whoop": {
      "command": "whoop-mcp"
    }
  }
}
```

### 4. Use

Ask Claude things like:
- "What's my recovery today?"
- "Log a 20-minute sauna session"
- "Set my alarm for 7:30 AM"
- "How did I sleep last night?"
- "Update my weight to 255 lbs"

## CLI Commands

```bash
whoop-mcp            # Run MCP server (stdio transport)
whoop-mcp login      # Authenticate with Whoop
whoop-mcp logout     # Remove stored tokens
whoop-mcp status     # Check authentication status
```

## How Auth Works

1. `whoop-mcp login` authenticates via Whoop's Cognito auth (same as the mobile app)
2. Tokens are stored at `~/.whoop/tokens.json` with `0600` permissions
3. Access tokens auto-refresh when expired — you shouldn't need to re-login
4. Your password is never stored

## Architecture

```
Claude Code  <--stdio-->  whoop-mcp  <--https-->  Whoop API
                              |
                        ~/.whoop/tokens.json
```

- **Transport:** stdio (Claude Code launches the server as a subprocess)
- **Auth:** File-based token persistence with auto-refresh
- **API:** Uses [whoop-write-api](https://github.com/jd1207/whoop-write-api) v0.4+ for all Whoop operations

## Development

```bash
git clone https://github.com/jd1207/whoop-mcp.git
cd whoop-mcp
pip install -e ".[dev]"
pytest
```

## License

MIT
