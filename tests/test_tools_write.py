"""tests for write tool handlers."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_create_activity():
    mock_client = AsyncMock()
    mock_client.create_activity.return_value = MagicMock(id="uuid-123")

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import create_activity
        result = await create_activity("sauna", 20)

    assert result["success"] is True
    assert result["activity_id"] == "uuid-123"


@pytest.mark.asyncio
async def test_update_weight():
    mock_client = AsyncMock()

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import update_weight
        result = await update_weight(255.0)

    assert result["success"] is True
    assert result["weight_kg"] == 115.7
    mock_client.update_weight.assert_called_once()


@pytest.mark.asyncio
async def test_list_activities():
    mock_workout = MagicMock(id="act-1", sport_id=1, start="2026-03-18T12:00:00Z")
    mock_client = AsyncMock()
    mock_client.get_workouts.return_value = [mock_workout]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import list_activities
        result = await list_activities(5)

    assert len(result["activities"]) == 1
    assert result["activities"][0]["id"] == "act-1"


@pytest.mark.asyncio
async def test_log_workout_no_exercises():
    mock_result = MagicMock(activity_id="workout-1", exercises_linked=False, error=None)
    mock_client = AsyncMock()
    mock_client.log_workout.return_value = mock_result

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import log_workout
        result = await log_workout(
            sport_id=45,
            start_time="2026-03-19T10:00:00Z",
            end_time="2026-03-19T11:00:00Z",
        )

    assert result["success"] is True
    assert result["activity_id"] == "workout-1"
    assert result["exercises_linked"] is False


@pytest.mark.asyncio
async def test_log_workout_with_exercises():
    mock_result = MagicMock(activity_id="workout-2", exercises_linked=True, error=None)
    mock_client = AsyncMock()
    mock_client.log_workout.return_value = mock_result

    exercises_json = json.dumps([
        {"name": "Bench Press", "sets": 3, "reps": 10, "weight": 135},
    ])

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import log_workout
        result = await log_workout(
            sport_id=45,
            start_time="2026-03-19T10:00:00Z",
            end_time="2026-03-19T11:00:00Z",
            exercises=exercises_json,
        )

    assert result["success"] is True
    assert result["exercises_linked"] is True
    call_args = mock_client.log_workout.call_args[0][0]
    assert call_args.sport_id == 45
    assert len(call_args.exercises) == 1
    assert call_args.exercises[0].name == "Bench Press"


@pytest.mark.asyncio
async def test_log_workout_bad_json():
    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=AsyncMock()):
        from whoop_write_mcp.tools_write import log_workout
        result = await log_workout(
            sport_id=45,
            start_time="2026-03-19T10:00:00Z",
            end_time="2026-03-19T11:00:00Z",
            exercises="not valid json",
        )

    assert result["success"] is False
    assert "invalid exercises JSON" in result["error"]


@pytest.mark.asyncio
async def test_link_exercises():
    mock_client = AsyncMock()
    mock_client.link_exercises_detailed.return_value = {"status": "linked"}

    exercises_json = json.dumps([{
        "exercise_id": "bench-1",
        "name": "Bench Press",
        "sets": [{"reps": 10, "weight": 135}, {"reps": 8, "weight": 155}],
    }])

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import link_exercises
        result = await link_exercises("activity-uuid", exercises_json)

    assert result["success"] is True
    call_args = mock_client.link_exercises_detailed.call_args
    assert call_args[0][0] == "activity-uuid"
    assert len(call_args[0][1]) == 1
    assert len(call_args[0][1][0].sets) == 2


@pytest.mark.asyncio
async def test_link_exercises_bad_json():
    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=AsyncMock()):
        from whoop_write_mcp.tools_write import link_exercises
        result = await link_exercises("activity-uuid", "{bad json")

    assert result["success"] is False
    assert "invalid exercises JSON" in result["error"]


@pytest.mark.asyncio
async def test_log_journal():
    mock_client = AsyncMock()

    entries_json = json.dumps([
        {"behavior_id": 101, "answered_yes": True},
        {"behavior_id": 102, "answered_yes": False, "magnitude": 3.0},
    ])

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import log_journal
        result = await log_journal("2026-03-19", entries_json, notes="felt good")

    assert result["success"] is True
    assert result["date"] == "2026-03-19"
    call_args = mock_client.log_journal.call_args
    assert call_args[0][0] == "2026-03-19"
    assert len(call_args[0][1]) == 2
    assert call_args[0][2] == "felt good"


@pytest.mark.asyncio
async def test_log_journal_bad_json():
    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=AsyncMock()):
        from whoop_write_mcp.tools_write import log_journal
        result = await log_journal("2026-03-19", "not json")

    assert result["success"] is False
    assert "invalid entries JSON" in result["error"]


@pytest.mark.asyncio
async def test_delete_activity():
    mock_client = AsyncMock()

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import delete_activity
        result = await delete_activity("act-uuid-1", is_recovery=True)

    assert result["success"] is True
    assert result["deleted"] == "act-uuid-1"
    mock_client.delete_activity.assert_called_once_with("act-uuid-1", is_recovery=True)


@pytest.mark.asyncio
async def test_set_alarm():
    mock_client = AsyncMock()

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_write import set_alarm
        result = await set_alarm("07:30", enabled=True)

    assert result["success"] is True
    assert result["alarm_time"] == "07:30"
    assert result["enabled"] is True
    mock_client.set_alarm.assert_called_once_with("07:30", enabled=True)
