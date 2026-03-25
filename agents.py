"""
Harvest Sub-Agents — each queries a specific domain and returns structured data.
The CoS (main LLM) decides which agents to call based on the question.
"""
import httpx
import json
import logging
from datetime import datetime

import config

log = logging.getLogger("harvest.agents")


async def query_ordino(action: str, params: dict = None) -> dict:
    """Query Ordino's data via the beacon-data-proxy edge function."""
    if not config.ORDINO_PROXY_URL or not config.ORDINO_PROXY_KEY:
        return {"error": "Ordino not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                config.ORDINO_PROXY_URL,
                json={"action": action, "params": params or {}},
                headers={
                    "x-beacon-key": config.ORDINO_PROXY_KEY,
                    "Content-Type": "application/json",
                },
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

    # TODO: Add Deal Agent (Gmail monitoring for stale follow-ups)
    # TODO: Add Investment Agent (LEAPS positions, hold periods)
    # TODO: Add Cash Flow Agent (Plaid transactions, anomalies)
    # TODO: Add Venture Studio (portfolio scoring, focus priorities)

    if not briefing_parts:
        return "Could not retrieve data from connected systems. Check configurations."

    return "\n".join(briefing_parts)


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
