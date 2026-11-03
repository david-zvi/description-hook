import json
import os
import subprocess
import sys
import unittest

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks", "describe.py")


def run(event):
    out = subprocess.run([sys.executable, HOOK], input=json.dumps(event), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["hookSpecificOutput"] if out.stdout.strip() else None


class DescribeTest(unittest.TestCase):
    def test_injects_rules_into_sessions_and_subagents(self):
        for event in ("SessionStart", "SubagentStart"):
            self.assertIn("Every Bash tool call must have a `description`",
                          run({"hook_event_name": event})["additionalContext"])

    def test_bash_without_description_is_denied(self):
        bash = {"hook_event_name": "PreToolUse", "tool_name": "Bash"}
        self.assertEqual(run({**bash, "tool_input": {"command": "ls"}})["permissionDecision"], "deny")
        self.assertEqual(run({**bash, "tool_input": {"command": "ls", "description": "  "}})["permissionDecision"], "deny")
        self.assertIsNone(run({**bash, "tool_input": {"command": "ls", "description": "Lists files."}}))


if __name__ == "__main__":
    unittest.main()
