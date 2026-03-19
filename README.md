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

### Step 1: Add the server

```bash
claude mcp add -s user whoop -- uvx whoop-mcp
```

### Step 2: Authenticate

```bash
whoop-mcp login
```

Enter your Whoop email and password when prompted. Credentials are used once to get tokens, then discarded. Tokens are cached at `~/.whoop/tokens.json` and auto-refresh — you shouldn't need to login again.

### Step 3: Use it

Ask Claude things like:

- "What's my recovery today?"
- "Log a 20-minute sauna session"
- "Set my alarm for 7:30 AM"
- "How did I sleep last night?"
- "Update my weight to 255 lbs"
- "Delete my last activity"

### Alternative: env vars (skip the login step)

```bash
claude mcp add -e WHOOP_EMAIL=you@example.com -e WHOOP_PASSWORD=yourpass -s user whoop -- uvx whoop-mcp
```

Server auto-authenticates on first tool call. Useful for automation.

### From source

```bash
git clone https://github.com/jd1207/whoop-mcp.git
cd whoop-mcp && pip install -e .
claude mcp add -s user whoop -- whoop-mcp
whoop-mcp login
```

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
2. No tokens? Auto-authenticates from `WHOOP_EMAIL`/`WHOOP_PASSWORD` env vars if set
3. No env vars? Returns a clear error: *"Run `whoop-mcp login` in your terminal"*
4. Tokens cached (`0600` permissions), auto-refresh on expiry
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
