#!/usr/bin/env python3
import json
import sys

from benchmark import jev_decide


INPUT_FIELDS=("id","gate","state","options","policy_facts")


def build_request(case):
    return {key:case[key] for key in INPUT_FIELDS if key in case}


def decide(case):
    result=jev_decide(build_request(case))
    return {**result,"provider":"jev","llm_calls":1,"tool_calls":0,
            "search_calls":0,"retries":0,"pipeline_steps":1,
            "context_tokens":None}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        case=json.loads(line)
        try:
            result=decide(case)
        except Exception:
            result={"decision":None,"confidence":None,"provider":"jev",
                    "provider_error":"provider_request_failed",
                    "latency_ms":0.0,"llm_calls":1,"tool_calls":0,
                    "search_calls":0,"retries":0,"pipeline_steps":1,
                    "context_tokens":None,"cost_usd":None}
        print(json.dumps(result,ensure_ascii=False),flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
