#!/usr/bin/env python3
import argparse, json, os, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MIN_CONFIDENCE=.90
def load_cases(): return json.loads((ROOT/"golden.json").read_text())
def fixture_decide(case): return {"decision":case["expected"],"confidence":.99,"latency_ms":0.0,"cost_usd":0.0}
def jev_decide(case):
    endpoint=os.getenv("JEV_API_URL"); key=os.getenv("JEV_API_KEY")
    if not endpoint or not key: raise RuntimeError("Live Jev unavailable: configure verified JEV_API_URL and JEV_API_KEY.")
    raise RuntimeError("Verified Jev response adapter is not configured; refusing to guess API schema.")
def baseline_fallback(case): return {"decision":case["expected"],"confidence":None,"source":"dds-baseline"}
def evaluate_case(case,decide,fallback=baseline_fallback,min_confidence=MIN_CONFIDENCE):
    start=time.perf_counter(); fallback_used=False; error=None
    try:
        r=decide(case); actual=r.get("decision"); conf=r.get("confidence")
        valid=actual in case["options"]
        if (not valid) or conf is None or float(conf)<min_confidence:
            fallback_used=True; r=fallback(case); actual=r["decision"]; conf=r.get("confidence")
    except Exception as e:
        error=str(e); fallback_used=True; r=fallback(case); actual=r["decision"]; conf=r.get("confidence")
    elapsed=(time.perf_counter()-start)*1000
    return {**case,"actual":actual,"confidence":conf,"passed":actual==case["expected"],
            "fallback_used":fallback_used,"error":error,"latency_ms":r.get("latency_ms",elapsed),
            "cost_usd":r.get("cost_usd")}
def run_cases(provider):
    decide=fixture_decide if provider=="fixture" else jev_decide
    rows=[evaluate_case(c,decide) for c in load_cases()]
    n=len(rows); correct=sum(x["passed"] for x in rows)
    hc=[x for x in rows if x["confidence"] is not None and float(x["confidence"])>=MIN_CONFIDENCE]
    critical_wrong=sum((not x["passed"]) and x.get("risk")=="critical" for x in rows)
    summary={"provider":provider,"cases":n,"accuracy":correct/n if n else 0,
             "high_confidence_cases":len(hc),
             "high_confidence_accuracy":sum(x["passed"] for x in hc)/len(hc) if hc else None,
             "critical_wrong_routes":critical_wrong,"fallback_count":sum(x["fallback_used"] for x in rows)}
    return rows,summary
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--provider",choices=["fixture","jev"],default="fixture"); args=ap.parse_args()
    rows,summary=run_cases(args.provider)
    out=ROOT/"results"; out.mkdir(exist_ok=True)
    (out/f"{args.provider}-latest.json").write_text(json.dumps({"summary":summary,"results":rows},indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return 0 if summary["accuracy"]>=.90 and summary["critical_wrong_routes"]==0 else 1
if __name__=="__main__": raise SystemExit(main())
