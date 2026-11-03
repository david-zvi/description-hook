"""Run the hook commands from hooks/hooks.json the way Claude Code does, for the tests."""
import json
import os
import subprocess

HOOKS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks")

with open(os.path.join(HOOKS, "hooks.json")) as f:
    COMMANDS = {name: entries[0]["hooks"][0]["command"] for name, entries in json.load(f)["hooks"].items()}


def run(event, path=os.environ["PATH"]):
    """Run the hooks.json command for this event through the shell and return its hookSpecificOutput, or None."""
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": os.path.dirname(HOOKS), "PATH": path}
    out = subprocess.run(["sh", "-c", COMMANDS[event["hook_event_name"]]], input=json.dumps(event),
                         capture_output=True, text=True, env=env, check=True)
    return json.loads(out.stdout)["hookSpecificOutput"] if out.stdout.strip() else None
