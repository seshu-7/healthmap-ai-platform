"""Deterministic business scoring for onboarding risk.

This module computes risk_score and risk_level from explicit rules so the
numeric outcome is auditable and versioned.
"""

from __future__ import annotations

from typing import Any


SCORING_POLICY_VERSION = "healthmap-v1"


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_lab_value(labs: list[dict], names: tuple[str, ...]) -> float | None:
    for lab in labs:
        test_name = str(lab.get("test_name") or lab.get("testName") or "").strip().lower()
        if not test_name:
            continue
        if any(test_name == name or name in test_name for name in names):
            value = _to_float(lab.get("value"))
            if value is not None:
                return value
    return None


def _risk_level(score: int) -> str:
    if score <= 3:
        return "LOW"
    if score <= 6:
        return "MODERATE"
    if score <= 8:
        return "HIGH"
    return "CRITICAL"


def score_patient_risk(
    demographics: dict,
    labs: list[dict],
    medications: list[dict],
    guidelines: list[dict],
) -> dict:
    """Compute deterministic risk score and rule-derived recommendations."""
    findings: list[str] = []
    recommendations: list[str] = []
    scoring_factors: list[dict] = []
    data_gaps: list[str] = []

    score = 1

    egfr = _find_lab_value(labs, ("egfr", "estimated glomerular filtration rate"))
    potassium = _find_lab_value(labs, ("potassium", "k"))
    phosphorus = _find_lab_value(labs, ("phosphorus", "phosphate"))
    hemoglobin = _find_lab_value(labs, ("hemoglobin", "hgb"))
    creatinine = _find_lab_value(labs, ("creatinine",))

    if egfr is None:
        data_gaps.append("Missing eGFR")
    elif egfr <= 15:
        score += 4
        scoring_factors.append({"factor": "eGFR<=15", "points": 4, "value": egfr})
        findings.append(f"Severe renal failure risk: eGFR {egfr:.1f} mL/min (<=15)")
        recommendations.append("Immediate nephrology escalation and dialysis planning")
    elif egfr <= 30:
        score += 3
        scoring_factors.append({"factor": "eGFR<=30", "points": 3, "value": egfr})
        findings.append(f"Advanced CKD risk: eGFR {egfr:.1f} mL/min (<=30)")
        recommendations.append("Urgent nephrology follow-up and CKD stage 4/5 care plan")
    elif egfr <= 45:
        score += 2
        scoring_factors.append({"factor": "eGFR<=45", "points": 2, "value": egfr})
        findings.append(f"Moderate CKD burden: eGFR {egfr:.1f} mL/min")

    if potassium is None:
        data_gaps.append("Missing potassium")
    elif potassium >= 6.0:
        score += 4
        scoring_factors.append({"factor": "potassium>=6.0", "points": 4, "value": potassium})
        findings.append(f"Critical hyperkalemia: potassium {potassium:.1f} mEq/L")
        recommendations.append("Same-day urgent hyperkalemia management")
    elif potassium >= 5.5:
        score += 3
        scoring_factors.append({"factor": "potassium>=5.5", "points": 3, "value": potassium})
        findings.append(f"High-risk hyperkalemia: potassium {potassium:.1f} mEq/L")
        recommendations.append("Urgent medication review for hyperkalemia contributors")

    if phosphorus is not None and phosphorus > 4.5:
        score += 1
        scoring_factors.append({"factor": "phosphorus>4.5", "points": 1, "value": phosphorus})
        findings.append(f"Hyperphosphatemia present: phosphorus {phosphorus:.1f} mg/dL")
        recommendations.append("Consider phosphate-binder evaluation")

    if hemoglobin is not None and hemoglobin < 10.0:
        score += 1
        scoring_factors.append({"factor": "hemoglobin<10", "points": 1, "value": hemoglobin})
        findings.append(f"Anemia risk signal: hemoglobin {hemoglobin:.1f} g/dL")
        recommendations.append("Assess for CKD-related anemia management")

    if creatinine is not None and creatinine >= 3.0:
        score += 1
        scoring_factors.append({"factor": "creatinine>=3.0", "points": 1, "value": creatinine})
        findings.append(f"Renal injury marker elevated: creatinine {creatinine:.1f} mg/dL")

    med_names = [
        str(m.get("drug_name") or m.get("drugName") or "").strip().lower()
        for m in medications
    ]
    has_raas = any(any(x in med for x in ("lisinopril", "enalapril", "losartan", "valsartan")) for med in med_names)
    if has_raas and potassium is not None and potassium >= 5.5:
        score += 1
        scoring_factors.append({"factor": "raas_with_hyperkalemia", "points": 1, "value": potassium})
        findings.append("RAAS medication present with hyperkalemia risk")
        recommendations.append("Review ACEi/ARB risk-benefit in current potassium context")

    age = _to_float(demographics.get("age"))
    if age is None:
        dob = str(demographics.get("date_of_birth") or "")
        if dob and len(dob) >= 4:
            # A coarse fallback if explicit age is unavailable.
            try:
                birth_year = int(dob[:4])
                age = max(0.0, 2026.0 - birth_year)
            except ValueError:
                age = None
    if age is not None and age >= 75:
        score += 1
        scoring_factors.append({"factor": "age>=75", "points": 1, "value": age})
        findings.append(f"Age vulnerability factor: {int(age)} years")

    if not guidelines:
        data_gaps.append("No guideline snippets retrieved")

    score = max(1, min(score, 10))
    level = _risk_level(score)

    if not findings:
        findings.append("No severe deterministic risk triggers detected from available data")
    if not recommendations:
        recommendations.append("Continue routine monitoring and reassess with new labs")

    primary_condition = demographics.get("primary_condition") or demographics.get("primaryCondition") or "general"
    condition_assessments = [
        {
            "condition": str(primary_condition),
            "severity": level,
            "key_indicators": [f["factor"] for f in scoring_factors] or ["no_major_triggers"],
        }
    ]

    return {
        "risk_score": score,
        "risk_level": level,
        "condition_assessments": condition_assessments,
        "key_findings": findings,
        "recommendations": list(dict.fromkeys(recommendations)),
        "data_gaps": data_gaps,
        "scoring_factors": scoring_factors,
        "scoring_policy_version": SCORING_POLICY_VERSION,
    }
