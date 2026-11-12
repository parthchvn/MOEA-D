"""Bounded regression tests for the independent audit, no research samples."""
from fractions import Fraction as F
import unittest
import audit as a


class AuditTests(unittest.TestCase):
    def test_masks_against_hand_computation(self):
        self.assertEqual(a.masks(2,0),(F(1,4),F(1,2),F(1,4)))
        self.assertEqual(a.masks(3,0),(F(8,27),F(12,27),F(6,27),F(1,27)))

    def test_directed_boundary_and_even_central_hole(self):
        self.assertIn(2,a.recipients(4,3,0))
        self.assertNotIn(0,a.recipients(4,3,2))
        starts=[min(a.recipients(7,4,i)) for i in range(8)]
        self.assertEqual(starts,[0,0,1,1,3,3,4,4])

    def test_drift_at_near_threshold(self):
        result=a.global_check(2,2,F(99,400))
        self.assertEqual(result['states'],81)

    def test_positive_condition_required(self):
        with self.assertRaises(AssertionError):
            a.phase_data(3,4,F(1,5),0,0)

    def test_final_pin_can_also_discover_reference(self):
        result=a.accept(3,3,(3,0,0,0),(1,1,2,3),1,3,0,2,0)
        self.assertEqual(result,((2,0,0,0),(0,1,2,3),0,3))

    def test_prepin_can_update_multiple_slots(self):
        w,b,lo,hi=a.accept(3,4,(0,0,0,0),(0,0,0,0),0,0,0,1,1)
        self.assertGreater(sum(x!=0 for x in b),1)

    def test_counterexamples_have_positive_probability(self):
        witness=a.failures()
        self.assertGreater(F(witness['reinfection']['exact_path_mass']),0)
        self.assertGreater(F(witness['noisy_error_count']['expected_error_increase']),0)
        self.assertEqual(F(witness['phase_omission']['reciprocal_drift']),0)

    def test_full_communication_has_clean_reseeding(self):
        for w in ((3,0,0,0),(1,2,3,0)):
            for phase in range(4):
                row=a.transition(3,4,F(3,4),w,phase)
                self.assertLessEqual(sum(q for v,q in row.items() if not a.seeds(v)),F(3,4))


if __name__=='__main__':
    unittest.main()
