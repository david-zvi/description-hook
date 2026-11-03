#!/usr/bin/env python3
"""Tell Claude, including subagents, to give every Bash or PowerShell command a plain-language description."""
import json
import sys

RULES = """\
# Describing commands (description-hook plugin)

Every Bash and PowerShell tool call must have a `description` in plain language: what the command does and why, \
in one sentence, understandable without knowing shell syntax (e.g. "Deletes the build folder so the \
next build starts clean"). Mention anything destructive, network-facing, or system-modifying explicitly.
"""


CODEX_RULES = """\
# Describing commands (description-hook plugin)

Start every shell command with a comment line giving a plain-language description: what the command does \
and why, in one sentence, understandable without knowing shell syntax. For example:

    # Deletes the build folder so the next build starts clean
    rm -rf build

Mention anything destructive, network-facing, or system-modifying explicitly. Commands without this \
comment are rejected.
"""


def main():
    event = json.load(sys.stdin)["hook_event_name"]
    rules = CODEX_RULES if "--codex" in sys.argv else RULES
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": rules}}))


if __name__ == "__main__":
    main()
