from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from statistics import mean

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import PatientProfile, Pregnancy


@dataclass
class PatientSummary:
    id: str
    user_id: str
    full_name: str
    email: str
    date_of_birth: datetime
    medical_record_number: str
    gestational_age_weeks: int | None
    pregnancy_status: str | None
    is_high_risk: bool
    latest_fetal_heart_rate_bpm: int | None
    latest_blood_pressure_systolic: int | None
    latest_blood_pressure_diastolic: int | None
    latest_risk_category: str | None
    latest_risk_probability: float | None
    latest_recommendation: str | None
    latest_activity_at: datetime | None


def _latest_by_timestamp(items, timestamp_field: str):
    if not items:
        return None
    return max(items, key=lambda item: getattr(item, timestamp_field) or datetime.min)


async def get_patient_summaries(db: AsyncSession) -> list[PatientSummary]:
    result = await db.execute(
        select(PatientProfile)
        .options(
            selectinload(PatientProfile.user),
            selectinload(PatientProfile.pregnancies).selectinload(Pregnancy.vitals),
            selectinload(PatientProfile.pregnancies).selectinload(Pregnancy.fetal_monitoring),
            selectinload(PatientProfile.pregnancies).selectinload(Pregnancy.risk_assessments),
        )
    )

    summaries: list[PatientSummary] = []

    for profile in result.scalars().unique().all():
        pregnancy = _latest_by_timestamp(profile.pregnancies, "started_at")
        latest_vitals = _latest_by_timestamp(pregnancy.vitals, "recorded_at") if pregnancy else None
        latest_fetal = _latest_by_timestamp(pregnancy.fetal_monitoring, "recorded_at") if pregnancy else None
        latest_risk = _latest_by_timestamp(pregnancy.risk_assessments, "assessed_at") if pregnancy else None

        latest_activity_at = max(
            [timestamp for timestamp in [
                getattr(latest_vitals, "recorded_at", None),
                getattr(latest_fetal, "recorded_at", None),
                getattr(latest_risk, "assessed_at", None),
                getattr(pregnancy, "started_at", None),
            ] if timestamp is not None],
            default=None,
        )

        summaries.append(
            PatientSummary(
                id=str(profile.id),
                user_id=str(profile.user_id),
                full_name=profile.user.full_name if profile.user else "Unknown",
                email=profile.user.email if profile.user else "",
                date_of_birth=profile.date_of_birth,
                medical_record_number=profile.medical_record_number,
                gestational_age_weeks=pregnancy.gestational_age_weeks if pregnancy else None,
                pregnancy_status=pregnancy.status if pregnancy else None,
                is_high_risk=bool(pregnancy.is_high_risk) if pregnancy else False,
                latest_fetal_heart_rate_bpm=(
                    latest_vitals.fetal_heart_rate_bpm
                    if latest_vitals and latest_vitals.fetal_heart_rate_bpm is not None
                    else getattr(latest_fetal, "baseline_fhr", None)
                ),
                latest_blood_pressure_systolic=getattr(latest_vitals, "blood_pressure_systolic", None),
                latest_blood_pressure_diastolic=getattr(latest_vitals, "blood_pressure_diastolic", None),
                latest_risk_category=getattr(latest_risk, "risk_category", None),
                latest_risk_probability=getattr(latest_risk, "c_section_probability", None),
                latest_recommendation=getattr(latest_risk, "recommended_action", None),
                latest_activity_at=latest_activity_at,
            )
        )

    return summaries


def get_overview_metrics(summaries: list[PatientSummary]) -> dict:
    active_patients = sum(1 for summary in summaries if summary.pregnancy_status == "active")
    monitoring_patients = sum(1 for summary in summaries if summary.latest_fetal_heart_rate_bpm is not None)
    high_risk_patients = sum(1 for summary in summaries if summary.is_high_risk or summary.latest_risk_category in {"high", "critical"})
    avg_fetal_heart_rate = (
        round(mean([summary.latest_fetal_heart_rate_bpm for summary in summaries if summary.latest_fetal_heart_rate_bpm is not None]), 1)
        if any(summary.latest_fetal_heart_rate_bpm is not None for summary in summaries)
        else None
    )

    recent_patients = sorted(
        summaries,
        key=lambda summary: summary.latest_activity_at or datetime.min,
        reverse=True,
    )[:4]

    alerts = []
    for summary in summaries:
        if summary.latest_risk_category in {"high", "critical"} or summary.is_high_risk:
            alerts.append(
                {
                    "patient_name": summary.full_name,
                    "level": "critical" if summary.latest_risk_category in {"high", "critical"} else "warning",
                    "message": summary.latest_recommendation or "Review with obstetrics team",
                    "triggered_at": summary.latest_activity_at or datetime.utcnow(),
                }
            )

    return {
        "total_patients": len(summaries),
        "active_patients": active_patients,
        "monitoring_patients": monitoring_patients,
        "high_risk_patients": high_risk_patients,
        "avg_fetal_heart_rate": avg_fetal_heart_rate,
        "alerts_count": len(alerts),
        "recent_patients": recent_patients,
        "alerts": alerts[:3],
    }