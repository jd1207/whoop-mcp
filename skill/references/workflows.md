# Whoop Coaching Workflows

Multi-step patterns for common scenarios. Each workflow shows the tool sequence, decision points, and what to say.

## Morning Readiness Check

When the user asks "how am I doing today" or starts a conversation:

```
1. get_recovery(days=1)
2. get_sleep(days=1)
3. get_strain(days=1)  — yesterday's strain for context

Decision:
- If all normal (green, 7+ hours, moderate strain): don't dump stats. Just coach.
  Say: "Ready to go. What's on the menu today?"
- If yellow with flags: brief mention.
  Say: "Recovery's at 52% with 5.8h sleep. We can train but let's see how warm-ups feel."
- If red or multi-day decline: full context.
  Say: "Third day of declining HRV (down 18% from your average). I'd swap today's heavy bench for a light technique day."
```

## Pre-Workout Assessment

When the user says they're starting a workout:

```
1. get_recovery(days=1)
2. Check what's programmed (from training memory)

If GREEN or HIGH YELLOW:
  - Proceed as programmed
  - "Recovery's solid. Let's hit it."

If LOW YELLOW:
  - Warm-ups become diagnostic
  - "Start your warm-ups and tell me how the bar feels at 60% — we'll decide from there."

If RED:
  - Suggest alternatives, don't dictate
  - "Recovery's at 28%. Options: (1) deload at 70% of planned weight, (2) swap to accessories only, (3) push through if you're feeling it. Your call."
```

## Post-Workout Sync

After a workout is completed:

```
1. log_workout(sport_id, start_time, end_time)
2. If detailed exercises logged: link_exercises(activity_id, exercises)
3. If meals were logged today: log_journal(date, entries) with caffeine/alcohol signals

Say: "Workout synced to Whoop — bench 285x3, 295x2. Nice session."
Don't: repeat every set back to them or over-explain the sync.
```

## Logging Simple Activities

When user mentions sauna, meditation, yoga, etc.:

```
1. create_activity(activity_type, duration_minutes)

Say: "Logged 20-min sauna."
Don't: ask for confirmation on low-risk activities. Just do it.
```

## Weekly Review

When user asks about their week or when Monday arrives:

```
1. get_recovery(days=7)
2. get_sleep(days=7)
3. get_strain(days=7)

Analyze:
- Recovery trend: improving / stable / declining
- Sleep consistency: are they getting enough? any bad nights?
- Strain budget: did they overdo it? underdo it?
- HRV trend: direction matters more than daily values

Report format (keep it concise):
"This week: recovery averaged 62% (up from 55% last week). Sleep was consistent at 6.5h.
Strain peaked Wednesday after heavy bench. HRV trending up — good sign for next week's progression."
```

## Journal Management

After meal logging, sync relevant signals to Whoop:

```
1. Count caffeine drinks from meals
2. Check for alcohol mentions
3. Check meal timing (late meals after 8 PM)

log_journal(date, entries):
  - caffeine: behavior_tracker_id=2, magnitude_input_value=count
  - alcohol: behavior_tracker_id=1, answered_yes=true/false
  - late meal: behavior_tracker_id=6, answered_yes=true/false
  - protein: behavior_tracker_id=89, magnitude_input_value=grams
```

## Red Day Protocol

When recovery is under 34%:

```
1. get_recovery(days=3) — check if it's a trend or one-off
2. get_sleep(days=3) — identify root cause

If single bad day with obvious cause (poor sleep, alcohol):
  - "Recovery's red at 28% — looks like last night's 4.5h sleep is the culprit.
    I'd go lighter today. How are you feeling?"

If 3+ day declining trend:
  - "This is the third day of declining recovery. HRV is down 22% from your weekly average.
    Strong recommendation: recovery day or light mobility work. Your body is asking for a break."

If user overrides (says they want to train anyway):
  - Acknowledge ONCE, then coach at their chosen intensity
  - "Got it — let's warm up and see how 70% feels. If RPE is under 7, we'll build from there."
  - Do NOT repeat the recovery warning
```

## Failure Handling

### Auth Expired
```
error: "whoop not connected" or token refresh failure
Say: "Whoop disconnected — you may need to re-login. Go to profile to reconnect."
Don't: show error codes or stack traces
```

### API Errors
```
error: WhoopAPIError or timeout
Say: "Couldn't reach Whoop right now. We'll train without biometrics — let me know how you're feeling."
Don't: retry in a loop or panic
```

### Stale Data
```
Recovery data is from yesterday (date mismatch)
Say: "Heads up — your Whoop data is from yesterday. It may not reflect how you slept last night."
Don't: pretend stale data is current
```
