# Tools — Harvest Connected Systems

## Live Connections

### Ordino (via beacon-data-proxy)
**Status:** CONNECTED
**What Harvest can query:**
- `query_projects` — Active projects, status, assigned PM
- `query_project_detail` — Single project deep dive
- `query_proposals` — Pipeline, conversion, values
- `query_invoices` — Outstanding, overdue, aging
- `query_pm_workload` — Active projects per PM
- `check_filing_readiness` — Filing completion percentage
- `query_ordino` — General query against any of 113 tables

**Proxy:** Supabase edge function `beacon-data-proxy`
**Auth:** `x-beacon-key` header

### CitiSignal (via API gateway)
**Status:** CONNECTED
**What Harvest can query:**
- Property violations, compliance scores
- DOB applications, complaints
- BIS data (vacate orders, restrictions)

**Proxy:** Supabase edge function `api-gateway`
**Auth:** Bearer token

## Planned Connections

### Gmail
**Status:** NOT CONNECTED
**What it would provide:**
- Deal communications monitoring
- Follow-up tracking (stale emails)
- Draft responses with approval gates

### Venture Studio
**Status:** NOT CONNECTED (URL/key configured but no tools built)
**What it would provide:**
- Portfolio scoring (62 ventures)
- Deal pipeline status
- AI Coach interactions

### Plaid
**Status:** NOT CONNECTED
**What it would provide:**
- Bank account balances across all entities
- Transaction monitoring, cash flow
- Expense anomaly detection

### ThinkorSwim / Brokerage
**Status:** NOT CONNECTED
**What it would provide:**
- LEAPS positions, Greeks, cost basis
- Hold period tracking with alerts
- V3 framework compliance

### Blooms in Bunches
**Status:** EMBEDDED KNOWLEDGE ONLY (no live data connection)
**What Harvest knows:**
- Revenue, COGS, financial targets (from Crockett Myers analysis in SOUL.md)
- Team structure, operational challenges
- Growth plan and initiative status

**Future:** Connect to Blooms OS Supabase for live data (orders, inventory, revenue)

### Google Sheets
**Status:** NOT CONNECTED
**What it would provide:**
- 20 years of household expense history
- Blooms quarterly tracker (50 tasks)
