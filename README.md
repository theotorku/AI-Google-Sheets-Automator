# AI Google Sheets Automator 🤖📊

Automate Google Sheets with natural language. Powered by GPT-4 and Google APIs.

## Project Structure

```
ai-sheets-automator/
├── .github/
│   ├── workflows/
│   │   ├── ci-cd.yml          # Main CI/CD pipeline
│   │   ├── scheduled-tests.yml # Nightly tests
│   │   └── emergency-rollback.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app
│   │   ├── auth.py            # Supabase Auth
│   │   ├── sandbox.py         # Secure Docker executor
│   │   ├── models/            # Database models
│   │   │   └── automation.py
│   │   ├── routes/
│   │   │   ├── api.py         # REST endpoints
│   │   │   └── webhooks.py
│   │   ├── services/
│   │   │   ├── gsheets.py     # Sheets service
│   │   │   └── openai.py      # AI service
│   │   ├── tests/
│   │   └── utils/
│   │       └── logging.py
│   │
│   ├── migrations/            # Alembic migrations
│   ├── Dockerfile
│   ├── docker-compose.test.yml
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   └── .env.sample
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── api.js         # Axios client
│   │   │   └── supabase.js    # Supabase client
│   │   ├── pages/
│   │   │   ├── api/           # Next.js API routes
│   │   │   │   └── generate.js
│   │   │   ├── _app.js
│   │   │   └── index.js
│   │   └── styles/
│   ├── next.config.js
│   ├── Dockerfile
│   └── .env.sample
│
├── monitoring/
├── scripts/
├── docs/
├── docker-compose.yml         # Local dev
├── Makefile                   # Common commands
└── README.md                  # Project overview
```

## Features

- 🔒 **Secure OAuth (Google + Supabase)**
- 🐳 **Secure Sandboxed Execution (Docker)**
- ⚡ **Next.js frontend**
- 📜 **GPT-4 code generation**

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements/base.txt
# Set up .env with SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
# Set up .env.local with NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
npm run dev
```

## Security Improvements 🛡️

- **Docker Sandbox**: Code is now executed in a locked-down container with resource limits (CPU/Memory).
- **RCE Prevention**: Scripts are mounted as files rather than passed via command line to prevent shell injection.
- **Credential Safety**: Service account credentials are no longer mounted into the sandbox.

## Deployment

- **Backend**: Google Cloud Run
- **Frontend**: Vercel

## Key Improvements Added

1. **Security**
   - Secure Docker sandbox with resource quotas.
   - Supabase Auth integration.
2. **Scalability**
   - Cloud Run auto-scales backend.
3. **Monitoring**
   - Prometheus + Grafana ready.
