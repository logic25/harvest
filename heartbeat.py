"""
Harvest Heartbeat — autonomous scheduled check-ins.
Sends proactive briefings to Manny via Telegram without being asked.
"""
import asyncio
import logging
from datetime import datetime

import telegram

import config
from agents import get_morning_briefing
from harvest import chat

log = logging.getLogger("harvest.heartbeat")


async def _send_telegram_message(text: str):
    """Send a message directly to Manny's Telegram chat (not via polling handler)."""
    if not config.TELEGRAM_TOKEN or not config.MANNY_CHAT_ID:
        log.warning("Cannot send heartbeat — TELEGRAM_TOKEN or MANNY_CHAT_ID not set")
        return

    bot = telegram.Bot(token=config.TELEGRAM_TOKEN)

    try:
        # Telegram has 4096 char limit
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await bot.send_message(
                    chat_id=config.MANNY_CHAT_ID,
                    text=chunk,
                    parse_mode="Markdown",
                )
        else:
            await bot.send_message(
                chat_id=config.MANNY_CHAT_ID,
                text=text,
                parse_mode="Markdown",
            )
        log.info("Heartbeat message sent successfully")
    except Exception as e:
        log.error(f"Failed to send heartbeat message: {e}")


def morning_briefing_job():
    """
    7:00 AM ET — Morning briefing.
    Gathers data from all connected systems, then has Claude synthesize
    into a prioritized daily action list.
    """
    log.info("Running morning briefing heartbeat...")

    try:
        # Create a new event loop for this thread (APScheduler runs in background thread)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Ask Claude to generate the morning briefing (uses the full agentic loop)
        prompt = (
            "Good morning. Give me the morning briefing. "
            "Check all connected systems and tell me what I should focus on today. "
            "Be specific — cite numbers, flag urgent items, and tell me who should handle what."
        )

        response = loop.run_until_complete(chat(prompt, user_id="heartbeat"))

        # Send via Telegram
        header = f"*Harvest Morning Briefing*\n_{datetime.now().strftime('%A, %B %d, %Y')}_\n\n"
        loop.run_until_complete(_send_telegram_message(header + response))

        loop.close()

    except Exception as e:
        log.error(f"Morning briefing failed: {e}", exc_info=True)


def midday_check_job():
    """
    12:00 PM ET — Midday check-in.
    Flags stale follow-ups and unanswered items.
    """
    log.info("Running midday check heartbeat...")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        prompt = (
            "Quick midday check. Anything urgent that came up since this morning? "
            "Any stale items or follow-ups I should handle before end of day?"
        )

        response = loop.run_until_complete(chat(prompt, user_id="heartbeat"))

        # Only send if there's something actionable (don't spam)
        if len(response) > 100:  # Skip generic "nothing new" responses
            header = "*Midday Check-In*\n\n"
            loop.run_until_complete(_send_telegram_message(header + response))

        loop.close()

    except Exception as e:
        log.error(f"Midday check failed: {e}", exc_info=True)


def weekly_summary_job():
    """
    Monday 8:00 AM ET — Weekly summary.
    Covers proposals, billing, bugs, deals, portfolio.
    """
    log.info("Running weekly summary heartbeat...")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        prompt = (
            "It's Monday morning. Give me the weekly summary. "
            "Cover: proposals sent/converted, billing trends, overdue invoices, "
            "any bugs or issues from last week, deal progress, and Blooms status. "
            "Compare to last week where possible."
        )

        response = loop.run_until_complete(chat(prompt, user_id="heartbeat"))

        header = f"*Weekly Summary*\n_{datetime.now().strftime('%B %d, %Y')}_\n\n"
        loop.run_until_complete(_send_telegram_message(header + response))

        loop.close()

    except Exception as e:
        log.error(f"Weekly summary failed: {e}", exc_info=True)


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
    )
    log.info("Scheduled: Weekly summary at 8:00 AM ET Mondays")
