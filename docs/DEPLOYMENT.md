# DEPLOYMENT & OPERATION GUIDE

## Personal Government Job Notification Intelligence & Eligibility Alert System

This guide outlines deployment on **Render Free Web Service**, external PostgreSQL setup, n8n orchestration, and local development.

---

## 1. Prerequisites & Environment Setup

### Required Credentials:

1. **Telegram MTProto (Inbound Private/Public Listener):**

   - Obtain `api_id` and `api_hash` from [my.telegram.org/apps](https://my.telegram.org/apps).
   - Generate your `TELEGRAM_SESSION` string once by running:
     ```powershell
     $env:PYTHONPATH="."
     .venv\Scripts\python.exe scripts/generate_session.py
     ```
   - Place the output string in `.env` as `TELEGRAM_SESSION`.
2. **Telegram Bot (Outgoing Alerts):**

   - Create a bot via [@BotFather](https://t.me/botfather).
   - Save the token as `TELEGRAM_BOT_TOKEN`.
   - Find your user ID via [@userinfobot](https://t.me/userinfobot) and set `TELEGRAM_ALERT_CHAT_ID`.
3. **External PostgreSQL Database:**

   - Create a free database on [Neon.tech](https://neon.tech), [Supabase.com](https://supabase.com), or Render PostgreSQL.
   - Set `DATABASE_URL` (format: `postgresql+asyncpg://user:password@host/dbname`).
4. **AI Providers (Configured with Automatic Fallback):**

   - **NVIDIA NIM (Primary):** Sign up at [build.nvidia.com](https://build.nvidia.com) $\rightarrow$ get API key $\rightarrow$ set `NIM_API_KEY`.
   - **Google Gemini (Secondary):** Get free key from [Google AI Studio](https://aistudio.google.com) $\rightarrow$ set `GEMINI_API_KEY`.
   - **OpenRouter (Tertiary):** Get key from [openrouter.ai](https://openrouter.ai) $\rightarrow$ set `OPENROUTER_API_KEY`.

---

## 2. Local Execution

1. **Activate Virtual Environment & Install Dependencies:**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Start FastAPI Application (Web UI, API, Health Check, and Pipeline):**

   ```powershell
   $env:PYTHONPATH="."
   .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. **Access Interfaces:**

   - **User Requirements & Eligibility Editor:** [http://localhost:8000/admin/requirements](http://localhost:8000/admin/requirements)
   - **Lightweight Health Ping:** [http://localhost:8000/health](http://localhost:8000/health)
   - **Interactive OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 3. Render Free Web Service Deployment

Render's free tier spins down after 15 minutes of inactivity and features an ephemeral filesystem.

### Strict Compliance Measures Implemented:

1. **Zero Local State Dependency:** All critical state (raw messages, jobs, sources, alerts, failures, user eligibility configuration) is durably persisted to the external PostgreSQL database.
2. **Lightweight Health Endpoint:** `/health` executes in < 5ms and returns HTTP 200 without touching the database or Telegram network APIs, making it ideal for external uptime monitors (e.g. UptimeRobot or CronJob pings).
3. **Clean Restart Recovery:** On wake up, the application initializes database connections and resumes MTProto message streaming without data loss.

### Render Configuration Steps:

1. Push this repository to GitHub/GitLab.
2. In the Render Dashboard, click **New +** $\rightarrow$ **Web Service**.
3. Connect your repository.
4. Set the following build and start commands:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `DATABASE_URL`
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`
   - `TELEGRAM_SESSION`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_ALERT_CHAT_ID`
   - `NIM_API_KEY`
   - `GEMINI_API_KEY`
   - `OPENROUTER_API_KEY`
   - `N8N_WEBHOOK_URL` (if running n8n)
6. Under **Health Check Path**, enter `/health`.

---

## 4. n8n Orchestration Workflow Setup

1. Open your n8n instance (cloud or self-hosted).
2. Go to **Workflows** $\rightarrow$ **Import from File**.
3. Select `n8n/workflows/job_intelligence_pipeline.json`.
4. The workflow will listen for new message events at `/webhook/job-event`, filter out non-jobs, and dispatch potential recruitment announcements to `http://localhost:8000/webhook/inbound-message`.

---

## 5. Editing Your Requirements Profile

As requested, your eligibility requirements are completely editable:

1. **Via Web Dashboard:**
   - Navigate to `http://localhost:8000/admin/requirements`.
   - Update your education degrees, engineering branches, maximum age, fresher status, and reservation category.
   - Click **Save Requirements**. Changes sync instantly to PostgreSQL.
2. **Via REST API:**
   - `GET /api/requirements` to inspect.
   - `PUT /api/requirements` with new JSON payload to update.
3. **Via CLI Helper:**
   ```powershell
   $env:PYTHONPATH="."
   .venv\Scripts\python.exe -m app.cli.requirements view
   .venv\Scripts\python.exe -m app.cli.requirements set-age 32
   ```
