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

Claude Code Desktop: first add the marketplace, with `/plugin marketplace add david-zvi/description-hook` in a CLI session or `claude plugin marketplace add david-zvi/description-hook` in a terminal. Then in Desktop click **+** next to the prompt box → **Add plugins** (if the menu shows **Plugins**, choose **Plugins → Browse plugins**). Plugins don't load in Desktop's WSL or cloud sessions; inside WSL, run the CLI and install there instead.

### Codex

```
codex plugin marketplace add david-zvi/description-hook
codex plugin add description-hook@description-hook
```

Codex desktop app: add the marketplace with the first command above, then open the **Plugins** tab, find description-hook, click **+**, and start a new chat.

Codex skips plugin hooks until you trust them: open `/hooks` in the CLI, or **Settings > Hooks** in the app. Do this again after every plugin update.

Codex's shell tool has no description field, so the description goes in the command itself, as a first-line comment:

```
# Deletes the build folder so the next build starts clean
rm -rf build
```

A leading comment may stop your saved "always allow" rules from matching a command, so Codex could ask you to approve commands you've allowed before. This hasn't been tested yet.

## Why not file edits?

Edit and Write prompts have no description field, and Claude Code doesn't show text from hooks in them. A subagent's explanation of an edit can't reach you before you approve it, so the plugin covers shell commands only.
