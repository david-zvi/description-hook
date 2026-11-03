#!/usr/bin/env python3
"""Block any Bash command that has no plain-language description."""
import json
import sys

NO_DESCRIPTION = ("Blocked: this Bash call has no `description`. Retry with a one-sentence, plain-language "
                  "description of what the command does and why.")


def main():
    e = json.load(sys.stdin)
    if not str((e.get("tool_input") or {}).get("description") or "").strip():
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": NO_DESCRIPTION}}))


if __name__ == "__main__":
    main()
