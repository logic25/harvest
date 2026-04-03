# Heartbeat — Harvest Autonomous Schedule

Harvest doesn't wait to be asked. It checks in on a rhythm.

## Daily Schedule

### 7:00 AM ET — Morning Briefing
**Trigger:** Every day
**What it does:**
- Queries Ordino: active projects, overdue invoices, proposals, PM workload, filing readiness
- Queries CitiSignal: any new violations or compliance changes
- Synthesizes via Claude into prioritized daily action list
- Sends to Manny's Telegram

**Format:**
```
Three things to focus on today:
1. [Most urgent — cite data, name who should handle it]
2. [Second priority — numbers, context, recommended action]
3. [Third — anything else that needs attention]

Also: [Quick notes on anything else worth knowing]
```

### 12:00 PM ET — Midday Check (Weekdays)
**Trigger:** Monday-Friday
**What it does:**
- Checks for stale follow-ups or unanswered items from morning
- Only sends if there's something actionable (doesn't spam)

### 8:00 AM ET Monday — Weekly Summary
**Trigger:** Every Monday
**What it does:**
- Proposals: sent this week vs last week, pipeline value
- Billing: invoiced this week, overdue aging
- Bugs/issues: any unresolved from last week
- Deals: EV charging, investor updates, any movement
- Blooms: quick health check (revenue trend, any flags)

## Future Schedule (Not Yet Implemented)

### 6:00 PM ET — End of Day (Planned)
- What's still open from the morning
- Roll unfinished items to tomorrow

### 1st of Month — Monthly Review (Planned)
- Revenue trends across all entities
- Goal progress ($10M target trajectory)
- Pattern report (behavioral insights)

### If No Message in 24 Hours (Planned)
- "Quiet day — anything I should know?"

## Configuration
- Scheduler: APScheduler BackgroundScheduler
- Timezone: US/Eastern
- Chat delivery: python-telegram-bot direct send API
- Heartbeat messages use the full agentic loop (Claude with tools)
