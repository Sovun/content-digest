# Boilerplate — Vite + React + TypeScript (Agentic Engineering)

This repo is a **bootstrap template**. It contains one file that matters: [`boilerplate.md`](./boilerplate.md) — a step-by-step prompt that scaffolds a new project following agentic engineering practices (spec-first, decisions recorded, governance separated from app code).

## What you get after running the bootstrap

A fully wired project at `<your-project-name>/` with:

- **Vite + React + TypeScript** app under `app/`
- **Vitest** configured and green from day one
- **ESLint + Prettier** (ESLint 10 flat-config compatible)
- **Strict TypeScript** (`strict`, `noImplicitAny`, `noUncheckedIndexedAccess`, path alias `@/*`)
- **Governance layer** at the repo root — `CLAUDE.md`, `docs/`, `.claude/` — physically separated from `app/`
- **Working agreement** embedded in `CLAUDE.md`: spec-first loop, ADR-required for new patterns, retro after every feature
- **Cowork dev-server auto-attach** via `.claude/launch.json`
- **4 commits** out of the box: scaffold → docs skeleton → hello-world feature → retrospective

## How to use

### Option A — Let Claude run it (recommended)

1. Open a new project folder in Claude Code.
2. Paste this into the chat:

   ```
   Read boilerplate.md from https://raw.githubusercontent.com/krivitsky/boilerplate-webapp/main/boilerplate.md and follow it step by step to bootstrap a new project.
   ```

   Or, if you've cloned this repo locally:

   ```
   Follow the instructions in boilerplate.md to bootstrap a new project.
   ```

3. Claude will interview you (Step 1), then execute all 8 steps without further prompting.

### Option B — Copy the file manually

Copy [`boilerplate.md`](./boilerplate.md) into any new project folder as `CLAUDE.md`, then tell Claude: `Follow CLAUDE.md`.

## What the bootstrap does NOT include (intentionally deferred)

Add these via the working-agreement loop once the project warrants them:

- Husky + lint-staged + commitlint
- GitHub Actions CI
- `.claude/commands/` slash-command wrappers (`/feature`, `/retro`, `/dev`)
- Vitest coverage thresholds
- npm workspaces (add if a second package appears)

See the "Deferred" section at the bottom of [`boilerplate.md`](./boilerplate.md) for rationale.

## Other agents

[`AGENTS.md`](./AGENTS.md) covers non-Claude agents (OpenAI Codex, etc.) with a tool-name mapping. The bootstrap steps are agent-agnostic; only the tool names differ.

## If you ARE Claude reading this in a new session

`boilerplate.md` contains your full instructions. Read it now and start at **Step 1** (interview the user). Do not write any code before completing Step 1.
