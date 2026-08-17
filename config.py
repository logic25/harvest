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

# Ordino Supabase auth — a real end-user JWT so beacon-data-proxy can derive
# profiles.company_id (REQUIRED once BEACON_PROXY_ALLOW_SHARED_SECRET_ONLY flips
# to 0). When these are unset, query_ordino falls back to shared-secret-only.
ORDINO_SUPABASE_URL = os.getenv("ORDINO_SUPABASE_URL", "https://mimlfjkisguktiqqkpkm.supabase.co")
ORDINO_ANON_KEY = os.getenv("ORDINO_ANON_KEY", "")          # Ordino public anon key (GoTrue login)
HARVEST_ORDINO_EMAIL = os.getenv("HARVEST_ORDINO_EMAIL", "")       # dedicated Harvest bot user
HARVEST_ORDINO_PASSWORD = os.getenv("HARVEST_ORDINO_PASSWORD", "")  # set in Railway (secret)

CITISIGNAL_API_URL = os.getenv("CITISIGNAL_API_URL", "")
CITISIGNAL_API_KEY = os.getenv("CITISIGNAL_API_KEY", "")

VENTURE_STUDIO_URL = os.getenv("VENTURE_STUDIO_URL", "")
VENTURE_STUDIO_KEY = os.getenv("VENTURE_STUDIO_KEY", "")

# Venture Studio Supabase (entity financials, tasks, initiatives for Blooms)
VS_SUPABASE_URL = os.getenv("VS_SUPABASE_URL", "")
VS_SUPABASE_KEY = os.getenv("VS_SUPABASE_KEY", "")

# Blooms OS Supabase (floral operations — orders, inventory, vendors)
BLOOMS_SUPABASE_URL = os.getenv("BLOOMS_SUPABASE_URL", "")
BLOOMS_SUPABASE_KEY = os.getenv("BLOOMS_SUPABASE_KEY", "")

# Supabase (shared memory store for Harvest + Blooms Agent)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Memory (local fallback if Supabase unavailable)
MEMORY_FILE = os.getenv("MEMORY_FILE", "/tmp/harvest_memory.json")

# Business roadmap Harvest reads for "what needs Manny" (the canonical list / COS decision queue)
ROADMAP_COS = os.getenv("ROADMAP_COS", "/Users/mannyrussell/OrdinoV2/docs/cos-operating-structure.md")
ROADMAP_CANONICAL = os.getenv("ROADMAP_CANONICAL", "/Users/mannyrussell/OrdinoV2/docs/roadmap-canonical.md")

# Heartbeat — Manny's Telegram chat ID for proactive messages
MANNY_CHAT_ID = os.getenv("MANNY_CHAT_ID", "")

PORT = int(os.getenv("PORT", "8080"))
