#!/usr/bin/env python3
"""Block any Bash or PowerShell command that has no plain-language description."""
import json
import sys

CLAUDE_NO_DESCRIPTION = "Blocked: this {} call's `description` is missing, empty, or not text. Retry with a " \
                        "one-sentence, plain-language description of what the command does and why."

CODEX_NO_COMMENT = "Blocked: this {} command doesn't start with a description comment. Retry with its first " \
                   "line as `# <one-sentence, plain-language description of what it does and why>`."


def verify_claude_comment(description):
    """For Claude Code, whose shell tools have a `description` field: is it non-empty text?"""
    return isinstance(description, str) and bool(description.strip())


def verify_codex_comment(command):
    """For Codex, whose shell tool has no description field: does the command start with a `# ...` comment?"""
    if not isinstance(command, str):
        return False
    for line in command.splitlines():
        line = line.strip()
        if line and not line.startswith("#!"):
            return line.startswith("#") and bool(line[1:].strip())
    return False


def main():
    e = json.load(sys.stdin)
    tool_input = e.get("tool_input", {})
    if "--codex" in sys.argv:
        ok, reason = verify_codex_comment(tool_input.get("command")), CODEX_NO_COMMENT
    else:
        ok, reason = verify_claude_comment(tool_input.get("description")), CLAUDE_NO_DESCRIPTION
    if ok:
        return
    print(json.dumps({"hookSpecificOutput": {"hookEventName": e["hook_event_name"], "permissionDecision": "deny",
                                             "permissionDecisionReason": reason.format(e.get("tool_name", "shell"))}}))


if __name__ == "__main__":
    main()
