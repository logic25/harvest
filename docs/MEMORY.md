# Memory — Harvest Persistent Context

Memory is the moat. Every conversation makes Harvest smarter.

## Storage
- **Primary:** Supabase `harvest_memory` table (survives Railway redeploys)
- **Fallback:** Local JSON file at `/tmp/harvest_memory.json`
- **Agent ID:** Each agent has its own memory (`harvest`, `blooms`)

## Memory Taxonomy

### Conversations (auto-captured)
Last 50 conversations stored with timestamp.
Used for: Context in follow-up questions, pattern detection.
```json
{
  "user": "How's the EV deal going?",
  "assistant": "Richie sent the Phase 1 numbers...",
  "timestamp": "2026-04-03T14:30:00"
}
```

### Patterns (manually or auto-detected)
Behavioral observations about Manny. Max 20 stored.
```
"Manny delays investor follow-ups by 3-5 days on average"
"Manny checks Ordino billing data every Monday morning"
"Blooms ordering happens Tuesday and Thursday — Bileysi's vendor schedule"
```

### Context Journal (decisions, relationships, initiatives)
Timestamped notes about important context. Max 30 stored.
```json
{
  "date": "2026-04-03",
  "note": "Richie meeting Monday re: EV deal Phase 1 — 16 sites, Tesla Supercharger"
}
```

## Retention Policy
- Conversations: Keep last 50 (older ones auto-pruned)
- Patterns: Keep last 20 (oldest replaced when new pattern detected)
- Context journal: Keep last 30 entries
- Full memory object upserted on every conversation

## Future Enhancements
- [ ] Automatic pattern detection (analyze conversation history for recurring themes)
- [ ] Decision log (track what was decided and outcome)
- [ ] Relationship graph (who knows who, last interaction date)
- [ ] Initiative tracker (cross-business goals with status)
- [ ] Blooms-specific memory (vendor preferences, seasonal ordering patterns)
