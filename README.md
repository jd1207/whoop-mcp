# whoop-write-mcp

MCP server for [Whoop](https://www.whoop.com/) — read biometrics, log activities, and manage your Whoop band from Claude.

Built on [whoop-write-api](https://github.com/jd1207/whoop-write-api) and the [Model Context Protocol](https://modelcontextprotocol.io/).

## Tools

### Read
| Tool | Description |
|------|-------------|
| `get_recovery` | Recovery score, HRV, resting HR (supports date range) |
| `get_sleep` | Sleep score, hours, respiratory rate |
| `get_strain` | Daily strain and heart rate from cycles |
| `get_body_measurement` | Height, weight, max HR |
| `get_sport_types` | List all Whoop sport/activity type IDs |
| `search_exercises` | Search exercise catalog by name, equipment, muscle group |
| `get_journal_behaviors` | Available journal questions for a date |

### Write
| Tool | Description |
|------|-------------|
| `create_activity` | Log sauna, meditation, yoga, running, etc. |
| `delete_activity` | Remove an activity by ID |
| `list_activities` | List recent activities with IDs |
| `update_weight` | Update body weight (lbs, converted to kg) |
| `set_alarm` | Set or disable Whoop alarm |
| `log_workout` | Full workout with optional exercise detail |
| `link_exercises` | Attach per-set exercise data to an activity |
| `log_journal` | Log caffeine, alcohol, supplements, notes |

## Connect to Claude Code

### Step 1: Add the server

```bash
claude mcp add -s user whoop -- uvx whoop-write-mcp
```

### Step 2: Authenticate

```bash
whoop-write-mcp login
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
claude mcp add -e WHOOP_EMAIL=you@example.com -e WHOOP_PASSWORD=yourpass -s user whoop -- uvx whoop-write-mcp
```

Server auto-authenticates on first tool call. Useful for automation.

### From source

```bash
git clone https://github.com/jd1207/whoop-write-mcp.git
cd whoop-write-mcp && pip install -e .
claude mcp add -s user whoop -- whoop-write-mcp
whoop-write-mcp login
```

## Managing

```bash
claude mcp list            # see registered servers
claude mcp remove whoop    # unregister
whoop-write-mcp status           # check auth state
whoop-write-mcp logout           # remove cached tokens
```

Or type `/mcp` inside Claude Code to manage connected servers.

## How Auth Works

1. First tool call checks for cached tokens at `~/.whoop/tokens.json`
2. No tokens? Auto-authenticates from `WHOOP_EMAIL`/`WHOOP_PASSWORD` env vars if set
3. No env vars? Returns a clear error: *"Run `whoop-write-mcp login` in your terminal"*
4. Tokens cached (`0600` permissions), auto-refresh on expiry
5. Password never stored on disk — only refresh tokens

## Architecture

```
Claude Code  <--stdio-->  whoop-write-mcp  <--https-->  Whoop API
                              |
                        ~/.whoop/tokens.json
```

## Claude Code Skill

The `skill/` directory contains a coaching intelligence skill that teaches Claude how to interpret Whoop data and make training decisions — not just call tools, but use them like a coach.

Install it to make any Claude Code agent smarter with Whoop data:

```bash
cp -r skill/ ~/.claude/skills/whoop-mcp/
```

What the skill provides:
- **Decision frameworks** — when to train heavy, when to deload, when to stay quiet
- **Signal priority** — sleep > HRV trend > recovery score > strain
- **Verbosity rules** — only surface data when it changes the recommendation
- **Multi-step workflows** — morning check-in, pre-workout assessment, post-workout sync
- **Biometric interpretation** — recovery zones, HRV trends, sleep thresholds, strain budgets

## Related Projects

- [whoop-write-api](https://github.com/jd1207/whoop-write-api) — the underlying Python library for Whoop's reverse-engineered API
- [SpotMe](https://github.com/jd1207/spotme) — self-hosted AI workout coach PWA that uses this MCP server

## Development

```bash
git clone https://github.com/jd1207/whoop-write-mcp.git
cd whoop-write-mcp
pip install -e ".[dev]"
pytest
```

## License

MIT
