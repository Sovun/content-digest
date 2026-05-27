# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## If you are Claude reading this in a new session

`boilerplate.md` contains your full instructions. Read it now and start at **Step 1** (interview the user). Do not write any code before completing Step 1.

## What this repo is

A bootstrap template for Vite + React + TypeScript projects following **agentic engineering** practices. The repo's only substantive content is `boilerplate.md` — an 8-step prompt that scaffolds a new project with spec-first workflow, ADR-required decisions, and governance physically separated from app code.

## File structure

```
boilerplate.md    ← the 8-step bootstrap prompt (the only file that matters)
CLAUDE.md         ← this file — entry point for Claude Code
AGENTS.md         ← tool-name mapping for non-Claude agents (Codex, etc.)
README.md         ← human-facing usage instructions
```

No `package.json`, no build step, no tests — this repo is documentation only.

## How boilerplate.md works

Running the bootstrap produces a new project at `<project-name>/` with this layout:

```
<project-name>/
  CLAUDE.md                     ← entry point for Claude (generated)
  README.md                     ← entry point for humans (generated)
  package.json                  ← root pass-through scripts
  .claude/
    settings.json               ← permission allowlist
    launch.json                 ← Cowork dev-server attach config
    rules/                      ← short Markdown rules Claude reads alongside CLAUDE.md
  docs/
    requirements/               ← feature specs
    decisions/                  ← ADRs
    retrospectives/             ← post-feature retros
    constraints.md
  app/                          ← all Vite + React + TS code lives here
```

**Governance/docs live at repo root; app code lives under `app/` — never mixed.**

The bootstrap follows 8 steps: interview → scaffold → docs skeleton → hello-world feature (spec-first) → working agreement → port probe + dev server → retrospective → hand-off.

## Editing this repo

Changes go to `boilerplate.md` only. CLAUDE.md, README.md, and AGENTS.md are meta-files that describe the template — update them only if the template's usage or structure changes.
