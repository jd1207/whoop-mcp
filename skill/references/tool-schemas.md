# Whoop MCP Tool Reference

## Read Tools

### get_recovery
Recovery score, HRV, and resting heart rate.
```
params: { days: int (default 1), start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD" }
returns: [{ date, recovery_score (0-100), hrv (ms), resting_hr (bpm), created_at }]
```

### get_sleep
Sleep performance, duration, and quality.
```
params: { days: int (default 1), start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD" }
returns: [{ date, performance (0-100), total_in_bed_hours, respiratory_rate, created_at }]
```

### get_strain
Daily strain and heart rate data.
```
params: { days: int (default 1), start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD" }
returns: [{ date, strain (0-21), avg_hr, start, end }]
```

### get_body_measurement
Current body metrics.
```
params: none
returns: { height_meter, weight_kilogram, max_heart_rate }
```

### get_sport_types
All available Whoop sport/activity type IDs.
```
params: none
returns: [{ id: int, name: str }]
```

### search_exercises
Search the Whoop exercise catalog.
```
params: { query: str, equipment: str (optional), muscle_group: str (optional), movement_pattern: str (optional) }
returns: [{ id, name, equipment, muscle_group }] (up to 50)
```

### get_journal_behaviors
Available journal questions for a date.
```
params: { date: "YYYY-MM-DD" }
returns: [{ id: int, question: str, type: str }]
```

## Write Tools

### create_activity
Log a simple activity (sauna, meditation, yoga, etc.).
```
params: { activity_type: str, duration_minutes: int, start_time: "ISO8601" (optional) }
returns: { id, sport_id, start, end }
```
Activity types: sauna, ice_bath, meditation, yoga, stretching, running, cycling, hiking, swimming, walking

### delete_activity
Remove an activity. Always confirm with user first.
```
params: { activity_id: str, is_recovery: bool (default false) }
returns: { success: bool }
```

### list_activities
Recent activities with IDs (useful before delete).
```
params: { limit: int (default 5) }
returns: [{ id, sport_id, start }]
```

### update_weight
Update body weight on Whoop. Accepts lbs, converts internally.
```
params: { weight_lbs: float }
returns: { success: bool, weight_kg: float }
```

### set_alarm
Set or disable the Whoop alarm.
```
params: { time_str: "HH:MM", enabled: bool (default true) }
returns: { success: bool }
```

### log_workout
Log a full workout with optional exercise detail.
```
params: {
  sport_id: int,
  start_time: "ISO8601",
  end_time: "ISO8601",
  exercises: "JSON string" (optional)
}
exercises format: '[{"name": "Bench Press", "sets": 3, "reps": 10, "weight": 135}]'
returns: { id, sport_id, start, end }
```

### link_exercises
Attach per-set exercise detail to an existing activity.
```
params: {
  activity_id: str,
  exercises: "JSON string"
}
exercises format: '[{"exercise_id": "whoop_id", "name": "Bench Press", "sets": [{"reps": 5, "weight": 225}]}]'
returns: { success: bool }
```

### log_journal
Log journal entry with behavior responses.
```
params: {
  date: "YYYY-MM-DD",
  entries: "JSON string",
  notes: str (optional)
}
entries format: '[{"behavior_tracker_id": 2, "answered_yes": true, "magnitude_input_value": 3}]'

Common behavior IDs:
  1 = alcohol (answered_yes: bool)
  2 = caffeine (magnitude_input_value: count of drinks)
  6 = late meal (answered_yes: bool)
  89 = protein intake (magnitude_input_value: grams)
```
