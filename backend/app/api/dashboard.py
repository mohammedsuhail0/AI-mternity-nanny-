from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.api.schemas import DashboardAlertResponse, DashboardOverviewResponse, PatientSummaryResponse
from app.db.models import User
from app.db.session import get_db
from app.services.dashboard_service import get_overview_metrics, get_patient_summaries
from dataclasses import asdict


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summaries = await get_patient_summaries(db)
    metrics = get_overview_metrics(summaries)
    return DashboardOverviewResponse(
        total_patients=metrics["total_patients"],
        active_patients=metrics["active_patients"],
        monitoring_patients=metrics["monitoring_patients"],
        high_risk_patients=metrics["high_risk_patients"],
        avg_fetal_heart_rate=metrics["avg_fetal_heart_rate"],
        alerts_count=metrics["alerts_count"],
        recent_patients=[PatientSummaryResponse(**asdict(summary)) for summary in metrics["recent_patients"]],
        alerts=[DashboardAlertResponse(**alert) for alert in metrics["alerts"]],
    )
