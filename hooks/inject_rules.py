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


def main():
    event = json.load(sys.stdin)["hook_event_name"]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": RULES}}))


if __name__ == "__main__":
    main()
