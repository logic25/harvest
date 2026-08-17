# HARVEST_CANONICAL — Amendments Log

*Per Rule Zero: proposals arrive as **numbered amendments citing specific sections**, never as a replacement doc. Fold these into the master when it's reconciled onto disk. Each accepted amendment also updates the master's Changelog.*

---

## Amendment 1 (2026-08-17) — Connection Registry + Connect/Disconnect UI; Memory Severability

**Cites:** §4.6 (Office independence), §4.7 (Office lifecycle), §4.9 (Severability & deal posture), §4.8 (Registry ownership distinction), §4.1 (Scoped memory), §6 (Current State), §7 (Roadmap).

**Origin:** 2026-08-17 session. Two capabilities the governing invariants already *require* but that are not yet built. Surfaced while wiring the Ordino JWT (each system = its own revocable credential) and reasoning about selling GLE/Ordino.

### 1.1 — Connection Registry + Connect/Disconnect UI  *(promotes §4.7 from concept to a committed build)*
Today each Office's connection is an env var + credential scattered across services (`ORDINO_*`, `BLOOMS_SUPABASE_*`, `CITISIGNAL_*` …). There is no single place to see or sever them. Amendment: build a **Connection Registry** — one authoritative, Plaid-style view of every Office connection, individually revocable, where revoking one never corrupts another (§4.6/§4.7).

- **Data model** (`connections` table in Harvest's memory DB): `office` (GLE/Blooms/CitiSignal/BinCheck/…), `system`, `access_shape` (**operate-in-tenant** = scoped JWT, or **watch-health** = owner/aggregate read — see 1.3), `credential_ref` (env-var name / secret pointer, never the secret itself), `scope_id` (§4.1: personal/family/portfolio/company/venture/deal), `status` (connected / disconnected / error), `connected_at`, `last_ok_at`, `last_error`.
- **UI** — served from `server.py` at `/connections` (Harvest already runs a web server + `/health`). Lists every Office with a live status dot, a **Connect** flow (register creds → test → mark connected), and a **Disconnect** button (revoke-at-source + clear the credential_ref + set status=disconnected). Mirrors the Executive-Office one-page ethos: at-a-glance, one click.
- **Disconnect semantics** = revoke at the SOURCE first (delete the bot user / rotate the secret in that system) — the authoritative kill — then clear Harvest's stored ref. Per-connection, isolated, read-only (§4.6 → severing never stops the underlying company operating).
- **Deal use:** selling an entity or disconnecting a partner becomes **one operation** in the registry, not "remember every env var."

### 1.2 — Memory Severability  *(makes §4.9 real)*
Harvest's memory (`memory_store.py`) is not yet tagged by entity, so on a sale you cannot cleanly split *"GLE/Ordino context that conveys with the buyer"* from *"the owner's own knowledge that stays"* (§4.9). Amendment: **every memory record carries a `scope_id`** from the §4.1 partition (personal / family / portfolio / company / venture / deal). A disconnect/sale then exports-or-purges exactly that scope, leaving the rest intact — clean cut, not a manual untangle.

### 1.3 — Access-shape per Office  *(clarifies §3 Offices + §4.2 authority)*
Every connection is one of two shapes, chosen deliberately per Office:
- **Operate-in-tenant** — Harvest reads/acts on *your specific data* inside a multi-tenant system (GLE in Ordino; Blooms *if/when* it's multi-tenant SaaS and you're a tenant). Requires a scoped identity (the JWT pattern). Heavier.
- **Watch-health** — Harvest reads *owner/portfolio aggregates* (revenue, active users, MRR, up/down) for CitiSignal, BinCheck, etc. One owner-level read-only endpoint per product; **no per-tenant identity**. Lighter and safer (a small metrics endpoint beats Harvest holding a full service key).
Rule: **default a new venture to watch-health**; only use operate-in-tenant where Harvest genuinely acts as you inside the app. Cost scales with the number of *systems you own* (~a handful), never with their *number of customers*.

### 1.4 — Current State (§6) delta
- Connection registry + UI: **planned → committed build** (not yet started).
- Memory: **not yet entity-scoped** (blocks clean severability).
- Per-system credentials already exist (Plaid-*structure* present); the missing pieces are the registry surface + entity tagging.

### 1.5 — Roadmap (§7) delta
- **Phase 1 (Executive Office):** add the Connection Registry + `/connections` UI.
- **Phase 4 (add Offices deliberately):** each new Office declares its **access_shape** (1.3) at connect time; default watch-health.
- **Cross-cutting:** entity-scope Harvest's memory (1.2) before any entity sale is realistic.

### Changelog (for the master doc)
- **v1.4 (2026-08-17)** — Added Connection Registry + connect/disconnect UI (§4.7 made buildable); memory severability via `scope_id` (§4.9 made real); the operate-in-tenant vs watch-health access-shape rule (§3/§4.2). Current State + Roadmap updated accordingly.
