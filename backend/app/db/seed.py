from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.db.models import (
    FetalMonitoring,
    PatientProfile,
    Pregnancy,
    RiskAssessment,
    User,
    UserRole,
    VitalSign,
)
from app.db.session import AsyncSessionLocal


DEMO_CLINICIAN_EMAIL = "demo.clinician@maternalmonitor.health"
DEMO_CLINICIAN_LEGACY_EMAIL = "demo.clinician@maternalmonitor.local"
DEMO_CLINICIAN_PASSWORD = "Demo1234!"


async def _get_or_create_user(email: str, full_name: str, role: UserRole, password: str) -> User:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is not None:
            return user

        user = User(
            email=email,
            full_name=full_name,
            role=role,
            hashed_password=hash_password(password),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def seed_demo_data() -> None:
    async with AsyncSessionLocal() as session:
        demo_user_result = await session.execute(select(User).where(User.email == DEMO_CLINICIAN_EMAIL))
        demo_user = demo_user_result.scalar_one_or_none()
        if demo_user is None:
            legacy_user_result = await session.execute(select(User).where(User.email == DEMO_CLINICIAN_LEGACY_EMAIL))
            demo_user = legacy_user_result.scalar_one_or_none()
            if demo_user is not None:
                demo_user.email = DEMO_CLINICIAN_EMAIL
                session.add(demo_user)
                await session.commit()
                await session.refresh(demo_user)
                return

        if demo_user is None:
            demo_user = User(
                email=DEMO_CLINICIAN_EMAIL,
                full_name="Demo Clinician",
                role=UserRole.PHYSICIAN,
                hashed_password=hash_password(DEMO_CLINICIAN_PASSWORD),
                is_active=True,
            )
            session.add(demo_user)
            await session.flush()

        patient_specs = [
            {
                "email": "maria.sanchez@demo.local",
                "name": "Maria Sanchez",
                "mrn": "MRN-1001",
                "dob": datetime(1994, 5, 14),
                "weeks": 34,
                "risk": True,
                "risk_factors": "Previous C-section; elevated blood pressure; obesity",
                "bp": (148, 92),
                "fhr": 142,
                "variability": "moderate",
                "risk_score": 0.81,
                "risk_category": "high",
            },
            {
                "email": "ana.park@demo.local",
                "name": "Ana Park",
                "mrn": "MRN-1002",
                "dob": datetime(1991, 11, 2),
                "weeks": 28,
                "risk": False,
                "risk_factors": "Singleton pregnancy",
                "bp": (118, 76),
                "fhr": 138,
                "variability": "moderate",
                "risk_score": 0.24,
                "risk_category": "low",
            },
            {
                "email": "julia.morris@demo.local",
                "name": "Julia Morris",
                "mrn": "MRN-1003",
                "dob": datetime(1988, 1, 23),
                "weeks": 38,
                "risk": True,
                "risk_factors": "Multiples; breech presentation",
                "bp": (132, 84),
                "fhr": 148,
                "variability": "minimal",
                "risk_score": 0.67,
                "risk_category": "medium",
            },
        ]

        for index, spec in enumerate(patient_specs, start=1):
            patient_user_result = await session.execute(select(User).where(User.email == spec["email"]))
            patient_user = patient_user_result.scalar_one_or_none()
            if patient_user is None:
                patient_user = User(
                    email=spec["email"],
                    full_name=spec["name"],
                    role=UserRole.PATIENT,
                    hashed_password=hash_password("Demo1234!"),
                    is_active=True,
                )
                session.add(patient_user)
                await session.flush()

            profile_result = await session.execute(
                select(PatientProfile).where(PatientProfile.medical_record_number == spec["mrn"])
            )
            profile = profile_result.scalar_one_or_none()
            if profile is None:
                profile = PatientProfile(
                    user_id=patient_user.id,
                    date_of_birth=spec["dob"],
                    medical_record_number=spec["mrn"],
                    emergency_contact_name="Next of kin",
                    emergency_contact_phone="+1-555-0101",
                    allergies="None",
                    pre_existing_conditions="None",
                )
                session.add(profile)
                await session.flush()

            pregnancy_result = await session.execute(
                select(Pregnancy).where(Pregnancy.patient_profile_id == profile.id)
            )
            pregnancy = pregnancy_result.scalar_one_or_none()
            if pregnancy is None:
                pregnancy = Pregnancy(
                    patient_profile_id=profile.id,
                    gestational_age_weeks=spec["weeks"],
                    expected_due_date=datetime.utcnow() + timedelta(days=(40 - spec["weeks"]) * 7),
                    is_high_risk=spec["risk"],
                    risk_factors=spec["risk_factors"],
                    status="active",
                    started_at=datetime.utcnow() - timedelta(days=60 + index * 10),
                )
                session.add(pregnancy)
                await session.flush()

            vital_exists = await session.execute(
                select(VitalSign).where(VitalSign.pregnancy_id == pregnancy.id)
            )
            if vital_exists.scalars().first() is None:
                session.add_all(
                    [
                        VitalSign(
                            pregnancy_id=pregnancy.id,
                            heart_rate_bpm=86 + index,
                            blood_pressure_systolic=spec["bp"][0],
                            blood_pressure_diastolic=spec["bp"][1],
                            temperature_celsius=36.8,
                            respiratory_rate=18,
                            oxygen_saturation=98,
                            contraction_frequency=2 + index,
                            contraction_duration_sec=40 + index,
                            contraction_intensity="moderate",
                            fetal_heart_rate_bpm=spec["fhr"],
                            fetal_movement_count=8 + index,
                            source="seed",
                            notes="Seeded demo observation",
                            recorded_at=datetime.utcnow() - timedelta(hours=index),
                        ),
                        VitalSign(
                            pregnancy_id=pregnancy.id,
                            heart_rate_bpm=88 + index,
                            blood_pressure_systolic=spec["bp"][0] + 2,
                            blood_pressure_diastolic=spec["bp"][1] + 1,
                            temperature_celsius=36.9,
                            respiratory_rate=19,
                            oxygen_saturation=97,
                            contraction_frequency=3 + index,
                            contraction_duration_sec=44 + index,
                            contraction_intensity="moderate",
                            fetal_heart_rate_bpm=spec["fhr"] + 1,
                            fetal_movement_count=9 + index,
                            source="seed",
                            notes="Second seeded observation",
                            recorded_at=datetime.utcnow() - timedelta(minutes=index * 30),
                        ),
                    ]
                )

            fetal_exists = await session.execute(
                select(FetalMonitoring).where(FetalMonitoring.pregnancy_id == pregnancy.id)
            )
            if fetal_exists.scalars().first() is None:
                session.add(
                    FetalMonitoring(
                        pregnancy_id=pregnancy.id,
                        baseline_fhr=spec["fhr"],
                        variability=spec["variability"],
                        accelerations=2 + index,
                        decelerations="none" if spec["risk_category"] == "low" else "variable",
                        deceleration_type="variable" if spec["risk_category"] != "low" else None,
                        uterine_activity="mild",
                        nst_score=8 if spec["risk_category"] != "high" else 6,
                        biophysical_profile_score=8,
                        signal_file_path=f"demo/signals/{spec['mrn'].lower()}.csv",
                        recorded_at=datetime.utcnow() - timedelta(hours=index),
                    )
                )

            risk_exists = await session.execute(
                select(RiskAssessment).where(RiskAssessment.pregnancy_id == pregnancy.id)
            )
            if risk_exists.scalars().first() is None:
                session.add(
                    RiskAssessment(
                        pregnancy_id=pregnancy.id,
                        c_section_probability=spec["risk_score"],
                        risk_category=spec["risk_category"],
                        risk_factors_identified=spec["risk_factors"],
                        confidence_score=0.91,
                        shap_values='{"bp": 0.31, "fetal_heart_rate": 0.14}',
                        recommended_action="Review with obstetrics team" if spec["risk_category"] != "low" else "Routine follow-up",
                        model_version="demo-heuristic-v1",
                        assessed_at=datetime.utcnow() - timedelta(hours=index),
                    )
                )

        await session.commit()