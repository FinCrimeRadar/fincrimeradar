#!/usr/bin/env python3
"""Test for check_ledger.py's stale-base claimId-removal guard.

Synthetic case, no real git call: monkeypatches the HEAD ledger read so
check_claim_id_removals() can be exercised against a fixed, fake HEAD.
Confirms it names a deleted claimId, ignores additions, and is clean when
the working tree matches HEAD.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_ledger as cl

HEAD_ENTRIES = [
    {"claimId": "guide-a.claim-one.001"},
    {"claimId": "guide-a.claim-two.001"},
    {"claimId": "guide-b.claim-three.001"},
]


class CheckClaimIdRemovalsTest(unittest.TestCase):
    def test_flags_a_dropped_claim_id(self):
        working = [e for e in HEAD_ENTRIES if e["claimId"] != "guide-b.claim-three.001"]
        with mock.patch.object(cl, "load_head_ledger", return_value=HEAD_ENTRIES):
            missing = cl.check_claim_id_removals(working)
        self.assertEqual(missing, ["guide-b.claim-three.001"])

    def test_does_not_flag_additions(self):
        working = HEAD_ENTRIES + [{"claimId": "guide-c.claim-new.001"}]
        with mock.patch.object(cl, "load_head_ledger", return_value=HEAD_ENTRIES):
            missing = cl.check_claim_id_removals(working)
        self.assertEqual(missing, [])

    def test_clean_when_working_tree_matches_head(self):
        with mock.patch.object(cl, "load_head_ledger", return_value=HEAD_ENTRIES):
            missing = cl.check_claim_id_removals(list(HEAD_ENTRIES))
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
