import os

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ALLOWED_USER_IDS = [int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()]

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
FAST_MODEL = "claude-haiku-4-5-20251001"

# Connected services
BEACON_URL = os.getenv("BEACON_URL", "")  # beaconrag.up.railway.app
BEACON_KEY = os.getenv("BEACON_KEY", "")

ORDINO_PROXY_URL = os.getenv("ORDINO_PROXY_URL", "")  # Supabase edge function URL
ORDINO_PROXY_KEY = os.getenv("ORDINO_PROXY_KEY", "")  # BEACON_ANALYTICS_KEY

CITISIGNAL_API_URL = os.getenv("CITISIGNAL_API_URL", "")
CITISIGNAL_API_KEY = os.getenv("CITISIGNAL_API_KEY", "")

VENTURE_STUDIO_URL = os.getenv("VENTURE_STUDIO_URL", "")
VENTURE_STUDIO_KEY = os.getenv("VENTURE_STUDIO_KEY", "")

# Memory
MEMORY_FILE = os.getenv("MEMORY_FILE", "/tmp/harvest_memory.json")

PORT = int(os.getenv("PORT", "8080"))
