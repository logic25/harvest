"""
Harvest Server — runs the Telegram bot + Flask health check.
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
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    log.info("Telegram bot started in background")

    # Start Flask for health check
    app.run(host="0.0.0.0", port=config.PORT)
