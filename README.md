# description-hook

A Claude Code plugin that makes Claude, **including subagents**, give every shell command a one-sentence, plain-language description ("Deletes the build folder so the next build starts clean"). Claude Code shows that description in the permission prompt, so you know what you're approving without reading shell syntax.

- Bash and PowerShell calls without a description are sent back to Claude to add one.
- The rule is injected into the main session and into every subagent, so you don't need it in your `CLAUDE.md`.

## Install

```
/plugin marketplace add david-zvi/description-hook
/plugin install description-hook@description-hook
```

Needs Python 3 on your PATH, as `python3` or `python`.

On Windows, the hook commands need Git Bash, which Claude Code uses for hooks when it's installed. Claude Code Desktop: install from **+ → Add plugins**. Plugins don't load in Desktop's WSL or cloud sessions; inside WSL, run the CLI and install there instead.

## Why not file edits?

Edit and Write prompts have no description field, and Claude Code doesn't show text from hooks in them. A subagent's explanation of an edit can't reach you before you approve it, so the plugin covers shell commands only.
