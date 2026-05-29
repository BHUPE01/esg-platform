# 🌿 ESG Data Ingestion & Audit Platform

> An enterprise-grade ESG (Environmental, Social, Governance) data pipeline that ingests messy raw data from multiple sources, normalizes it into a clean schema, validates it against configurable business rules, and provides a full analyst review workflow — with an immutable audit trail on every action.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running the Project](#running-the-project)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Data Sources](#-data-sources)
- [Pipeline Flow](#-pipeline-flow)
- [Default Credentials](#-default-credentials)
- [Deployment](#-deployment)
- [License](#-license)

---

## 🔍 Overview

The ESG Audit Platform solves a real enterprise problem: ESG data arrives from dozens of systems (SAP ERPs, utility providers, travel booking platforms) in wildly inconsistent formats. This platform:

1. **Ingests** raw files (CSV exports, JSON APIs) and stores every row exactly as received
2. **Normalizes** messy data — maps ugly SAP column names, converts units, parses multi-format dates
3. **Validates** records against configurable business rules (negative values, suspicious quantities, invalid airport codes)
4. **Queues** flagged records for analyst review with approve / reject / edit workflow
5. **Logs** every action permanently with before/after snapshots for regulatory compliance

---

## 🛠 Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Language |
| Django | 5.0 | Web framework |
| Django REST Framework | 3.15 | REST API layer |
| PostgreSQL | 15+ | Primary database |
| Simple JWT | 5.3 | JWT authentication |
| pandas / dateutil | latest | Date parsing & data handling |
| django-cors-headers | 4.4 | CORS for React frontend |
| WhiteNoise | 6.7 | Static file serving |
| dj-database-url | 2.2 | Database URL parsing |
| python-dotenv | 1.0 | Environment variable management |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| Vite | 5 | Build tool |
| TailwindCSS | 3 | Styling |
| React Router | 6 | Client-side routing |
| Axios | latest | HTTP client |

---

## ✨ Features

### 🏢 Multi-Tenancy
- Every record is scoped to an **Organization**
- Users belong to organizations with roles: `admin`, `analyst`, `viewer`
- One Django instance serves multiple clients with complete data isolation

### 📥 Data Ingestion
- **SAP CSV** — handles ugly German column names (`WERKS`, `MENGE`, `MEINS`), BOM characters, semicolon/comma delimiters, European number formats
- **Utility Electricity CSV** — billing period data with meter IDs, kWh readings, tariff codes
- **Travel API JSON** — flight and hotel data from mock Concur-style API
- Every row stored as **immutable raw JSON** — source of truth, never modified

### 🔄 Normalization Pipeline
- Maps SAP field names to clean schema (`WERKS` → `site_code`, `MENGE` → `quantity`)
- Converts units to SI base units (gallons → L, MWh → kWh, tonnes → kg)
- Parses multi-format dates (`25.05.2026`, `2026/05/20`, ISO 8601)
- Handles European decimal format (`1.500,75` → `1500.75`)
- Records normalization warnings without blocking the pipeline

### ✅ Configurable Validation Rules
| Rule | Source | Description |
|---|---|---|
| Negative Quantity | SAP, Utility | Fuel/electricity cannot be negative |
| Quantity Threshold | SAP, Utility | Flags suspiciously high values |
| Invalid Airport Code | Travel | Validates against IATA code list |
| Unknown Unit | SAP | Flags unrecognized units of measure |
| Missing Required Field | All | Configurable required field check |
| Invalid Date Range | Utility | billing_end cannot precede billing_start |
| Duplicate Meter Period | Utility | Detects double-submitted billing data |

### 🔍 Analyst Review Workflow
- **Review queue** — all pending and flagged records in one view
- **Approve** — mark record as verified
- **Reject** — reject with mandatory notes explaining why
- **Edit** — correct specific fields (whitelisted), full audit trail on every change

### 📜 Immutable Audit Log
- Every action recorded: `ingested`, `normalized`, `flagged`, `approved`, `rejected`, `updated`
- **Before/after snapshots** stored as JSON for every change
- `changed_by` user and exact timestamp on every entry
- Cannot be modified or deleted — enforced at application and admin level

### 📊 Dashboard
- Total raw records ingested
- Normalization success/failure counts
- Review status breakdown (pending / flagged / approved / rejected)
- Open flags by severity (error vs warning)
- Source type breakdown
- Recent upload batch activity

---

## 📁 Project Structure

```
esg-platform/
│
├── backend/                          # Django backend
│   ├── esg_platform/                 # Django project config
│   │   ├── settings.py               # All configuration
│   │   ├── urls.py                   # Root URL router
│   │   └── wsgi.py                   # Production entry point
│   │
│   ├── apps/
│   │   ├── core/                     # Foundation: Org, AuditLog, Dashboard
│   │   │   ├── models.py             # Organization, AuditLog, write_audit_log()
│   │   │   ├── serializers.py
│   │   │   ├── views.py              # Dashboard, AuditLog API, CurrentUser
│   │   │   ├── urls.py
│   │   │   └── admin.py
│   │   │
│   │   ├── ingestion/                # Raw data intake
│   │   │   ├── models.py             # DataSource, UploadBatch, RawRecord
│   │   │   ├── parsers.py            # SAP CSV, Utility CSV, Travel JSON parsers
│   │   │   ├── services.py           # ingest_batch() orchestrator
│   │   │   ├── views.py              # File upload endpoint
│   │   │   └── urls.py
│   │   │
│   │   ├── normalization/            # Data cleaning pipeline
│   │   │   ├── models.py             # NormalizedRecord (unified schema)
│   │   │   ├── normalizers.py        # Per-source normalizer functions
│   │   │   ├── services.py           # normalize_batch(), normalize_single()
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── validation/               # Business rule enforcement
│   │   │   ├── models.py             # ValidationRule, ValidationFlag
│   │   │   ├── rules.py              # 7 rule checker functions
│   │   │   ├── services.py           # validate_record(), validate_batch()
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   └── review/                   # Analyst workflow
│   │       ├── views.py              # Approve, Reject, Edit, Queue
│   │       └── urls.py
│   │
│   ├── scripts/
│   │   └── seed_data.py              # Test data: org, users, rules
│   │
│   ├── test_data/
│   │   ├── sap_sample.csv            # Messy SAP export with bad rows
│   │   ├── utility_sample.csv        # Electricity data with duplicates/negatives
│   │   └── travel_sample.json        # Mock travel API response
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── .env                          # Secret config (not committed)
│
└── frontend/                         # React frontend
    ├── src/
    │   ├── api/                      # Axios API clients
    │   ├── contexts/                 # AuthContext (JWT state)
    │   ├── components/               # Layout, Sidebar
    │   └── pages/                    # Dashboard, Upload, Records, Flags, Audit
    ├── package.json
    └── tailwind.config.js
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have these installed:

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **PostgreSQL 15+** — [postgresql.org](https://www.postgresql.org/download/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Git**

---

### Backend Setup

#### 1. Clone and navigate

```bash
git clone https://github.com/your-username/esg-platform.git
cd esg-platform/backend
```

#### 2. Create virtual environment

```bash
# Linux / Mac
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set up PostgreSQL

```bash
# Open PostgreSQL shell
psql -U postgres

# Run these commands inside psql:
CREATE USER esg_user WITH PASSWORD 'esg_password';
CREATE DATABASE esg_db OWNER esg_user;
GRANT ALL PRIVILEGES ON DATABASE esg_db TO esg_user;
\q
```

> **Windows users:** PostgreSQL shell is at `C:\Program Files\PostgreSQL\16\bin\psql.exe -U postgres`

#### 5. Configure environment variables

Create `backend/.env`:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
DATABASE_URL=postgresql://esg_user:esg_password@localhost:5432/esg_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

#### 6. Run migrations

```bash
python manage.py makemigrations core ingestion normalization validation review
python manage.py migrate
```

#### 7. Create superuser

```bash
python manage.py createsuperuser
# Follow prompts: username, email, password
```

#### 8. Seed test data

```bash
# Linux / Mac
python manage.py shell --command="exec(open('scripts/seed_data.py').read())"

# Windows
python manage.py shell --command="exec(open('scripts/seed_data.py').read())"
```

This creates:
- Organization: **Acme Corporation**
- Users: `admin` / `admin123` and `analyst1` / `analyst123`
- Data sources for SAP, Utility, and Travel
- 7 pre-configured validation rules

---

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000/api" > .env
```

---

### Running the Project

Open **two terminals**:

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate   # or .\venv\Scripts\Activate on Windows
python manage.py runserver
# Runs at http://localhost:8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# Runs at http://localhost:5173
```

Open **http://localhost:5173** in your browser.

---

## 🔐 Environment Variables

| Variable | Required | Description | Example |
|---|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key | `your-50-char-random-string` |
| `DEBUG` | ✅ | Debug mode | `True` (dev) / `False` (prod) |
| `DATABASE_URL` | ✅ | PostgreSQL connection URL | `postgresql://user:pass@localhost:5432/db` |
| `ALLOWED_HOSTS` | ✅ | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | ✅ | React app origin | `http://localhost:5173` |

---

## 📡 API Reference

All endpoints require `Authorization: Bearer <access_token>` except auth endpoints.

### Authentication

```http
POST /api/auth/token/
Content-Type: application/json

{"username": "analyst1", "password": "analyst123"}
```

```json
{
  "access": "eyJ0eXAiOiJKV1Q...",
  "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

```http
POST /api/auth/token/refresh/
Body: {"refresh": "<refresh_token>"}
```

---

### Core

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/core/me/` | Current user info |
| `GET` | `/api/core/organizations/` | List organizations |
| `POST` | `/api/core/organizations/` | Create organization |
| `GET` | `/api/core/dashboard/?org=1` | Dashboard stats |
| `GET` | `/api/core/audit-logs/?org=1` | Full audit log |

---

### Ingestion

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/ingestion/data-sources/?org=1` | List data sources |
| `POST` | `/api/ingestion/data-sources/` | Create data source |
| `POST` | `/api/ingestion/upload/` | Upload file (multipart) |
| `GET` | `/api/ingestion/batches/?org=1` | List upload batches |
| `GET` | `/api/ingestion/raw-records/?batch=1` | View raw records |

**Upload example:**
```bash
curl -X POST http://localhost:8000/api/ingestion/upload/ \
  -H "Authorization: Bearer <token>" \
  -F "data_source_id=1" \
  -F "file=@test_data/sap_sample.csv"
```

---

### Normalization

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/normalization/records/?org=1` | List normalized records |
| `GET` | `/api/normalization/records/?review_status=flagged` | Filter by status |
| `GET` | `/api/normalization/records/?source_type=sap_csv` | Filter by source |
| `GET` | `/api/normalization/records/<id>/` | Single record detail |
| `POST` | `/api/normalization/normalize-batch/` | Run normalization |

---

### Validation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/validation/rules/?org=1` | List validation rules |
| `POST` | `/api/validation/rules/` | Create rule |
| `GET` | `/api/validation/flags/?org=1&status=open` | List open flags |
| `POST` | `/api/validation/flags/<id>/resolve/` | Resolve / dismiss flag |
| `POST` | `/api/validation/validate-batch/` | Run validation |

---

### Review

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/review/queue/?org=1` | Pending + flagged records |
| `POST` | `/api/review/records/<id>/approve/` | Approve a record |
| `POST` | `/api/review/records/<id>/reject/` | Reject with notes |
| `PATCH` | `/api/review/records/<id>/edit/` | Edit specific fields |

**Approve example:**
```bash
curl -X POST http://localhost:8000/api/review/records/1/approve/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Verified against source system"}'
```

---

## 📊 Data Sources

### SAP CSV Export

Messy SAP-style export with German column names, mixed date formats, inconsistent units:

```csv
WERKS,MENGE,MEINS,BUDAT
PLANT01,500,L,25.05.2026
PLANT02,1.500,m3,2026/05/20
PLANT03,-50,L,2026-05-18
```

Normalizes to: `site_code`, `quantity` (Decimal), `unit_normalized` (SI), `record_date` (ISO date)

---

### Utility Electricity CSV

```csv
meter_id,billing_start,billing_end,kwh,tariff
METER-001,2026-04-01,2026-04-30,4500,business_standard
METER-002,2026-04-01,2026-04-30,-200,residential
```

Validates: negative kWh, billing date ranges, duplicate meter periods

---

### Travel API JSON

```json
[
  {
    "traveler": "Alice Johnson",
    "departure_airport": "LHR",
    "arrival_airport": "JFK",
    "cabin_class": "business",
    "hotel_nights": 3,
    "travel_date": "2026-05-10"
  }
]
```

Validates: IATA airport codes, cabin class values

---

## 🔄 Pipeline Flow

```
Upload File
    │
    ▼
┌─────────────┐
│  INGESTION  │  Parse file → store each row as raw JSON (immutable)
└──────┬──────┘
       │ POST /api/normalization/normalize-batch/
       ▼
┌──────────────────┐
│  NORMALIZATION   │  Map fields → convert units → parse dates → store clean record
└──────┬───────────┘
       │ POST /api/validation/validate-batch/
       ▼
┌──────────────┐
│  VALIDATION  │  Run rules → create flags → mark records as flagged/pending
└──────┬───────┘
       │ Analyst reviews via /api/review/queue/
       ▼
┌────────────┐
│   REVIEW   │  Approve / Reject / Edit → full audit trail written
└──────┬─────┘
       │
       ▼
┌───────────────┐
│   AUDIT LOG   │  Permanent, immutable record of every action
└───────────────┘
```

Each step is triggered manually via API (or automatically chained in the upload UI).

---

## 🔑 Default Credentials

After running `seed_data.py`:

| User | Password | Role |
|---|---|---|
| `admin` | `admin123` | Superuser (Django admin access) |
| `analyst1` | `analyst123` | Analyst (review workflow) |

**Django Admin Panel:** http://localhost:8000/admin/

---

## 🌐 Deployment

### Free Tier Deployment

| Service | What it hosts | Free tier |
|---|---|---|
| [Render](https://render.com) | Django backend | 750 hrs/month |
| [Render](https://render.com) | PostgreSQL database | 1 GB storage |
| [Vercel](https://vercel.com) | React frontend | Unlimited |

### Backend — Render

1. Push your code to GitHub

2. Add these files to `backend/`:

**`Procfile`**
```
web: gunicorn esg_platform.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate
```

**`runtime.txt`**
```
python-3.11.9
```

Add `gunicorn` to `requirements.txt`:
```
gunicorn==21.2.0
```

3. On Render dashboard:
   - New → Web Service → connect your GitHub repo
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn esg_platform.wsgi --bind 0.0.0.0:$PORT`

4. Add environment variables on Render:
   ```
   SECRET_KEY=<generate a strong random key>
   DEBUG=False
   DATABASE_URL=<Render PostgreSQL URL — auto-filled if you add a Render DB>
   ALLOWED_HOSTS=your-app.onrender.com
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

5. Add a Render PostgreSQL database and link it to your web service.

---

### Frontend — Vercel

1. On Vercel dashboard:
   - New Project → import your GitHub repo
   - Root directory: `frontend`
   - Framework preset: Vite
   - Build command: `npm run build`
   - Output directory: `dist`

2. Add environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api
   ```

3. Deploy — Vercel handles everything else.

---

### Update `settings.py` for production

```python
# In settings.py, update ALLOWED_HOSTS and CORS origins
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# Make sure DEBUG=False in production
DEBUG = os.getenv("DEBUG", "False") == "True"
```

---

## 🧪 Testing the Full Workflow

After setup, test the complete pipeline:

```bash
# 1. Get JWT token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst1","password":"analyst123"}' | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# 2. Upload SAP CSV
curl -X POST http://localhost:8000/api/ingestion/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "data_source_id=1" \
  -F "file=@test_data/sap_sample.csv"

# 3. Normalize batch (use batch id from step 2)
curl -X POST http://localhost:8000/api/normalization/normalize-batch/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch_id": 1}'

# 4. Run validation
curl -X POST http://localhost:8000/api/validation/validate-batch/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch_id": 1}'

# 5. Check dashboard
curl http://localhost:8000/api/core/dashboard/?org=1 \
  -H "Authorization: Bearer $TOKEN"

# 6. View flags
curl "http://localhost:8000/api/validation/flags/?org=1&status=open" \
  -H "Authorization: Bearer $TOKEN"

# 7. Approve a record
curl -X POST http://localhost:8000/api/review/records/1/approve/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Verified with plant manager"}'

# 8. View audit log
curl "http://localhost:8000/api/core/audit-logs/?org=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📌 Key Design Principles

- **Raw data is immutable** — original files are stored exactly as received and never modified
- **Layered pipeline** — Ingestion → Normalization → Validation → Review are separate, independent layers
- **Everything is audited** — every action writes a permanent before/after log entry
- **Configurable rules** — validation thresholds live in the database, not in code
- **Multi-tenant by default** — all data is scoped to an Organization from day one
- **No overengineering** — synchronous pipeline, single Django process, no microservices

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with Django · PostgreSQL · React · TailwindCSS*
