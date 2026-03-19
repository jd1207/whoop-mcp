"""whoop MCP server — exposes whoop biometrics and controls to Claude."""
from __future__ import annotations
import asyncio
import sys
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Whoop",
    version="0.1.0",
    description="Read biometrics, log activities, and manage your Whoop from Claude.",
)


# -- read tools --

@mcp.tool()
async def get_recovery(days: int = 1) -> str:
    """Get recent Whoop recovery scores including HRV, resting HR, and recovery percentage.

    Args:
        days: Number of days of recovery data to return (default 1)
    """
    import json
    from whoop_write_mcp.tools import get_recovery as _get_recovery
    result = await _get_recovery(days)
    return json.dumps(result)


@mcp.tool()
async def get_sleep(days: int = 1) -> str:
    """Get recent Whoop sleep data including sleep score and hours.

    Args:
        days: Number of days of sleep data to return (default 1)
    """
    import json
    from whoop_write_mcp.tools import get_sleep as _get_sleep
    result = await _get_sleep(days)
    return json.dumps(result)


@mcp.tool()
async def get_strain(days: int = 1) -> str:
    """Get recent Whoop strain/cycle data.

    Args:
        days: Number of days of strain data to return (default 1)
    """
    import json
    from whoop_write_mcp.tools import get_cycles as _get_cycles
    result = await _get_cycles(days)
    return json.dumps(result)


# -- write tools --

@mcp.tool()
async def create_activity(
    activity_type: str,
    duration_minutes: int,
    start_time: str | None = None,
) -> str:
    """Log an activity to Whoop. Supports: sauna, ice_bath, meditation, yoga, stretching, running, cycling, hiking, swimming, walking.

    Args:
        activity_type: Type of activity (sauna, ice_bath, meditation, yoga, stretching, running, cycling, hiking, swimming, walking)
        duration_minutes: Duration of the activity in minutes
        start_time: Optional ISO 8601 start time. If omitted, assumes activity just ended.
    """
    import json
    from whoop_write_mcp.tools import create_activity as _create
    result = await _create(activity_type, duration_minutes, start_time)
    return json.dumps(result)


@mcp.tool()
async def delete_activity(activity_id: str, is_recovery: bool = False) -> str:
    """Delete an activity from Whoop. Use list_activities first to find the ID.

    Args:
        activity_id: The Whoop activity ID to delete
        is_recovery: Whether this is a recovery activity (default false)
    """
    import json
    from whoop_write_mcp.tools import delete_activity as _delete
    result = await _delete(activity_id, is_recovery)
    return json.dumps(result)


@mcp.tool()
async def list_activities(limit: int = 5) -> str:
    """List recent Whoop activities with their IDs, sport types, and start times.

    Args:
        limit: Maximum number of activities to return (default 5)
    """
    import json
    from whoop_write_mcp.tools import list_activities as _list
    result = await _list(limit)
    return json.dumps(result)


@mcp.tool()
async def update_weight(weight_lbs: float) -> str:
    """Update body weight on Whoop. Accepts pounds, converts to kg automatically.

    Args:
        weight_lbs: Body weight in pounds
    """
    import json
    from whoop_write_mcp.tools import update_weight as _update
    result = await _update(weight_lbs)
    return json.dumps(result)


@mcp.tool()
async def set_alarm(time_str: str, enabled: bool = True) -> str:
    """Set or disable the Whoop alarm.

    Args:
        time_str: Alarm time in HH:MM format
        enabled: Whether the alarm should be enabled (default true)
    """
    import json
    from whoop_write_mcp.tools import set_alarm as _set
    result = await _set(time_str, enabled)
    return json.dumps(result)


# -- CLI --

def main():
    """entry point for whoop-mcp command."""
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
    # default: run MCP server over stdio
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
        print("Not logged in. Run: whoop-mcp login")
        return
    if tokens_expired(tokens):
        print("Token expired. Run: whoop-mcp login")
    else:
        import time
        remaining = int(tokens.expires_at - time.time())
        print(f"Authenticated. Token valid for {remaining // 60} minutes.")
