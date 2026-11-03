#!/usr/bin/env python3
"""Make Claude, including subagents, give every Bash command a plain-language description."""
import json
import sys

RULES = """\
# Describing commands (description-hook plugin)

Every Bash tool call must have a `description` in plain language: what the command does and why, \
in one sentence, understandable without knowing shell syntax (e.g. "Deletes the build folder so the \
next build starts clean"). Mention anything destructive, network-facing, or system-modifying explicitly.
"""

NO_DESCRIPTION = ("Blocked: this Bash call has no `description`. Retry with a one-sentence, plain-language "
                  "description of what the command does and why.")


def say(event, **out):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, **out}}))


def main():
    e = json.load(sys.stdin)
    event = e["hook_event_name"]
    if event in ("SessionStart", "SubagentStart"):
        return say(event, additionalContext=RULES)
    if not str((e.get("tool_input") or {}).get("description") or "").strip():
        say(event, permissionDecision="deny", permissionDecisionReason=NO_DESCRIPTION)


if __name__ == "__main__":
    main()
