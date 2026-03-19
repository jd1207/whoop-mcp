"""tests for whoop tool handlers."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_create_activity():
    mock_client = AsyncMock()
    mock_client.create_activity.return_value = MagicMock(id="uuid-123")

    with patch("whoop_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_mcp.tools import create_activity
        result = await create_activity("sauna", 20)

    assert result["success"] is True
    assert result["activity_id"] == "uuid-123"


@pytest.mark.asyncio
async def test_get_recovery():
    mock_recovery = MagicMock()
    mock_recovery.created_at = "2026-03-18T10:00:00Z"
    mock_recovery.recovery_score = 79.0
    mock_recovery.hrv = 68.3
    mock_recovery.resting_hr = 50

    mock_client = AsyncMock()
    mock_client.get_recovery.return_value = [mock_recovery]

    with patch("whoop_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_mcp.tools import get_recovery
        result = await get_recovery(1)

    assert len(result["recoveries"]) == 1
    assert result["recoveries"][0]["recovery_score"] == 79.0


@pytest.mark.asyncio
async def test_update_weight():
    mock_client = AsyncMock()

    with patch("whoop_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_mcp.tools import update_weight
        result = await update_weight(255.0)

    assert result["success"] is True
    assert result["weight_kg"] == 115.7
    mock_client.update_weight.assert_called_once()


@pytest.mark.asyncio
async def test_list_activities():
    mock_workout = MagicMock()
    mock_workout.id = "act-1"
    mock_workout.sport_id = 1
    mock_workout.start = "2026-03-18T12:00:00Z"

    mock_client = AsyncMock()
    mock_client.get_workouts.return_value = [mock_workout]

    with patch("whoop_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_mcp.tools import list_activities
        result = await list_activities(5)

    assert len(result["activities"]) == 1
    assert result["activities"][0]["id"] == "act-1"
