import os
import tempfile
import unittest

from hook_runner import input_used_up_by, make_broken_python3, run


def bash(tool_input):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": tool_input}


class RequireDescriptionTest(unittest.TestCase):
    def test_bash_description_is_required(self):
        cases = [
            ({"command": "ls"}, "deny"),
            ({"command": "ls", "description": ""}, "deny"),
            ({"command": "ls", "description": "  "}, "deny"),
            ({"command": "ls", "description": None}, "deny"),
            ({"command": "ls", "description": "Lists files."}, None),
        ]
        for tool_input, expected in cases:
            with self.subTest(tool_input=tool_input):
                out = run(bash(tool_input))
                self.assertEqual(out and out["permissionDecision"], expected)
                if out:
                    self.assertEqual(out["hookEventName"], "PreToolUse")

    def test_python_fallback_receives_input_after_python3_used_it_up(self):
        with tempfile.TemporaryDirectory() as fake_bin:
            fake_python3 = make_broken_python3(fake_bin)
            no_description = bash({"command": "ls"})

            out = run(no_description, path=fake_bin + os.pathsep + os.environ["PATH"])

            self.assertEqual(input_used_up_by(fake_python3), no_description)
            self.assertEqual(out["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
