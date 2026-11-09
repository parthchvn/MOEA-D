"""Independent finite-state and trajectory checks for the manuscript-aligned engine."""

from __future__ import annotations

import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sim  # Its neighborhood convention is the only shared legacy component.


@lru_cache
def masks(n: int, operator: str):
    """Literal XOR masks with exact probabilities under one operator invocation."""
    if operator == "one":
        return tuple((1 << i, Fraction(1, n)) for i in range(n))
    return tuple((mask, Fraction((n - 1) ** (n - mask.bit_count()), n**n))
                 for mask in range(1 << n))


def proposals(n, parent, mutation, noise, p):
    for mut, pm in masks(n, mutation):
        child = parent ^ mut
        if p < 1:
            yield child, child, pm * (1 - p)
        if p:
            for err, pe in masks(n, noise):
                yield child, child ^ err, pm * p * pe


def literal_update(n, genomes, labels, recipients, lo, hi, child, observed_copy):
    """Use genotypes and both objective components; offer the same child to all recipients."""
    obs = observed_copy.bit_count()
    ref = (max(hi, obs), max(n - lo, n - obs))

    def cost(slot, weight):
        return max(slot * abs(ref[0] - weight), (n - slot) * abs(ref[1] - (n - weight)))

    new_genomes = list(genomes)
    new_labels = list(labels)
    for slot in recipients:
        if cost(slot, obs) <= cost(slot, labels[slot]):
            new_genomes[slot] = child
            new_labels[slot] = obs
    return (tuple(g.bit_count() for g in new_genomes), tuple(new_labels), n - ref[1], ref[0])


class NeighborhoodKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.binary = Path(cls.temp.name, "sweep")
        subprocess.run(
            [*shlex.split(os.environ.get("CXX", "c++")), "-std=c++17", "-O2",
             str(ROOT / "scripts/neighborhood_sweep.cpp"), "-o", str(cls.binary)],
            check=True, timeout=120,
        )

    def cli(self, *args):
        proc = subprocess.run([str(self.binary), *map(str, args)],
                              capture_output=True, text=True, check=True, timeout=15)
        return json.loads(proc.stdout)

    def step(self, n, size, breeder, truth, labels, lo, hi, child, obs):
        out = self.cli("step", n, size, breeder, ",".join(map(str, truth)),
                       ",".join(map(str, labels)), lo, hi, child, obs)
        return tuple(out["true"]), tuple(out["stored"]), out["lo"], out["hi"]

    def test_cardinality_and_boundary_orientation(self):
        for n in (2, 3, 4, 7):
            for size in range(1, n + 2):
                expected = sim.build_neighborhoods(n, size)
                for breeder in range(n + 1):
                    actual = self.cli("neighbors", n, size, breeder)
                    self.assertEqual(actual, expected[breeder], (n, size, breeder))
                    self.assertEqual(len(actual), len(set(actual)))

    def test_recomputed_cost_ties_and_ungated_neighbors(self):
        # The candidate changes the upper extreme, making weight two an accepted tie.
        self.assertEqual(self.step(3, 1, 2, [0, 1, 1, 1], [0, 1, 1, 1], 0, 1, 2, 2),
                         ((0, 1, 2, 1), (0, 1, 2, 1), 0, 2))
        # Absolute distance at k=1 would accept the tie; Chebyshev costs 3 and 4 reject it.
        self.assertEqual(self.step(3, 1, 1, [0]*4, [0]*4, 0, 3, 2, 2),
                         ((0, 0, 0, 0), (0, 0, 0, 0), 0, 3))
        # An observed extreme updates the reference even when every recipient rejects.
        self.assertEqual(self.step(4, 2, 3, [0,1,2,3,0], [0,1,2,3,0], 0, 3, 4, 4),
                         ((0,1,2,3,0), (0,1,2,3,0), 0, 4))
        # Pinned breeder 1 rejects observation 0, but repairs its neighbor at slot 0.
        self.assertEqual(self.step(3, 3, 1, [2,1,2,3], [0,1,2,3], 0, 3, 0, 0),
                         ((0,1,2,3), (0,1,2,3), 0, 3))

    def test_pinned_and_moving_kernels_against_literal_genotypes(self):
        fixtures = [
            (2, 1, 1, (1,0,3), (0,1,2), 0,2),          # T=1 wrong states
            (2, 3, 1, (1,0,3), (0,1,2), 0,2),          # shared full broadcast
            (3, 2, 2, (1,2,4,5), (1,1,1,2), 1,2),      # moving extrema, even T
            (4, 3, 1, (0,3,5,12,7), (1,1,2,2,3), 1,3), # broadcasting to endpoints
        ]
        p = Fraction(1, 5)
        for n, size, breeder, genomes, labels, lo, hi in fixtures:
            truth = tuple(g.bit_count() for g in genomes)
            recipients = sim.build_neighborhoods(n, size)[breeder]
            outcomes = {}
            for mutation in ("one", "bit"):
                for noise in ("one", "bit"):
                    literal, native = defaultdict(Fraction), defaultdict(Fraction)
                    for child, obs_copy, prob in proposals(n, genomes[breeder], mutation, noise, p):
                        result = literal_update(n, genomes, labels, recipients, lo, hi, child, obs_copy)
                        literal[result] += prob
                        pair = child.bit_count(), obs_copy.bit_count()
                        if pair not in outcomes:
                            outcomes[pair] = self.step(n, size, breeder, truth, labels, lo, hi, *pair)
                        native[outcomes[pair]] += prob
                    self.assertEqual(sum(literal.values()), 1)
                    self.assertEqual(native, literal, (n, size, mutation, noise))

    def test_more_recipients_can_delay_current_exact_assignment(self):
        # Same realized masks; a broadcast changes breeder 1's future parent.
        n = 2
        expected = {1: [(0,0,1), (0,1,1), (0,1,2)],
                    3: [(0,1,1), (0,0,1), (0,2,2)]}
        for size, sequence in expected.items():
            genomes, labels, lo, hi = [0, 0, 1], [0, 0, 1], 0, 1
            for r, mask in enumerate((0b01, 0b01, 0b10)):
                child = genomes[r] ^ mask
                recipients = sim.build_neighborhoods(n, size)[r]
                actual = self.step(n, size, r, [g.bit_count() for g in genomes],
                                   labels, lo, hi, child.bit_count(), child.bit_count())
                projected = literal_update(n, genomes, labels, recipients, lo, hi, child, child)
                self.assertEqual(actual, projected)
                self.assertEqual(actual[0], sequence[r])
                # At p=0 an accepted copy is exactly the child's genotype. For
                # any unchanged weight shared by two genotypes in this explicit
                # path the genotypes coincide, including the tie at breeder 2.
                for k in recipients:
                    if actual[1][k] == child.bit_count():
                        genomes[k] = child
                labels, lo, hi = actual[1:]

    def test_native_sampler_matches_literal_joint_weight_law(self):
        # Same production function as the timed trials, compared against an
        # exact bit-string oracle independent of binomial decomposition. If noise
        # is bitwise, activation is once per evaluation, shared by all bits.
        n, parent, draws = 4, 0b0011, 40000
        for mutation in ("one", "bit"):
            for noise in ("one", "bit"):
                for factor in (0, 1, n):
                    p = Fraction(factor, n)
                    exact = defaultdict(Fraction)
                    for child, obs_copy, chance in proposals(n, parent, mutation, noise, p):
                        exact[child.bit_count(), obs_copy.bit_count()] += chance
                    counts = self.cli("sample", n, parent.bit_count(), factor, 8319, draws,
                                      mutation, noise)
                    self.assertEqual(len(counts), n+1)
                    self.assertTrue(all(len(row) == n+1 for row in counts))
                    self.assertEqual(sum(map(sum, counts)), draws)
                    for y, row in enumerate(counts):
                        for c, count in enumerate(row):
                            self.assertGreaterEqual(count, 0)
                            if exact[y, c] == 0:
                                self.assertEqual(count, 0)
                            else:
                                # Pointwise non-asymptotic binomial concentration;
                                # tolerance is prechosen, not fitted to this seed.
                                self.assertLess(abs(count/draws-float(exact[y,c])),
                                                math.sqrt(math.log(2e10)/(2*draws)),
                                                (mutation, noise, factor, y, c))

    def test_seed_replay_and_boundary_order(self):
        args = (12, 4, 1, 917, 100, "bit", "bit", "uniform", "observed")
        record = self.cli(*args)
        self.assertEqual(record, self.cli(*args))
        self.assertEqual(record["init_evals"], 13)
        self.assertEqual(record["attempts"], 13 * record["sweeps"])
        for earlier, later in (("archive_sweep", "front_sweep"), ("front_sweep", "exact_sweep"),
                               ("U", "S"), ("S", "post_sweep"), ("exact_sweep", "post_sweep")):
            if record[later] is not None:
                self.assertIsNotNone(record[earlier])
                self.assertLessEqual(record[earlier], record[later])
        ideal = self.cli(12, 1, 0, 333, 1, "one", "one", "uniform", "ideal")
        self.assertEqual(ideal["U"], 0)
        self.assertEqual(ideal["init_evals"], 13)
        if ideal["post_sweep"] is None:
            self.assertEqual(ideal["sweeps"], 1)
        if ideal["S"] is not None:
            self.assertEqual(ideal["post_sweep"], ideal["S"])

    def test_first_exact_can_precede_post_stored_target_event(self):
        # At n=2, p=1 the three initial genotype weights are independently
        # Bin(2,1/2); the observed weights are independently redrawn from
        # that same law. True exact and stored not exact has probability
        # (1/32)*(31/32), giving many opportunities even across C++ libraries.
        for seed in range(1024):
            record = self.cli(2, 2, 2, seed, 0, "bit", "bit", "uniform", "observed")
            if record["exact_sweep"] == 0 and record["S"] is None:
                self.assertEqual((record["front_sweep"], record["archive_sweep"]), (0, 0))
                self.assertIsNone(record["post_sweep"])
                return
        self.fail("No true-exact but unpinned initial boundary in the fixed seed bank")

    def test_boundary_zero_and_diagnostic_costs(self):
        result = self.cli(8, 3, 1, 123, 0, "bit", "bit", "corner", "ideal")
        for metric in ("attempts", "init_evals", "sweeps", "comparisons", "external_replacements",
                       "external_changes", "endpoint_repairs_own", "endpoint_repairs_external", "U", "S"):
            self.assertEqual(result[metric], 0, metric)
        for metric in ("front_sweep", "archive_sweep", "exact_sweep", "post_sweep", "first_corner_donor"):
            self.assertIsNone(result[metric], metric)
        for phase in ("U", "S"):
            self.assertEqual(result["bad_at_" + phase], 1)
            self.assertEqual(result["max_error_at_" + phase], 2)

    def test_supplied_corner_law_at_finite_horizon(self):
        # Separate implementation of the analytic survival function: w0=2 is the
        # only mismatch; breeder 1 can repair it iff its broadcast includes slot 0.
        n, cap, repeats = 4, 7, 96
        self_hit = (1 / n)**2 * (1 - 1 / n)**(n-2)
        donor_hit = (1 / n) * (1 - 1 / n)**(n-1)
        for size in (1, 3):
            survival = ((1-self_hit) * (1-donor_hit if size == 3 else 1))**cap
            survivors = 0
            saw_archive_earlier = False
            for index in range(repeats):
                record = self.cli(n, size, 0, 50000+index, cap, "bit", "bit", "corner", "ideal")
                self.assertEqual(record["init_evals"], 0)
                self.assertEqual((record["U"], record["S"]), (0,0))
                self.assertEqual(record["exact_sweep"], record["post_sweep"])
                self.assertEqual(record["front_sweep"], record["exact_sweep"])
                survivors += record["post_sweep"] is None
                self.assertEqual(record["comparisons"], size * record["attempts"])
                self.assertLessEqual(record["external_changes"], record["external_replacements"])
                repaired = record["post_sweep"] is not None
                if record["archive_sweep"] is not None:
                    saw_archive_earlier |= (not repaired or record["archive_sweep"] < record["post_sweep"])
                self.assertEqual(record["endpoint_repairs_own"] + record["endpoint_repairs_external"],
                                 int(repaired))
                if size == 1:
                    self.assertEqual(record["external_replacements"], 0)
                if repaired:
                    self.assertIn(record["first_corner_donor"], (0,) if size == 1 else (0, 1))
                    self.assertEqual(record["endpoint_repairs_external"], int(record["first_corner_donor"] == 1))
                    self.assertEqual(record["sweeps"], record["post_sweep"])
                    self.assertLessEqual(record["archive_sweep"], record["post_sweep"])
                else:
                    self.assertEqual(record["sweeps"], cap)
            if size == 1:
                self.assertTrue(saw_archive_earlier, "Rejected offspring should enter the archive")
            # Seeded Monte Carlo smoke check, not a verification of an asymptotic law.
            self.assertLess(abs(survivors/repeats - survival),
                            math.sqrt(math.log(2e6)/(2*repeats)))


if __name__ == "__main__":
    unittest.main()
