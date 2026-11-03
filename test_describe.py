import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HOOKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks")


def run(script, event):
    out = subprocess.run([sys.executable, os.path.join(HOOKS, script)], input=json.dumps(event),
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["hookSpecificOutput"] if out.stdout.strip() else None


def run_command(event, command, path):
    """Run a hooks.json command string through the shell, the way Claude Code does."""
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": os.path.dirname(HOOKS), "PATH": path}
    out = subprocess.run(["sh", "-c", command], input=json.dumps(event), capture_output=True, text=True, env=env)
    return json.loads(out.stdout)["hookSpecificOutput"]


class DescribeTest(unittest.TestCase):
    def test_injects_rules_into_sessions_and_subagents(self):
        for event in ("SessionStart", "SubagentStart"):
            out = run("inject_rules.py", {"hook_event_name": event})
            self.assertEqual(out["hookEventName"], event)
            self.assertIn("Every Bash tool call must have a `description`", out["additionalContext"])

    def test_bash_without_description_is_denied(self):
        bash = {"hook_event_name": "PreToolUse", "tool_name": "Bash"}
        run_rd = lambda tool_input: run("require_description.py", {**bash, "tool_input": tool_input})
        self.assertEqual(run_rd({"command": "ls"})["permissionDecision"], "deny")
        self.assertEqual(run_rd({"command": "ls", "description": "  "})["permissionDecision"], "deny")
        self.assertIsNone(run_rd({"command": "ls", "description": "Lists files."}))

    def test_fallback_to_python_still_gets_stdin(self):
        # A fake `python3` that swallows stdin and fails forces the fallback after `||`.
        bindir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bindir)
        with open(os.path.join(bindir, "python3"), "w") as f:
            f.write("#!/bin/sh\ncat >/dev/null\nexit 1\n")
        os.chmod(os.path.join(bindir, "python3"), 0o755)
        os.symlink(sys.executable, os.path.join(bindir, "python"))
        with open(os.path.join(HOOKS, "hooks.json")) as f:
            hooks = json.load(f)["hooks"]
        bash = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"}}
        session = {"hook_event_name": "SessionStart"}
        path = bindir + os.pathsep + os.environ["PATH"]
        self.assertEqual(run_command(bash, hooks["PreToolUse"][0]["hooks"][0]["command"], path)
                         ["permissionDecision"], "deny")
        self.assertIn("additionalContext", run_command(session, hooks["SessionStart"][0]["hooks"][0]["command"], path))


if __name__ == "__main__":
    unittest.main()
