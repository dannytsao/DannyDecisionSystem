#!/usr/bin/env python3
"""Executable 4-way benchmark harness.

Adapters exchange JSONL on stdin/stdout. Each input row is a DDS case. Each
output row must contain decision and may contain confidence plus telemetry.
This keeps DDS/Jev validation provider-neutral and prevents fixture results
from being mistaken for measured value.
"""
import argparse, json, os, shlex, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ARMS=("dds_baseline","cheap_llm","jev","hybrid")
METRICS=("latency_ms","llm_calls","tool_calls","search_calls","retries","pipeline_steps","context_tokens","cost_usd")

def load_cases(dataset):
    return json.loads((ROOT/f"{dataset}.json").read_text())

def run_command(command,cases):
    started=time.perf_counter()
    # Labels and retrospective metadata belong to the scorer, never the adapter.
    inputs=[{k:c[k] for k in ("id","gate","state","options","policy_facts") if k in c} for c in cases]
    p=subprocess.run(shlex.split(command),input="\n".join(json.dumps(c) for c in inputs)+"\n",
                     text=True,capture_output=True,timeout=300)
    if p.returncode:
        raise RuntimeError(f"adapter failed ({p.returncode}): {p.stderr[-1000:]}")
    rows=[json.loads(line) for line in p.stdout.splitlines() if line.strip()]
    if len(rows)!=len(cases):
        raise RuntimeError(f"adapter returned {len(rows)} rows for {len(cases)} cases")
    for case,row in zip(cases,rows):
        if not isinstance(row,dict) or row.get("decision") not in (None,*case["options"]):
            raise RuntimeError(f"adapter returned invalid decision for {case['id']}")
    elapsed=(time.perf_counter()-started)*1000
    return rows,elapsed

def score(cases,outputs,elapsed_ms):
    rows=[]; totals={m:0 for m in METRICS}; known={m:0 for m in METRICS}
    for case,out in zip(cases,outputs):
        decision=out.get("decision")
        row={"id":case["id"],"language":case.get("language"),"expected":case["expected"],
             "decision":decision,"passed":decision==case["expected"],"confidence":out.get("confidence")}
        for m in METRICS:
            v=out.get(m); row[m]=v
            if isinstance(v,(int,float)): totals[m]+=v; known[m]+=1
        rows.append(row)
    n=len(rows)
    resolved=sum(r["decision"] is not None for r in rows)
    metrics={"cases":n,"resolved_cases":resolved,"decision_coverage":resolved/n if n else 0,
             "accuracy":sum(r["passed"] for r in rows)/n if resolved==n and n else None,
             "resolved_accuracy":sum(r["passed"] for r in rows)/resolved if resolved else None,
             "critical_wrong_routes":sum(r["decision"] is not None and (not r["passed"]) and c.get("risk")=="critical" for r,c in zip(rows,cases)),
             "wall_latency_ms":elapsed_ms}
    for m in METRICS:
        metrics[m+"_total"]=totals[m] if known[m] else None
        metrics[m+"_mean"]=totals[m]/known[m] if known[m] else None
        metrics[m+"_coverage"]=known[m]/n if n else 0
    slices={}
    for lang in sorted({c.get("language") for c in cases if c.get("language")}):
        subset=[r for r in rows if r["language"]==lang]
        answered=[r for r in subset if r["decision"] is not None]
        slices[lang]={"cases":len(subset),"resolved_cases":len(answered),
                      "accuracy":sum(r["passed"] for r in subset)/len(subset) if len(answered)==len(subset) else None,
                      "resolved_accuracy":sum(r["passed"] for r in answered)/len(answered) if answered else None}
    return rows,metrics,slices

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",choices=["golden","historical"],default="historical")
    ap.add_argument("--arm",choices=ARMS,required=True)
    ap.add_argument("--command",help="Adapter command; otherwise FOURWAY_<ARM>_CMD is used")
    args=ap.parse_args()
    command=args.command or os.getenv(f"FOURWAY_{args.arm.upper()}_CMD")
    if not command:
        print(json.dumps({"arm":args.arm,"status":"not_configured",
          "required_env":f"FOURWAY_{args.arm.upper()}_CMD"}))
        return 2
    cases=load_cases(args.dataset)
    outputs,elapsed=run_command(command,cases)
    rows,metrics,slices=score(cases,outputs,elapsed)
    payload={"arm":args.arm,"dataset":args.dataset,
             "status":"measured" if metrics["decision_coverage"]==1 else "partial_coverage",
             "metrics":metrics,"language_slices":slices,"results":rows}
    out=ROOT/"results"; out.mkdir(exist_ok=True)
    (out/f"four-way-{args.arm}-{args.dataset}.json").write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps({"arm":args.arm,"dataset":args.dataset,"metrics":metrics,"language_slices":slices},indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
