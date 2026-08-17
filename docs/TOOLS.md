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

### Blooms in Bunches — Venture Studio
**Status:** CONNECTED (via Venture Studio Supabase)
**What Harvest can query:**
- `get_financials` — Revenue TTM, EBITDA, annual expenses, yearly financials (revenue, profit, owner salary)
- `get_tasks` — Initiative tracker (50-task quarterly plan), status, priorities, due dates
- `get_expenses` — Recurring and one-off expenses by category and date range
- `get_valuation` — Valuation history (low/mid/high range, methodology)
- `discover_schema` — List all tables and columns
- `query_table` — General query against any table

**Proxy:** Direct Supabase REST API (PostgREST)
**Auth:** `apikey` + `Authorization: Bearer` headers
**Env vars:** `VS_SUPABASE_URL`, `VS_SUPABASE_KEY`

**Baselines (Crockett Myers 2025):** Revenue $842K, COGS 42.9% (target 34.4%), profit $41.7K

### Blooms in Bunches — Blooms OS
**Status:** PLANNED (Supabase project exists, tables not yet populated)
**What it will provide:**
- Product catalog, recipes, flower library
- Daily orders, vendor orders, delivery tracking
- Cooler inventory, shopping lists
- Production planning for events

**Env vars:** `BLOOMS_SUPABASE_URL`, `BLOOMS_SUPABASE_KEY`

### Google Sheets
**Status:** NOT CONNECTED
**What it would provide:**
- 20 years of household expense history
- Blooms quarterly tracker (50 tasks)
