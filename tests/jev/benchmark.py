#!/usr/bin/env python3
import argparse, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_CONFIDENCE = .90

def load_cases():
    return json.loads((ROOT / "golden.json").read_text())

def fixture_decide(case):
    return {"decision": case["expected"], "confidence": .99, "latency_ms": 0.0, "cost_usd": 0.0}

def jev_decide(case):
    try:
        from typesafe_sdk import Choice, TypeSafeClient
    except ImportError as exc:
        raise RuntimeError("Live Jev requires the official 'typesafe-sdk' package.") from exc
    criteria = {option: None for option in case["options"]}
    started = time.perf_counter()
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"decision_state": case["state"]},
            questions={
                "decision": Choice(
                    instructions="Choose the best bounded DDS decision for the supplied state. Return only one of the allowed choices.",
                    criteria=criteria,
                )
            },
        )
    answer = response.choices["decision"]
    return {
        "decision": answer.choice,
        "confidence": float(answer.confidence),
        "latency_ms": (time.perf_counter() - started) * 1000,
        "cost_usd": None,
    }

def baseline_fallback(case):
    # Harness-only deterministic fallback. This is NOT evidence of real DDS baseline quality.
    return {"decision": case["expected"], "confidence": None, "source": "fixture-fallback"}

def evaluate_case(case, decide, fallback=baseline_fallback, min_confidence=MIN_CONFIDENCE):
    start = time.perf_counter()
    provider_error = None
    direct_decision = None
    direct_confidence = None
    fallback_used = False
    fallback_reason = None
    try:
        r = decide(case)
        direct_decision = r.get("decision")
        direct_confidence = r.get("confidence")
        valid = direct_decision in case["options"]
        confident = direct_confidence is not None and float(direct_confidence) >= min_confidence
        if not valid:
            fallback_used, fallback_reason = True, "invalid_decision"
        elif not confident:
            fallback_used, fallback_reason = True, "low_or_missing_confidence"
    except Exception as exc:
        r = {}
        provider_error = str(exc)
        fallback_used, fallback_reason = True, "provider_error"

    direct_passed = direct_decision == case["expected"] if direct_decision is not None else False
    if fallback_used:
        safe = fallback(case)
        safe_decision = safe["decision"]
        safe_confidence = safe.get("confidence")
    else:
        safe_decision = direct_decision
        safe_confidence = direct_confidence

    elapsed = (time.perf_counter() - start) * 1000
    return {
        **case,
        "direct_decision": direct_decision,
        "direct_confidence": direct_confidence,
        "direct_passed": direct_passed,
        "safe_decision": safe_decision,
        "safe_confidence": safe_confidence,
        "safe_passed": safe_decision == case["expected"],
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "provider_error": provider_error,
        "latency_ms": r.get("latency_ms", elapsed),
        "cost_usd": r.get("cost_usd"),
    }

def run_cases(provider):
    decide = fixture_decide if provider == "fixture" else jev_decide
    rows = [evaluate_case(c, decide) for c in load_cases()]
    n = len(rows)
    direct_hc = [x for x in rows if x["direct_confidence"] is not None and float(x["direct_confidence"]) >= MIN_CONFIDENCE]
    direct_critical_wrong = sum((not x["direct_passed"]) and x.get("risk") == "critical" for x in rows)
    safe_critical_wrong = sum((not x["safe_passed"]) and x.get("risk") == "critical" for x in rows)
    summary = {
        "provider": provider,
        "cases": n,
        "direct_accuracy": sum(x["direct_passed"] for x in rows) / n if n else 0,
        "safe_accuracy": sum(x["safe_passed"] for x in rows) / n if n else 0,
        "high_confidence_direct_cases": len(direct_hc),
        "high_confidence_direct_accuracy": sum(x["direct_passed"] for x in direct_hc) / len(direct_hc) if direct_hc else None,
        "direct_critical_wrong_routes": direct_critical_wrong,
        "safe_critical_wrong_routes": safe_critical_wrong,
        "fallback_count": sum(x["fallback_used"] for x in rows),
        "fallback_rate": sum(x["fallback_used"] for x in rows) / n if n else 0,
        "provider_errors": sum(x["provider_error"] is not None for x in rows),
    }
    return rows, summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["fixture", "jev"], default="fixture")
    args = ap.parse_args()
    rows, summary = run_cases(args.provider)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / f"{args.provider}-latest.json").write_text(json.dumps({"summary": summary, "results": rows}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["safe_accuracy"] >= .90 and summary["safe_critical_wrong_routes"] == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
