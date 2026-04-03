"""
Harvest Server — runs the Telegram bot (main thread) + Flask health check (background)
+ APScheduler heartbeat (background).
"""
import threading
import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

import config
from bot import run_bot
from heartbeat import setup_heartbeat

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("harvest.server")

app = Flask(__name__)

# Heartbeat scheduler (runs in background thread)
scheduler = BackgroundScheduler(timezone="US/Eastern")


@app.route("/health")
def health():
    heartbeat_jobs = [
        {"id": job.id, "name": job.name, "next_run": str(job.next_run_time)}
        for job in scheduler.get_jobs()
    ]
    return jsonify({
        "service": "harvest",
        "status": "ok",
        "ordino_configured": bool(config.ORDINO_PROXY_URL),
        "citisignal_configured": bool(config.CITISIGNAL_API_URL),
        "telegram_configured": bool(config.TELEGRAM_TOKEN),
        "heartbeat_configured": bool(config.MANNY_CHAT_ID),
        "heartbeat_jobs": heartbeat_jobs,
    })


if __name__ == "__main__":
    # Start heartbeat scheduler (background thread)
    setup_heartbeat(scheduler)
    scheduler.start()
    log.info("Heartbeat scheduler started")

    # Start Flask in background thread (health check only)
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=config.PORT, use_reloader=False),
        daemon=True,
    )
    flask_thread.start()
    log.info(f"Flask health check started on port {config.PORT}")

    # Run Telegram bot in main thread (needs signal handlers)
    run_bot()
