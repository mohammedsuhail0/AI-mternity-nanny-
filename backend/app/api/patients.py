from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import (
    PatientProfile,
    Pregnancy,
    VitalSign,
    FetalMonitoring,
    RiskAssessment,
    User,
)
from app.api.schemas import (
    PatientProfileCreate,
    PatientProfileResponse,
    PatientSummaryResponse,
    PregnancyCreate,
    PregnancyResponse,
    VitalSignCreate,
    VitalSignResponse,
    FetalMonitoringCreate,
    FetalMonitoringResponse,
    RiskAssessmentResponse,
)
from app.api.auth import get_current_user
from app.services.dashboard_service import get_patient_summaries
from dataclasses import asdict
from uuid import UUID


router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=list[PatientSummaryResponse])
async def list_patient_summaries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summaries = await get_patient_summaries(db)
    return [PatientSummaryResponse(**asdict(summary)) for summary in summaries]


@router.post("/", response_model=PatientProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_patient_profile(
    profile_data: PatientProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(
        select(PatientProfile).where(
            PatientProfile.medical_record_number == profile_data.medical_record_number
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medical record number already exists",
        )

    profile = PatientProfile(
        user_id=current_user.id,
        **profile_data.model_dump(),
    )
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=PatientProfileResponse)
async def get_patient_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile


@router.post("/{profile_id}/pregnancies", response_model=PregnancyResponse, status_code=status.HTTP_201_CREATED)
async def create_pregnancy(
    profile_id: UUID,
    pregnancy_data: PregnancyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    pregnancy = Pregnancy(
        patient_profile_id=profile_id,
        **pregnancy_data.model_dump(),
    )
    db.add(pregnancy)
    await db.flush()
    await db.refresh(pregnancy)
    return pregnancy


@router.post(
    "/pregnancies/{pregnancy_id}/vitals",
    response_model=VitalSignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_vitals(
    pregnancy_id: UUID,
    vitals_data: VitalSignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Pregnancy).where(Pregnancy.id == pregnancy_id)
    )
    pregnancy = result.scalar_one_or_none()
    if pregnancy is None:
        raise HTTPException(status_code=404, detail="Pregnancy not found")

    vital = VitalSign(
        pregnancy_id=pregnancy_id,
        **vitals_data.model_dump(),
    )
    db.add(vital)
    await db.flush()
    await db.refresh(vital)
    return vital


@router.get("/pregnancies/{pregnancy_id}/vitals", response_model=list[VitalSignResponse])
async def get_vitals(
    pregnancy_id: UUID,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(VitalSign)
        .where(VitalSign.pregnancy_id == pregnancy_id)
        .order_by(VitalSign.recorded_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.post(
    "/pregnancies/{pregnancy_id}/fetal-monitoring",
    response_model=FetalMonitoringResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_fetal_monitoring(
    pregnancy_id: UUID,
    data: FetalMonitoringCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Pregnancy).where(Pregnancy.id == pregnancy_id)
    )
    pregnancy = result.scalar_one_or_none()
    if pregnancy is None:
        raise HTTPException(status_code=404, detail="Pregnancy not found")

    record = FetalMonitoring(
        pregnancy_id=pregnancy_id,
        **data.model_dump(),
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.get(
    "/pregnancies/{pregnancy_id}/risk-assessments",
    response_model=list[RiskAssessmentResponse],
)
async def get_risk_assessments(
    pregnancy_id: UUID,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.pregnancy_id == pregnancy_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
