from pathlib import Path
from fractions import Fraction
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wrra_cross_domain_1_0 import (  # noqa: E402
    GridAction,
    GridState,
    MachineState,
    ScheduleState,
    grid_dc_flows,
    grid_renderer_actions,
    grid_transition,
    run_grid_exact,
    run_scheduling_exact,
    schedule_actions,
    schedule_renderer_actions,
)


class CrossDomainTests(unittest.TestCase):
    def test_dc_balance_and_exact_fraction_arithmetic(self):
        action = GridAction(1, 0, 0, 0)
        flows = grid_dc_flows(3, action)
        self.assertEqual(
            flows,
            (Fraction(5, 3), Fraction(-4, 3), Fraction(1, 3)),
        )

    def test_grid_renderer_never_adds_actions(self):
        state = GridState(0, Fraction(0), Fraction(0), Fraction(0))
        self.assertLessEqual(len(grid_renderer_actions(state)), 16)
        self.assertIsNotNone(grid_transition(state, GridAction(0, 0, 0, 0)))

    def test_grid_exact_cross_check(self):
        result = run_grid_exact()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["renderer_value_mismatches"], 0)
        self.assertGreater(result["residue_sensitive_visible_classes"], 0)

    def test_schedule_renderer_quotients_duplicates(self):
        state = ScheduleState(
            ("A1", "A2", "B1"),
            MachineState(0, "-"),
            MachineState(0, "-"),
        )
        self.assertLess(
            len(schedule_renderer_actions(state)),
            len(schedule_actions(state)),
        )

    def test_scheduling_exact_cross_check(self):
        result = run_scheduling_exact()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["renderer_value_mismatches"], 0)
        self.assertGreater(result["residue_sensitive_visible_classes"], 0)


if __name__ == "__main__":
    unittest.main()
