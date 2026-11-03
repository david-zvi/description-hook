import unittest

from hook_runner import run


class RequireDescriptionTest(unittest.TestCase):
    def test_description_is_required(self):
        cases = [
            ({"command": "ls"}, "deny"),
            ({"command": "ls", "description": ""}, "deny"),
            ({"command": "ls", "description": "  "}, "deny"),
            ({"command": "ls", "description": None}, "deny"),
            ({"command": "ls", "description": 42}, "deny"),
            ({"command": "ls", "description": "Lists files."}, None),
        ]
        for tool_name in ("Bash", "PowerShell"):
            for tool_input, expected in cases:
                with self.subTest(tool_name=tool_name, tool_input=tool_input):
                    out = run({"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input})
                    self.assertEqual(out and out["permissionDecision"], expected)
                    if out:
                        self.assertEqual(out["hookEventName"], "PreToolUse")
                        self.assertIn(f"this {tool_name} call", out["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main()
