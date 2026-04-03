"""
Harvest Server — runs the Telegram bot (main thread) + Flask health check (background).
"""
import threading
import logging
from flask import Flask, jsonify

import config
from bot import run_bot

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("harvest.server")

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "service": "harvest",
        "status": "ok",
        "ordino_configured": bool(config.ORDINO_PROXY_URL),
        "citisignal_configured": bool(config.CITISIGNAL_API_URL),
        "telegram_configured": bool(config.TELEGRAM_TOKEN),
    })


if __name__ == "__main__":
    # Start Flask in background thread (health check only)
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=config.PORT, use_reloader=False),
        daemon=True,
    )
    flask_thread.start()
    log.info(f"Flask health check started on port {config.PORT}")

    # Run Telegram bot in main thread (needs signal handlers)
    run_bot()
