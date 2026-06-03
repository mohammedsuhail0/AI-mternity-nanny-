# Product Requirements Document

## AI Maternal Monitor

## 1. Overview
AI Maternal Monitor is a clinical web application for tracking maternal and fetal health during pregnancy. It combines manual patient data entry, fetal monitoring, vital sign tracking, and AI-assisted risk assessment to help clinicians identify high-risk cases earlier and review patient status from a single dashboard.

## 2. Problem Statement
Clinicians monitoring pregnancy often need to review maternal vitals, fetal heart rate trends, and risk indicators across multiple tools or paper workflows. This slows down review, increases fragmentation, and makes it harder to spot deterioration early. The product aims to centralize monitoring and surface meaningful alerts in a single clinical dashboard.

## 3. Product Goals
- Give clinicians a single place to view active maternal patients and pregnancy status.
- Support recording of maternal vitals and fetal monitoring observations.
- Provide AI-based risk scoring to flag pregnancies that may need closer review.
- Make patient review faster with a dashboard, alerts, and trend-focused views.
- Provide secure login and role-aware access for clinical staff.

## 4. MVP Scope

### In Scope
- Authentication: login, registration, token-based session handling.
- Dashboard: summary cards, recent patients, and alert panels.
- Patient profiles: create and view patient records.
- Pregnancy records: create pregnancies under a patient profile.
- Vital signs: record and list maternal and fetal vitals.
- Fetal monitoring: record and view fetal monitoring observations.
- Risk assessments: display computed AI risk results for pregnancies.
- Basic navigation between clinical sections in the frontend.

### Out of Scope for MVP
- Multi-hospital tenant management.
- Full EHR integration.
- Billing, claims, or insurance workflows.
- Messaging/chat between clinicians.
- Patient-facing mobile app.
- Advanced analytics dashboards beyond core monitoring.
- Production-grade model explainability UI beyond simple risk outputs.

## 5. Target Users
- Obstetricians and maternal-fetal medicine specialists.
- Nurses and midwives recording vitals and monitoring data.
- Hospital administrators managing access.
- Optional future: patients, if a separate patient portal is added later.

## 6. Core User Stories
- As a clinician, I want to log in securely so I can access patient data.
- As a clinician, I want to create a patient profile so I can begin monitoring.
- As a clinician, I want to add a pregnancy to a patient profile so records are organized correctly.
- As a clinician, I want to record vitals and fetal monitoring observations so trends are stored over time.
- As a clinician, I want to see AI risk results so I can prioritize review.
- As a clinician, I want a dashboard summary so I can quickly identify the patients that need attention.

## 7. Functional Requirements

### 7.1 Authentication
- Users can register and log in with email and password.
- The system issues access and refresh tokens.
- Protected routes require valid authentication.
- Users can view their own profile details.

### 7.2 Patient Management
- Create patient profiles with demographic and medical context fields.
- Retrieve a patient profile by ID.
- Store a medical record number uniquely per patient profile.

### 7.3 Pregnancy Management
- Create one or more pregnancies under a patient profile.
- Store gestational age, due date, high-risk status, and risk factors.
- Retrieve pregnancy records for display and monitoring.

### 7.4 Vitals Tracking
- Record maternal vitals including blood pressure, temperature, respiratory rate, oxygen saturation, contractions, and fetal heart rate.
- Retrieve vitals in descending time order.
- Support a source field such as manual or device-based entry.

### 7.5 Fetal Monitoring
- Record fetal monitoring observations such as baseline FHR, variability, accelerations, decelerations, and NST score.
- Support storing a raw signal file reference for future waveform data.

### 7.6 Risk Assessment
- Store AI-generated risk assessments for pregnancies.
- Show risk category, probability, confidence, and recommended action.
- Allow clinicians to view the latest assessments and prior history.

### 7.7 Dashboard and Navigation
- Show top-level stats such as active patients, monitoring count, average fetal heart rate, and alerts.
- Show recent patients and current risk level.
- Provide navigation to patient, monitoring, AI assessment, FHR, reports, and settings sections.

## 8. Non-Functional Requirements
- Security: JWT-based auth, protected endpoints, and role-aware access.
- Reliability: database writes should be atomic and consistent.
- Performance: common dashboard views should load quickly for a typical clinic workload.
- Auditability: important clinical actions should be trackable later.
- Usability: clinicians should be able to read key data quickly without clutter.
- Maintainability: backend and frontend should stay cleanly separated with shared schemas.

## 9. Current Implementation Snapshot

### Backend
- FastAPI app with auth and patient routers.
- SQLAlchemy models for users, patient profiles, pregnancies, vitals, fetal monitoring, risk assessments, and audit logs.
- ML service that can load a saved model and produce a risk prediction when available.

### Frontend
- Next.js app with login, register, dashboard, layout, sidebar, and header components.
- Clinical UI components for patient cards, vital cards, and fetal heart rate charts.
- Auth context and API client scaffolding.

## 10. Known Gaps To Finish MVP
- Several frontend routes listed in the sidebar do not yet exist as full pages.
- Frontend auth and API helpers are not fully aligned with backend response shapes.
- Registration flow expects fields that the backend does not currently accept.
- Some ORM model fields need cleanup so the database schema is valid and consistent.
- Service layer code still references fields and schemas that do not match the current models.
- AI model output is not yet surfaced through an API endpoint or tied into the dashboard.
- Patient and monitoring pages need real data fetching instead of static mock content.

## 11. Success Metrics
- Clinicians can log in and reach the dashboard without manual setup.
- A patient profile and pregnancy can be created successfully.
- Vitals and fetal monitoring entries can be recorded and retrieved.
- Risk assessments can be viewed for a pregnancy.
- The dashboard shows useful summary data rather than placeholder-only content.

## 12. MVP Milestones

### Phase 1: Backend Stabilization
- Fix schema/model mismatches.
- Align auth, patient, and pregnancy flows.
- Confirm database migrations and startup work.

### Phase 2: Frontend Wiring
- Connect login and register flows to the backend correctly.
- Replace static dashboard data with live API data.
- Implement the missing sidebar routes.

### Phase 3: Monitoring and Risk Flow
- Add endpoints or service hooks for AI risk assessment.
- Surface vitals and fetal monitoring trends in the UI.
- Show alerts and risk levels in a clinically usable format.

### Phase 4: MVP Hardening
- Add audit logging for critical actions.
- Improve empty states, error states, and loading states.
- Verify end-to-end clinician workflow.

## 13. Open Questions
- Should registration be open to clinicians only, or admin-approved?
- Which roles should be allowed to create patient profiles?
- Should AI risk assessment be run automatically on every new vitals record or triggered manually?
- What clinical thresholds should generate alerts in the MVP?
- Should the MVP support multiple pregnancies per patient by default or a single active pregnancy workflow?

## 14. Recommended MVP Definition
The MVP should allow a clinician to log in, create or open a patient, add a pregnancy, record vitals and fetal monitoring data, and view a risk summary on the dashboard. Anything beyond that should be treated as post-MVP unless it is required to make that flow work reliably.