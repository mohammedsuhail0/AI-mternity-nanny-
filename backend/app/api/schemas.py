from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional, Literal


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- Auth ----
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: UUID
    exp: datetime
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=255)


class UserResponse(ORMBaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---- Patient ----
class PatientProfileCreate(BaseModel):
    date_of_birth: datetime
    medical_record_number: str = Field(min_length=1, max_length=50)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    allergies: Optional[str] = None
    pre_existing_conditions: Optional[str] = None


class PatientProfileResponse(ORMBaseModel):
    id: UUID
    user_id: UUID
    date_of_birth: datetime
    medical_record_number: str
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    allergies: Optional[str]
    pre_existing_conditions: Optional[str]


# ---- Pregnancy ----
class PregnancyCreate(BaseModel):
    gestational_age_weeks: int = Field(ge=0, le=45)
    expected_due_date: Optional[datetime] = None
    is_high_risk: bool = False
    risk_factors: Optional[str] = None


class PregnancyResponse(ORMBaseModel):
    id: UUID
    patient_profile_id: UUID
    gestational_age_weeks: int
    expected_due_date: Optional[datetime]
    is_high_risk: bool
    risk_factors: Optional[str]
    status: str
    started_at: datetime
    ended_at: Optional[datetime]


# ---- Vitals ----
class VitalSignCreate(BaseModel):
    heart_rate_bpm: Optional[int] = Field(ge=30, le=220, default=None)
    blood_pressure_systolic: Optional[int] = Field(ge=50, le=260, default=None)
    blood_pressure_diastolic: Optional[int] = Field(ge=30, le=160, default=None)
    temperature_celsius: Optional[float] = Field(ge=30, le=45, default=None)
    respiratory_rate: Optional[int] = Field(ge=5, le=60, default=None)
    oxygen_saturation: Optional[int] = Field(ge=50, le=100, default=None)
    contraction_frequency: Optional[int] = Field(ge=0, default=None)
    contraction_duration_sec: Optional[int] = Field(ge=0, default=None)
    contraction_intensity: Optional[str] = None
    fetal_heart_rate_bpm: Optional[int] = Field(ge=50, le=220, default=None)
    fetal_movement_count: Optional[int] = Field(ge=0, default=None)
    source: str = "manual"
    notes: Optional[str] = None


class VitalSignResponse(ORMBaseModel):
    id: UUID
    pregnancy_id: UUID
    recorded_at: datetime
    heart_rate_bpm: Optional[int]
    blood_pressure_systolic: Optional[int]
    blood_pressure_diastolic: Optional[int]
    temperature_celsius: Optional[float]
    respiratory_rate: Optional[int]
    oxygen_saturation: Optional[int]
    contraction_frequency: Optional[int]
    contraction_duration_sec: Optional[int]
    contraction_intensity: Optional[str]
    fetal_heart_rate_bpm: Optional[int]
    fetal_movement_count: Optional[int]
    source: str
    notes: Optional[str]


# ---- Fetal Monitoring ----
class FetalMonitoringCreate(BaseModel):
    baseline_fhr: Optional[int] = Field(ge=50, le=220, default=None)
    variability: Optional[str] = None
    accelerations: Optional[int] = Field(ge=0, default=None)
    decelerations: Optional[str] = None
    deceleration_type: Optional[str] = None
    uterine_activity: Optional[str] = None
    nst_score: Optional[int] = Field(ge=0, le=10, default=None)
    biophysical_profile_score: Optional[int] = Field(ge=0, le=10, default=None)
    signal_file_path: Optional[str] = None


class FetalMonitoringResponse(ORMBaseModel):
    id: UUID
    pregnancy_id: UUID
    recorded_at: datetime
    baseline_fhr: Optional[int]
    variability: Optional[str]
    accelerations: Optional[int]
    decelerations: Optional[str]
    deceleration_type: Optional[str]
    uterine_activity: Optional[str]
    nst_score: Optional[int]
    biophysical_profile_score: Optional[int]
    signal_file_path: Optional[str]


# ---- Risk Assessment ----
class RiskAssessmentResponse(ORMBaseModel):
    id: UUID
    pregnancy_id: UUID
    assessed_at: datetime
    c_section_probability: float
    risk_category: str
    risk_factors_identified: Optional[str]
    confidence_score: float
    shap_values: Optional[str]
    recommended_action: Optional[str]
    model_version: str


class PatientSummaryResponse(ORMBaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    email: str
    date_of_birth: datetime
    medical_record_number: str
    gestational_age_weeks: Optional[int]
    pregnancy_status: Optional[str]
    is_high_risk: bool
    latest_fetal_heart_rate_bpm: Optional[int]
    latest_blood_pressure_systolic: Optional[int]
    latest_blood_pressure_diastolic: Optional[int]
    latest_risk_category: Optional[str]
    latest_risk_probability: Optional[float]
    latest_recommendation: Optional[str]
    latest_activity_at: Optional[datetime]


class DashboardAlertResponse(BaseModel):
    patient_name: str
    level: str
    message: str
    triggered_at: datetime


class DashboardOverviewResponse(BaseModel):
    total_patients: int
    active_patients: int
    monitoring_patients: int
    high_risk_patients: int
    avg_fetal_heart_rate: Optional[float]
    alerts_count: int
    recent_patients: list[PatientSummaryResponse]
    alerts: list[DashboardAlertResponse]


class CompanionChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list["CompanionChatTurn"] = Field(default_factory=list)
    attachments: list["CompanionAttachment"] = Field(default_factory=list)
    journey: Optional["CompanionJourneyContext"] = None


class CompanionChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class CompanionAttachment(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, max_length=8000)
    mime_type: Optional[str] = Field(default=None, max_length=100)


class CompanionJourneyContext(BaseModel):
    stage_title: Optional[str] = None
    stage_detail: Optional[str] = None
    stage_label: Optional[str] = None


class CompanionChatResponse(BaseModel):
    reply: str
    safety_note: str
    suggested_prompts: list[str]
    action_label: Optional[str] = None
    action_url: Optional[str] = None


# ---- Alert ----
class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertResponse(ORMBaseModel):
    id: UUID
    pregnancy_id: UUID
    level: AlertLevel
    message: str
    triggered_at: datetime
    acknowledged: bool
