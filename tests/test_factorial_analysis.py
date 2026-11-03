import unittest

from scripts.analyze_factorial import analyze


class FactorialAnalysisTests(unittest.TestCase):
    def records(self):
        rows = []
        for radius in (0, 1, 3):
            for mutation in ("exact", "lazy"):
                base = (200 if mutation == "exact" else 120) if radius == 1 else 100
                for value in (base, base * 2, base * 3):
                    rows.append(dict(n=8, radius=radius, mutation=mutation,
                                     seed=len(rows), archive_evaluations=value,
                                     alignment_evaluations=value * 2, evaluations=value * 2,
                                     observation_evaluations=value * 2,
                                     archive_censored=False, alignment_censored=False))
        return rows

    def test_known_radius_ratios_and_paired_endpoint_resampling(self):
        result = analyze(self.records(), bootstrap=1000)
        contrasts = result["contrasts"]["8"]
        self.assertAlmostEqual(contrasts["R"]["exact_archive"]["estimate"], 2)
        self.assertAlmostEqual(contrasts["R"]["lazy_archive"]["estimate"], 1.2)
        # Alignment is exactly twice archive on each trajectory. Preserving the
        # endpoint pair makes the radius attenuation exactly zero in every draw.
        self.assertEqual(contrasts["contrasts"]["S_exact"]["ci95"], [0.0, 0.0])
        self.assertEqual(contrasts["contrasts"]["S_lazy"]["ci95"], [0.0, 0.0])

    def test_censoring_prevents_unconditional_contrast(self):
        rows = self.records()
        rows[6]["alignment_evaluations"] = None
        rows[6]["alignment_censored"] = True
        result = analyze(rows, bootstrap=100)
        self.assertIn("inconclusive", result["contrasts"]["8"]["status"])
        cell = result["cells"]["n=8,r=1,mutation=exact"]
        self.assertIsNone(cell["events"]["alignment"]["mean_ci95"])
        self.assertEqual(cell["events"]["alignment"]["censored"], 1)

    def test_duplicate_seeds_are_rejected(self):
        rows = self.records()
        rows[1]["seed"] = rows[0]["seed"]
        with self.assertRaises(ValueError):
            analyze(rows, bootstrap=100)


if __name__ == "__main__":
    unittest.main()
