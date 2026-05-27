# Agent Instructions

See [`CLAUDE.md`](./CLAUDE.md) for full context on this repo.

The bootstrap prompt is in [`boilerplate.md`](./boilerplate.md). Read it and start at **Step 1** (interview the user). Do not write any code before completing Step 1.

## Tool-name notes for non-Claude agents

`boilerplate.md` was written for Claude Code. If you are a different agent:

| Claude Code term | Your equivalent |
|-----------------|----------------|
| `AskUserQuestion` tool | Your interactive input / clarification mechanism |
| `Bash` tool | Your shell execution tool |
| `Write` / `Edit` / `Read` tools | Your file I/O tools |
| `.claude/settings.json` permissions | Your equivalent allowlist config (skip if none) |
| `.claude/launch.json` | Cowork-specific; skip if not using Cowork |

All steps are otherwise agent-agnostic — scaffold, configure, spec, implement, commit, retro.
