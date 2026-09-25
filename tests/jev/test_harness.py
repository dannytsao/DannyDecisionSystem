#!/usr/bin/env python3
import json, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import benchmark

def case(case_id):
    return next(c for c in benchmark.load_cases() if c["id"] == case_id)

class HarnessTests(unittest.TestCase):
    def test_golden_schema(self):
        cases=benchmark.load_cases()
        self.assertGreaterEqual(len(cases),10)
        for c in cases:
            self.assertIn(c["expected"],c["options"])
            self.assertIn("risk",c)

    def test_fixture_acceptance(self):
        rows,s,_=benchmark.run_cases("fixture")
        self.assertGreaterEqual(s["direct_accuracy"],.90)
        self.assertGreaterEqual(s["safe_accuracy"],.90)
        self.assertEqual(s["direct_critical_wrong_routes"],0)
        self.assertEqual(s["safe_critical_wrong_routes"],0)
        self.assertEqual(s["fallback_count"],0)

    def test_timeout_fallback(self):
        c=case("T01")
        r=benchmark.evaluate_case(c,lambda _: (_ for _ in ()).throw(TimeoutError("timeout")))
        self.assertFalse(r["direct_passed"]); self.assertTrue(r["safe_passed"])
        self.assertTrue(r["fallback_used"]); self.assertEqual(r["fallback_reason"],"provider_error")

    def test_invalid_response_fallback(self):
        c=case("T01")
        r=benchmark.evaluate_case(c,lambda _: {"decision":"BOGUS","confidence":.99})
        self.assertFalse(r["direct_passed"]); self.assertTrue(r["safe_passed"])
        self.assertTrue(r["fallback_used"]); self.assertEqual(r["fallback_reason"],"invalid_decision")

    def test_low_confidence_fallback(self):
        c=case("T01")
        r=benchmark.evaluate_case(c,lambda _: {"decision":c["expected"],"confidence":.5})
        self.assertTrue(r["direct_passed"]); self.assertTrue(r["safe_passed"])
        self.assertTrue(r["fallback_used"]); self.assertEqual(r["fallback_reason"],"low_or_missing_confidence")

    # S04/S05: deterministic DDS authority/evidence policy must not be delegated.
    def test_s04_hard_rule_authority_preserved(self):
        c=case("T11")
        self.assertEqual(c.get("engine_expected"),"HARD_RULE")
        self.assertEqual(c["expected"],"HUMAN_APPROVAL")

    def test_s05_fresh_evidence_policy_preserved(self):
        c=case("T12")
        self.assertEqual(c.get("engine_expected"),"HARD_RULE")
        self.assertEqual(c["expected"],"SEARCH")

    # S06-S09: bounded routing gates must preserve expected outcomes.
    def test_s06_false_finish_guard(self):
        c=case("T05"); self.assertEqual(c["expected"],"CONTINUE")
        self.assertTrue(benchmark.evaluate_case(c,benchmark.fixture_decide)["safe_passed"])

    def test_s07_wasteful_continue_guard(self):
        c=case("T06"); self.assertEqual(c["expected"],"FINISH")
        self.assertTrue(benchmark.evaluate_case(c,benchmark.fixture_decide)["safe_passed"])

    def test_s08_fast_path_routing(self):
        c=case("T07"); self.assertEqual(c["expected"],"FAST_PATH")
        self.assertTrue(benchmark.evaluate_case(c,benchmark.fixture_decide)["safe_passed"])

    def test_s09_deep_reasoning_routing(self):
        c=case("T08"); self.assertEqual(c["expected"],"DEEP_REASONING")
        self.assertTrue(benchmark.evaluate_case(c,benchmark.fixture_decide)["safe_passed"])

    # S10: metrics required to compare provider quality vs safe DDS behavior.
    def test_s10_total_task_metrics_schema(self):
        _,s,_=benchmark.run_cases("fixture")
        required={"direct_accuracy","safe_accuracy","high_confidence_direct_accuracy",
                  "direct_critical_wrong_routes","safe_critical_wrong_routes",
                  "fallback_count","fallback_rate","provider_errors"}
        self.assertTrue(required.issubset(s))

    def test_historical_dataset_schema(self):
        data=json.loads((ROOT/"historical.json").read_text())
        self.assertGreaterEqual(len(data),30)
        languages=set()
        for c in data:
            self.assertIn(c["expected"],c["options"])
            self.assertIn(c["language"],{"en","zh-TW","mixed"})
            self.assertIn("source_type",c)
            languages.add(c["language"])
        self.assertEqual(languages,{"en","zh-TW","mixed"})

if __name__=="__main__":
    unittest.main()
