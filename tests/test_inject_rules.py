import os
import tempfile
import unittest

from hook_runner import input_used_up_by, make_broken_python3, run


class InjectRulesTest(unittest.TestCase):
    def test_injects_rules_into_sessions_and_subagents(self):
        for event in ("SessionStart", "SubagentStart"):
            with self.subTest(event=event):
                out = run({"hook_event_name": event})
                self.assertEqual(out["hookEventName"], event)
                self.assertIn("Every Bash tool call must have a `description`", out["additionalContext"])

    def test_python_fallback_receives_input_after_python3_used_it_up(self):
        with tempfile.TemporaryDirectory() as fake_bin:
            fake_python3 = make_broken_python3(fake_bin)
            session_start = {"hook_event_name": "SessionStart"}

            out = run(session_start, path=fake_bin + os.pathsep + os.environ["PATH"])

            self.assertEqual(input_used_up_by(fake_python3), session_start)
            self.assertIn("additionalContext", out)


if __name__ == "__main__":
    unittest.main()
