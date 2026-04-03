# Harvest

**Your personal AI Chief of Staff — as a contact in your phone.**

Harvest is a Telegram bot that connects to all your businesses, investments, and operations. Ask it anything — it queries your systems, reasons about the data, and gives you actionable answers.

## What It Does

- **GLE Operations** — queries Ordino for projects, proposals, invoices, PM workload, filing readiness
- **Property Intelligence** — pulls from CitiSignal for violations, compliance, applications
- **Morning Briefings** — "What should I focus on today?" gets a prioritized action list
- **Business Analysis** — billing trends, pipeline health, overdue collections
- **Personal Context** — knows your team, your goals, your businesses

## Architecture

```
You (Telegram)
  → Harvest Bot (Railway)
    → Claude Sonnet (reasoning)
    → Ordino Proxy (projects, invoices, proposals)
    → CitiSignal API (properties, violations)
    → Venture Studio (portfolio, scoring)
    → SOUL.md (your identity, goals, context)
```

## Connected Systems

| System | What Harvest Can Query |
|--------|----------------------|
| Ordino (GLE) | Projects, proposals, invoices, PMs, filing readiness |
| CitiSignal | Property violations, compliance, applications |
| Venture Studio | Portfolio scoring, deal pipeline |
| Future: Plaid | Bank accounts, transactions, cash flow |
| Future: ThinkorSwim | LEAPS positions, capital gains |
| Future: Gmail | Deal communications, follow-ups |

## Setup

### Prerequisites
- Python 3.10+
- Telegram bot token (from @BotFather)
- Anthropic API key
- Ordino beacon-data-proxy access

### Environment Variables

```
TELEGRAM_TOKEN=         # From @BotFather
ANTHROPIC_API_KEY=      # From console.anthropic.com
ORDINO_PROXY_URL=       # Ordino's beacon-data-proxy URL
ORDINO_PROXY_KEY=       # Beacon analytics key
```

### Deploy on Railway

1. Connect `logic25/harvest` repo
2. Add environment variables
3. Deploy — bot starts polling automatically

### Run Locally

```bash
pip install -r requirements.txt
export TELEGRAM_TOKEN=...
export ANTHROPIC_API_KEY=...
export ORDINO_PROXY_URL=...
export ORDINO_PROXY_KEY=...
python server.py
```

## Files

| File | Purpose |
|------|---------|
| `server.py` | Flask health check + bot startup |
| `bot.py` | Telegram message handling |
| `harvest.py` | Claude chat with tool calling |
| `agents.py` | Data gathering from connected systems |
| `config.py` | Environment variable loading |
| `soul.md` | Harvest's identity, context, and rules |

## SOUL.md

Defines who Harvest is, who Manny is, what the businesses are, and the rules for how Harvest thinks. Claude reads this on every message. This is Harvest's "personality" and institutional knowledge.

## Roadmap

- [ ] Morning briefing (scheduled daily summary)
- [ ] Gmail integration (deal follow-up monitoring)
- [ ] Plaid integration (bank accounts, cash flow)
- [ ] Investment tracking (LEAPS, brokerage)
- [ ] Initiative tracking (cross-business goals)
- [ ] Behavioral pattern detection
- [ ] Content review agent (YouTube/X summaries)
- [ ] Voice interface

## Related Projects

- **Ordino** — GLE's project management platform
- **Beacon** — Ordino's CoS agent (building code RAG + operational tools)
- **CitiSignal** — NYC property monitoring
- **Venture Studio** — Portfolio management + AI Coach
- **ChargeRank** — EV charging site analysis
