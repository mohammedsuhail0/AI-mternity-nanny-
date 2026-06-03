"""
C-Section Risk Prediction Model Training Pipeline

Trains a binary classification model to predict C-section risk based on
maternal and fetal vital signs, demographics, and clinical history.
Targets: >= 95% sensitivity, >= 85% specificity.
"""

import numpy as np
import pandas as pd
import joblib
import os
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, accuracy_score
)
import shap
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Feature columns expected by the model
NUMERIC_FEATURES = [
    "maternal_age", "bmi", "gestational_age_weeks",
    "heart_rate", "systolic_bp", "diastolic_bp",
    "temperature", "respiratory_rate", "spo2",
    "fetal_heart_rate", "fetal_variability",
    "contraction_frequency", "contraction_duration",
    "hemoglobin", "glucose", "creatinine",
]

CATEGORICAL_FEATURES = [
    "has_diabetes", "has_hypertension", "has_preeclampsia",
    "previous_c_section", "is_multiples", "presentation_breech",
]

TARGET = "c_section_required"


def generate_synthetic_dataset(n_samples: int = 10000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic dataset for initial model training and testing.
    In production, replace with real EHR data from the Neon Postgres DB.
    """
    rng = np.random.RandomState(random_state)

    data = pd.DataFrame({
        "maternal_age": rng.normal(30, 5, n_samples).clip(15, 50),
        "bmi": rng.normal(28, 6, n_samples).clip(16, 55),
        "gestational_age_weeks": rng.normal(39, 2, n_samples).clip(24, 42),
        "heart_rate": rng.normal(85, 12, n_samples).clip(50, 160),
        "systolic_bp": rng.normal(115, 18, n_samples).clip(80, 200),
        "diastolic_bp": rng.normal(75, 12, n_samples).clip(40, 140),
        "temperature": rng.normal(37.0, 0.4, n_samples).clip(35.5, 40.0),
        "respiratory_rate": rng.normal(18, 3, n_samples).clip(10, 35),
        "spo2": rng.normal(97, 2, n_samples).clip(70, 100),
        "fetal_heart_rate": rng.normal(140, 12, n_samples).clip(80, 200),
        "fetal_variability": rng.normal(12, 5, n_samples).clip(0, 30),
        "contraction_frequency": rng.exponential(3, n_samples).clip(0, 20),
        "contraction_duration": rng.normal(45, 15, n_samples).clip(15, 120),
        "hemoglobin": rng.normal(12, 2, n_samples).clip(6, 18),
        "glucose": rng.normal(90, 25, n_samples).clip(50, 300),
        "creatinine": rng.normal(0.8, 0.2, n_samples).clip(0.3, 2.5),
        "has_diabetes": rng.choice([0, 1], n_samples, p=[0.85, 0.15]),
        "has_hypertension": rng.choice([0, 1], n_samples, p=[0.80, 0.20]),
        "has_preeclampsia": rng.choice([0, 1], n_samples, p=[0.92, 0.08]),
        "previous_c_section": rng.choice([0, 1], n_samples, p=[0.70, 0.30]),
        "is_multiples": rng.choice([0, 1], n_samples, p=[0.90, 0.10]),
        "presentation_breech": rng.choice([0, 1], n_samples, p=[0.95, 0.05]),
    })

    # Simulate C-section probability based on clinical risk factors
    logit = (
        -3.0
        + 0.03 * data["maternal_age"]
        + 0.05 * data["bmi"]
        - 0.15 * data["gestational_age_weeks"]
        + 0.02 * data["systolic_bp"]
        + 0.03 * data["diastolic_bp"]
        - 0.08 * data["spo2"]
        - 0.03 * data["fetal_heart_rate"]
        - 0.1 * data["fetal_variability"]
        + 0.08 * data["contraction_frequency"]
        + 1.5 * data["has_diabetes"]
        + 1.2 * data["has_hypertension"]
        + 2.5 * data["has_preeclampsia"]
        + 1.8 * data["previous_c_section"]
        + 2.0 * data["is_multiples"]
        + 2.2 * data["presentation_breech"]
        + rng.normal(0, 0.5, n_samples)
    )

    probs = 1 / (1 + np.exp(-logit))
    # Threshold to get ~25% positive rate (typical C-section baseline)
    threshold = np.percentile(probs, 75)
    data[TARGET] = (probs > threshold).astype(int)

    logger.info(f"Generated synthetic dataset: {n_samples} samples, "
                f"positive rate: {data[TARGET].mean():.2%}")
    return data


def train_model(df: pd.DataFrame, model_dir: str = "ml/models"):
    """Train and evaluate the C-section risk prediction model."""
    os.makedirs(model_dir, exist_ok=True)

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    # Split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale numeric features
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[NUMERIC_FEATURES] = scaler.fit_transform(X_train[NUMERIC_FEATURES])
    X_test_scaled[NUMERIC_FEATURES] = scaler.transform(X_test[NUMERIC_FEATURES])

    # Model 1: Gradient Boosting (primary)
    logger.info("Training Gradient Boosting Classifier...")
    gb_model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        random_state=42,
    )
    gb_model.fit(X_train_scaled, y_train)

    # Model 2: Random Forest (ensemble backup)
    logger.info("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train_scaled, y_train)

    # Evaluate both models
    results = {}
    for name, model in [("gradient_boosting", gb_model), ("random_forest", rf_model)]:
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]

        sensitivity = confusion_matrix(y_test, y_pred)[1, 1] / confusion_matrix(y_test, y_pred)[1, :].sum()
        specificity = confusion_matrix(y_test, y_pred)[0, 0] / confusion_matrix(y_test, y_pred)[0, :].sum()

        results[name] = {
            "accuracy": accuracy_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "sensitivity": sensitivity,
            "specificity": specificity,
            "report": classification_report(y_test, y_pred),
        }

        logger.info(f"\n{name.upper()} Results:")
        logger.info(f"  Accuracy:    {results[name]['accuracy']:.4f}")
        logger.info(f"  ROC AUC:     {results[name]['roc_auc']:.4f}")
        logger.info(f"  Sensitivity: {results[name]['sensitivity']:.4f} (target >= 0.95)")
        logger.info(f"  Specificity: {results[name]['specificity']:.4f} (target >= 0.85)")
        logger.info(results[name]["report"])

    # Select best model by sensitivity
    best_name = max(results, key=lambda k: results[k]["sensitivity"])
    best_model = gb_model if best_name == "gradient_boosting" else rf_model
    logger.info(f"Selected best model: {best_name}")

    # Cross-validation on best model
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = cross_validate(
        best_model, X_train_scaled, y_train, cv=cv,
        scoring=["roc_auc", "recall", "precision"],
    )
    logger.info(f"Cross-validation ROC AUC: {cv_results['test_roc_auc'].mean():.4f} (+/- {cv_results['test_roc_auc'].std():.4f})")

    # SHAP explainability
    logger.info("Computing SHAP values for explainability...")
    explainer = shap.TreeExplainer(best_model)
    shap_values = explainer.shap_values(X_test_scaled.head(100))

    # Save artifacts
    artifacts = {
        "model": best_model,
        "scaler": scaler,
        "model_name": best_name,
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "metrics": results[best_name],
        "shap_explainer": explainer,
    }

    model_path = os.path.join(model_dir, "c_section_risk.pkl")
    joblib.dump(artifacts, model_path)
    logger.info(f"Model artifacts saved to {model_path}")

    return artifacts


def predict_risk(patient_data: dict, model_path: str = "ml/models/c_section_risk.pkl") -> dict:
    """
    Predict C-section risk for a single patient.
    Returns prediction, probability, and SHAP explanation.
    """
    artifacts = joblib.load(model_path)
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    explainer = artifacts["shap_explainer"]
    features = artifacts["features"]

    # Build feature vector
    X = pd.DataFrame([patient_data])
    for col in CATEGORICAL_FEATURES:
        if col not in X.columns:
            X[col] = 0
    X = X[features]

    # Scale and predict
    X[NUMERIC_FEATURES] = scaler.transform(X[NUMERIC_FEATURES])
    proba = model.predict_proba(X)[0, 1]
    prediction = int(proba >= 0.65)  # Configurable threshold

    # SHAP explanation
    shap_values = explainer.shap_values(X)
    top_features = sorted(
        zip(features, shap_values[0]),
        key=lambda x: abs(x[1]),
        reverse=True,
    )[:5]

    return {
        "prediction": prediction,
        "probability": float(proba),
        "risk_level": "HIGH" if proba >= 0.65 else ("MODERATE" if proba >= 0.40 else "LOW"),
        "top_risk_factors": [
            {"feature": f, "impact": round(float(impact), 4)}
            for f, impact in top_features
        ],
    }


if __name__ == "__main__":
    logger.info("Starting C-Section Risk Model Training Pipeline")
    df = generate_synthetic_dataset(n_samples=15000)
    artifacts = train_model(df)
    logger.info("Training pipeline complete")
