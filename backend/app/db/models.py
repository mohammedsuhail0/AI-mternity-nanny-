import uuid
from datetime import datetime
from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    Text,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    PATIENT = "patient"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.PATIENT
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    date_of_birth: Mapped[datetime] = mapped_column(DateTime)
    medical_record_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50))
    allergies: Mapped[str | None] = mapped_column(Text)
    pre_existing_conditions: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="patient_profile")
    pregnancies = relationship("Pregnancy", back_populates="patient_profile")


class Pregnancy(Base):
    __tablename__ = "pregnancies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id")
    )
    gestational_age_weeks: Mapped[int] = mapped_column(default=0)
    expected_due_date: Mapped[datetime | None] = mapped_column(DateTime)
    is_high_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_factors: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active")
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    patient_profile = relationship("PatientProfile", back_populates="pregnancies")
    vitals = relationship("VitalSign", back_populates="pregnancy")
    fetal_monitoring = relationship("FetalMonitoring", back_populates="pregnancy")
    risk_assessments = relationship("RiskAssessment", back_populates="pregnancy")


class VitalSign(Base):
    __tablename__ = "vital_signs"
    __table_args__ = (
        Index("idx_vitals_pregnancy_timestamp", "pregnancy_id", "recorded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pregnancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pregnancies.id")
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    # Maternal vitals
    heart_rate_bpm: Mapped[int | None] = mapped_column(nullable=True)
    blood_pressure_systolic: Mapped[int | None] = mapped_column(nullable=True)
    blood_pressure_diastolic: Mapped[int | None] = mapped_column(nullable=True)
    temperature_celsius: Mapped[float | None] = mapped_column(nullable=True)
    respiratory_rate: Mapped[int | None] = mapped_column(nullable=True)
    oxygen_saturation: Mapped[int | None] = mapped_column(nullable=True)
    contraction_frequency: Mapped[int | None] = mapped_column(nullable=True)
    contraction_duration_sec: Mapped[int | None] = mapped_column(nullable=True)
    contraction_intensity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Fetal vitals
    fetal_heart_rate_bpm: Mapped[int | None] = mapped_column(nullable=True)
    fetal_movement_count: Mapped[int | None] = mapped_column(nullable=True)
    # Metadata
    source: Mapped[str] = mapped_column(String(50), default="manual")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    pregnancy = relationship("Pregnancy", back_populates="vitals")


class FetalMonitoring(Base):
    __tablename__ = "fetal_monitoring"
    __table_args__ = (
        Index("idx_fetal_pregnancy_timestamp", "pregnancy_id", "recorded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pregnancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pregnancies.id")
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    # CTG / NST data
    baseline_fhr: Mapped[int | None] = mapped_column(nullable=True)
    variability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    accelerations: Mapped[int | None] = mapped_column(nullable=True)
    decelerations: Mapped[str | None] = mapped_column(String(50), nullable=True)
    deceleration_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    uterine_activity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Scoring
    nst_score: Mapped[int | None] = mapped_column(nullable=True)
    biophysical_profile_score: Mapped[int | None] = mapped_column(nullable=True)
    # Raw signal reference
    signal_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pregnancy = relationship("Pregnancy", back_populates="fetal_monitoring")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pregnancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pregnancies.id")
    )
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    # AI predictions
    c_section_probability: Mapped[float] = mapped_column()
    risk_category: Mapped[str] = mapped_column(String(20))
    risk_factors_identified: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column()
    # Explainability
    shap_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Clinical action
    recommended_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_version: Mapped[str] = mapped_column(String(50))

    pregnancy = relationship("Pregnancy", back_populates="risk_assessments")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_user_timestamp", "user_id", "created_at"),
        Index("idx_audit_action", "action"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str | None] = mapped_column(String(100))
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    details: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    user = relationship("User", back_populates="audit_logs")
