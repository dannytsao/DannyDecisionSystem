#!/usr/bin/env python3
"""Shadow-only policy → Jev → LLM chain using JSONL provider commands."""
import json
import os
import shlex
import subprocess
import sys
import time

from dds_policy_adapter import decide as policy_decide

THRESHOLD = 0.90


def invoke(command, case):
    if not command:
        return None
    try:
        run = subprocess.run(shlex.split(command), input=json.dumps(case) + "\n",
                             text=True, capture_output=True, timeout=30, check=True)
        lines = run.stdout.splitlines()
        if len(lines) != 1:
            return None
        result = json.loads(lines[0])
        if not isinstance(result, dict) or result.get("decision") not in case["options"]:
            return None
        return result
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def decide(case, jev=None, llm=None):
    start = time.perf_counter()
    policy = policy_decide(case)
    if policy["decision"] is not None:
        return {**policy, "route": "hard_rule", "fallback_used": False}

    jev_result = jev(case) if jev else None
    if jev_result and jev_result.get("decision") in case["options"]:
        try:
            confident = float(jev_result.get("confidence")) >= THRESHOLD
        except (TypeError, ValueError):
            confident = False
        if confident:
            return {**jev_result, "route": "jev", "fallback_used": False,
                    "latency_ms": (time.perf_counter() - start) * 1000}

    llm_result = llm(case) if llm else None
    if llm_result and llm_result.get("decision") in case["options"]:
        return {**llm_result, "route": "llm_fallback", "fallback_used": True,
                "latency_ms": (time.perf_counter() - start) * 1000}
    return {"decision": None, "confidence": None, "route": "unresolved",
            "fallback_used": True, "latency_ms": (time.perf_counter() - start) * 1000,
            "cost_usd": None}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            case = json.loads(line)
            result = decide(
                case,
                jev=lambda c: invoke(os.getenv("HYBRID_JEV_CMD"), c),
                llm=lambda c: invoke(os.getenv("HYBRID_LLM_CMD"), c),
            )
            print(json.dumps(result, ensure_ascii=False), flush=True)
