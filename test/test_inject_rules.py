import unittest

from hook_runner import run


class InjectRulesTest(unittest.TestCase):
    def test_injects_rules_into_sessions_and_subagents(self):
        for event in ("SessionStart", "SubagentStart"):
            with self.subTest(event=event):
                out = run({"hook_event_name": event})
                self.assertEqual(out["hookEventName"], event)
                self.assertIn("Every Bash tool call must have a `description`", out["additionalContext"])


if __name__ == "__main__":
    unittest.main()
