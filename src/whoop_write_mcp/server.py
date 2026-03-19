"""whoop MCP server — exposes whoop biometrics and controls to Claude."""
from __future__ import annotations
import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("Whoop")


# -- read tools --

@mcp.tool()
async def get_recovery(
    days: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get Whoop recovery scores (HRV, resting HR, recovery %).
    Use days for recent data, or start_date/end_date (YYYY-MM-DD) for a range.
    """
    from whoop_write_mcp.tools_read import get_recovery as _get
    return json.dumps(await _get(days, start_date, end_date))


@mcp.tool()
async def get_sleep(
    days: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get Whoop sleep data (score, hours, efficiency, respiratory rate).
    Use days for recent data, or start_date/end_date (YYYY-MM-DD) for a range.
    """
    from whoop_write_mcp.tools_read import get_sleep as _get
    return json.dumps(await _get(days, start_date, end_date))


@mcp.tool()
async def get_strain(
    days: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get Whoop strain/cycle data (strain score, avg heart rate).
    Use days for recent data, or start_date/end_date (YYYY-MM-DD) for a range.
    """
    from whoop_write_mcp.tools_read import get_cycles as _get
    return json.dumps(await _get(days, start_date, end_date))


@mcp.tool()
async def get_body_measurement() -> str:
    """Get Whoop body measurements — height (meters), weight (kg), max heart rate."""
    from whoop_write_mcp.tools_read import get_body_measurement as _get
    return json.dumps(await _get())


@mcp.tool()
async def get_sport_types() -> str:
    """List all Whoop sport types with their IDs. Use these IDs with log_workout."""
    from whoop_write_mcp.tools_read import get_sport_types as _get
    return json.dumps(await _get())


@mcp.tool()
async def search_exercises(
    query: str = "",
    equipment: str | None = None,
    muscle_group: str | None = None,
    movement_pattern: str | None = None,
) -> str:
    """Search Whoop exercise catalog by name, equipment, muscle group, or movement pattern.
    Returns exercise_ids needed for log_workout and link_exercises. Max 50 results.
    """
    from whoop_write_mcp.tools_read import search_exercises as _search
    return json.dumps(await _search(query, equipment, muscle_group, movement_pattern))


@mcp.tool()
async def get_journal_behaviors(date: str) -> str:
    """Get available Whoop journal questions for a date (YYYY-MM-DD).
    Returns behavior IDs needed for log_journal.
    """
    from whoop_write_mcp.tools_read import get_journal_behaviors as _get
    return json.dumps(await _get(date))


# -- write tools --

@mcp.tool()
async def create_activity(
    activity_type: str,
    duration_minutes: int,
    start_time: str | None = None,
) -> str:
    """Log a simple activity to Whoop (sauna, ice_bath, meditation, yoga, stretching, etc).
    For workouts with exercises, use log_workout instead.
    """
    from whoop_write_mcp.tools_write import create_activity as _create
    return json.dumps(await _create(activity_type, duration_minutes, start_time))


@mcp.tool()
async def delete_activity(activity_id: str, is_recovery: bool = False) -> str:
    """Delete an activity from Whoop. Use list_activities to find the ID first."""
    from whoop_write_mcp.tools_write import delete_activity as _delete
    return json.dumps(await _delete(activity_id, is_recovery))


@mcp.tool()
async def list_activities(limit: int = 5) -> str:
    """List recent Whoop activities with IDs, sport types, and start times."""
    from whoop_write_mcp.tools_write import list_activities as _list
    return json.dumps(await _list(limit))


@mcp.tool()
async def update_weight(weight_lbs: float) -> str:
    """Update body weight on Whoop. Accepts pounds, converts to kg automatically."""
    from whoop_write_mcp.tools_write import update_weight as _update
    return json.dumps(await _update(weight_lbs))


@mcp.tool()
async def set_alarm(time_str: str, enabled: bool = True) -> str:
    """Set or disable the Whoop alarm. Time in HH:MM format."""
    from whoop_write_mcp.tools_write import set_alarm as _set
    return json.dumps(await _set(time_str, enabled))


@mcp.tool()
async def log_workout(
    sport_id: int,
    start_time: str,
    end_time: str,
    exercises: str | None = None,
) -> str:
    """Log a full workout to Whoop with optional exercises.
    Use get_sport_types to find sport_id. Times in ISO 8601.
    Simple exercise format: [{"name": "Bench Press", "sets": 3, "reps": 10, "weight": 135}].
    """
    from whoop_write_mcp.tools_write import log_workout as _log
    return json.dumps(await _log(sport_id, start_time, end_time, exercises))


@mcp.tool()
async def link_exercises(activity_id: str, exercises: str) -> str:
    """Link detailed exercises to an existing Whoop activity with per-set granularity.
    Use search_exercises to find exercise_ids.
    Format: [{"exercise_id": "id", "name": "Name", "sets": [{"reps": 10, "weight": 135}]}].
    """
    from whoop_write_mcp.tools_write import link_exercises as _link
    return json.dumps(await _link(activity_id, exercises))


@mcp.tool()
async def log_journal(date: str, entries: str, notes: str = "") -> str:
    """Log a Whoop journal entry. Use get_journal_behaviors to find behavior IDs.
    Format: [{"behavior_id": 101, "answered_yes": true, "magnitude": 3.0}].
    """
    from whoop_write_mcp.tools_write import log_journal as _log
    return json.dumps(await _log(date, entries, notes))


