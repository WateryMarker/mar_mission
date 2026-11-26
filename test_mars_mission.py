"""Unit tests for MARS 2099 (mars_mission.py)."""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import mars_mission


def make_stats(**overrides):
    stats = {
        "oxygen": 80,
        "energy": 60,
        "hull": 70,
        "samples": 0,
        "supply_kit": True,
    }
    stats.update(overrides)
    return stats


class TestResourceManagement(unittest.TestCase):
    def test_change_resource_clamps_to_0_and_100(self):
        stats = make_stats(oxygen=90, energy=10)
        mars_mission.change_resource(stats, "oxygen", 25)
        mars_mission.change_resource(stats, "energy", -30)
        self.assertEqual(stats["oxygen"], 100)
        self.assertEqual(stats["energy"], 0)


class TestPerformAction(unittest.TestCase):
    def test_explore_success(self):
        stats = make_stats()
        with patch("mars_mission.random.randint", return_value=2), redirect_stdout(io.StringIO()):
            ok = mars_mission.perform_action("1", stats)
        self.assertTrue(ok)
        self.assertEqual(stats["oxygen"], 65)
        self.assertEqual(stats["energy"], 52)
        self.assertEqual(stats["samples"], 2)

    def test_explore_insufficient_resources(self):
        stats = make_stats(oxygen=10, energy=50)
        with redirect_stdout(io.StringIO()):
            ok = mars_mission.perform_action("1", stats)
        self.assertFalse(ok)
        self.assertEqual(stats["oxygen"], 10)
        self.assertEqual(stats["samples"], 0)

    def test_repair_hull_caps_at_100(self):
        stats = make_stats(hull=90)
        with redirect_stdout(io.StringIO()):
            ok = mars_mission.perform_action("2", stats)
        self.assertTrue(ok)
        self.assertEqual(stats["oxygen"], 75)
        self.assertEqual(stats["energy"], 48)
        self.assertEqual(stats["hull"], 100)

    def test_charge_solar_success(self):
        stats = make_stats(energy=60)
        with redirect_stdout(io.StringIO()):
            ok = mars_mission.perform_action("3", stats)
        self.assertTrue(ok)
        self.assertEqual(stats["oxygen"], 72)
        self.assertEqual(stats["energy"], 85)

    def test_supply_kit_one_time_use(self):
        stats = make_stats(oxygen=50, energy=50, supply_kit=True)
        with redirect_stdout(io.StringIO()):
            first = mars_mission.perform_action("4", stats)
            second = mars_mission.perform_action("4", stats)
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertFalse(stats["supply_kit"])
        self.assertEqual(stats["oxygen"], 70)
        self.assertEqual(stats["energy"], 70)


class TestTriggerEvent(unittest.TestCase):
    def test_storm_event_choices(self):
        stats1 = make_stats()
        with patch("mars_mission.random.choice", return_value=("พายุฝุ่นกำลังเข้าใกล้", "storm")), \
             patch("builtins.input", return_value="1"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats1)
        self.assertEqual(stats1["oxygen"], 75)

        stats2 = make_stats()
        with patch("mars_mission.random.choice", return_value=("พายุฝุ่นกำลังเข้าใกล้", "storm")), \
             patch("builtins.input", return_value="2"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats2)
        self.assertEqual(stats2["hull"], 58)
        self.assertEqual(stats2["samples"], 1)

    def test_ice_event_choices(self):
        stats1 = make_stats()
        with patch("mars_mission.random.choice", return_value=("ตรวจพบน้ำแข็งใต้พื้นผิว", "ice")), \
             patch("builtins.input", return_value="1"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats1)
        self.assertEqual(stats1["energy"], 54)
        self.assertEqual(stats1["oxygen"], 92)
        self.assertEqual(stats1["samples"], 1)

        stats2 = make_stats()
        with patch("mars_mission.random.choice", return_value=("ตรวจพบน้ำแข็งใต้พื้นผิว", "ice")), \
             patch("builtins.input", return_value="2"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats2)
        self.assertEqual(stats2["energy"], 50)
        self.assertEqual(stats2["oxygen"], 100)
        self.assertEqual(stats2["hull"], 62)

    def test_signal_event_choices(self):
        stats1 = make_stats()
        with patch("mars_mission.random.choice", return_value=("มีสัญญาณเรียก Wi-Fi", "signal")), \
             patch("builtins.input", return_value="1"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats1)
        self.assertEqual(stats1["energy"], 72)

        stats2 = make_stats()
        with patch("mars_mission.random.choice", return_value=("มีสัญญาณเรียก Wi-Fi", "signal")), \
             patch("builtins.input", return_value="2"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats2)
        self.assertEqual(stats2["energy"], 60)

    def test_solar_event_choices(self):
        stats1 = make_stats()
        with patch("mars_mission.random.choice", return_value=("เกิดแสงอาทิตย์ปะทุ", "solar")), \
             patch("builtins.input", return_value="1"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats1)
        self.assertEqual(stats1["energy"], 75)

        stats2 = make_stats()
        with patch("mars_mission.random.choice", return_value=("เกิดแสงอาทิตย์ปะทุ", "solar")), \
             patch("builtins.input", return_value="2"), \
             redirect_stdout(io.StringIO()):
            mars_mission.trigger_event(stats2)
        self.assertEqual(stats2["energy"], 52)
        self.assertEqual(stats2["hull"], 80)


class TestFinishMission(unittest.TestCase):
    def run_finish(self, stats, failed=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            mars_mission.finish_mission(stats, failed=failed)
        return buf.getvalue()

    def test_ranks(self):
        self.assertIn("RANK: S", self.run_finish(make_stats(samples=3, oxygen=60, energy=60, hull=60)))
        self.assertIn("RANK: A", self.run_finish(make_stats(samples=3, oxygen=30, energy=30, hull=30)))
        self.assertIn("RANK: B", self.run_finish(make_stats(samples=3, oxygen=10, energy=10, hull=10)))
        self.assertIn("RANK: C", self.run_finish(make_stats(samples=1, oxygen=50, energy=50, hull=50)))
        self.assertIn("RANK: D", self.run_finish(make_stats(samples=0, oxygen=10, energy=10, hull=10)))
        self.assertIn("RANK: F", self.run_finish(make_stats(oxygen=0), failed=True))


class TestMainGameFlow(unittest.TestCase):
    def test_full_5_day_mission_success(self):
        # 5 days: each day pick action "1" (explore) and event choice "1"
        inputs = ["9", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"]
        buf = io.StringIO()
        with patch("builtins.input", side_effect=inputs), \
             patch("mars_mission.random.randint", return_value=1), \
             patch("mars_mission.random.choice", return_value=("มีสัญญาณเรียก Wi-Fi", "signal")), \
             redirect_stdout(buf):
            mars_mission.main()
        output = buf.getvalue()
        self.assertIn("ไม่พบคำสั่งนี้", output)
        self.assertIn("MISSION COMPLETE", output)

    def test_early_mission_failure_when_oxygen_reaches_zero(self):
        # Day 1: action 1 (-15 O2), then repeated storm choice 1 (-5 O2) won't reach 0 in 1 day,
        # so simulate 5 days of exploring + storm to drain O2, or test energy draining to 0.
        # Day 1-5: explore (-15 O2, -8 Energy) + ice choice 2 (-10 Energy) => Energy drains quickly
        inputs = ["1", "2"] * 4
        buf = io.StringIO()
        with patch("builtins.input", side_effect=inputs), \
             patch("mars_mission.random.randint", return_value=1), \
             patch("mars_mission.random.choice", return_value=("เกิดแสงอาทิตย์ปะทุ", "solar")), \
             redirect_stdout(buf):
            mars_mission.main()
        output = buf.getvalue()
        self.assertIn("MISSION FAILED", output)


if __name__ == "__main__":
    unittest.main()
