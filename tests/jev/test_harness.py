#!/usr/bin/env python3
import sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import benchmark

class HarnessTests(unittest.TestCase):
    def test_golden_schema(self):
        cases=benchmark.load_cases()
        self.assertGreaterEqual(len(cases),10)
        for c in cases:
            self.assertIn(c["expected"],c["options"])
            self.assertIn("risk",c)

    def test_fixture_acceptance(self):
        rows,s=benchmark.run_cases("fixture")
        self.assertGreaterEqual(s["direct_accuracy"],.90)
        self.assertGreaterEqual(s["safe_accuracy"],.90)
        self.assertEqual(s["direct_critical_wrong_routes"],0)
        self.assertEqual(s["safe_critical_wrong_routes"],0)
        self.assertEqual(s["fallback_count"],0)

    def test_timeout_fallback(self):
        c=benchmark.load_cases()[0]
        r=benchmark.evaluate_case(c,lambda _: (_ for _ in ()).throw(TimeoutError("timeout")))
        self.assertFalse(r["direct_passed"])
        self.assertTrue(r["safe_passed"])
        self.assertTrue(r["fallback_used"])
        self.assertEqual(r["fallback_reason"],"provider_error")

    def test_invalid_response_fallback(self):
        c=benchmark.load_cases()[0]
        r=benchmark.evaluate_case(c,lambda _: {"decision":"BOGUS","confidence":.99})
        self.assertFalse(r["direct_passed"])
        self.assertTrue(r["safe_passed"])
        self.assertTrue(r["fallback_used"])
        self.assertEqual(r["fallback_reason"],"invalid_decision")

    def test_low_confidence_fallback(self):
        c=benchmark.load_cases()[0]
        r=benchmark.evaluate_case(c,lambda _: {"decision":c["expected"],"confidence":.5})
        self.assertTrue(r["direct_passed"])
        self.assertTrue(r["safe_passed"])
        self.assertTrue(r["fallback_used"])
        self.assertEqual(r["fallback_reason"],"low_or_missing_confidence")

if __name__=="__main__":
    unittest.main()
