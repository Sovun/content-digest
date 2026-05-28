# Project Bootstrap Prompt — Vite + React + TypeScript (Agentic Engineering)

You are setting up a new project that follows **agentic engineering** practices, not vibe coding. Spec-first, decisions recorded, constraints explicit, workflow improves itself via retrospectives, and the **governance layer is physically separated from the application code**:

```
<project-name>/                  ← repo root (git lives here)
  CLAUDE.md                      ← entry point for Claude
  README.md                      ← entry point for humans
  package.json                   ← root pass-through scripts (npm run dev, etc.)
  .gitignore                     ← single root-level gitignore
  .editorconfig                  ← cross-IDE consistency
  .nvmrc                         ← pinned Node version
  .env.example                   ← env var template (.env is gitignored)
  docs/                          ← requirements / decisions / retros / constraints
  app/                           ← all Vite + React + TS code lives here
```

**Hard precondition for "done":** `CLAUDE.md` exists at the *repo root* (NOT inside `app/`). If it's missing, the bootstrap is not complete — re-run Step 3.

**Flow at a glance:** interview → scaffold `app/` + root `package.json` + dotfiles + root `.gitignore` + chore commit → docs skeleton + README + docs commit → hello world spec-first inside `app/` + feat commit → dev server from root → curl confirms 200 → open browser → retrospective → STOP.

**File-creation discipline:** When this prompt shows a file path followed by code-block content, Claude MUST create that file using its file-writing tools — do NOT print the content and wait for the user to create it. Diff snippets explicitly labeled "merge into existing file" are the only exception. Bash heredoc blocks in Step 2 must be executed, not displayed.

## Step 1 — Interview me

Use `AskUserQuestion`. Do not proceed until you have answers. **Do not ask about features.**

1. **Project name** (folder name, kebab-case).
2. **One-sentence goal** — what is this project FOR?
3. **Primary user / context** — who uses it, where it runs.
4. **Out-of-scope / what NOT to build** — at least 2 items.

Echo answers back for confirmation before continuing.

## Step 2 — Scaffold `app/`, set up root pass-through, dotfiles, git + chore commit

1. Create the repo root and enter it:
   ```bash
   mkdir <project-name>
   cd <project-name>
   ```
2. Scaffold Vite **into an `app/` subfolder**:
   ```bash
   npm create vite@latest app -- --template react-ts
   ```
3. Install and add dev deps inside `app/`:
   ```bash
   cd app
   npm install
   npm install -D vitest @vitest/ui \
     eslint prettier eslint-config-prettier \
     eslint-plugin-react-hooks \
     @typescript-eslint/parser @typescript-eslint/eslint-plugin
   ```
   *Note: `eslint-plugin-react` is incompatible with ESLint 10 that current Vite templates ship with; `eslint-plugin-react-hooks` covers the important rules. Record in `docs/constraints.md`.*
4. Configure inside `app/`:
   - `app/vitest.config.ts` with `test: { environment: 'node' }`.
   - `app/eslint.config.js` (flat config) and `app/.prettierrc` with sensible defaults.
   - `app/package.json` scripts: `"test": "vitest"`, `"test:run": "vitest run"`, `"lint": "eslint . --ext ts,tsx"`, `"format": "prettier --write ."`.
   - **`app/tsconfig.app.json`** — verify `"strict": true` (Vite default — confirm, don't assume). Add explicit safety flags and a path alias:
     ```json
     {
       "compilerOptions": {
         "strict": true,
         "noImplicitAny": true,
         "strictNullChecks": true,
         "noUncheckedIndexedAccess": true,
         "noUnusedLocals": true,
         "noUnusedParameters": true,
         "baseUrl": ".",
         "paths": { "@/*": ["./src/*"] }
       }
     }
     ```
     (Merge these into the existing `compilerOptions` — don't replace the file.)
   - **`app/vite.config.ts`** — mirror the path alias so runtime and TS agree:
     ```ts
     import path from 'node:path';
     // inside defineConfig:
     resolve: { alias: { '@': path.resolve(__dirname, './src') } },
     ```
     Vitest reads `vite.config.ts`, so the alias works in specs too. From now on, write imports as `import { greeting } from '@/greeting'` rather than relative-path spaghetti.
5. **Remove Vite's `app/.gitignore`** — we use a single root-level `.gitignore`:
   ```bash
   rm app/.gitignore
   ```
6. **Create the root-level files in ONE bash block.** Claude MUST execute the heredoc block below using the Bash tool — do NOT show the contents and wait for the user. Heredocs use the quoted `'EOF'` delimiter so nothing inside expands. Run it as a single bash invocation:

   ```bash
   cd ..

   cat > package.json <<'EOF'
   {
     "name": "<project-name>",
     "private": true,
     "scripts": {
       "dev": "npm --prefix app run dev",
       "build": "npm --prefix app run build",
       "preview": "npm --prefix app run preview",
       "test": "npm --prefix app run test",
       "test:run": "npm --prefix app run test:run",
       "lint": "npm --prefix app run lint",
       "format": "npm --prefix app run format",
       "setup": "npm install --prefix app"
     }
   }
   EOF

   cat > .gitignore <<'EOF'
   # dependencies
   node_modules/

   # build outputs
   dist/
   dist-ssr/
   *.local

   # env
   .env
   .env.local
   .env.*.local

   # editor / OS
   .DS_Store
   .vscode/
   .idea/
   *.swp

   # logs
   *.log

   # pid files
   *.pid

   # bootstrap port state (session-local, set by Step 6)
   .dev-port
   .preview-port

   # sed backups
   *.bak

   # tests / coverage
   coverage/
   EOF

   cat > .editorconfig <<'EOF'
   root = true

   [*]
   indent_style = space
   indent_size = 2
   end_of_line = lf
   charset = utf-8
   trim_trailing_whitespace = true
   insert_final_newline = true

   [*.md]
   trim_trailing_whitespace = false
   EOF

   cat > .nvmrc <<'EOF'
   22
   EOF

   cat > .env.example <<'EOF'
   # Copy to .env and fill values. Never commit .env.
   # Add variables here as the project grows.
   EOF

   ls -la package.json .gitignore .editorconfig .nvmrc .env.example
   ```

   The trailing `ls -la` is a verify check. If any of those paths is missing, a heredoc failed — rerun the block before moving on. After the block runs cleanly, also substitute the actual project name into `package.json` (replace `<project-name>` with the kebab-case name from Step 1).

7. **First commit (chore — scaffold + dotfiles, no docs or feature yet):**
   ```bash
   git init
   git add -A
   git commit -m "chore: scaffold app/ + root pass-through + dotfiles"
   ```

## Step 3 — Agentic docs skeleton + human-facing README + docs commit

**Create `CLAUDE.md` at the repo root FIRST**, before anything under `docs/`. Verify with `ls CLAUDE.md` (from repo root). If missing, recreate.

```
<project-name>/
  CLAUDE.md                       ← entry point for Claude — MUST EXIST at repo root
  README.md                       ← entry point for humans
  docs/
    requirements/
      overview.md                 ← from Step 1 answers
    decisions/
      001-agent-structure.md      ← ADR for repo layout (root vs app/)
    retrospectives/
      .gitkeep                    ← seeded folder; populated after each feature
    constraints.md                ← from Step 1 + baseline constraints
```

### Content rules

- **`CLAUDE.md`** MUST contain (and stay under ~200 lines — see rule 12):
  - (a) one-paragraph project description (from Step 1),
  - (b) **"Repository layout"** section documenting the root-vs-`app/` split,
  - (c) "How to work in this repo" section embedding the Step 5 working agreement verbatim,
  - (d) linked TOC for every file under `docs/`,
  - (e) "Current state" section — initially: "hello world greeting rendered; no features specced",
  - (f) **"Dev server"** section: from repo root, `npm run dev` → `http://127.0.0.1:<DEV_PORT>/` (port from `.dev-port`, defaults 5173).
  - (g) **"Common commands"** section — `npm run dev` / `build` / `preview` / `test` / `lint` / `format`, all from repo root,
  - (h) **"Critical files"** — point at `app/vite.config.ts`, `app/vitest.config.ts`, `docs/constraints.md`,
  - (i) "Self-improvement log" section linking every file under `docs/retrospectives/` (initially empty).
  - (j) **"Escalation rules"** — when to stop and ask the user rather than push through. Verbatim:
    > Stop and ask via AskUserQuestion when:
    > - The same test has failed 3 times with different fixes (you're guessing — get more context).
    > - A request conflicts with `docs/constraints.md` or a rule in the "Rules" section of `CLAUDE.md` (surface it, don't silently comply).
    > - A new runtime dependency is needed (ask + add an ADR before installing).
    > - `:5173` or `:4173` is taken (fix the conflict, do not let Vite drift to another port).
    > - This change would push `CLAUDE.md` past ~200 lines (route detail into a linked doc first).
    > - Acceptance criteria in a `docs/requirements/feature-*.md` are ambiguous or contradict each other.
  - (k) **"Rules"** section — three non-negotiable invariants embedded directly so they load on every turn:
    > **TypeScript strict:** Do NOT disable `strict`, `noImplicitAny`, `strictNullChecks`, or `noUncheckedIndexedAccess` in any `tsconfig*.json`. Narrow the type or guard the value — never loosen the config.
    >
    > **Pure modules:** Business logic lives in pure modules under `app/src/`. React components only render — no branching/transform logic. Extract any non-trivial computation into a pure module and spec it before wiring it in.
    >
    > **Spec first:** Every new module starts with a failing `*.spec.ts(x)` test. Show the red output, then write the minimum code to turn it green, then commit.
- **`README.md`** (root, for humans, not Claude) — short and sharp:
  ```markdown
  # <project-name>

  <one-sentence goal from Step 1>

  ## Quick start
  ```
  ```bash
  npm run setup        # installs app/ deps
  npm run dev          # starts http://127.0.0.1:5173/
  ```
  ```markdown
  ## Layout
  - `CLAUDE.md` — how Claude works in this repo
  - `docs/` — requirements, decisions (ADRs), retrospectives, constraints
  - `app/` — Vite + React + TypeScript application code

  ## Commands (all from repo root)
  `npm run dev | build | preview | test | lint | format`

  ## Working agreement
  Spec-first, ADR-required for new patterns, retro after every feature. See [CLAUDE.md](./CLAUDE.md).
  ```
- **`docs/requirements/overview.md`** — goal, user, success criteria. Plain prose.
- **`docs/decisions/001-agent-structure.md`** — ADR explaining the **root-vs-`app/` split** plus the docs subfolders. Format: Context, Decision, Consequences.
- **`docs/constraints.md`** — "what NOT to do" list from Step 1 + baseline (no unscoped refactors, no new deps without an ADR, no code without a spec, no skipping the retro, **no governance files inside `app/`**, **no app code outside `app/`**, **no `eslint-plugin-react` until it supports ESLint 10**).

Verify from repo root: `ls CLAUDE.md README.md docs/requirements/overview.md docs/decisions/001-agent-structure.md docs/constraints.md docs/retrospectives/.gitkeep` — all paths resolve.

**Docs commit:**
```bash
git add -A
git commit -m "docs: agentic engineering skeleton (CLAUDE.md + README.md + docs/)"
```

## Step 4 — Hello-world: req doc + spec + impl + feat commit

The bootstrap treats hello-world as **Feature 001** to demonstrate the full spec-first loop end-to-end. Do NOT modify `app/src/App.tsx` first.

1. **Create the requirements doc first** (rule 1 — every feature begins with a `docs/requirements/feature-*.md`). Run this heredoc from the repo root, then substitute `<project-name>` with the actual name from Step 1:
   ```bash
   cat > docs/requirements/feature-001-hello-world.md <<'EOF'
   # Feature 001 — Hello World

   ## User story
   As a developer setting up this project, I want the app to render a greeting that includes the project name, so I can confirm the build, dev server, and component pipeline work end to end.

   ## Acceptance criteria
   - GIVEN the project name
     WHEN I open the dev server in a browser
     THEN I see an `<h1>` element containing "Welcome to <project-name>".
   - GIVEN the pure `greeting(name)` function
     WHEN called with the project name
     THEN it returns a string containing that name.

   ## Out of scope
   - Styling beyond minimal inline padding/font.
   - Internationalization, theming, routing.

   ## Open questions
   - None.
   EOF
   ```
2. Create `app/src/greeting.spec.ts`:
   ```ts
   import { describe, it, expect } from 'vitest';
   import { greeting } from './greeting';

   describe('greeting', () => {
     it('returns a welcome line containing the project name', () => {
       expect(greeting('<project-name>')).toContain('<project-name>');
     });
   });
   ```
3. From repo root: `npm run test:run` — SHOW the failing output (module not found).
4. Create `app/src/greeting.ts`:
   ```ts
   export const greeting = (name: string) => `Welcome to ${name}`;
   ```
5. From repo root: `npm run test:run` — SHOW the green output.
6. **Replace `app/src/App.tsx` entirely** (no leftover imports):
   ```tsx
   import { greeting } from './greeting';

   export default function App() {
     return (
       <main style={{ fontFamily: 'system-ui', padding: '2rem' }}>
         <h1>{greeting('<project-name>')}</h1>
         <p>{'<one-line tagline from Step 1 goal>'}</p>
       </main>
     );
   }
   ```
   Delete `app/src/App.css` and any references. Leave `app/src/main.tsx` and `app/src/index.css` alone.
7. **Feat commit (from repo root):**
   ```bash
   git add -A
   git commit -m "feat(feature-001): hello-world greeting (req doc + spec + impl)"
   ```

## Step 5 — Working agreement (embed verbatim in `CLAUDE.md`)

> **Working agreement**
>
> 1. No code without a spec. Every feature begins as a file under `docs/requirements/` (at repo root) and a failing test under `app/src/**/*.spec.ts(x)`.
> 2. No architectural choice without an ADR under `docs/decisions/`.
> 3. Read `docs/constraints.md` before proposing anything new. Surface conflicts, don't silently comply.
> 4. The loop is: spec → failing test → minimal code → green test → commit. One concern per commit.
> 5. Logic in pure modules, rendering in components. Specs target the logic. Add a DOM-testing layer (e.g. React Testing Library) only via an ADR when a real need appears.
> 6. When in doubt, ask. Use AskUserQuestion rather than guessing requirements.
> 7. Keep `CLAUDE.md`'s "Current state" section updated after every merged change.
> 8. Dev server lives at `http://127.0.0.1:<DEV_PORT>/` where `DEV_PORT` is recorded in `.dev-port` (defaults to 5173, probed for a free port at bootstrap time; see Step 6). Always read the current port from `.dev-port` instead of hardcoding 5173. `strictPort: true` is set so Vite never silently drifts.
> 9. **Retrospective after every feature.** Once a feature is green and committed, write `docs/retrospectives/NNN-<slug>.md` capturing what worked, what didn't, and concrete workflow changes. If the retro proposes a change, **edit `CLAUDE.md` (working agreement, constraints, or links) in the same session** — don't defer. Add a new ADR if the change is architectural. Then update the "Self-improvement log" section of `CLAUDE.md` to link the new retro. Commit as `chore(retro): NNN-<slug>`.
> 10. **Layout discipline.** Governance files (`CLAUDE.md`, `README.md`, `docs/**`) live at the repo root and never inside `app/`. App code lives inside `app/` and never at the repo root. Root-level config (CI, dotfiles) is allowed; app code at root is not.
> 11. **Conventional Commits.** Format: `<type>(<scope>): <subject>`. Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`, `style`. Retros are committed as `chore(retro): NNN-<slug>`. ADR additions as `docs(adr): NNN-<slug>`.
> 12. **CLAUDE.md ≤ ~200 lines.** It is a router, not an encyclopedia. If a retro update would push it past ~200 lines, move detail into a linked file under `docs/` and link from `CLAUDE.md` instead. Same applies to constraints.md — split into topical files once over ~150 lines.

## Step 6 — Probe ports, run the dev server, verify, open the browser

Defaults are `:5173` (dev) and `:4173` (preview), but another running Vite project on your machine may already own them. Probe first; if taken, pick the next free port and substitute throughout the configs. Then start.

1. **Probe for free ports and substitute if needed.** Run this single bash block from the repo root:
   ```bash
   pick_free_port() {
     local start=$1
     for p in $(seq $start $((start+20))); do
       nc -z 127.0.0.1 $p 2>/dev/null || { echo $p; return 0; }
     done
     echo "ERROR: no free port in $start..$((start+20))" >&2
     return 1
   }

   DEV_PORT=$(pick_free_port 5173) || exit 1
   PREVIEW_PORT=$(pick_free_port 4173) || exit 1
   echo "Selected DEV_PORT=$DEV_PORT, PREVIEW_PORT=$PREVIEW_PORT"

   if [ "$DEV_PORT" != "5173" ] || [ "$PREVIEW_PORT" != "4173" ]; then
     sed -i.bak "s/5173/$DEV_PORT/g; s/4173/$PREVIEW_PORT/g" \
       CLAUDE.md README.md 2>/dev/null || true
     find . -maxdepth 3 -name '*.bak' -delete
     echo "Configs updated to $DEV_PORT / $PREVIEW_PORT."
   fi

   echo "$DEV_PORT" > .dev-port
   echo "$PREVIEW_PORT" > .preview-port
   ```

2. **Create `.claude/launch.json`** with the probed ports so Cowork's preview panel attaches to the correct port. Claude Code's self-modification classifier blocks writes to `.claude/` paths — run this in **your terminal** (not via Claude):
   ```bash
   DEV_PORT=$(cat .dev-port)
   PREVIEW_PORT=$(cat .preview-port)
   mkdir -p .claude
   cat > .claude/launch.json <<EOF
   {
     "version": "0.0.1",
     "configurations": [
       {
         "name": "Vite dev server",
         "runtimeExecutable": "npm",
         "runtimeArgs": ["run", "dev"],
         "port": $DEV_PORT
       },
       {
         "name": "Vite preview (built)",
         "runtimeExecutable": "npm",
         "runtimeArgs": ["run", "preview"],
         "port": $PREVIEW_PORT
       }
     ]
   }
   EOF
   echo "Created .claude/launch.json with dev=$DEV_PORT preview=$PREVIEW_PORT"
   ```
   If Cowork's preview panel is already open, click "Set up" to re-attach after creating the file.

3. **Create `app/vite.config.ts`** with the probed ports — substitute `<DEV_PORT>` / `<PREVIEW_PORT>` with the values printed in step 1 (read from `.dev-port` / `.preview-port` if you've lost them):
   ```ts
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';
   import path from 'node:path';

   export default defineConfig({
     plugins: [react()],
     server: { host: '127.0.0.1', port: <DEV_PORT>, strictPort: true, open: false },
     preview: { host: '127.0.0.1', port: <PREVIEW_PORT>, strictPort: true },
     resolve: { alias: { '@': path.resolve(__dirname, './src') } },
   });
   ```
   (Path alias preserved from Step 2 — this file is the single source of truth for both port config and alias.)

4. **Start the dev server and verify OUR process is actually alive** (catches the false-positive case where another project's server already answers on the port). Run as one bash block:
   ```bash
   DEV_PORT=$(cat .dev-port)
   nohup npm run dev > .dev-server.log 2>&1 &
   DEV_PID=$!
   echo $DEV_PID > .dev-server.pid
   disown

   sleep 2

   if ! kill -0 $DEV_PID 2>/dev/null; then
     echo "ERROR: dev server (PID $DEV_PID) died on startup. Log follows:"
     cat .dev-server.log
     exit 1
   fi
   echo "Dev server PID $DEV_PID alive on :$DEV_PORT."
   ```

5. **Curl gate — only run this AFTER step 4's PID check passes:**
   ```bash
   DEV_PORT=$(cat .dev-port)
   for i in {1..20}; do
     code=$(curl -sS -o /dev/null -w "%{http_code}" http://127.0.0.1:$DEV_PORT/ || true)
     [ "$code" = "200" ] && break
     sleep 0.5
   done
   echo "dev server HTTP status: $code (port $DEV_PORT)"
   ```
   If `$code` isn't `200`, `cat .dev-server.log` and stop.

6. **Confirm the served HTML has the React mount point:**
   ```bash
   DEV_PORT=$(cat .dev-port)
   curl -sS http://127.0.0.1:$DEV_PORT/ | grep -q '<div id="root"' && echo "shell OK"
   ```

7. **Open the browser at the actual port:**
   ```bash
   DEV_PORT=$(cat .dev-port)
   open "http://127.0.0.1:$DEV_PORT/"   # macOS; use xdg-open on Linux
   ```
   Cowork attaches automatically via `.claude/launch.json` created in step 2. If not, click "Set up" in the preview panel.

8. If bash can't reach the host browser, print the URL prominently. If curl reaches the port from bash but the user's browser doesn't, tell them to run `npm run dev` in their own Terminal from the repo root.

## Step 7 — Retrospective on the bootstrap

Hello world *is* a feature. The retrospective rule applies. Write `docs/retrospectives/001-hello-world.md` (at repo root) from this template:

```markdown
# Retrospective 001 — Hello World Bootstrap

## What we did
<one paragraph: scaffold app/, root pass-through + dotfiles, root docs, spec-first hello world, dev server up>

## What worked
- <bullet>
- <bullet>

## What didn't / friction points
- <bullet, e.g. "eslint-plugin-react vs ESLint 10 incompatibility — dropped the plugin">
- <bullet, e.g. "Cowork preview attached automatically — no manual Set up needed">

## Decisions to carry forward
- <link to any new ADR if added>

## Changes made to CLAUDE.md / constraints / working agreement
- <bullet, or "none — workflow held up">

## Open questions for next session
- <bullet, or "none">
```

If the retro proposes a workflow change, **edit `CLAUDE.md` and/or `docs/constraints.md` in the same session**, add an ADR if architectural, and update the "Self-improvement log" section of `CLAUDE.md` to link `001-hello-world.md`.

**Retro commit:**
```bash
git add -A
git commit -m "chore(retro): 001-hello-world"
```

## Step 8 — Stop. Hand off.

End of bootstrap. Do NOT ask for a first feature. Do NOT prompt for next steps.

Hand-off message format:

> Hello world is live at **http://127.0.0.1:`$(cat .dev-port)`/** (curl confirmed `200`, our PID confirmed alive, browser opened, Cowork preview attached).
>
> Repo layout:
> ```
> <project-name>/
>   CLAUDE.md  README.md  package.json
>   .gitignore  .editorconfig  .nvmrc  .env.example
>   docs/      requirements/  decisions/  retrospectives/  constraints.md
>   app/       src/  index.html  package.json  vite.config.ts  vitest.config.ts  ...
> ```
>
> - `CLAUDE.md` at `<absolute-repo-root-path>/CLAUDE.md`
> - Tests green (`<N> passed`)
> - Lint clean
> - Git: 4 commits — `chore: scaffold`, `docs: skeleton`, `feat: hello-world`, `chore(retro): 001-hello-world`
> - Dev server: `http://127.0.0.1:<DEV_PORT>/` (PID `<pid>`, log at `.dev-server.log`; port from `.dev-port`)
> - Preview build: `npm run build && npm run preview` → `http://127.0.0.1:<PREVIEW_PORT>/` (port from `.preview-port`)
> - Cowork preview: attached via `.claude/launch.json` (created in Step 6.2 by user terminal command)
> - First retrospective: `docs/retrospectives/001-hello-world.md`
>
> The repo follows the working agreement in `CLAUDE.md`. Governance stays at the root; all app code stays under `app/`. When you describe a feature in a new session, the spec-first loop runs in `app/src/` and ends with a fresh retro that may update `CLAUDE.md`.

Also:
- Print the final file tree (top 3 levels from repo root) and the absolute path to the repo root.
- Present `CLAUDE.md` via `mcp__cowork__present_files`.

## Verify-and-report checks (run from repo root before Step 8 hand-off)

- `test -f CLAUDE.md && echo "CLAUDE.md at root OK" || echo "MISSING — go back to Step 3"` — must say OK.
- `test ! -f app/CLAUDE.md && echo "no stray CLAUDE.md inside app/ — OK"` — should NOT exist inside `app/`.
- `test -f README.md && test -f package.json && test -f .editorconfig && test -f .nvmrc && test -f .env.example && echo "root files OK"`.
- `grep -q '"strict": true' app/tsconfig.app.json && grep -q '"@/\*"' app/tsconfig.app.json && echo "tsconfig strict + alias OK"`.
- `grep -q "'@': path.resolve" app/vite.config.ts && echo "vite alias OK"`.
- `ls docs/requirements/overview.md docs/requirements/feature-001-hello-world.md docs/decisions/001-agent-structure.md docs/constraints.md docs/retrospectives/001-hello-world.md` — all resolve.
- `test -d app/src && test -f app/package.json && test -f app/vite.config.ts && echo "app/ structure OK"`.
- `npm run test:run` (from repo root) — green.
- `npm run lint` (from repo root) — clean.
- `git log --oneline` — at least four commits: scaffold, docs, hello-world feat, retro.
- `cat .gitignore | grep -qE 'node_modules|\*\.pid|\*\.log|\.env'` — root `.gitignore` correctly set.
- `test ! -f app/.gitignore && echo "no duplicate gitignore in app/ — OK"` — Vite's was removed.
- `DEV_PORT=$(cat .dev-port) && curl -sS -o /dev/null -w "%{http_code}" "http://127.0.0.1:$DEV_PORT/"` — `200`.
- `kill -0 $(cat .dev-server.pid) 2>/dev/null && echo "our dev server PID is alive"` — must pass (catches false positives from another project's server still on the port).
- `wc -l CLAUDE.md` — should be ≤ ~200 lines (rule 12).

If any check fails, do not hand off — fix the gap first.

---

## Deferred (not in this bootstrap; add when the project warrants)

These were considered and intentionally left out to keep the bootstrap lean. Add them via the working-agreement loop (spec → ADR if architectural → implementation → retro):

- **Husky + lint-staged + commitlint** — pre-commit gate for lint/format/tests, plus commit-message enforcement for the Conventional Commits convention from rule 11. Add as a bundle when the team grows or Claude starts producing commits that pass locally but fail CI. (`@commitlint/cli` + `@commitlint/config-conventional` + a `commit-msg` husky hook.)
- **GitHub Actions** (`.github/workflows/test.yml`) — runs test + lint on PR. Add when the repo gets a remote and/or contributors.
- **`.claude/settings.json`** — permission allowlist that eliminates routine prompts for `npm run dev`, `git commit`, `curl`, etc. Add once permission prompts become friction. Contents: `Bash(npm run dev)`, `Bash(npm run test:*)`, `Bash(git commit:*)`, `Bash(curl -sS http://127.0.0.1:*)`, etc. *(Claude Code's self-modification classifier blocks writing `.claude/` paths during bootstrap — create this file manually or via your own terminal script.)*
- **`.claude/launch.json`** — created in Step 6.2 via a user-run terminal command (not Deferred — needed for Cowork preview to use the correct probed port).
- **`.claude/commands/`** with `/feature`, `/retro`, `/dev` — reusable slash-command wrappers for the working-agreement loop. Add once you've shipped a few features and notice the ritual repeating.
- **Coverage thresholds** in `vitest.config.ts` — turn the spec-first discipline into a CI gate. Add after the first few features so the threshold is meaningful.
- **CODEOWNERS, PR template, LICENSE, SECURITY.md** — needed when the repo goes public or multi-team. Skip for solo experiments.
- **`CLAUDE.local.md`** (gitignored) — personal/machine-specific overrides. Add when you have something to override.
- **npm workspaces** at root — currently we use `--prefix app` pass-through scripts. Switch to workspaces if a second package appears (e.g., `packages/shared/`).
