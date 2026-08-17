"""
Harvest Sub-Agents — each queries a specific domain and returns structured data.
The CoS (main LLM) decides which agents to call based on the question.
"""
import httpx
import json
import logging
import os
import re
from datetime import datetime

import config

log = logging.getLogger("harvest.agents")

# Cache for Blooms entity ID (looked up once, reused)
_blooms_entity_id: str | None = None


def read_roadmap_priorities() -> list[str]:
    """Read the canonical COS decision queue so the morning brief surfaces 'what needs Manny'
    straight from the business roadmap. Read-only; fails soft if the file isn't reachable."""
    cos = getattr(config, "ROADMAP_COS", "")
    out: list[str] = []
    try:
        if cos and os.path.exists(cos):
            m = re.search(r"decision queue.*?\n(.*?)(?:\n##|\Z)", open(cos).read(), re.S | re.I)
            if m:
                for line in m.group(1).splitlines():
                    mm = re.match(r"^\d+\.\s*(.+)", line.strip())
                    if mm:
                        out.append(re.sub(r"\*\*", "", mm.group(1)).strip())
    except Exception as e:
        log.warning(f"roadmap read failed: {e}")
    return out


# ── Ordino JWT (identifies Harvest as the GLE company to beacon-data-proxy) ──
# Cached access token so we don't log in on every call. Supabase access tokens
# are ~1h; we refresh a little early.
_ordino_jwt: dict = {"token": None, "exp": 0.0}


async def _get_ordino_jwt() -> str | None:
    """Log into Ordino's Supabase as the Harvest bot user (GoTrue password grant),
    cache the access token, refresh near expiry. Returns None (→ shared-secret-only
    fallback) when the bot creds aren't configured."""
    import time
    if not (config.ORDINO_SUPABASE_URL and config.ORDINO_ANON_KEY
            and config.HARVEST_ORDINO_EMAIL and config.HARVEST_ORDINO_PASSWORD):
        return None
    now = time.time()
    if _ordino_jwt["token"] and now < _ordino_jwt["exp"] - 120:  # 2-min skew
        return _ordino_jwt["token"]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{config.ORDINO_SUPABASE_URL}/auth/v1/token?grant_type=password",
                headers={"apikey": config.ORDINO_ANON_KEY, "Content-Type": "application/json"},
                json={"email": config.HARVEST_ORDINO_EMAIL,
                      "password": config.HARVEST_ORDINO_PASSWORD},
            )
        if resp.status_code != 200:
            log.error(f"Ordino JWT login failed {resp.status_code}: {resp.text[:160]}")
            return None
        data = resp.json()
        _ordino_jwt["token"] = data.get("access_token")
        _ordino_jwt["exp"] = now + float(data.get("expires_in", 3600))
        return _ordino_jwt["token"]
    except Exception as e:
        log.error(f"Ordino JWT login error: {e}")
        return None


async def query_ordino(action: str, params: dict = None) -> dict:
    """Query Ordino's data via the beacon-data-proxy edge function."""
    if not config.ORDINO_PROXY_URL or not config.ORDINO_PROXY_KEY:
        return {"error": "Ordino not configured"}

    headers = {
        "x-beacon-key": config.ORDINO_PROXY_KEY,
        "Content-Type": "application/json",
    }
    # Forward a real Supabase JWT so the proxy derives company_id (required once
    # BEACON_PROXY_ALLOW_SHARED_SECRET_ONLY is off). If unset, no header is added
    # and the proxy uses the legacy shared-secret path (works while the flag is 1).
    jwt = await _get_ordino_jwt()
    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                config.ORDINO_PROXY_URL,
                json={"action": action, "params": params or {}},
                headers=headers,
            )
            if resp.status_code != 200:
                return {"error": f"Ordino returned {resp.status_code}: {resp.text[:200]}"}
            return resp.json()
    except Exception as e:
        log.error(f"Ordino query error: {e}")
        return {"error": str(e)}


async def query_citisignal(property_id: str) -> dict:
    """Query CitiSignal for property intelligence."""
    if not config.CITISIGNAL_API_URL or not config.CITISIGNAL_API_KEY:
        return {"error": "CitiSignal not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{config.CITISIGNAL_API_URL}?path=properties/{property_id}/full-sync",
                headers={
                    "Authorization": f"Bearer {config.CITISIGNAL_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            return resp.json()
    except Exception as e:
        log.error(f"CitiSignal query error: {e}")
        return {"error": str(e)}


async def get_morning_briefing() -> str:
    """Gather data from all connected systems for the morning briefing."""
    briefing_parts = []

    # 1. Business operations (Ordino)
    projects = await query_ordino("query_projects", {"status": "active"})
    invoices = await query_ordino("query_invoices", {"status": "overdue"})
    proposals = await query_ordino("query_proposals")
    readiness = await query_ordino("check_filing_readiness")
    pm_workload = await query_ordino("query_pm_workload")

    if not projects.get("error"):
        data = projects.get("data", [])
        briefing_parts.append(f"BUSINESS (GLE):\n- {len(data)} active projects")

    if not invoices.get("error"):
        inv_data = invoices.get("data", {})
        outstanding = inv_data.get("outstanding_total", 0)
        invoice_list = inv_data.get("invoices", [])
        overdue = [i for i in invoice_list if i.get("status") == "overdue"]
        if overdue:
            briefing_parts.append(
                f"- ⚠️ {len(overdue)} overdue invoices (${outstanding:,.0f}). "
                f"Has Sai followed up on the oldest ones?"
            )

    if not proposals.get("error"):
        prop_data = proposals.get("data", {})
        pipeline = prop_data.get("total_pipeline_value", 0)
        proposals_list = prop_data.get("proposals", [])
        # Count this month
        now = datetime.utcnow()
        this_month = [p for p in proposals_list
                      if p.get("created_at", "")[:7] == now.strftime("%Y-%m")]
        briefing_parts.append(
            f"- {len(this_month)} proposals sent this month. Pipeline: ${pipeline:,.0f}"
        )

    if not readiness.get("error"):
        ready_data = readiness.get("data", [])
        ready = [r for r in ready_data if r.get("readiness_pct", 0) == 100]
        nearly = [r for r in ready_data if 80 <= r.get("readiness_pct", 0) < 100]
        if ready:
            names = ", ".join(r.get("name", "?")[:30] for r in ready[:3])
            briefing_parts.append(f"- {len(ready)} projects ready to file: {names}")
        if nearly:
            briefing_parts.append(f"- {len(nearly)} projects nearly ready (80%+)")

    if not pm_workload.get("error"):
        pm_data = pm_workload.get("data", [])
        for pm in pm_data[:4]:
            if pm.get("active_projects", 0) > 0:
                briefing_parts.append(
                    f"  {pm['name']}: {pm['active_projects']} active projects"
                )

    # 2. Blooms in Bunches (Venture Studio)
    try:
        vs_ok = bool(config.VS_SUPABASE_URL and config.VS_SUPABASE_KEY)
        if vs_ok:
            entity_id = await _get_blooms_entity_id()
            if entity_id:
                # Entity overview
                entity_data = await _blooms_supabase_get(
                    "venture_studio", "entities",
                    {
                        "id": f"eq.{entity_id}",
                        "select": "revenue_ttm,ebitda,annual_expenses,status",
                    },
                )
                entity = (entity_data.get("data") or [{}])[0]

                blooms_parts = []
                rev = entity.get("revenue_ttm")
                if rev:
                    blooms_parts.append(f"- Revenue TTM: ${rev:,.0f}")
                ebitda = entity.get("ebitda")
                if ebitda:
                    blooms_parts.append(f"- EBITDA: ${ebitda:,.0f}")
                expenses = entity.get("annual_expenses")
                if expenses and rev:
                    cogs_pct = (expenses / rev * 100) if rev > 0 else 0
                    flag = ""
                    if cogs_pct > 45:
                        flag = " — URGENT: dangerously high"
                    elif cogs_pct > 40:
                        flag = " — WARNING: above 40% target"
                    blooms_parts.append(
                        f"- Expenses/Revenue ratio: {cogs_pct:.1f}%{flag}"
                    )

                # Overdue tasks
                tasks_data = await _blooms_supabase_get(
                    "venture_studio", "tasks",
                    {
                        "or": f"(entity_id.eq.{entity_id})",
                        "status": "eq.todo",
                        "due_date": f"lt.{datetime.utcnow().strftime('%Y-%m-%d')}",
                        "select": "title,due_date,priority",
                        "limit": "5",
                    },
                )
                overdue = tasks_data.get("data", [])
                if overdue:
                    blooms_parts.append(
                        f"- ⚠️ {len(overdue)} overdue Blooms tasks"
                    )
                    for t in overdue[:3]:
                        blooms_parts.append(
                            f"  → {t.get('title', '?')} (due {t.get('due_date', '?')})"
                        )

                if blooms_parts:
                    briefing_parts.append("BLOOMS IN BUNCHES:\n" + "\n".join(blooms_parts))
    except Exception as e:
        log.warning(f"Blooms briefing section failed: {e}")

    # TODO: Add Deal Agent (Gmail monitoring for stale follow-ups)
    # TODO: Add Investment Agent (LEAPS positions, hold periods)
    # TODO: Add Cash Flow Agent (Plaid transactions, anomalies)
    # TODO: Add Venture Studio (portfolio scoring, focus priorities)

    # Roadmap — what actually needs Manny, straight from the canonical COS decision queue
    try:
        decisions = read_roadmap_priorities()
        if decisions:
            lines = "\n".join(f"- {d}" for d in decisions)
            briefing_parts.append(f"NEEDS YOU (from your roadmap):\n{lines}")
    except Exception as e:
        log.warning(f"roadmap section failed: {e}")

    if not briefing_parts:
        return "Could not retrieve data from connected systems. Check configurations."

    return "\n".join(briefing_parts)


async def _blooms_supabase_get(
    source: str, table: str, params: dict = None
) -> dict:
    """Shared helper to query either Venture Studio or Blooms OS Supabase."""
    if source == "blooms_os":
        base_url = config.BLOOMS_SUPABASE_URL
        key = config.BLOOMS_SUPABASE_KEY
    else:
        base_url = config.VS_SUPABASE_URL
        key = config.VS_SUPABASE_KEY

    if not base_url or not key:
        return {"error": f"Blooms {source} Supabase not configured"}

    url = f"{base_url.rstrip('/')}/rest/v1/{table}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params=params or {})
            if resp.status_code != 200:
                return {"error": f"Supabase returned {resp.status_code}: {resp.text[:200]}"}
            return {"data": resp.json()}
    except Exception as e:
        log.error(f"Blooms Supabase query error ({source}/{table}): {e}")
        return {"error": str(e)}


async def _get_blooms_entity_id() -> str | None:
    """Look up and cache the Blooms entity UUID from Venture Studio."""
    global _blooms_entity_id
    if _blooms_entity_id:
        return _blooms_entity_id

    result = await _blooms_supabase_get(
        "venture_studio", "entities",
        {"name": "eq.Blooms", "select": "id", "limit": "1"},
    )
    rows = result.get("data", [])
    if rows:
        _blooms_entity_id = rows[0]["id"]
        log.info(f"Blooms entity ID: {_blooms_entity_id}")
    return _blooms_entity_id


async def query_blooms(action: str, params: dict = None) -> dict:
    """Query Blooms data from Venture Studio or Blooms OS Supabase."""
    params = params or {}

    # Check at least one source is configured
    vs_ok = bool(config.VS_SUPABASE_URL and config.VS_SUPABASE_KEY)
    bos_ok = bool(config.BLOOMS_SUPABASE_URL and config.BLOOMS_SUPABASE_KEY)
    if not vs_ok and not bos_ok:
        return {"error": "No Blooms Supabase connections configured"}

    try:
        if action == "discover_schema":
            source = params.get("source", "venture_studio")
            if source == "blooms_os" and not bos_ok:
                return {"error": "Blooms OS Supabase not configured"}
            if source == "venture_studio" and not vs_ok:
                return {"error": "Venture Studio Supabase not configured"}

            base_url = (config.BLOOMS_SUPABASE_URL if source == "blooms_os"
                        else config.VS_SUPABASE_URL)
            key = (config.BLOOMS_SUPABASE_KEY if source == "blooms_os"
                   else config.VS_SUPABASE_KEY)

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{base_url.rstrip('/')}/rest/v1/",
                    headers={
                        "apikey": key,
                        "Authorization": f"Bearer {key}",
                    },
                )
                if resp.status_code != 200:
                    return {"error": f"Schema discovery failed: {resp.status_code}"}

                spec = resp.json()
                # Extract table names and their columns from OpenAPI spec
                tables = {}
                definitions = spec.get("definitions", {})
                for table_name, table_def in definitions.items():
                    props = table_def.get("properties", {})
                    tables[table_name] = list(props.keys())

                return {"source": source, "tables": tables}

        elif action == "query_table":
            source = params.get("source", "venture_studio")
            table = params.get("table")
            if not table:
                return {"error": "query_table requires 'table' param"}

            query_params = {}
            if params.get("select"):
                query_params["select"] = params["select"]
            if params.get("order"):
                query_params["order"] = params["order"]
            if params.get("limit"):
                query_params["limit"] = str(params["limit"])
            else:
                query_params["limit"] = "50"

            # Apply filters
            for col, filt in (params.get("filters") or {}).items():
                query_params[col] = filt

            return await _blooms_supabase_get(source, table, query_params)

        elif action == "get_financials":
            if not vs_ok:
                return {"error": "Venture Studio Supabase not configured"}

            entity_id = await _get_blooms_entity_id()
            if not entity_id:
                return {"error": "Blooms entity not found in Venture Studio"}

            # Get entity overview
            entity_result = await _blooms_supabase_get(
                "venture_studio", "entities",
                {
                    "id": f"eq.{entity_id}",
                    "select": "name,revenue_ttm,ebitda,annual_expenses,budget,spent,"
                              "add_backs,prev_quarter_value,status,employees,"
                              "owner_involvement",
                },
            )

            # Get yearly financials
            fin_params = {
                "entity_id": f"eq.{entity_id}",
                "select": "year,revenue,net_profit,owner_salary,one_time_expenses,"
                          "non_recurring_costs,interest,taxes,depreciation,amortization",
                "order": "year.desc",
            }
            if params.get("year"):
                fin_params["year"] = f"eq.{params['year']}"

            financials_result = await _blooms_supabase_get(
                "venture_studio", "entity_financials", fin_params,
            )

            return {
                "entity": (entity_result.get("data") or [None])[0],
                "financials": financials_result.get("data", []),
                "error": entity_result.get("error") or financials_result.get("error"),
            }

        elif action == "get_tasks":
            if not vs_ok:
                return {"error": "Venture Studio Supabase not configured"}

            entity_id = await _get_blooms_entity_id()
            if not entity_id:
                return {"error": "Blooms entity not found in Venture Studio"}

            # First find projects for this entity
            proj_result = await _blooms_supabase_get(
                "venture_studio", "projects",
                {
                    "entity_id": f"eq.{entity_id}",
                    "select": "id,name,status,phase",
                },
            )
            project_ids = [p["id"] for p in proj_result.get("data", [])]

            if not project_ids:
                # Try tasks with direct entity_id
                task_params = {
                    "entity_id": f"eq.{entity_id}",
                    "select": "id,title,status,priority,due_date,category,"
                              "completed,completed_date",
                    "order": "due_date.asc.nullslast",
                    "limit": "50",
                }
            else:
                # Tasks belong to projects
                pid_list = ",".join(project_ids)
                task_params = {
                    "project_id": f"in.({pid_list})",
                    "select": "id,title,status,priority,due_date,category,"
                              "completed,completed_date,project_id",
                    "order": "due_date.asc.nullslast",
                    "limit": "50",
                }

            if params.get("status"):
                task_params["status"] = f"eq.{params['status']}"
            if params.get("priority"):
                task_params["priority"] = f"eq.{params['priority']}"

            tasks_result = await _blooms_supabase_get(
                "venture_studio", "tasks", task_params,
            )

            return {
                "projects": proj_result.get("data", []),
                "tasks": tasks_result.get("data", []),
                "error": tasks_result.get("error"),
            }

        elif action == "get_expenses":
            if not vs_ok:
                return {"error": "Venture Studio Supabase not configured"}

            entity_id = await _get_blooms_entity_id()
            if not entity_id:
                return {"error": "Blooms entity not found in Venture Studio"}

            exp_params = {
                "entity_id": f"eq.{entity_id}",
                "select": "id,description,amount,category,expense_date,"
                          "is_recurring,recurring_frequency,notes",
                "order": "expense_date.desc",
                "limit": "50",
            }
            if params.get("start_date"):
                exp_params["expense_date"] = f"gte.{params['start_date']}"
            if params.get("end_date"):
                exp_params["expense_date"] = f"lte.{params['end_date']}"
            if params.get("category"):
                exp_params["category"] = f"eq.{params['category']}"

            return await _blooms_supabase_get(
                "venture_studio", "entity_expenses", exp_params,
            )

        elif action == "get_valuation":
            if not vs_ok:
                return {"error": "Venture Studio Supabase not configured"}

            entity_id = await _get_blooms_entity_id()
            if not entity_id:
                return {"error": "Blooms entity not found in Venture Studio"}

            return await _blooms_supabase_get(
                "venture_studio", "entity_valuations",
                {
                    "entity_id": f"eq.{entity_id}",
                    "select": "valuation_date,valuation_low,valuation_mid,"
                              "valuation_high,multiple_used,methodology,notes",
                    "order": "valuation_date.desc",
                    "limit": "10",
                },
            )

        else:
            return {"error": f"Unknown blooms action: {action}"}

    except Exception as e:
        log.error(f"Blooms query error: {e}")
        return {"error": str(e)}


# Tool definitions for Claude
TOOLS = [
    {
        "name": "query_ordino",
        "description": "Query Ordino (GLE's project management system) for business data. "
                       "Available actions: query_projects, query_project_detail, query_proposals, "
                       "query_invoices, query_property_violations, query_pm_workload, "
                       "check_filing_readiness, query_ordino (general query for any table).",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to perform. Use 'query_ordino' for general queries "
                                   "with table/select/filters params."
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the action. For query_ordino: {table, select, filters, limit}. "
                                   "For others: {status, search, project_id, address, pm_name, etc.}"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "query_citisignal",
        "description": "Query CitiSignal for NYC property intelligence — violations, applications, "
                       "compliance scores, vacate orders, building data. Provide property_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type": "string",
                    "description": "The CitiSignal property UUID"
                }
            },
            "required": ["property_id"]
        }
    },
    {
        "name": "query_blooms",
        "description": "Query Blooms in Bunches business data. Two data sources: "
                       "'venture_studio' has financials, tasks, expenses, valuations; "
                       "'blooms_os' has floral operations (when available). "
                       "Actions: discover_schema (list tables/columns), "
                       "query_table (general query with table/select/filters/order/limit), "
                       "get_financials (revenue, profit, EBITDA — compare to baselines: "
                       "$842K revenue, 42.9% COGS vs 34.4% target), "
                       "get_tasks (initiative tracker — 50-task quarterly plan), "
                       "get_expenses (recurring and one-off costs), "
                       "get_valuation (valuation history low/mid/high).",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to perform.",
                    "enum": [
                        "discover_schema",
                        "query_table",
                        "get_financials",
                        "get_tasks",
                        "get_expenses",
                        "get_valuation",
                    ],
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the action. "
                                   "discover_schema: {source}. "
                                   "query_table: {source, table, select, filters, order, limit}. "
                                   "get_financials: {year}. "
                                   "get_tasks: {status, priority}. "
                                   "get_expenses: {start_date, end_date, category}. "
                                   "get_valuation: no params needed.",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "get_morning_briefing",
        "description": "Get a comprehensive morning briefing from all connected systems. "
                       "Covers: active projects, overdue invoices, proposals, filing readiness, "
                       "PM workload. Call this when Manny asks 'what should I focus on' or "
                       "'good morning' or 'what's happening today'.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]
