import unittest

from hook_runner import POWERSHELLS, run


class RequireDescriptionTest(unittest.TestCase):
    def check_description_is_required(self, tool_name, powershell=None):
        cases = [
            ({"command": "ls"}, "deny"),
            ({"command": "ls", "description": ""}, "deny"),
            ({"command": "ls", "description": "  "}, "deny"),
            ({"command": "ls", "description": None}, "deny"),
            ({"command": "ls", "description": 42}, "deny"),
            ({"command": "ls", "description": "Lists files."}, None),
        ]
        for tool_input, expected in cases:
            with self.subTest(tool_name=tool_name, powershell=powershell, tool_input=tool_input):
                out = run({"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input},
                          "hooks.json", powershell=powershell)
                self.assertEqual(out and out["permissionDecision"], expected)
                if out:
                    self.assertEqual(out["hookEventName"], "PreToolUse")
                    self.assertIn(f"this {tool_name} call", out["permissionDecisionReason"])

    def test_bash_description_is_required(self):
        self.check_description_is_required("Bash")

    def test_powershell_description_is_required(self):
        if not POWERSHELLS:
            self.skipTest("no PowerShell installed")
        for powershell in POWERSHELLS:
            self.check_description_is_required("PowerShell", powershell)

    def test_codex_leading_comment_is_required(self):
        cases = [
            ("ls", "deny"),
            ("#\nls", "deny"),
            ("ls\n# Lists files", "deny"),
            (["bash", "-lc", "# Lists files\nls"], "deny"),
            ("# Lists files\nls", None),
            ("\n  \n# Lists files\nls", None),
            ("#!/bin/sh\n# Lists files\nls", None),
        ]
        for command, expected in cases:
            with self.subTest(command=command):
                out = run({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}},
                          "codex-hooks.json")
                self.assertEqual(out and out["permissionDecision"], expected)
                if out:
                    self.assertEqual(out["hookEventName"], "PreToolUse")
                    self.assertIn("this Bash command", out["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main()
