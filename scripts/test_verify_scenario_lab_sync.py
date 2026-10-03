#!/usr/bin/env python3
"""Tests for verify_scenario_lab_sync.compare."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verify_scenario_lab_sync import compare

REPO = [
    {"entity_id": "a"},
    {"entity_id": "b", "module": "fraud"},
    {"entity_id": "c", "module": "risk_scoring"},
]


class CompareTest(unittest.TestCase):
    def test_reordered_identical_data_matches(self):
        self.assertEqual(compare(REPO, list(reversed(REPO))), [])

    def test_explicit_kyc_equals_missing_module(self):
        live = [{"entity_id": "a", "module": "kyc"}] + REPO[1:]
        self.assertEqual(compare(REPO, live), [])

    def test_missing_id(self):
        out = "\n".join(compare(REPO, REPO[:2]))
        self.assertIn("missing IDs", out)
        self.assertIn("['c']", out)
        self.assertIn("expected total 3", out)

    def test_extra_id(self):
        out = "\n".join(compare(REPO, REPO + [{"entity_id": "d"}]))
        self.assertIn("extra IDs", out)
        self.assertIn("['d']", out)

    def test_same_total_different_ids_is_not_a_count_only_pass(self):
        live = REPO[:2] + [{"entity_id": "z", "module": "risk_scoring"}]
        out = "\n".join(compare(REPO, live))
        self.assertIn("missing IDs", out)
        self.assertIn("extra IDs", out)

    def test_module_mismatch_with_same_ids(self):
        live = [REPO[0], REPO[1], {"entity_id": "c", "module": "fraud"}]
        out = "\n".join(compare(REPO, live))
        self.assertIn("count mismatch", out)
        self.assertNotIn("missing IDs", out)

    def test_duplicate_in_repository_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, r"repository: duplicate entity_id.*'a'"):
            compare(REPO + [{"entity_id": "a"}], REPO)

    def test_duplicate_in_live_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, r"live: duplicate entity_id.*'a'"):
            compare(REPO, REPO + [{"entity_id": "a"}])

    def test_identical_payloads_with_same_duplicate_cannot_pass(self):
        dup = REPO + [{"entity_id": "a"}]
        with self.assertRaises(ValueError):
            compare(dup, list(dup))

    def test_malformed_payloads_raise(self):
        for bad in (None, {}, [], {"cases": REPO}, ["x"], [{"name": "no id"}], [{"entity_id": 5}],
                    [{"entity_id": "a", "module": 3}]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    compare(REPO, bad)


if __name__ == "__main__":
    unittest.main()
