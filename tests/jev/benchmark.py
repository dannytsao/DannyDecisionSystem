#!/usr/bin/env python3
import argparse, json, os, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load_cases():
    return json.loads((ROOT/"golden.json").read_text())

def fixture_decide(case):
    # Harness self-test only: proves metrics/reporting, not Jev quality.
    return {"decision":case["expected"],"confidence":0.99,"latency_ms":0.0,"cost_usd":0.0}

def jev_decide(case):
    endpoint=os.getenv("JEV_API_URL")
    key=os.getenv("JEV_API_KEY")
    if not endpoint or not key:
        raise RuntimeError("Live Jev is fail-closed: set JEV_API_URL and JEV_API_KEY after verifying the current API contract.")
    raise RuntimeError("Implement the verified Jev response adapter before live execution; do not guess the API schema.")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--provider",choices=["fixture","jev"],default="fixture")
    args=ap.parse_args()
    decide=fixture_decide if args.provider=="fixture" else jev_decide
    rows=[]
    for c in load_cases():
        start=time.perf_counter()
        try:
            r=decide(c)
            elapsed=(time.perf_counter()-start)*1000
            actual=r["decision"]; conf=float(r.get("confidence",0))
            passed=actual==c["expected"]
            rows.append({**c,"actual":actual,"confidence":conf,"passed":passed,
                         "latency_ms":r.get("latency_ms",elapsed),"cost_usd":r.get("cost_usd")})
        except Exception as e:
            rows.append({**c,"actual":"ERROR","confidence":None,"passed":False,"error":str(e)})
    n=len(rows); correct=sum(x["passed"] for x in rows)
    hc=[x for x in rows if x["confidence"] is not None and x["confidence"]>=.90]
    hcc=sum(x["passed"] for x in hc)
    critical_wrong=sum((not x["passed"]) and x.get("risk")=="critical" for x in rows)
    summary={"provider":args.provider,"cases":n,"accuracy":correct/n if n else 0,
             "high_confidence_cases":len(hc),"high_confidence_accuracy":hcc/len(hc) if hc else None,
             "critical_wrong_routes":critical_wrong}
    out=ROOT/"results"; out.mkdir(exist_ok=True)
    (out/f"{args.provider}-latest.json").write_text(json.dumps({"summary":summary,"results":rows},indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return 0 if summary["accuracy"]>=.90 and critical_wrong==0 else 1

if __name__=="__main__":
    raise SystemExit(main())
