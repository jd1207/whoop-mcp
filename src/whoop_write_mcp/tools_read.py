"""whoop read tool handlers."""
from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


async def get_recovery(
    days: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """get recovery scores, optionally filtered by date range."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    recoveries = await client.get_recovery(start=start_date, end=end_date)
    if not start_date and not end_date:
        recoveries = recoveries[:days]
    results = []
    for r in recoveries:
        results.append({
            "date": r.created_at[:10],
            "recovery_score": r.recovery_score,
            "hrv": r.hrv,
            "resting_hr": r.resting_hr,
        })
    return {"recoveries": results}


async def get_sleep(
    days: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """get sleep data, optionally filtered by date range."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    sleeps = await client.get_sleep(start=start_date, end=end_date)
    if not start_date and not end_date:
        sleeps = sleeps[:days]
    results = []
    for s in sleeps:
        results.append({
            "date": s.created_at[:10],
            "score": s.performance,
            "hours": round(s.total_in_bed_hours, 1),
            "efficiency": s.efficiency,
            "respiratory_rate": s.respiratory_rate,
        })
    return {"sleeps": results}


async def get_cycles(
    days: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """get strain/cycle data, optionally filtered by date range."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    cycles = await client.get_cycles(start=start_date, end=end_date)
    if not start_date and not end_date:
        cycles = cycles[:days]
    results = []
    for c in cycles:
        results.append({
            "date": c.start[:10],
            "strain": c.strain,
            "avg_hr": c.avg_hr,
        })
    return {"cycles": results}


async def get_body_measurement() -> dict:
    """get body measurements (height, weight, max hr)."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    m = await client.get_body_measurement()
    return {
        "height_meters": m.height_meter,
        "weight_kg": round(m.weight_kilogram, 1),
        "max_heart_rate": m.max_heart_rate,
    }


async def get_sport_types() -> dict:
    """get available whoop sport types."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    types = await client.get_sport_types()
    return {"sport_types": [{"id": t.id, "name": t.name} for t in types]}


async def search_exercises(
    query: str = "",
    equipment: str | None = None,
    muscle_group: str | None = None,
    movement_pattern: str | None = None,
) -> dict:
    """search whoop exercise catalog by name, equipment, muscle group, or movement."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    catalog = await client.get_exercises()

    if query:
        results = catalog.search(query)
    elif equipment or muscle_group or movement_pattern:
        results = catalog.filter(
            equipment=equipment,
            muscle_group=muscle_group,
            movement_pattern=movement_pattern,
        )
    else:
        results = catalog.exercises

    return {
        "exercises": [
            {
                "exercise_id": e.exercise_id,
                "name": e.name,
                "equipment": e.equipment,
                "muscle_groups": e.muscle_groups,
                "exercise_type": e.exercise_type,
            }
            for e in results[:50]
        ],
        "total": len(results),
    }


async def get_journal_behaviors(date: str) -> dict:
    """get available journal behavior trackers for a date."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    behaviors = await client.get_journal_behaviors(date)
    return {
        "behaviors": [
            {
                "id": b.id,
                "title": b.title,
                "question": b.question_text,
                "type": b.behavior_type,
            }
            for b in behaviors
        ]
    }
