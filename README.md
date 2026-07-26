# AI Maternal Monitor

AI Maternal Monitor is a full-stack maternal and fetal health monitoring project. It combines:
- a **FastAPI backend** for authentication, patient data, monitoring records, and dashboard APIs,
- a **Next.js frontend** for clinician and patient-facing interfaces,
- an **ML training pipeline** for C-section risk prediction.

## Repository Structure

```text
AI-mternity-nanny-/
├── backend/                  # FastAPI app, DB models, API routes, services
│   ├── app/
│   │   ├── api/              # Routers and Pydantic schemas
│   │   ├── core/             # Settings, logging, security
│   │   ├── db/               # SQLAlchemy models, session, seed data
│   │   └── services/         # Dashboard/ML/auth/patient service logic
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Next.js 14 App Router UI
│   ├── app/                  # Routes (dashboard, auth, patient companion)
│   ├── components/           # Reusable UI/layout/clinical components
│   └── context/              # Auth state provider
├── ml/
│   └── train_model.py        # Model training + synthetic data generation
├── docs/
│   └── PRD.md                # Product requirements and MVP definition
├── LLM_SETUP_GUIDE.md
├── LLM_ACTIVATION_REPORT.md
└── test_llm_health.py
```

## Key Technologies

### Backend
- **Python 3 / FastAPI** for REST APIs
- **SQLAlchemy (async)** + **aiosqlite** (default local DB) for persistence
- **Pydantic v2** for request/response validation
- **JWT auth** (`python-jose`) and password hashing (`passlib`/bcrypt)
- **Structlog** for structured logging

### Frontend
- **Next.js 14 (App Router)** + **React 18**
- **TypeScript**
- **Tailwind CSS**
- **Zustand** for auth store/state
- **Recharts** for clinical chart UI

### ML
- **scikit-learn**, **pandas**, **numpy**, **joblib**, **shap**
- Synthetic-data training pipeline for C-section risk classification

## How the Code is Organized

### 1) API Layer (`backend/app/api`)
- `auth.py`: register/login/current-user endpoints
- `patients.py`: patient profile, pregnancy, vitals, fetal monitoring, risk history endpoints
- `dashboard.py`: dashboard overview metrics endpoint
- `companion.py`: patient companion chat endpoint with emergency detection and LLM fallback
- `schemas.py`: all Pydantic request/response models

### 2) Core/Infrastructure Layer (`backend/app/core`, `backend/app/db`)
- `config.py`: environment-driven settings
- `security.py`: token and password helpers
- `logging.py`: structured logger setup
- `session.py`: async DB engine/session lifecycle
- `models.py`: domain models (`User`, `PatientProfile`, `Pregnancy`, `VitalSign`, `FetalMonitoring`, `RiskAssessment`, `AuditLog`)
- `seed.py`: demo clinician/patient and monitoring seed data

### 3) Service Layer (`backend/app/services`)
- `dashboard_service.py`: patient summaries and dashboard aggregation logic
- `ml_service.py`: model loading and risk prediction helper
- `auth_service.py` and `patient_service.py`: additional service utilities (partially legacy/in-progress)

### 4) Frontend Feature Areas (`frontend/app`)
- `/patient-companion`: patient-facing guided assistant UI
- `/dashboard`: clinician dashboard pages
- `/auth/register` and `/auth/login`: auth routes (currently redirected/in-progress)
- Shared layout in `frontend/app/layout.tsx` and reusable components in `frontend/components`

## Local Development

### 1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend docs: `http://localhost:8000/docs`
Health: `http://localhost:8000/health`

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend app: `http://localhost:3000`

### 3. Optional ML Training
```bash
python ml/train_model.py
```

## Current Project Status

The repo contains active MVP work and some partially integrated areas. `docs/PRD.md` documents intended scope, known gaps, and milestone plans.
