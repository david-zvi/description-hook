"""Run the hook commands from hooks/hooks.json (Claude Code) or hooks/codex-hooks.json (Codex), for the tests."""
import json
import os
import shutil
import subprocess
import unittest

HOOKS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks")
ROOT = os.path.dirname(HOOKS)
POWERSHELLS = [p for p in ("powershell", "pwsh") if shutil.which(p)]


def load_hooks(hooks_file):
    with open(os.path.join(HOOKS, hooks_file)) as f:
        return json.load(f)["hooks"]


COMMANDS = load_hooks("hooks.json")


def find_hook(event, hooks_file):
    """The hook that runs for this event: the first entry with no matcher or a matcher equal to the tool name."""
    for entry in load_hooks(hooks_file)[event["hook_event_name"]]:
        matcher = entry.get("matcher")
        if matcher is None or matcher == event.get("tool_name"):
            return entry["hooks"][0]


def run(event, hooks_file, path=os.environ["PATH"], powershell=None):
    """Run the hook for this event and return its hookSpecificOutput, or None."""
    hook = find_hook(event, hooks_file)
    # Claude Code and Codex fill in the plugin root before running the command, as we do here.
    command = hook["command"].replace("${CLAUDE_PLUGIN_ROOT}", ROOT).replace("${PLUGIN_ROOT}", ROOT)
    # Shells are found by full path on the real PATH: tests pass a restricted `path`, and on Linux
    # subprocess would look for the shell itself in that restricted PATH and not find it.
    if hook.get("shell") == "powershell":
        if powershell is None:
            raise unittest.SkipTest("no PowerShell to run this hook with")
        argv = [shutil.which(powershell), "-NoProfile", "-Command", command]
    else:
        argv = [shutil.which("bash"), "-c", command]
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": ROOT, "PLUGIN_ROOT": ROOT, "PATH": path}
    out = subprocess.run(argv, input=json.dumps(event), capture_output=True, text=True, env=env, check=True)
    return json.loads(out.stdout)["hookSpecificOutput"] if out.stdout.strip() else None
