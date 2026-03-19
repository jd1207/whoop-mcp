"""whoop write tool handlers."""
from __future__ import annotations
import json as _json
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


async def create_activity(
    activity_type: str,
    duration_minutes: int,
    start_time: str | None = None,
) -> dict:
    """log an activity to whoop."""
    from whoop_write_mcp.auth import get_whoop_client

    if start_time:
        start = start_time
    else:
        end = datetime.now(timezone.utc)
        start = (end - timedelta(minutes=duration_minutes)).isoformat().replace("+00:00", "Z")

    end_time = (
        datetime.fromisoformat(start.replace("Z", "+00:00"))
        + timedelta(minutes=duration_minutes)
    ).isoformat().replace("+00:00", "Z")

    client = await get_whoop_client()
    result = await client.create_activity(activity_type, start=start, end=end_time)
    return {"success": True, "activity_id": result.id}


async def delete_activity(activity_id: str, is_recovery: bool = False) -> dict:
    """delete an activity from whoop."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    await client.delete_activity(activity_id, is_recovery=is_recovery)
    return {"success": True, "deleted": activity_id}


async def list_activities(limit: int = 5) -> dict:
    """list recent whoop activities."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    workouts = await client.get_workouts()
    activities = [
        {"id": w.id, "sport": w.sport_id, "start": str(w.start)}
        for w in workouts[:limit]
    ]
    return {"activities": activities}


async def update_weight(weight_lbs: float) -> dict:
    """update body weight on whoop (converts lbs to kg)."""
    from whoop_write_mcp.auth import get_whoop_client
    weight_kg = weight_lbs / 2.20462
    client = await get_whoop_client()
    await client.update_weight(weight_kg)
    return {"success": True, "weight_kg": round(weight_kg, 1)}


async def set_alarm(time_str: str, enabled: bool = True) -> dict:
    """set or disable whoop alarm."""
    from whoop_write_mcp.auth import get_whoop_client
    client = await get_whoop_client()
    await client.set_alarm(time_str, enabled=enabled)
    return {"success": True, "alarm_time": time_str, "enabled": enabled}


async def log_workout(
    sport_id: int,
    start_time: str,
    end_time: str,
    exercises: str | None = None,
) -> dict:
    """log a full workout to whoop, optionally with exercises."""
    from whoop_write_mcp.auth import get_whoop_client
    from whoop import WorkoutWrite, ExerciseWrite

    exercise_list = None
    if exercises:
        try:
            parsed = _json.loads(exercises)
        except _json.JSONDecodeError as e:
            return {"success": False, "error": f"invalid exercises JSON: {e}"}
        exercise_list = [
            ExerciseWrite(
                name=ex["name"],
                sets=ex["sets"],
                reps=ex["reps"],
                weight=ex.get("weight", 0),
                weight_unit=ex.get("weight_unit", "lbs"),
            )
            for ex in parsed
        ]

    workout = WorkoutWrite(
        sport_id=sport_id,
        start=start_time,
        end=end_time,
        exercises=exercise_list,
    )
    client = await get_whoop_client()
    result = await client.log_workout(workout)
    return {
        "success": True,
        "activity_id": result.activity_id,
        "exercises_linked": result.exercises_linked,
        "error": result.error,
    }


async def link_exercises(activity_id: str, exercises: str) -> dict:
    """link detailed exercises to an existing whoop activity."""
    from whoop_write_mcp.auth import get_whoop_client
    from whoop import DetailedExercise, ExerciseSet

    try:
        parsed = _json.loads(exercises)
    except _json.JSONDecodeError as e:
        return {"success": False, "error": f"invalid exercises JSON: {e}"}

    exercise_list = [
        DetailedExercise(
            exercise_id=ex["exercise_id"],
            name=ex["name"],
            sets=[
                ExerciseSet(
                    reps=s.get("reps", 0),
                    weight=s.get("weight", 0),
                    time_seconds=s.get("time_seconds"),
                )
                for s in ex.get("sets", [])
            ],
            exercise_type=ex.get("exercise_type", "STRENGTH"),
            volume_format=ex.get("volume_format", "REPS"),
        )
        for ex in parsed
    ]
    client = await get_whoop_client()
    result = await client.link_exercises_detailed(activity_id, exercise_list)
    return {"success": True, "result": result}


async def log_journal(date: str, entries: str, notes: str = "") -> dict:
    """log a journal entry to whoop."""
    from whoop_write_mcp.auth import get_whoop_client
    from whoop import JournalInput

    try:
        parsed = _json.loads(entries)
    except _json.JSONDecodeError as e:
        return {"success": False, "error": f"invalid entries JSON: {e}"}

    inputs = [
        JournalInput(
            behavior_tracker_id=e["behavior_id"],
            answered_yes=e["answered_yes"],
            magnitude_input_value=e.get("magnitude"),
        )
        for e in parsed
    ]
    client = await get_whoop_client()
    await client.log_journal(date, inputs, notes)
    return {"success": True, "date": date}
