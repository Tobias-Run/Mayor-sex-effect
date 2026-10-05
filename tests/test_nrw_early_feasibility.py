"""Check precision mathematics against independent distributions/simulation."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
AVAILABLE = all(importlib.util.find_spec(x) for x in ["numpy", "scipy"])
if AVAILABLE:
    import numpy as np
    from scipy.stats import nct, t
    from nrw_early_feasibility import (design_support, gaussian_t_mde,
                                     gaussian_t_power, optimistic_options)


@unittest.skipUnless(AVAILABLE, "Optional feasibility dependencies not installed")
class EarlyFeasibilityTests(unittest.TestCase):
    def test_null_size_including_one_election_group(self):
        for n1, n0 in [(1, 2), (1, 3), (3, 3), (22, 23), (300, 300)]:
            for alpha in [.05, .025]:
                self.assertAlmostEqual(gaussian_t_power(0, n1, n0, alpha), alpha, places=8)

    def test_power_matches_noncentral_t_reference(self):
        for n1, n0, effect in [(2, 4, 1), (3, 3, 2), (22, 23, .8)]:
            df = n1+n0-2
            critical = t.ppf(.975, df)
            ncp = effect/math.sqrt(1/n1+1/n0)
            expected = nct.cdf(-critical, df, ncp)+nct.sf(critical, df, ncp)
            self.assertAlmostEqual(gaussian_t_power(effect, n1, n0), expected, places=7)

    def test_mde_against_raw_outcome_monte_carlo(self):
        # Compute rejection frequencies from simulated group samples, rather
        # than reusing the numerical integration or noncentral-t formula.
        rng = np.random.default_rng(20261005)
        n1, n0, repetitions = 3, 3, 50000
        effect = gaussian_t_mde(n1, n0)
        a = rng.normal(effect, 1, size=(repetitions, n1))
        b = rng.normal(0, 1, size=(repetitions, n0))
        pooled = (((a-a.mean(axis=1, keepdims=True))**2).sum(axis=1)
                  + ((b-b.mean(axis=1, keepdims=True))**2).sum(axis=1))/(n1+n0-2)
        statistic = (a.mean(axis=1)-b.mean(axis=1))/np.sqrt(pooled*(1/n1+1/n0))
        power = np.mean(np.abs(statistic) > t.ppf(.975, n1+n0-2))
        self.assertLess(abs(power-.8), .01)

    def test_rank_exposes_insufficient_side_support(self):
        one_winner = design_support([.7, -.4, -.9, -1.2])
        self.assertLess(one_winner["linear_rank"], one_winner["linear_columns"])
        two_winners = design_support([.7, 4.8, -.4, -.9, -1.2, -5.1])
        self.assertEqual(two_winners["linear_rank"], 4)
        self.assertEqual(two_winners["quadratic_rank"], 5)

    def test_upper_bound_respects_supported_label_without_imputing(self):
        labels = [None, "female"]
        self.assertEqual(optimistic_options(labels, 1), {True})
        self.assertEqual(labels, [None, "female"])
        self.assertEqual(optimistic_options(["male", "male"], 0), set())
        self.assertEqual(optimistic_options([None, None], 0), {True, False})

    def test_absent_cutoff_side_is_not_an_estimate(self):
        with self.assertRaises(ValueError):
            gaussian_t_power(1, 0, 2)


if __name__ == "__main__":
    unittest.main()
