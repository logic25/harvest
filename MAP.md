# Harvest — your whole world, one page

*The map. Not a plan — a picture of what already exists. Created 2026-08-07.*

**Sharper names (adopted from a parallel refinement):** "The Briefing" → **Executive Office** (the brief is just one of its outputs; it also coordinates offices, resolves conflicts, prioritizes, asks approvals, routes tasks). "Memory" → **Shared Knowledge Layer** (it sits *behind* everything, not below — decisions, context, goals, preferences, playbooks, documents, relationships). And the frame that ties it together: **Harvest is an *organization*, not a bag of agents** — departments, institutional memory, escalation paths, approvals, SOPs. Every office shares one internal shape: *Inbox → Analyze → Research → Model → Recommend → Executive Office.* Build order (three independent takes agree): **Executive Office → Knowledge Layer → GLE → Strike → Finance → Health → …**

```
                          YOU  (Manny)
                one page. you just approve.
                          ▲
             "Done · Needs you · FYI"   ◀── the ONLY missing box:
                          │                  the approve arrow + clean one-page
             ┌────────────────────────────┐
             │      THE BRIEFING          │  ✅ get_morning_briefing() + heartbeat.py
             │   Harvest — chief of staff │     already pulls projects, overdue invoices,
             └────────────────────────────┘     proposals, filing-readiness, PM workload
                          ▲
   ┌─────────┬───────────┼───────────┬───────────┬──────────┐
┌──┴───┐ ┌───┴───┐  ┌────┴────┐  ┌───┴────┐  ┌───┴────┐ ┌───┴───┐
│GLE ★ │ │Blooms │  │CitiSig  │  │Strike  │  │Proving │ │Finance│
│query_│ │query_ │  │query_   │  │= LEAP  │  │Ground  │ │Health │
│ordino│ │blooms │  │citisig  │  │ trader │  │(Logan) │ │  —    │
│ ✅   │ │ ✅    │  │ ✅      │  │ repo   │  │ repo   │ │not    │
│wired │ │wired  │  │wired    │  │not wired│ │not wired││ yet  │
└──┬───┘ └───────┘  └─────────┘  └────────┘  └────────┘ └───────┘
   └──────────────────┬───────────────────────────────────┘
             ┌────────────────────────────┐
             │          MEMORY            │  ✅ memory_store.py (Supabase-backed)
             │       decisions + why      │     needs the "why" upgrade
             └────────────────────────────┘

   delivered via Telegram ✅        to triage later: benchline · kodacompanion · open-hempstead
```

## What's built vs. what's left

| Box | Real code | Status |
|---|---|---|
| **The Briefing** | `agents.py:get_morning_briefing()` + `heartbeat.py` | ✅ built (prose — needs one-page format) |
| **GLE room** ★ | `agents.py:query_ordino` (projects, invoices, proposals, readiness, workload) | ✅ wired — most mature room |
| **Blooms room** | `agents.py:query_blooms` | ✅ wired |
| **CitiSignal room** | `agents.py:query_citisignal` | ✅ wired |
| **Memory** | `memory_store.py` (Supabase) | ✅ built — needs "decisions + why" |
| **Delivery** | Telegram bot (`bot.py`) | ✅ built |
| **Strike / Investments** | separate repo `~/LEAP trader` | 🟡 exists, not wired as a room yet |
| **Proving Ground (Logan)** | separate repo `~/proving-ground` | 🟡 exists, not wired |
| **Finance / Health** | — | 🔴 not built (later) |
| **The "approve" arrow** | — | 🔴 **the one true gap** — Harvest only *reads* today |

## The only real work left (small)
1. **The approve arrow** — Harvest reads everything, executes nothing (SOUL.md bans it). Give it **one** gated action: approve → do. *(This is the whole project.)*
2. **One-page format** — turn the prose briefing into **Done · Needs you · FYI**.
3. **Focus GLE first** — it's the most-wired room and where the money is.

## The one rule
**One room at a time. GLE is already wired — so it's first.** Don't wire Strike or Proving Ground until the GLE briefing + one approve action run and you trust them.

## The other repos (park, don't panic)
`benchline`, `kodacompanion`, `open-hempstead` — separate experiments. Triage later. Not part of the Harvest core. They are *not* the thing that's "all over the place" — the core is right here, in one folder.
