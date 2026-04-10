"""
Harvest Heartbeat — autonomous scheduled check-ins.
Sends proactive briefings to Manny via Telegram without being asked.
"""
import asyncio
import logging
import traceback
from datetime import datetime

import httpx
import telegram
import telegram.error

import config
from agents import get_morning_briefing

log = logging.getLogger("harvest.heartbeat")


def _send_sync(text: str):
    """Send a Telegram message synchronously using httpx (no async/event loop issues)."""
    if not config.TELEGRAM_TOKEN or not config.MANNY_CHAT_ID:
        log.warning("Cannot send heartbeat — TELEGRAM_TOKEN or MANNY_CHAT_ID not set")
        return False

    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"

    # Split long messages
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] if len(text) > 4000 else [text]

    for chunk in chunks:
        # Try Markdown first, fall back to plain text if it fails
        for parse_mode in ["Markdown", None]:
            try:
                resp = httpx.post(url, json={
                    "chat_id": config.MANNY_CHAT_ID,
                    "text": chunk,
                    "parse_mode": parse_mode,
                }, timeout=30)

                data = resp.json()
                if data.get("ok"):
                    if parse_mode is None:
                        log.info("Sent as plain text (Markdown failed)")
                    break  # Success, move to next chunk
                else:
                    error_desc = data.get("description", "unknown")
                    if "parse" in error_desc.lower() and parse_mode == "Markdown":
                        log.warning(f"Markdown parse failed, retrying as plain text: {error_desc}")
                        continue  # Try without Markdown
                    else:
                        log.error(f"Telegram API error: {error_desc}")
                        return False
            except Exception as e:
                log.error(f"Failed to send chunk: {e}")
                if parse_mode is None:
                    return False  # Both attempts failed

    log.info("Heartbeat message sent successfully")
    return True


def _run_chat_sync(prompt: str) -> str:
    """Run the async chat function synchronously in a fresh event loop."""
    # Import here to avoid circular imports at module load time
    from harvest import chat

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(chat(prompt, user_id="heartbeat"))
    finally:
        loop.close()


def _get_raw_briefing_sync() -> str:
    """Get raw briefing data synchronously (no Claude, just data)."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(get_morning_briefing())
    finally:
        loop.close()


def morning_briefing_job():
    """
    7:00 AM ET — Morning briefing.
    Gathers data from all connected systems, then has Claude synthesize
    into a prioritized daily action list.
    Falls back to raw data if Claude fails.
    """
    log.info("=== MORNING BRIEFING HEARTBEAT STARTING ===")
    today = datetime.now().strftime("%A, %B %d, %Y")

    try:
        # Try the full Claude-powered briefing
        prompt = (
            "Good morning. Give me the morning briefing. "
            "Check all connected systems and tell me what I should focus on today. "
            "Be specific — cite numbers, flag urgent items, and tell me who should handle what."
        )

        response = _run_chat_sync(prompt)
        header = f"Harvest Morning Briefing\n{today}\n\n"
        sent = _send_sync(header + response)

        if sent:
            log.info("=== MORNING BRIEFING SENT SUCCESSFULLY ===")
        else:
            log.error("=== MORNING BRIEFING SEND FAILED ===")
            # Try raw data fallback
            _send_fallback_briefing(today)

    except Exception as e:
        log.error(f"=== MORNING BRIEFING CLAUDE FAILED: {e} ===")
        log.error(traceback.format_exc())
        # Fall back to raw data briefing
        _send_fallback_briefing(today)


def _send_fallback_briefing(today: str):
    """Send a simple data-only briefing if Claude fails."""
    log.info("Attempting fallback briefing (raw data, no Claude)...")
    try:
        raw_data = _get_raw_briefing_sync()
        fallback_msg = (
            f"Harvest Morning Briefing (simplified)\n"
            f"{today}\n\n"
            f"Note: Full AI briefing failed. Here's the raw data:\n\n"
            f"{raw_data}\n\n"
            f"(Claude was unavailable — will try full briefing tomorrow)"
        )
        sent = _send_sync(fallback_msg)
        if sent:
            log.info("Fallback briefing sent")
        else:
            # Last resort — just tell Manny something broke
            _send_sync(
                f"Harvest Heartbeat Alert\n{today}\n\n"
                "Morning briefing failed. Both Claude and raw data encountered errors. "
                "Text me directly to check if I'm working."
            )
    except Exception as e2:
        log.error(f"Fallback briefing also failed: {e2}")
        # Absolute last resort
        try:
            _send_sync(
                f"Harvest is having issues this morning ({today}). "
                "Text me directly to see if I can respond."
            )
        except Exception:
            log.error("ALL send attempts failed. Heartbeat is broken.")


def midday_check_job():
    """
    12:00 PM ET — Midday check-in (weekdays).
    Flags stale follow-ups and unanswered items.
    """
    log.info("=== MIDDAY CHECK HEARTBEAT STARTING ===")

    try:
        prompt = (
            "Quick midday check. Anything urgent that came up since this morning? "
            "Any stale items or follow-ups I should handle before end of day?"
        )

        response = _run_chat_sync(prompt)

        # Only send if there's something actionable
        if len(response) > 100:
            header = "Midday Check-In\n\n"
            _send_sync(header + response)
            log.info("=== MIDDAY CHECK SENT ===")
        else:
            log.info("=== MIDDAY CHECK SKIPPED (nothing actionable) ===")

    except Exception as e:
        log.error(f"=== MIDDAY CHECK FAILED: {e} ===")
        log.error(traceback.format_exc())


def weekly_summary_job():
    """
    Monday 8:00 AM ET — Weekly summary.
    Covers proposals, billing, bugs, deals, portfolio.
    """
    log.info("=== WEEKLY SUMMARY HEARTBEAT STARTING ===")
    today = datetime.now().strftime("%B %d, %Y")

    try:
        prompt = (
            "It's Monday morning. Give me the weekly summary. "
            "Cover: proposals sent/converted, billing trends, overdue invoices, "
            "any bugs or issues from last week, deal progress, and Blooms status. "
            "Compare to last week where possible."
        )

        response = _run_chat_sync(prompt)
        header = f"Weekly Summary — {today}\n\n"
        _send_sync(header + response)
        log.info("=== WEEKLY SUMMARY SENT ===")

    except Exception as e:
        log.error(f"=== WEEKLY SUMMARY FAILED: {e} ===")
        log.error(traceback.format_exc())


def setup_heartbeat(scheduler):
    """
    Register all heartbeat jobs with the APScheduler instance.
    Called from server.py during startup.
    """
    # Morning briefing — every day at 7:00 AM ET
    scheduler.add_job(
        morning_briefing_job,
        "cron",
        hour=7,
        minute=0,
        timezone="US/Eastern",
        id="morning_briefing",
        name="Morning Briefing",
        replace_existing=True,
        misfire_grace_time=3600,  # Allow up to 1 hour late if service was down
    )
    log.info("Scheduled: Morning briefing at 7:00 AM ET daily")

    # Midday check — weekdays at 12:00 PM ET
    scheduler.add_job(
        midday_check_job,
        "cron",
        hour=12,
        minute=0,
        day_of_week="mon-fri",
        timezone="US/Eastern",
        id="midday_check",
        name="Midday Check-In",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    log.info("Scheduled: Midday check at 12:00 PM ET weekdays")

    # Weekly summary — Monday at 8:00 AM ET
    scheduler.add_job(
        weekly_summary_job,
        "cron",
        hour=8,
        minute=0,
        day_of_week="mon",
        timezone="US/Eastern",
        id="weekly_summary",
        name="Weekly Summary",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    log.info("Scheduled: Weekly summary at 8:00 AM ET Mondays")
