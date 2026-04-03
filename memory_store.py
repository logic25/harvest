"""
Harvest Memory Store — persistent memory via Supabase with local fallback.
Replaces the /tmp JSON file approach that resets on Railway redeploy.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

import httpx

import config

log = logging.getLogger("harvest.memory")

# Local fallback path (used when Supabase is unreachable)
LOCAL_MEMORY_PATH = Path(config.MEMORY_FILE)


def _supabase_headers() -> dict:
    """Build headers for Supabase REST API calls."""
    return {
        "apikey": config.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _supabase_url(path: str) -> str:
    """Build full Supabase REST URL."""
    base = config.SUPABASE_URL.rstrip("/")
    return f"{base}/rest/v1/{path}"


def _is_supabase_configured() -> bool:
    """Check if Supabase credentials are available."""
    return bool(config.SUPABASE_URL and config.SUPABASE_SERVICE_KEY)


# ---------------------------------------------------------------------------
# Core CRUD
# ---------------------------------------------------------------------------

def load_memory(agent_id: str = "harvest") -> dict:
    """Load memory for an agent. Returns dict with conversations, patterns, context_journal."""
    if _is_supabase_configured():
        try:
            return _load_from_supabase(agent_id)
        except Exception as e:
            log.warning(f"Supabase load failed, falling back to local: {e}")

    return _load_from_local()


def save_memory(memory: dict, agent_id: str = "harvest"):
    """Save full memory object for an agent."""
    if _is_supabase_configured():
        try:
            _save_to_supabase(agent_id, memory)
            return
        except Exception as e:
            log.warning(f"Supabase save failed, falling back to local: {e}")

    _save_to_local(memory)


def append_conversation(agent_id: str, user_msg: str, assistant_msg: str):
    """Append a conversation to memory (convenience method)."""
    memory = load_memory(agent_id)
    memory.setdefault("conversations", []).append({
        "user": user_msg,
        "assistant": assistant_msg[:500],
        "timestamp": datetime.now().isoformat(),
    })
    # Keep last 50 conversations
    memory["conversations"] = memory["conversations"][-50:]
    save_memory(memory, agent_id)


def add_pattern(agent_id: str, pattern: str):
    """Record an observed behavioral pattern."""
    memory = load_memory(agent_id)
    memory.setdefault("patterns", []).append(pattern)
    memory["patterns"] = memory["patterns"][-20:]
    save_memory(memory, agent_id)


def add_context_entry(agent_id: str, note: str):
    """Add a context journal entry (decisions, relationships, etc)."""
    memory = load_memory(agent_id)
    memory.setdefault("context_journal", []).append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "note": note,
    })
    memory["context_journal"] = memory["context_journal"][-30:]
    save_memory(memory, agent_id)


# ---------------------------------------------------------------------------
# Supabase implementation
# ---------------------------------------------------------------------------

def _load_from_supabase(agent_id: str) -> dict:
    """Load memory from Supabase harvest_memory table."""
    url = _supabase_url("harvest_memory")
    params = {
        "agent_id": f"eq.{agent_id}",
        "order": "updated_at.desc",
        "limit": "1",
    }

    with httpx.Client(timeout=10) as client:
        resp = client.get(url, headers=_supabase_headers(), params=params)
        resp.raise_for_status()
        rows = resp.json()

    if not rows:
        # No memory yet — return empty structure
        return {"conversations": [], "patterns": [], "context_journal": []}

    content = rows[0].get("content", {})
    if isinstance(content, str):
        content = json.loads(content)

    return content


def _save_to_supabase(agent_id: str, memory: dict):
    """Upsert memory to Supabase harvest_memory table."""
    url = _supabase_url("harvest_memory")

    # Check if row exists
    check_params = {"agent_id": f"eq.{agent_id}", "select": "id"}
    with httpx.Client(timeout=10) as client:
        check = client.get(url, headers=_supabase_headers(), params=check_params)
        check.raise_for_status()
        existing = check.json()

    payload = {
        "agent_id": agent_id,
        "memory_type": "full",
        "content": memory,
        "updated_at": datetime.now().isoformat(),
    }

    headers = _supabase_headers()

    with httpx.Client(timeout=10) as client:
        if existing:
            # Update existing row
            row_id = existing[0]["id"]
            update_url = f"{url}?id=eq.{row_id}"
            resp = client.patch(update_url, headers=headers, json=payload)
        else:
            # Insert new row
            payload["created_at"] = datetime.now().isoformat()
            resp = client.post(url, headers=headers, json=payload)

        resp.raise_for_status()

    log.debug(f"Memory saved to Supabase for agent={agent_id}")


# ---------------------------------------------------------------------------
# Local file fallback
# ---------------------------------------------------------------------------

def _load_from_local() -> dict:
    """Load memory from local JSON file."""
    if LOCAL_MEMORY_PATH.exists():
        try:
            return json.loads(LOCAL_MEMORY_PATH.read_text())
        except Exception:
            pass
    return {"conversations": [], "patterns": [], "context_journal": []}


def _save_to_local(memory: dict):
    """Save memory to local JSON file."""
    try:
        LOCAL_MEMORY_PATH.write_text(json.dumps(memory, indent=2, default=str))
    except Exception as e:
        log.error(f"Failed to save local memory: {e}")
