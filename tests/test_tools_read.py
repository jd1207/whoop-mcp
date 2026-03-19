"""tests for read tool handlers."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_get_recovery():
    mock_recovery = MagicMock(
        created_at="2026-03-18T10:00:00Z", recovery_score=79.0, hrv=68.3, resting_hr=50,
    )
    mock_client = AsyncMock()
    mock_client.get_recovery.return_value = [mock_recovery]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_recovery
        result = await get_recovery(1)

    assert len(result["recoveries"]) == 1
    assert result["recoveries"][0]["recovery_score"] == 79.0


@pytest.mark.asyncio
async def test_get_recovery_date_range():
    mock_recovery = MagicMock(
        created_at="2026-03-10T10:00:00Z", recovery_score=85.0, hrv=72.0, resting_hr=48,
    )
    mock_client = AsyncMock()
    mock_client.get_recovery.return_value = [mock_recovery]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_recovery
        result = await get_recovery(start_date="2026-03-01", end_date="2026-03-15")

    mock_client.get_recovery.assert_called_once_with(start="2026-03-01", end="2026-03-15")
    assert len(result["recoveries"]) == 1


@pytest.mark.asyncio
async def test_get_sleep():
    mock_sleep = MagicMock(
        created_at="2026-03-18T08:00:00Z", performance=88.0,
        total_in_bed_hours=7.8, efficiency=92.0, respiratory_rate=15.5,
    )
    mock_client = AsyncMock()
    mock_client.get_sleep.return_value = [mock_sleep]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_sleep
        result = await get_sleep(1)

    assert len(result["sleeps"]) == 1
    assert result["sleeps"][0]["score"] == 88.0
    assert result["sleeps"][0]["efficiency"] == 92.0
    assert result["sleeps"][0]["respiratory_rate"] == 15.5


@pytest.mark.asyncio
async def test_get_sleep_date_range():
    mock_sleep = MagicMock(
        created_at="2026-03-10T08:00:00Z", performance=90.0,
        total_in_bed_hours=7.5, efficiency=93.0, respiratory_rate=14.8,
    )
    mock_client = AsyncMock()
    mock_client.get_sleep.return_value = [mock_sleep]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_sleep
        result = await get_sleep(start_date="2026-03-01", end_date="2026-03-15")

    mock_client.get_sleep.assert_called_once_with(start="2026-03-01", end="2026-03-15")
    assert len(result["sleeps"]) == 1


@pytest.mark.asyncio
async def test_get_cycles():
    mock_cycle = MagicMock(start="2026-03-18T06:00:00Z", strain=14.2, avg_hr=72)
    mock_client = AsyncMock()
    mock_client.get_cycles.return_value = [mock_cycle]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_cycles
        result = await get_cycles(1)

    assert result["cycles"][0]["strain"] == 14.2
    assert result["cycles"][0]["avg_hr"] == 72


@pytest.mark.asyncio
async def test_get_cycles_date_range():
    mock_cycle = MagicMock(start="2026-03-10T06:00:00Z", strain=12.5, avg_hr=68)
    mock_client = AsyncMock()
    mock_client.get_cycles.return_value = [mock_cycle]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_cycles
        result = await get_cycles(start_date="2026-03-01", end_date="2026-03-15")

    mock_client.get_cycles.assert_called_once_with(start="2026-03-01", end="2026-03-15")
    assert len(result["cycles"]) == 1


@pytest.mark.asyncio
async def test_get_body_measurement():
    mock_body = MagicMock(height_meter=1.85, weight_kilogram=90.5, max_heart_rate=195)
    mock_client = AsyncMock()
    mock_client.get_body_measurement.return_value = mock_body

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_body_measurement
        result = await get_body_measurement()

    assert result["height_meters"] == 1.85
    assert result["weight_kg"] == 90.5
    assert result["max_heart_rate"] == 195


@pytest.mark.asyncio
async def test_get_sport_types():
    mock_type = MagicMock(id=44)
    mock_type.name = "Yoga"
    mock_client = AsyncMock()
    mock_client.get_sport_types.return_value = [mock_type]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_sport_types
        result = await get_sport_types()

    assert result["sport_types"][0] == {"id": 44, "name": "Yoga"}


@pytest.mark.asyncio
async def test_search_exercises_by_query():
    mock_exercise = MagicMock(
        exercise_id="bench-press-1",
        equipment="BARBELL", muscle_groups=["CHEST", "TRICEPS"], exercise_type="STRENGTH",
    )
    mock_exercise.name = "Bench Press"
    mock_catalog = MagicMock()
    mock_catalog.search.return_value = [mock_exercise]
    mock_client = AsyncMock()
    mock_client.get_exercises.return_value = mock_catalog

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import search_exercises
        result = await search_exercises(query="bench")

    assert len(result["exercises"]) == 1
    assert result["exercises"][0]["name"] == "Bench Press"
    assert result["total"] == 1
    mock_catalog.search.assert_called_once_with("bench")


@pytest.mark.asyncio
async def test_search_exercises_by_filter():
    mock_exercise = MagicMock(
        exercise_id="squat-1",
        equipment="BARBELL", muscle_groups=["QUADS"], exercise_type="STRENGTH",
    )
    mock_exercise.name = "Squat"
    mock_catalog = MagicMock()
    mock_catalog.filter.return_value = [mock_exercise]
    mock_client = AsyncMock()
    mock_client.get_exercises.return_value = mock_catalog

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import search_exercises
        result = await search_exercises(equipment="BARBELL", muscle_group="QUADS")

    assert len(result["exercises"]) == 1
    mock_catalog.filter.assert_called_once_with(
        equipment="BARBELL", muscle_group="QUADS", movement_pattern=None,
    )


@pytest.mark.asyncio
async def test_get_journal_behaviors():
    mock_behavior = MagicMock(
        id=101, title="Caffeine",
        question_text="Did you have caffeine today?", behavior_type="BOOLEAN",
    )
    mock_client = AsyncMock()
    mock_client.get_journal_behaviors.return_value = [mock_behavior]

    with patch("whoop_write_mcp.auth.get_whoop_client", return_value=mock_client):
        from whoop_write_mcp.tools_read import get_journal_behaviors
        result = await get_journal_behaviors("2026-03-19")

    assert len(result["behaviors"]) == 1
    assert result["behaviors"][0]["title"] == "Caffeine"
    mock_client.get_journal_behaviors.assert_called_once_with("2026-03-19")
