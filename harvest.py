"""
Harvest — Personal AI Chief of Staff
Main conversation handler using Claude with tools.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

import anthropic

import config
from agents import TOOLS, query_ordino, query_citisignal, get_morning_briefing
from memory_store import load_memory, save_memory, append_conversation

log = logging.getLogger("harvest")

# Load SOUL.md
SOUL_PATH = Path(__file__).parent / "soul.md"
SOUL = SOUL_PATH.read_text() if SOUL_PATH.exists() else ""


def build_system_prompt(memory: dict) -> str:
    """Build the system prompt from SOUL + memory + current context."""
    parts = [SOUL]

    # Add recent patterns from memory
    if memory.get("patterns"):
        parts.append("\n## Observed Patterns")
        for pattern in memory["patterns"][-5:]:
            parts.append(f"- {pattern}")

    # Add context journal entries
    if memory.get("context_journal"):
        parts.append("\n## Recent Context")
        for entry in memory["context_journal"][-10:]:
            parts.append(f"- [{entry.get('date', '?')}] {entry.get('note', '')}")

    parts.append(f"\n## Current Date/Time: {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}")

    return "\n\n".join(parts)


async def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result as a string."""
    log.info(f"Tool call: {tool_name}({json.dumps(tool_input)[:200]})")

    try:
        if tool_name == "query_ordino":
            result = await query_ordino(
                action=tool_input.get("action", "query_projects"),
                params=tool_input.get("params", {})
            )
        elif tool_name == "query_citisignal":
            result = await query_citisignal(tool_input.get("property_id", ""))
        elif tool_name == "get_morning_briefing":
            result = await get_morning_briefing()
            return result  # Already a string
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, indent=2, default=str)[:10000]
    except Exception as e:
        log.error(f"Tool execution error: {e}")
        return json.dumps({"error": str(e)})


async def chat(user_message: str, user_id: str = "manny") -> str:
    """Main conversation handler — sends message to Claude with tools."""
    memory = load_memory(agent_id="harvest")
    system_prompt = build_system_prompt(memory)

    client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

    messages = [{"role": "user", "content": user_message}]

    # Add recent conversation history for context
    recent = memory.get("conversations", [])[-6:]
    history = []
    for conv in recent:
        history.append({"role": "user", "content": conv.get("user", "")})
        history.append({"role": "assistant", "content": conv.get("assistant", "")})
    messages = history + messages

    # Agentic loop — Claude may call multiple tools
    max_rounds = 5
    for round_num in range(max_rounds):
        response = await client.messages.create(
            model=config.MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        # Check if Claude wants to use tools
        tool_calls = [b for b in response.content if b.type == "tool_use"]

        if not tool_calls:
            # No more tool calls — extract the text response
            text_parts = [b.text for b in response.content if hasattr(b, "text")]
            final_response = "\n".join(text_parts)

            # Save to memory (persistent via Supabase)
            append_conversation("harvest", user_message, final_response)

            return final_response

        # Execute tool calls
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_call in tool_calls:
            result = await handle_tool_call(tool_call.name, tool_call.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    return "I'm still processing — this question required more steps than expected. Can you simplify?"
