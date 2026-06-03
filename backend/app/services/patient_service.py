from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    AuditLog,
    FetalMonitoring,
    PatientProfile,
    Pregnancy,
    RiskAssessment,
    VitalSign,
)


async def get_patient_profile(db: AsyncSession, patient_id: str) -> PatientProfile | None:
    result = await db.execute(
        select(PatientProfile)
        .where(PatientProfile.id == patient_id)
        .options(selectinload(PatientProfile.pregnancies))
    )
    return result.scalar_one_or_none()


async def create_patient_profile(db: AsyncSession, data: dict) -> PatientProfile:
    profile = PatientProfile(**data)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_patient_profile(db: AsyncSession, patient_id: str, data: dict) -> PatientProfile | None:
    profile = await get_patient_profile(db, patient_id)
    if not profile:
        return None
    for key, value in data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    profile.updated_at = datetime.now(timezone.utc)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def create_pregnancy(db: AsyncSession, data: dict) -> Pregnancy:
    pregnancy = Pregnancy(**data)
    db.add(pregnancy)
    await db.commit()
    await db.refresh(pregnancy)
    return pregnancy


async def get_pregnancy(db: AsyncSession, pregnancy_id: str) -> Pregnancy | None:
    result = await db.execute(
        select(Pregnancy).where(Pregnancy.id == pregnancy_id)
    )
    return result.scalar_one_or_none()


async def list_pregnancies_by_patient(db: AsyncSession, patient_id: str) -> list[Pregnancy]:
    result = await db.execute(
        select(Pregnancy)
        .where(Pregnancy.patient_id == patient_id)
        .order_by(Pregnancy.created_at.desc())
    )
    return list(result.scalars().all())


async def create_vital_sign(db: AsyncSession, data: dict) -> VitalSign:
    vital = VitalSign(**data)
    db.add(vital)
    await db.commit()
    await db.refresh(vital)
    return vital


async def list_vitals_by_patient(db: AsyncSession, patient_id: str, limit: int = 50) -> list[VitalSign]:
    result = await db.execute(
        select(VitalSign)
        .where(VitalSign.patient_id == patient_id)
        .order_by(VitalSign.recorded_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_fetal_monitoring(db: AsyncSession, data: dict) -> FetalMonitoring:
    entry = FetalMonitoring(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def list_fetal_by_patient(db: AsyncSession, patient_id: str, limit: int = 50) -> list[FetalMonitoring]:
    result = await db.execute(
        select(FetalMonitoring)
        .where(FetalMonitoring.patient_id == patient_id)
        .order_by(FetalMonitoring.recorded_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_risk_assessment(db: AsyncSession, data: dict) -> RiskAssessment:
    assessment = RiskAssessment(**data)
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment


async def list_risks_by_patient(db: AsyncSession, patient_id: str, limit: int = 20) -> list[RiskAssessment]:
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.patient_id == patient_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_audit_log(db: AsyncSession, data: dict) -> AuditLog:
    log = AuditLog(**data)
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
