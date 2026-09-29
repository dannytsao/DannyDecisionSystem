#!/usr/bin/env python3
"""Limited executable DDS policy check, not a full DDS Runtime baseline.

Only explicit input facts can trigger hard rules. An unsupported state abstains.
The benchmark scorer owns expected labels and never sends them here.
"""
import json
import sys
import time


def decide(case):
    started=time.perf_counter()
    facts=case.get("policy_facts") or {}
    decision=None
    rule=None
    if facts.get("irreversible_action") is True and facts.get("user_approval") is False:
        decision="HUMAN_APPROVAL"
        rule="explicit_approval"
    elif facts.get("fresh_external_information_required") is True:
        decision="SEARCH" if "SEARCH" in case["options"] else "SEARCH_FIRST"
        rule="fresh_evidence"
    if decision not in case["options"]:
        decision=None
        rule=None
    return {"decision":decision,"rule":rule,"confidence":None,
            "latency_ms":(time.perf_counter()-started)*1000,
            "llm_calls":0,"tool_calls":0,"search_calls":0,"retries":0,
            "pipeline_steps":1 if rule else 0,"context_tokens":0,"cost_usd":0.0}


if __name__=="__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(decide(json.loads(line)),ensure_ascii=False),flush=True)
