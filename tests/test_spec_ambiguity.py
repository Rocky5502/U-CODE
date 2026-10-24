"""First-party mathematical oracle-ambiguity checks; no Go code executed."""
import unittest

from ucode.spec_ambiguity import (
    MAX_BALANCE, almost_equal_payout_witness, independent_spec_risks,
)


class SettlementWitnessTests(unittest.TestCase):
    def test_odd_pool_has_two_feasible_almost_equal_assignments(self):
        w = almost_equal_payout_witness(10, (0, 5))
        self.assertEqual(w.actual_loser_deltas, (0, -5))
        self.assertEqual(w.recovered_pool, 5)
        self.assertEqual(set(w.possible_winner_deltas), {(2, 3), (3, 2)})
        self.assertFalse(w.pre_fix_spec_determines_unique_winner_assignment)

    def test_equal_loser_balances_even_pool_has_one_assignment(self):
        w = almost_equal_payout_witness(10, (10, 10))
        self.assertEqual(w.possible_winner_deltas, ((10, 10),))
        self.assertTrue(w.pre_fix_spec_determines_unique_winner_assignment)

    def test_no_loser_balance_no_payout(self):
        w = almost_equal_payout_witness(10, (0, 0))
        self.assertEqual(w.possible_winner_deltas, ((0, 0),))
        self.assertEqual(w.actual_loser_deltas, (0, 0))

    def test_nominal_zero_has_no_payout(self):
        self.assertEqual(almost_equal_payout_witness(
            0, (1, 3)).possible_winner_deltas, ((0, 0),))

    def test_loss_never_exceeds_loser_balance_or_nominal_amount(self):
        for nominal in range(12):
            for first in range(12):
                for second in range(12):
                    w = almost_equal_payout_witness(nominal, (first, second))
                    self.assertEqual(sum(w.actual_loser_deltas),
                                     -w.recovered_pool)
                    for balance, delta in zip((first, second),
                                              w.actual_loser_deltas):
                        self.assertGreaterEqual(balance + delta, 0)
                        self.assertGreaterEqual(delta, -nominal)

    def test_all_candidate_awards_preserve_zero_sum(self):
        for nominal in range(8):
            for x in range(8):
                for y in range(8):
                    w = almost_equal_payout_witness(nominal, (x, y))
                    for a in w.possible_winner_deltas:
                        self.assertEqual(sum(a)+sum(w.actual_loser_deltas), 0)
                        self.assertLessEqual(abs(a[0]-a[1]), 1)

    def test_order_of_loser_balances_does_not_resolve_winner_tiebreak(self):
        self.assertEqual(
            set(almost_equal_payout_witness(20, (0, 5)).possible_winner_deltas),
            set(almost_equal_payout_witness(20, (5, 0)).possible_winner_deltas))

    def test_oddness_iff_two_symmetric_allocations(self):
        for pool in range(12):
            w = almost_equal_payout_witness(pool, (0, pool))
            self.assertEqual(len(w.possible_winner_deltas),
                             2 if pool % 2 else 1)

    def test_reject_negative_or_noninteger_cases(self):
        for nominal, balances in [
            (-1, (1, 2)), (1.0, (1, 2)), (2, (-1, 5)),
            (2, (True, 5)), (1, (1, 2, 3)), (1, [1, 2]),
            (MAX_BALANCE+1, (1, 2)),
        ]:
            with self.subTest(nominal=nominal,balances=balances), self.assertRaises(ValueError):
                almost_equal_payout_witness(nominal, balances)

    def test_large_boundary_avoids_machine_integer_overflow(self):
        w = almost_equal_payout_witness(MAX_BALANCE, (MAX_BALANCE, MAX_BALANCE))
        self.assertEqual(w.recovered_pool, 2*MAX_BALANCE)
        self.assertEqual(w.possible_winner_deltas, ((MAX_BALANCE, MAX_BALANCE),))

    def test_witness_not_a_full_pr_oracle(self):
        w = almost_equal_payout_witness(10, (0, 5))
        risks = independent_spec_risks(w)
        self.assertIn("database_idempotency_and_retry_semantics_not_modelled", risks)
        self.assertIn("odd_remainder_tiebreak_not_determined_by_checked_invariants",
                      risks)
        self.assertIn("authoritative_task_scope_and_oracle_still_unapproved", risks)

    def test_no_fixed_gold_winner_by_order(self):
        w = almost_equal_payout_witness(10, (5, 0))
        self.assertEqual(len(w.possible_winner_deltas), 2)
        self.assertNotEqual(w.possible_winner_deltas[0],
                            w.possible_winner_deltas[1])


if __name__ == "__main__":
    unittest.main()
