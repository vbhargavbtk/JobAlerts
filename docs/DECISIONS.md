# ARCHITECTURE DECISION LOG (ADR)

> **Document Status:** AUTHORITATIVE & BINDING  
> **Rule:** Every architectural choice, provider selection, and operational mechanism is logged here with rationale, tradeoffs, and verified capabilities. Changes require formal updates to this log.

---

## ADR-001: Telegram Ingestion via MTProto (Telethon) instead of Telegram Bot API

- **Context:** The system must monitor both public Telegram channels and **private Telegram channels** that the user's personal account is already a member of.
- **Decision:** Use Python with `Telethon` (MTProto client) authenticating as a user session.
- **Why Bot API Was Rejected:** Telegram Bots *cannot* read messages in private channels unless added as an Administrator by the channel owner. For external recruitment channels, the user is only a regular subscriber. Only MTProto user clients can stream messages from joined private channels.
- **Security & Session Management:** The user session will be generated once via an interactive CLI helper (`scripts/generate_session.py`) producing a base64 `StringSession`. This string is stored strictly in environment variables (`TELEGRAM_SESSION`). No session files or credentials are saved to git.
- **Limits & Verification:** Passive listening via `events.NewMessage` generates negligible traffic and does not trigger Telegram flood limits.

---

## ADR-002: Workflow Orchestration via n8n

- **Context:** Step-by-step pipeline execution, error handling, AI provider failover routing, alert dispatching, and audit logging require visual and programmatic orchestration.
- **Decision:** Lock orchestration to `n8n`.
- **Implementation Strategy:**
  - Python listener captures raw events, saves to database, and posts to an n8n webhook (`/webhook/job-event`).
  - n8n executes the pipeline steps or delegates heavy computing (browser rendering, PDF OCR, AI calls) to dedicated Python micro-endpoints while managing state, retries, and conditional logic.
  - Workflows are exported as version-controlled JSON definitions in `n8n/workflows/` for reproducible deployment in any environment (local or cloud).
- **Tradeoffs:** Requires running an n8n instance (via Node.js or container) alongside the Python services. This provides superior observability and decoupled retries compared to an all-in-one script.

---

## ADR-003: External Persistent PostgreSQL Database

- **Context:** The application will be hosted on platforms like Render (free tier) where the local filesystem is ephemeral and restarts happen frequently on idle spin-down.
- **Decision:** Use an external, managed PostgreSQL database (e.g. Supabase, Neon, or Render PostgreSQL).
- **Mandatory Tables:** `channels`, `processed_messages`, `jobs`, `sources`, `alerts`, `failures`, and `user_requirements`.
- **Verification:** All critical state (raw messages, parsed jobs, deduplication fingerprints, user eligibility rules, retry queues) is written directly to PostgreSQL. Ephemeral restarts do not cause message loss.

---

## ADR-004: Multi-Provider AI Strategy with Strict Fallback Order

- **Context:** Job extraction requires extracting structured factual JSON from noisy recruitment text/PDFs. Free tiers have rate limits (RPM/RPD) and occasional downtime.
- **Decision:** Implement a provider-independent `AIProvider` interface with automatic fallover:
  1. **Primary: NVIDIA NIM** (`https://integrate.api.nvidia.com/v1`, using models such as `meta/llama-3.3-70b-instruct` or `meta/llama-3.1-8b-instruct`). High accuracy and OpenAI-compatible API.
  2. **Secondary: Google Gemini** (`gemini-2.5-flash` via Google AI Studio API). Verified 10-15 RPM, 250-1,500 RPD free tier.
  3. **Tertiary: OpenRouter** (`https://openrouter.ai/api/v1` with verified free-tier models such as `meta-llama/llama-3.3-70b-instruct:free`).
  4. **Exhaustion Fallback:** If all providers fail or return invalid schemas, mark job as `AI_REVIEW_REQUIRED` without fabricating data.
- **Verification:** All endpoints use environment variables (`NIM_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`). Models are dynamically configurable in `config/ai.yaml`.

---

## ADR-005: 4-Tier Content Acquisition & Fallback Pipeline

- **Context:** Recruitment posts in Telegram often contain shortened links, heavy client-side JavaScript, dead links, or scanned PDF circulars.
- **Decision:** Implement a progressive 4-tier acquisition pipeline:
  - **Level 1 (Direct HTTP):** `httpx` + `readability-lxml` / `trafilatura` for fast, lightweight parsing.
  - **Level 2 (Headless Browser):** `playwright` (Chromium) for dynamic SPA / JS-heavy government portals.
  - **Level 3 (Search Fallback):** If original links are broken or missing, search via DuckDuckGo / Tavily using organization + post name + notification number to retrieve official circulars.
  - **Level 4 (PDF & OCR):** `pdfplumber` / `pypdf` for clean PDF text. If page text density is below threshold (scanned image PDF), route to `pytesseract` OCR.

---

## ADR-006: Deterministic Eligibility Engine & User Requirement Editing

- **Context:** The system must evaluate user qualifications against extracted job criteria. The user explicitly required: *"is hould able to edit the requirements of me"*.
- **Decision:**
  - Eligibility logic is **strictly deterministic** (not left to AI discretion). Rules evaluate explicit numerical and categorical boundaries: Age, Degrees, Branches, Experience, Categories, Locations, Excluded Types.
  - Evaluation produces `PASS`, `FAIL`, or `UNKNOWN`.
  - **Absolute Constraint:** Any `FAIL` $\rightarrow$ `NOT_ELIGIBLE`. Any `UNKNOWN` $\rightarrow$ `UNCERTAIN`. All `PASS` $\rightarrow$ `ELIGIBLE`. `UNKNOWN` is never promoted to `PASS`.
  - **User Editing:** User eligibility profile is stored in the `user_requirements` database table and backed by a local configuration file.
  - **Editing Interfaces Provided:**
    1. **Interactive Web Dashboard / REST API:** Secure endpoints (`GET /api/requirements`, `PUT /api/requirements`) with a clean browser interface to inspect and update education, age limits, branches, fresher preferences, and category relaxations.
    2. **CLI Utility:** `python -m app.cli.update_requirements` for rapid terminal editing.
    3. **Telegram Bot Command:** `/profile` to view and `/set_age`, `/set_degree`, `/set_branch` to edit on mobile.

---

## ADR-007: Cryptographic Job Fingerprinting & Cross-Channel Deduplication

- **Context:** The same government notification is commonly forwarded or reposted across dozens of public and private Telegram channels.
- **Decision:** Compute a deterministic SHA-256 fingerprint from normalized fields: `normalize(organization) + "|" + normalize(post_name) + "|" + normalize(notification_number) + "|" + normalize(application_deadline)`.
- If an incoming message matches an existing fingerprint, link the new message and source to the existing `jobs` record in PostgreSQL and suppress duplicate alert notifications.
