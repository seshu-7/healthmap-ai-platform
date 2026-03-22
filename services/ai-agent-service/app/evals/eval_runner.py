"""AI Eval Framework — automated tests for agent accuracy.
Scores: correctness, completeness, hallucination, format.
Usage: python -m app.evals.eval_runner --ci --threshold 0.80"""
import json, time, argparse
from app.models.schemas import EvalResult

EVAL_SCENARIOS = [
    {"scenario_id": "EVAL-001", "description": "CKD Stage 4 declining eGFR",
     "patient_data": {"demographics": {"patient_id":"T001","first_name":"John","last_name":"Doe","primary_condition":"CKD","conditions":["CKD","hypertension"]},
      "labs": [{"test_name":"eGFR","value":22.0,"unit":"mL/min","reference_range":">60","is_abnormal":True},
               {"test_name":"Potassium","value":5.8,"unit":"mEq/L","reference_range":"3.5-5.0","is_abnormal":True},
               {"test_name":"Creatinine","value":3.1,"unit":"mg/dL","reference_range":"0.7-1.3","is_abnormal":True}],
      "medications": [{"drug_name":"Lisinopril","dosage":"20mg"},{"drug_name":"Amlodipine","dosage":"10mg"}]},
     "expected_risk_range": [7, 10], "must_mention": ["eGFR","potassium","nephrology"],
     "must_not_mention": ["diabetes","insulin","HbA1c"], "expected_alert": True},
    {"scenario_id": "EVAL-002", "description": "Well-controlled diabetes",
     "patient_data": {"demographics": {"patient_id":"T002","first_name":"Jane","last_name":"Smith","primary_condition":"diabetes","conditions":["diabetes"]},
      "labs": [{"test_name":"HbA1c","value":6.5,"unit":"%","reference_range":"<7.0","is_abnormal":False},
               {"test_name":"eGFR","value":88.0,"unit":"mL/min","reference_range":">60","is_abnormal":False}],
      "medications": [{"drug_name":"Metformin","dosage":"1000mg"}]},
     "expected_risk_range": [1, 4], "must_mention": ["HbA1c","glucose","metformin"],
     "must_not_mention": ["dialysis","urgent","critical"], "expected_alert": False},
    {"scenario_id": "EVAL-003", "description": "Complex: CKD+Diabetes+HF",
     "patient_data": {"demographics": {"patient_id":"T003","first_name":"Robert","last_name":"Johnson","primary_condition":"heart_failure","conditions":["heart_failure","CKD","diabetes"]},
      "labs": [{"test_name":"BNP","value":850.0,"unit":"pg/mL","reference_range":"<100","is_abnormal":True},
               {"test_name":"eGFR","value":35.0,"unit":"mL/min","reference_range":">60","is_abnormal":True},
               {"test_name":"HbA1c","value":8.5,"unit":"%","reference_range":"<7.0","is_abnormal":True},
               {"test_name":"Potassium","value":5.3,"unit":"mEq/L","reference_range":"3.5-5.0","is_abnormal":True}],
      "medications": [{"drug_name":"Carvedilol","dosage":"25mg"},{"drug_name":"Furosemide","dosage":"40mg"},{"drug_name":"Metformin","dosage":"500mg"}]},
     "expected_risk_range": [8, 10], "must_mention": ["BNP","heart failure","eGFR","HbA1c"],
     "must_not_mention": [], "expected_alert": True},
    {"scenario_id": "EVAL-004", "description": "Stable hypertension only",
     "patient_data": {"demographics": {"patient_id":"T004","first_name":"Mary","last_name":"Williams","primary_condition":"hypertension","conditions":["hypertension"]},
      "labs": [{"test_name":"eGFR","value":78.0,"unit":"mL/min","reference_range":">60","is_abnormal":False},
               {"test_name":"Potassium","value":4.2,"unit":"mEq/L","reference_range":"3.5-5.0","is_abnormal":False}],
      "medications": [{"drug_name":"Amlodipine","dosage":"5mg"}]},
     "expected_risk_range": [1, 3], "must_mention": ["blood pressure","amlodipine"],
     "must_not_mention": ["dialysis","critical","insulin"], "expected_alert": False},
    {"scenario_id": "EVAL-005", "description": "Diabetes with worsening kidney",
     "patient_data": {"demographics": {"patient_id":"T005","first_name":"Carlos","last_name":"Garcia","primary_condition":"diabetes","conditions":["diabetes","CKD"]},
      "labs": [{"test_name":"HbA1c","value":9.2,"unit":"%","reference_range":"<7.0","is_abnormal":True},
               {"test_name":"eGFR","value":42.0,"unit":"mL/min","reference_range":">60","is_abnormal":True},
               {"test_name":"uACR","value":350.0,"unit":"mg/g","reference_range":"<30","is_abnormal":True}],
      "medications": [{"drug_name":"Metformin","dosage":"1000mg"},{"drug_name":"Glipizide","dosage":"10mg"}]},
     "expected_risk_range": [7, 9], "must_mention": ["HbA1c","eGFR","kidney","endocrinology"],
     "must_not_mention": ["heart failure","BNP"], "expected_alert": True},
]

def score_correctness(actual, expected_range):
    lo, hi = expected_range
    if lo <= actual <= hi: return 1.0
    return max(0.0, 1.0 - min(abs(actual-lo), abs(actual-hi)) * 0.25)

def score_completeness(text, must_mention):
    if not must_mention: return 1.0
    lower = text.lower()
    return sum(1 for t in must_mention if t.lower() in lower) / len(must_mention)

def detect_hallucination(text, must_not_mention):
    if not must_not_mention: return False
    lower = text.lower()
    return any(t.lower() in lower for t in must_not_mention)

def validate_format(response):
    return all(k in response for k in ["risk_score","risk_level","key_findings","recommendations"])

def run_single_eval(scenario, agent_response):
    text = json.dumps(agent_response, default=str)
    c = score_correctness(agent_response.get("risk_score",5), tuple(scenario["expected_risk_range"]))
    comp = score_completeness(text, scenario["must_mention"])
    hall = detect_hallucination(text, scenario["must_not_mention"])
    fmt = validate_format(agent_response)
    passed = c >= 0.75 and comp >= 0.75 and not hall and fmt
    return EvalResult(scenario_id=scenario["scenario_id"], passed=passed,
        correctness_score=c, completeness_score=comp, hallucination_detected=hall,
        format_valid=fmt, details={
            "description": scenario["description"],
            "expected_risk_range": scenario["expected_risk_range"],
            "actual_risk_score": agent_response.get("risk_score"),
            "missing": [t for t in scenario["must_mention"] if t.lower() not in text.lower()],
            "hallucinated": [t for t in scenario["must_not_mention"] if t.lower() in text.lower()],
        })

def _mock_response(scenario):
    labs = scenario["patient_data"].get("labs", [])
    abnormal = sum(1 for l in labs if l.get("is_abnormal"))
    conds = scenario["patient_data"]["demographics"].get("conditions", [])
    risk = min(10, max(1, abnormal * 2 + len(conds)))
    level = "LOW" if risk <= 3 else "MODERATE" if risk <= 6 else "HIGH" if risk <= 8 else "CRITICAL"
    findings = [f"{l['test_name']} {l['value']} {l['unit']}" for l in labs if l.get("is_abnormal")]
    return {"risk_score": risk, "risk_level": level, "key_findings": findings,
            "recommendations": [f"Monitor {c}" for c in conds],
            "condition_assessments": [{"condition": c, "severity": "moderate"} for c in conds]}

def run_all_evals(agent_fn=None, scenarios=None, ci_mode=False, accuracy_threshold=0.80):
    scenarios = scenarios or EVAL_SCENARIOS
    results, start = [], time.time()
    for s in scenarios:
        resp = agent_fn(s["patient_data"]) if agent_fn else _mock_response(s)
        results.append(run_single_eval(s, resp))
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    rate = passed / total if total else 0
    return {
        "summary": {"total_scenarios": total, "passed": passed, "failed": total-passed,
            "pass_rate": round(rate,3), "threshold": accuracy_threshold,
            "meets_threshold": rate >= accuracy_threshold, "elapsed_seconds": round(time.time()-start,2)},
        "scores": {"avg_correctness": round(sum(r.correctness_score for r in results)/max(total,1),3),
            "avg_completeness": round(sum(r.completeness_score for r in results)/max(total,1),3),
            "hallucination_count": sum(1 for r in results if r.hallucination_detected),
            "format_failures": sum(1 for r in results if not r.format_valid)},
        "results": [{"scenario_id":r.scenario_id,"passed":r.passed,"correctness":r.correctness_score,
            "completeness":r.completeness_score,"hallucination":r.hallucination_detected,
            "format_valid":r.format_valid,"details":r.details} for r in results],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.80)
    args = parser.parse_args()
    report = run_all_evals(accuracy_threshold=args.threshold)
    print("\n" + "="*60 + "\nEVAL REPORT\n" + "="*60)
    print(json.dumps(report["summary"], indent=2))
    for r in report["results"]:
        s = "PASS" if r["passed"] else "FAIL"
        print(f"  [{s}] {r['scenario_id']}: corr={r['correctness']}, comp={r['completeness']}, hall={r['hallucination']}")
    if args.ci and not report["summary"]["meets_threshold"]:
        print(f"\nFAILED: {report['summary']['pass_rate']} < {args.threshold}")
        exit(1)
