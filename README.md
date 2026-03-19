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

## Connect to Claude Code

```bash
claude mcp add -e WHOOP_EMAIL=you@example.com -e WHOOP_PASSWORD=yourpass -s user whoop -- uvx whoop-mcp
```

That's it. The `-s user` flag makes it available across all projects. Ask Claude: *"What's my recovery today?"*

The server auto-authenticates on first tool call, caches tokens at `~/.whoop/tokens.json`, and refreshes automatically. Your password is used once to get tokens, never stored on disk.

### From source

```bash
git clone https://github.com/jd1207/whoop-mcp.git
cd whoop-mcp && pip install -e .
claude mcp add -e WHOOP_EMAIL=you@example.com -e WHOOP_PASSWORD=yourpass -s user whoop -- whoop-mcp
```

### Alternative: interactive login

If you prefer not to pass credentials in the command:

```bash
whoop-mcp login
claude mcp add -s user whoop -- uvx whoop-mcp
```

## Usage

Once connected, ask Claude things like:

- "What's my recovery today?"
- "Log a 20-minute sauna session"
- "Set my alarm for 7:30 AM"
- "How did I sleep last night?"
- "Update my weight to 255 lbs"
- "Delete my last activity"

## Managing

```bash
claude mcp list            # see registered servers
claude mcp remove whoop    # unregister
whoop-mcp status           # check auth state
whoop-mcp logout           # remove cached tokens
```

Or type `/mcp` inside Claude Code to manage connected servers.

## How Auth Works

1. First tool call checks for cached tokens at `~/.whoop/tokens.json`
2. No tokens? Auto-authenticates using `WHOOP_EMAIL`/`WHOOP_PASSWORD` env vars
3. Tokens cached (`0600` permissions), auto-refresh on expiry
4. If refresh fails, re-authenticates from env vars
5. Password never stored on disk — only refresh tokens

## Architecture

```
Claude Code  <--stdio-->  whoop-mcp  <--https-->  Whoop API
                              |
                        ~/.whoop/tokens.json
```

## Development

```bash
git clone https://github.com/jd1207/whoop-mcp.git
cd whoop-mcp
pip install -e ".[dev]"
pytest
```

## License

MIT
