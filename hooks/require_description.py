#!/usr/bin/env python3
"""Block any Bash or PowerShell command that has no plain-language description."""
import json
import sys

NO_DESCRIPTION = ("Blocked: this {} call's `description` is missing, empty, or not text. Retry with a "
                  "one-sentence, plain-language description of what the command does and why.")


def main():
    e = json.load(sys.stdin)
    description = e.get("tool_input", {}).get("description", "")
    if not isinstance(description, str) or not description.strip():
        reason = NO_DESCRIPTION.format(e.get("tool_name", "shell"))
        print(json.dumps({"hookSpecificOutput": {"hookEventName": e["hook_event_name"], "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    main()
