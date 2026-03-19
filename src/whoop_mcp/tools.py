"""whoop tool handlers for MCP."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def get_recovery(days: int = 1) -> dict:
    """get recent recovery scores."""
    from whoop_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    recoveries = await client.get_recovery()
    results = []
    for r in recoveries[:days]:
        results.append({
            "date": r.created_at[:10],
            "recovery_score": r.recovery_score,
            "hrv": r.hrv,
            "resting_hr": r.resting_hr,
        })
    return {"recoveries": results}


async def get_sleep(days: int = 1) -> dict:
    """get recent sleep data."""
    from whoop_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    sleeps = await client.get_sleep()
    results = []
    for s in sleeps[:days]:
        results.append({
            "date": s.created_at[:10],
            "score": s.performance,
            "hours": round(s.total_in_bed_hours, 1),
        })
    return {"sleeps": results}


async def get_cycles(days: int = 1) -> dict:
    """get recent strain/cycle data."""
    from whoop_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    cycles = await client.get_cycles()
    results = []
    for c in cycles[:days]:
        results.append({
            "date": c.start[:10],
            "strain": c.strain,
        })
    return {"cycles": results}


async def create_activity(
    activity_type: str,
    duration_minutes: int,
    start_time: str | None = None,
) -> dict:
    """log an activity to whoop."""
    from whoop_mcp.auth import get_whoop_client

    if start_time:
        start = start_time
    else:
        end = datetime.utcnow()
        start = (end - timedelta(minutes=duration_minutes)).isoformat() + "Z"

    end_time = (
        datetime.fromisoformat(start.replace("Z", ""))
        + timedelta(minutes=duration_minutes)
    ).isoformat() + "Z"

    client = await get_whoop_client()
    result = await client.create_activity(activity_type, start=start, end=end_time)
    return {"success": True, "activity_id": result.id}


async def delete_activity(activity_id: str, is_recovery: bool = False) -> dict:
    """delete an activity from whoop."""
    from whoop_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    await client.delete_activity(activity_id, is_recovery=is_recovery)
    return {"success": True, "deleted": activity_id}


async def list_activities(limit: int = 5) -> dict:
    """list recent whoop activities."""
    from whoop_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    workouts = await client.get_workouts()
    activities = [
        {"id": w.id, "sport": w.sport_id, "start": str(w.start)}
        for w in workouts[:limit]
    ]
    return {"activities": activities}


async def update_weight(weight_lbs: float) -> dict:
    """update body weight on whoop (converts lbs to kg)."""
    from whoop_mcp.auth import get_whoop_client
    weight_kg = weight_lbs / 2.20462
    client = await get_whoop_client()
    await client.update_weight(weight_kg)
    return {"success": True, "weight_kg": round(weight_kg, 1)}


async def set_alarm(time_str: str, enabled: bool = True) -> dict:
    """set or disable whoop alarm."""
    from whoop_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    await client.set_alarm(time_str, enabled=enabled)
    return {"success": True, "alarm_time": time_str, "enabled": enabled}
