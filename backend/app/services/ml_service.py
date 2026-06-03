import joblib
import numpy as np
import structlog
from pathlib import Path
from typing import Optional

from app.core.config import Settings

logger = structlog.get_logger()


class MLService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = None
        self.load_model()

    def load_model(self) -> None:
        model_path = Path(self.settings.MODEL_PATH)
        if model_path.exists():
            self.model = joblib.load(model_path)
            logger.info("ml_model_loaded", path=str(model_path))
        else:
            logger.warning("ml_model_not_found", path=str(model_path))

    def predict_risk(
        self,
        maternal_age: float,
        gestational_weeks: float,
        blood_pressure_systolic: float,
        blood_pressure_diastolic: float,
        heart_rate: float,
        fetal_heart_rate: float,
        has_gestational_diabetes: bool,
        has_preeclampsia: bool,
        previous_c_section: bool,
    ) -> dict:
        if self.model is None:
            return {"risk_score": 0.0, "risk_level": "unknown", "can_predict": False}

        features = np.array([[
            maternal_age,
            gestational_weeks,
            blood_pressure_systolic,
            blood_pressure_diastolic,
            heart_rate,
            fetal_heart_rate,
            float(has_gestational_diabetes),
            float(has_preeclampsia),
            float(previous_c_section),
        ]])

        probability = float(self.model.predict_proba(features)[0][1])
        prediction = probability >= self.settings.PREDICTION_THRESHOLD

        if probability >= 0.8:
            risk_level = "high"
        elif probability >= 0.5:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_score": round(probability, 4),
            "risk_level": risk_level,
            "prediction": prediction,
            "can_predict": True,
        }

    def get_feature_importance(self) -> Optional[dict]:
        if self.model is None or not hasattr(self.model, "feature_importances_"):
            return None

        feature_names = [
            "maternal_age",
            "gestational_weeks",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "heart_rate",
            "fetal_heart_rate",
            "has_gestational_diabetes",
            "has_preeclampsia",
            "previous_c_section",
        ]

        importances = self.model.feature_importances_
        return {name: float(imp) for name, imp in zip(feature_names, importances)}
