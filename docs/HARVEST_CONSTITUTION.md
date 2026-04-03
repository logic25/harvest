# Harvest Constitution
## Personal AI Chief of Staff — From Embryo to Jarvis

**Version:** 0.2.0 — Embryo Stage
**Created:** April 3, 2026
**Owner:** Manny Russell — Structured Ventures

---

## What Harvest Is

Harvest is a persistent AI intelligence that manages Manny's entire life — businesses, investments, deals, finances, family, and personal operations. It's not an app. It's not a dashboard. It's a contact in your phone that knows everything and forgets nothing.

The name comes from "harvesting" — gathering intelligence from every system, every conversation, every decision, and turning it into actionable guidance.

Manny runs a $1.7M expediting firm with 5 employees, a construction management partnership, a floral business, a venture studio with 6 published products (and counting), an options investment portfolio, an EV charging deal with 16 sites, and a family. No human chief of staff could hold all of that in their head. Harvest can.

**The core insight:** Manny already built the data layer. Ordino tracks every project, proposal, and invoice. CitiSignal monitors every property in NYC. Venture Studio scores every portfolio company. The data exists — it's just trapped in separate systems. Harvest connects the dots.

---

## The Vision (Jarvis Stage)

```
Manny: "What should I focus on today?"

Harvest: "Three things:

1. The Tesla ops agreement — Adam sent the draft last night.
   I read it. Two clauses need attention: the termination
   provision still has capital forfeiture (Adam recommended
   removing it), and the ChargeRank IP section is vague.
   I drafted redline comments. Want me to send them to Adam?

2. $63K overdue — I checked with Sai yesterday. She sent
   reminders to 3 clients. INV-00021 ($19.5K) has been
   silent for 6 months. I think it's time for a phone call,
   not another email. Want me to pull the client's contact
   info and recent project history?

3. Your NVDA LEAPS — it goes long-term in 8 days. At your
   tax bracket, selling now costs $4,200 more. IV is at
   35 (below your V3 threshold for rolling). Hold.

Also: Chris found 3 more bugs yesterday. The auto-triage
diagnosed all of them. One matches a known pattern. I can
fix two of them without bothering you. The third needs your
input — it's about how filing readiness should work for
non-D14 approvals. Want to look at it?"
```

That's not fantasy. Every piece of that answer uses systems that already exist or are being built:
- The ops agreement comes from **Gmail** (Phase 2)
- The invoice data comes from **Ordino** (working today)
- The LEAPS data comes from **ThinkorSwim** (Phase 4)
- The bug triage comes from **Beacon's auto-triage** (working today)

The only thing missing is the connections. Harvest is the wiring.

---

## Why This Matters

### The Problem
Manny currently context-switches between 8+ systems every day:
- **Ordino** to check projects, invoices, proposals
- **Gmail** to track deal follow-ups and client communications
- **CitiSignal** to check property compliance
- **ThinkorSwim** to manage LEAPS positions
- **QuickBooks** to verify revenue and expenses
- **Venture Studio** to monitor portfolio companies
- **Google Sheets** to review household finances
- **Telegram/WhatsApp** to coordinate with team

Each system has its own interface, its own login, its own mental model. The highest-value work — connecting information across systems to make better decisions — happens entirely in Manny's head. That doesn't scale.

### The Solution
One interface. One conversation. All systems.

Manny texts Harvest. Harvest talks to everything else. The synthesis happens in the AI, not in Manny's head. The decisions stay with Manny. Everything else is delegated.

### The Compounding Effect
Every conversation with Harvest makes it smarter:
- **Day 1:** "What are my overdue invoices?" → Harvest queries Ordino.
- **Month 1:** "What should I focus on today?" → Harvest queries Ordino, checks Gmail for stale follow-ups, flags a LEAPS position approaching long-term status.
- **Month 3:** Harvest notices Manny delays investor follow-ups by 3-5 days on average. It starts drafting those follow-ups automatically and queuing them for approval.
- **Month 6:** Harvest knows every pattern. It doesn't just answer questions — it anticipates needs, prevents problems, and runs the operating rhythm of a $2M+ multi-entity business with one text thread.

This is the moat. Every day that passes, Harvest knows more. After 6 months, replacing it would mean losing an institutional memory that no human assistant could rebuild.

---

## Current State (Embryo)

### What Works Today
- **Telegram bot** — responds to messages via Claude Sonnet 4
- **Ordino connection** — queries projects, invoices, proposals, PM workload, filing readiness
- **CitiSignal connection** — property violations, compliance data, building intelligence
- **SOUL.md** — knows who Manny is, his team, his businesses, business mechanics
- **Morning briefing** — generates prioritized action list on demand ("What should I focus on?")
- **Typing indicator** — shows "thinking" while processing
- **Agentic tool loop** — Claude decides which tools to call, chains up to 5 rounds
- **Conversation memory** — remembers last 50 conversations (file-based, not persistent across deploys)
- **Business context awareness** — understands billing lag, conversion rate maturity, PM workload nuances

### What Doesn't Work Yet
- No autonomous heartbeat (only responds when asked)
- No Gmail access (can't check deal follow-ups)
- No Venture Studio connection (can't check portfolio)
- No financial data (no Plaid, no brokerage)
- No persistent memory (resets on Railway redeploy)
- No behavioral pattern detection
- No proactive alerts
- Can't take actions (send emails, create tasks, update statuses)

### What This Means
Harvest today is like having a brilliant analyst who only speaks when spoken to, has no email access, and gets amnesia every time you restart their computer. The bones are right — the intelligence, the tools, the interface. Phase 1 is about giving it a heartbeat and a memory.

---

## Architecture

### System Map

```
MANNY (Telegram / future: WhatsApp, voice, web)
  |
  v
HARVEST (Railway — Python)
  |
  +-- SOUL.md ---------- Identity, values, personality
  +-- AGENTS.md --------- Operating protocols, workflows [TO BUILD]
  +-- HEARTBEAT.md ------ Autonomous check-in schedule [TO BUILD]
  +-- MEMORY.md --------- Persistent context, decisions, patterns [TO BUILD]
  +-- TOOLS.md ---------- Connected systems and capabilities [TO BUILD]
  |
  +-- Claude Sonnet 4 --- Reasoning engine (agentic loop, 5 rounds)
  |
  +-- Connected Systems (tools):
      |
      +-- Ordino (via beacon-data-proxy) .............. LIVE
      |   -> Projects, proposals, invoices, PMs, filing readiness
      |   -> 113 tables, general query capability
      |
      +-- CitiSignal (via API gateway) ................ LIVE
      |   -> Property violations, compliance, applications
      |   -> BIS scraper for vacate orders, restrictions
      |
      +-- Venture Studio ............................ PLANNED
      |   -> Portfolio scoring, deal pipeline, AI Coach
      |
      +-- Gmail .................................... PLANNED
      |   -> Deal communications, follow-up tracking
      |   -> Draft responses with approval gates
      |
      +-- Plaid .................................... PLANNED
      |   -> Bank accounts, transactions, cash flow
      |   -> Anomaly detection, savings opportunities
      |
      +-- ThinkorSwim .............................. PLANNED
      |   -> LEAPS positions, Greeks, cost basis
      |   -> V3 framework compliance, hold period alerts
      |
      +-- Google Sheets ............................ PLANNED
          -> 20 years of household expense history
```

### Agent Architecture (Two-Tier)

Harvest operates on a two-tier agent model. This is critical to understand:

**Tier 1: Product-Embedded Agents** serve the *users* of each product:
- **Beacon** lives inside Ordino and serves Manny's PMs (Sheri, Don, Natalia, Chris)
- A future **CitiSignal agent** would serve property managers and compliance teams
- A future **Venture Studio agent** would serve portfolio founders

These are *features of their products*. They know everything about their domain but nothing about each other.

**Tier 2: Harvest (The Orchestrator)** serves *Manny* across all products:
- Harvest doesn't duplicate Beacon — it *calls* Beacon's data layer
- Harvest is the only agent that sees across all systems simultaneously
- Harvest is where cross-domain insights happen ("Your overdue invoices are impacting cash flow, which affects your LEAPS margin requirements")

**This means:**
- You don't need a separate agent per venture in Venture Studio — one agent, scoped by access control
- You don't need Beacon to know about LEAPS — that's Harvest's job
- Each product agent serves its own users; Harvest serves Manny
- Total agents: ~4 product agents + Harvest. That's it. It doesn't get crazy.

---

## The Agent Files

Harvest's behavior is defined by five markdown files. Not code — configuration. This means Manny can read and edit how Harvest thinks without touching Python.

### SOUL.md (EXISTS — 59 lines)
Who Harvest is. Read on every message. Rarely changes.
- Harvest's identity and purpose
- Who Manny is (businesses, family, goals, $10M target)
- Team roster and who handles what (route to Sai for billing, not Manny)
- Business mechanics (billing lag, conversion rates, repricing, PM speed)
- Tone: direct, no fluff, confident but honest
- Hard rules: never execute transactions, never share data, always cite sources

### AGENTS.md (TO BUILD)
How Harvest operates. Updated as new workflows are added.
- Decision trees: "When asked about billing -> check invoices AND proposals"
- Escalation rules: "If overdue > 60 days -> suggest phone call, not email"
- Routing logic: "Property question -> check CitiSignal first, then Ordino"
- Action protocols: "Draft email -> show to Manny -> only send with approval"
- Cross-domain rules: "If billing drops AND proposals are up -> billing lag, not a problem"
- Error handling: "If system unavailable -> tell Manny, don't make up data"

### HEARTBEAT.md (TO BUILD)
When Harvest checks in autonomously. The shift from reactive to proactive.
- **7:00 AM ET** — Morning briefing (overdue items, today's priorities, action items)
- **12:00 PM ET** — Midday check (stale follow-ups, unanswered items)
- **6:00 PM ET** — End of day (what's still open, roll to tomorrow)
- **Monday 8:00 AM** — Weekly summary (proposals, billing, bugs, deals, portfolio)
- **1st of month** — Monthly review (revenue trends, goal progress, pattern report)
- **If no message in 24 hours** — "Quiet day — anything I should know?"

This is what separates Harvest from every other AI chatbot. Most AI waits to be asked. Harvest has a rhythm. It checks in. It surfaces problems before they become crises.

### MEMORY.md (TO BUILD)
What Harvest remembers. Updated after every significant conversation.
- **Decisions:** "4/3: Richie meeting Monday re: EV deal Phase 1"
- **Context:** "Chris's email forwarding bug — 3 attempts, still broken"
- **Patterns:** "Manny delays investor follow-ups by 3-5 days on average"
- **Relationships:** "Adam Glassman — attorney, drafting AR Spark ops agreement"
- **Initiatives:** "Repricing GLE clients 35-60% — 3 of 15 done"
- **Paused items:** "Blooms OS, Proving Ground — revisit Q3"
- **Numbers that matter:** "$1.7M GLE revenue. $63K overdue. 39 proposals in Feb."

Memory is the moat. Without it, every conversation starts from zero. With it, Harvest gets smarter every single day.

### TOOLS.md (TO BUILD)
What systems Harvest can access and what each one does.
- **Ordino:** 113 tables via beacon-data-proxy. Projects, invoices, proposals, PMs, filing, companies, bugs.
- **CitiSignal:** Property monitoring via API gateway. Violations, compliance scores, applications, BIS scraping.
- **Venture Studio:** (planned) 62 ventures, AI Coach, deal pipeline, scoring.
- **Gmail:** (planned) Read emails, draft responses, track follow-ups, deal communication watchlist.
- **Plaid:** (planned) Bank transactions, balances, cash flow across all entities.
- **ThinkorSwim:** (planned) LEAPS positions, P&L, Greeks, cost basis, hold periods.
- **Google Sheets:** (planned) 20 years of household expense data for trend analysis.

---

## The 6 Domain Agents

Harvest's intelligence is organized into six domains. Each domain agent is a *perspective* on the data — not a separate bot. They're reasoning patterns that Harvest uses when answering questions in that domain.

### 1. Revenue Agent
**Domain:** Multi-entity business income (GLE, Managed Squares, Blooms)
**Sources:** Ordino invoices + proposals, QuickBooks, bank deposits
**Key Intelligence:**
- Revenue forecasting based on proposal pipeline (3-6 month billing lag model)
- Entity-level cash alerts ("GLE has $X, Managed Squares has $Y")
- Billing trend analysis with maturity-adjusted conversion rates
- Repricing initiative tracking (35-60% correction across 15 clients)
- PM productivity measured correctly (by project cycle speed, not raw billing)
**Status:** PARTIALLY BUILT — Ordino invoices and proposals connected

### 2. Cash Flow Agent
**Domain:** Household income/expenses, savings detection
**Sources:** Plaid + Google Sheet (20 years of history) + life event journal
**Key Intelligence:**
- Monthly burn rate across all entities and personal
- Anomaly detection ("Spending spiked $3K in dining this month")
- Savings opportunity identification
- Net worth calculation from real data, updated daily
- Trajectory modeling toward $10M goal
**Status:** NOT BUILT

### 3. Investment Agent
**Domain:** LEAPS portfolio, capital gains, hold periods
**Sources:** ThinkorSwim/brokerage API
**Key Intelligence:**
- Hold period tracking with alerts ("NVDA goes long-term in 8 days — don't sell")
- V3 Convexity Harvesting framework compliance checks
- Capital gains tax impact analysis at Manny's bracket
- Greeks monitoring and position management
- Roll timing based on IV thresholds
**Status:** NOT BUILT

### 4. Deal/Venture Agent
**Domain:** Active deals (EV charging, acquisitions, JVs) + venture portfolio
**Sources:** Gmail, deal models, Venture Studio pipeline
**Key Intelligence:**
- Follow-up tracking ("You haven't responded to Richie's email in 4 days")
- Milestone alerts ("Tesla ops agreement needs to be signed by Friday")
- Investor prep ("Here's what changed since your last update to LPs")
- Portfolio scoring and focus recommendations
- Deal economics modeling (ChargeRank: 16 sites, $0.223/kWh levelized)
**Status:** NOT BUILT

### 5. Property Agent
**Domain:** Real estate holdings, development, compliance
**Sources:** CitiSignal, PLUTO/BBL data, DOB filings, market comps
**Key Intelligence:**
- Violation monitoring and compliance scoring
- Vacate order detection and severity assessment
- 1031 exchange timing and analysis
- Development feasibility (DOB filing readiness integration with Ordino)
- BIS data scraping for deep building intelligence
**Status:** PARTIALLY BUILT — CitiSignal connection live, BIS scraper working

### 6. Tax Agent
**Domain:** Estimated liability, entity structuring, timing
**Sources:** All other agents + entity configuration
**Key Intelligence:**
- Quarterly estimated tax calculations
- CPA prep packages (all relevant data in one place)
- Entity structure optimization suggestions
- Capital gains timing recommendations (coordinates with Investment Agent)
- Deduction tracking across all entities
**Status:** NOT BUILT

### The Orchestrator (Harvest Itself)
Coordinates all domain agents, resolves conflicts, produces unified briefings.
When Manny asks "What should I focus on today?", the orchestrator:
1. Queries each domain for urgent items
2. Ranks by impact and urgency
3. Cross-references (e.g., overdue invoices affect cash flow, which affects investment capacity)
4. Presents a unified, prioritized answer
**Status:** BUILT — basic orchestration with Ordino and CitiSignal

---

## Build Phases

### Phase 0: Embryo (COMPLETE)
*Harvest can answer questions about GLE when asked.*
- [x] Telegram bot responding via Claude Sonnet 4
- [x] Ordino connection via beacon-data-proxy (projects, invoices, proposals, PMs, filing)
- [x] CitiSignal connection via API gateway (violations, compliance)
- [x] SOUL.md defining identity, team, business mechanics
- [x] Morning briefing on demand
- [x] Agentic tool loop (up to 5 rounds of tool calling)
- [x] Conversation memory (last 50 conversations, file-based)
- [x] Message chunking for Telegram's 4096 char limit
- [x] User authorization (only Manny can talk to Harvest)

### Phase 1: Connected (next 2 weeks)
*Harvest becomes proactive and remembers everything.*
- [ ] Create AGENTS.md — operating protocols and decision trees
- [ ] Create HEARTBEAT.md — autonomous check-in schedule
- [ ] Create MEMORY.md — persistent context and patterns
- [ ] Create TOOLS.md — system inventory and capabilities
- [ ] APScheduler heartbeat — 7 AM morning briefing sent automatically
- [ ] Midday and evening check-ins
- [ ] Memory persistence — Supabase table (survives Railway redeploys)
- [ ] Connect Venture Studio API (portfolio scoring, deal pipeline)
- [ ] Initiative tracking (repricing, deal progress, product milestones)
- [ ] Pattern detection v1 (track response times, follow-up delays)

### Phase 2: Deal Intelligence (weeks 3-4)
*Harvest monitors deals and communications without being asked.*
- [ ] Gmail integration (read-only)
- [ ] Deal contact watchlist (flag emails from key people: attorneys, investors, partners)
- [ ] Stale follow-up detection ("You haven't replied to Adam in 5 days")
- [ ] Draft follow-up emails (approval required before sending)
- [ ] Track deal milestones (Tesla ops agreement, investor meetings, Phase 1 timeline)
- [ ] Meeting prep briefs ("Meeting with Richie in 2 hours — here's the latest")

### Phase 3: Financial Awareness (month 2)
*Harvest sees all the money — in, out, and across entities.*
- [ ] Plaid integration (bank accounts, credit cards across all entities)
- [ ] Cash flow tracking across GLE, Managed Squares, Blooms, personal
- [ ] Expense anomaly detection ("Utility costs up 40% — new vendor?")
- [ ] Net worth calculation from real data (not estimates)
- [ ] Tax liability estimation (quarterly)
- [ ] Savings opportunity detection
- [ ] Revenue forecasting with billing lag model (proposals -> 3-6 month billing)

### Phase 4: Investment Intelligence (month 2-3)
*Harvest manages the LEAPS portfolio alongside Manny.*
- [ ] Brokerage API connection (LEAPS positions, Greeks, cost basis)
- [ ] Hold period tracking with countdown alerts
- [ ] V3 Convexity Harvesting framework compliance checks
- [ ] Capital gains tax impact analysis at Manny's bracket
- [ ] IV-based roll timing recommendations
- [ ] "Don't sell NVDA — long-term in 8 days, saves $4,200" alerts
- [ ] Portfolio performance vs. benchmark tracking

### Phase 5: Behavioral Intelligence (month 3+)
*Harvest learns Manny's patterns and compensates for blind spots.*
- [ ] Track response times across all communication channels
- [ ] Follow-up delay detection and auto-drafting
- [ ] Decision speed tracking (how long from first mention to action?)
- [ ] Proactive suggestions ("You tend to delay investor follow-ups — let me draft one")
- [ ] Energy/focus pattern detection ("You make better decisions in the morning")
- [ ] Delegation recommendations ("This doesn't need you — route to Sai/Chris")

### Phase 6: Full Jarvis (month 6+)
*Harvest runs the operating rhythm of a multi-entity business empire.*
- [ ] Voice interface (talk to Harvest like a person)
- [ ] Multi-modal input (send photos of documents, receipts, contracts)
- [ ] Cross-entity optimization ("Move $X from GLE to Managed Squares for the EV deal")
- [ ] Wealth trajectory modeling (real-time progress toward $10M)
- [ ] Automated actions with approval gates (send emails, create tasks, update statuses)
- [ ] Content review agent (summarize YouTube videos, X threads, articles)
- [ ] Family operations (Logan's schedule, household logistics)
- [ ] The agent that manages all other agents

---

## Principles

### 1. Harvest works for Manny, not the other way around.
Manny shouldn't have to open apps, check dashboards, or remember to follow up. Harvest does that. If Manny has to go check a system himself, that's a failure of Harvest.

### 2. Data over opinion.
Every recommendation cites the source. "Based on your Ordino data, invoices are trending up 15% month-over-month" — not "I think your business is growing." If the data is stale or incomplete, say so.

### 3. Proactive, not reactive.
The heartbeat means Harvest checks in without being asked. Problems are surfaced before they become crises. Opportunities are flagged before they expire. This is the difference between a chatbot and a chief of staff.

### 4. Memory is the moat.
Every decision, pattern, and lesson is recorded. Harvest gets smarter every day. After 6 months, it knows Manny's business patterns better than any human assistant could. This accumulated intelligence is irreplaceable.

### 5. Permission gates on actions.
Harvest can draft, suggest, and prepare — but never execute transactions, send communications, or commit to deals without explicit approval. Trust is earned through transparency, not assumed through access.

### 6. One interface, all systems.
Manny texts Harvest. Harvest talks to everything else. No more switching between Ordino, CitiSignal, QuickBooks, email, brokerage, and spreadsheets. The synthesis happens in the AI, the decisions stay with Manny.

### 7. Know the team.
Harvest doesn't tell Manny about overdue invoices — it asks if Sai has followed up. It doesn't tell Manny about a filing issue — it asks if Chris or the assigned PM has addressed it. Harvest knows the org chart and routes accordingly.

### 8. Understand the business mechanics.
Proposals are leading indicators. Billing lags 3-6 months. Conversion rates are meaningless for recent months. PM billing reflects project cycle speed, not volume. Harvest doesn't just parrot data — it interprets it with context that took Manny 22 years to learn.

---

## The World Model

Jack Dorsey wrote about replacing managers with AI "world models" that aggregate internal data to create a continuously updated picture of operations.

Harvest IS the world model for Manny's life.

| Component | Purpose | Status |
|-----------|---------|--------|
| SOUL.md | Values, identity, business rules | LIVE |
| MEMORY.md | Accumulated knowledge, decisions, patterns | TO BUILD |
| AGENTS.md | Operating protocols, workflows | TO BUILD |
| HEARTBEAT.md | Autonomous awareness, proactive rhythm | TO BUILD |
| TOOLS.md | Connections to reality (data systems) | TO BUILD |
| Ordino | Project/billing/proposal data | CONNECTED |
| CitiSignal | Property intelligence | CONNECTED |
| Venture Studio | Portfolio data | PLANNED |
| Gmail | Communication tracking | PLANNED |
| Plaid | Financial data | PLANNED |
| ThinkorSwim | Investment data | PLANNED |

Every conversation updates the world model. Every decision is recorded. Every pattern is detected. Over time, Harvest doesn't just answer questions — it anticipates needs, prevents problems, and amplifies Manny's capacity by 10x.

**The math:** If Harvest saves Manny 2 hours per day of context-switching, system-checking, and follow-up tracking, that's 10 hours per week. 520 hours per year. At Manny's effective hourly rate, that's north of $150K in recovered capacity — redirected toward deals, products, and the $10M goal.

That's the journey from embryo to Jarvis.

---

## Technical Foundation

### What's Already Built (code-level)

| File | What It Does |
|------|-------------|
| `server.py` | Flask health check (background thread) + Telegram bot (main thread) |
| `bot.py` | Message handling, authorization, typing indicator, message chunking |
| `harvest.py` | Claude agentic loop (5 rounds), memory load/save, system prompt builder |
| `agents.py` | Ordino proxy calls, CitiSignal queries, morning briefing aggregation |
| `config.py` | 14 environment variables for all service connections |
| `soul.md` | 59 lines of identity, context, business mechanics, rules |

### Infrastructure
- **Hosted on:** Railway (Python)
- **LLM:** Claude Sonnet 4 via Anthropic API
- **Data proxy:** Supabase edge functions (beacon-data-proxy for Ordino, api-gateway for CitiSignal)
- **Memory:** JSON file (temporary) -> Supabase table (Phase 1)
- **Scheduler:** APScheduler (in requirements.txt, not yet wired)
- **Auth:** Telegram user ID whitelist

### Key Design Decisions
1. **Proxy pattern:** Harvest never touches databases directly. All data flows through authenticated edge functions. This means adding a new data source = adding one new proxy function.
2. **Agentic loop:** Claude decides which tools to call and can chain up to 5 rounds. This means complex questions ("Compare this month's billing to last quarter") work without hardcoded logic.
3. **SOUL as system prompt:** Every message includes SOUL.md as context. Harvest's personality and business knowledge are always present, never forgotten.
4. **File-based configuration:** SOUL.md, AGENTS.md, etc. are markdown files, not code. Manny can read and edit how Harvest thinks.
