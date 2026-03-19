# whoop-mcp

MCP server for Whoop. Wraps whoop-write-api as tools for Claude.

## Architecture

```
Claude Code <--stdio--> whoop-mcp <--https--> Whoop API
                            |
                      ~/.whoop/tokens.json
```

## Commands

```bash
.venv/bin/pytest -x --tb=short              # run tests
.venv/bin/whoop-write-mcp login             # authenticate with whoop
.venv/bin/whoop-write-mcp status            # check auth state
.venv/bin/whoop-write-mcp                   # run server (stdio)
```

## Directory Layout

- `src/whoop_write_mcp/` — package source
  - `server.py` — FastMCP app, tool registration
  - `cli.py` — CLI entry point (login, status, logout)
  - `tools_read.py` — read tool handlers (recovery, sleep, strain, body, catalog, journal behaviors)
  - `tools_write.py` — write tool handlers (activities, workouts, exercises, journal, weight, alarm)
  - `auth.py` — token persistence and refresh
- `tests/` — pytest suite
  - `test_tools_read.py` — read handler tests
  - `test_tools_write.py` — write handler tests
  - `test_auth.py` — auth tests

## Tools (15 total)

**Read tools:** get_recovery, get_sleep, get_strain, get_body_measurement, get_sport_types, search_exercises, get_journal_behaviors

**Write tools:** create_activity, delete_activity, list_activities, log_workout, link_exercises, log_journal, update_weight, set_alarm

## Key Patterns

- all whoop imports are lazy (inside functions)
- tools return dicts, server.py json-serializes them
- JSON string params for complex inputs (exercises, journal entries) with error handling
- auth tokens stored at ~/.whoop/tokens.json (0600 perms)
- auto-refresh on expired access token
- transport: stdio only (for Claude Code subprocess)

## Dependencies

- `mcp[cli]` — MCP Python SDK with FastMCP
- `whoop-write-api` — reverse-engineered Whoop API client
- `pydantic` — input validation

## Testing

- mock whoop client in all tests, never hit real API
- patch at `whoop_write_mcp.auth.get_whoop_client` (lazy import source)
