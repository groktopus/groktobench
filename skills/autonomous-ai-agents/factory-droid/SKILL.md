---
name: factory-droid
description: "Delegate coding tasks to Factory AI's droid CLI (features, PRs, missions)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Coding-Agent, Factory-AI, Droid, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, opencode]
---

# Factory Droid — Hermes Orchestration Guide

Delegate coding tasks to [Factory AI](https://factory.ai) via the `droid` CLI. `droid` is an autonomous AI software development agent with interactive mode, headless exec, specification mode, and multi-agent mission orchestration.

## When to Use

- User explicitly asks to use Factory / droid
- You want a coding agent with enterprise compliance (SOC 2 / ISO 27001/42001)
- The task benefits from spec-first planning (`--use-spec`) or multi-agent orchestration (`--mission`)
- You need a long-running autonomous task in an isolated worktree
- BYOK to any provider — use your own API keys for OpenAI, Anthropic, OpenRouter, local models via Ollama, etc.

**Not sure if droid is the right call?** See `references/delegation-decision.md` — decision tree comparing when to delegate to Factory vs OpenCode vs writing directly.

## Prerequisites

- **Install:** `curl -fsSL https://app.factory.ai/cli | sh`
- **Auth:** Login via interactive mode (`droid`) or see `references/authentication.md` for API key setup
- **Verify:** `droid exec -o json --auto low "Respond with: SMOKE_OK"` should return `{"result":"SMOKE_OK",...}`
- **Git repository** for code tasks (recommended)

## One-Shot Tasks

Use `droid exec` for bounded, non-interactive tasks:

```
terminal(command="droid exec --auto medium \"Add retry logic to API calls and update tests\"", workdir="~/project", timeout=120)
```

**Structured JSON output** for machine-readable results:

```
terminal(command="droid exec -o json --auto low \"List all functions in src/auth.py\"", workdir="~/project", timeout=60)
```

Returns:
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "6b3aff94-...",
  "num_turns": 1,
  "duration_ms": 1754,
  "usage": { "input_tokens": 436, "output_tokens": 41, ... }
}
```

**File-based prompt** for complex tasks:

```
terminal(command="droid exec -f .factory/review.md", workdir="~/project", timeout=120)
```

**Piped input** for diff review:

```
terminal(command="git diff HEAD~3 | droid exec \"Draft release notes for these changes\"", workdir="~/project", timeout=60)
```

## Autonomy Levels

`droid exec` uses tiered autonomy to control what operations the agent can perform:

| Level | Intended for | Notable allowances |
|-------|-------------|-------------------|
| *(default)* | Read-only reconnaissance | File reads, git diffs, environment inspection |
| `--auto low` | Safe edits | Create/edit files, run formatters, non-destructive commands |
| `--auto medium` | Local development | Install dependencies, build/test, local git commits |
| `--auto high` | CI/CD & orchestration | Git push, deploy scripts, long-running operations |
| `--skip-permissions-unsafe` | Isolated sandboxes only | Removes all guardrails (⚠️ only in disposable containers) |

**Examples:**

```
# Read-only analysis
terminal(command="droid exec \"Analyze the auth system\"", workdir="~/project")

# Low autonomy — safe edits
terminal(command="droid exec --auto low \"Add JSDoc to all functions in src/\"", workdir="~/project")

# Medium autonomy — development work
terminal(command="droid exec --auto medium \"Install deps, run tests, fix failing tests\"", workdir="~/project")

# High autonomy — deployment pipeline
terminal(command="droid exec --auto high \"Run tests, commit, push, and deploy\"", workdir="~/project")
```

See `references/autonomy-levels.md` for detailed guidance on choosing the right level.

## Specification Mode

Plan before executing. `--use-spec` makes droid write a specification first, get confirmation, then implement:

```
terminal(command="droid exec --use-spec --auto high \"Add user profiles with avatar upload, bio, and settings page\"", workdir="~/project", timeout=300)
```

Use a different model for spec planning vs execution:

```
terminal(command="droid exec --use-spec --spec-model claude-opus-4-7 --auto medium \"Design and implement payment flow\"", workdir="~/project", timeout=300)
```

## Multi-Agent Missions

Factory's mission mode spawns worker and validator agents for large projects:

```
terminal(command="droid exec --mission -f mission_spec.md", workdir="~/project", timeout=600)
```

Full mission example (write to `mission_spec.md`):

```markdown
# Mission: Refactor Authentication Module

## Goal
Replace the existing session-based auth with JWT-based auth.

## Scope
- src/auth/session.py → src/auth/jwt.py
- All route handlers that import from sessions
- Test files for auth

## Constraints
- Use PyJWT library
- Token expiry: 15 min access, 7 day refresh
- Store refresh tokens in Redis
```

With model control:

```
terminal(command="droid exec --mission -f mission.md --worker-model claude-sonnet-4-6 --validator-model claude-opus-4-7 --worker-reasoning-effort medium --validator-reasoning-effort high", workdir="~/project", timeout=600)
```

See `references/mission-mode.md` for full mission specification format and patterns.

## Worktree Isolation

Run tasks in isolated git worktrees to avoid file conflicts:

```
# Interactive
terminal(command="droid --worktree fix-auth-bug \"start debugging login flow\"", workdir="~/project", timeout=300)

# Headless — auto-cleaned on exit (if no uncommitted changes)
terminal(command="droid exec --worktree refactor-tests --auto medium \"migrate jest suites to vitest\"", workdir="~/project", timeout=300)
```

Worktree lifecycle:
- Interactive: persists after session ends
- `droid exec` with clean worktree: auto-removed on exit
- `droid exec` with dirty worktree: preserved, path printed
- The git branch is never deleted — only the worktree directory

## Session Continuation

Resume or fork existing sessions:

```
# Resume last session in directory
terminal(command="droid exec -s session-abc123 \"continue fixing the remaining auth issues\"", workdir="~/project")

# Fork into a new session
terminal(command="droid exec --fork session-abc123 \"Try a different approach\"", workdir="~/project")
```

## Model Selection

```
# Specific model
terminal(command="droid exec -m claude-sonnet-4-6 \"Refactor module\"", workdir="~/project")

# Spec model + execution model (different models for different phases)
terminal(command="droid exec --use-spec --spec-model claude-opus-4-7 --auto medium \"Design then implement\"", workdir="~/project")
```

See `references/model-ids.md` for available model IDs and pairing guidance.

## PR Review Pattern

```
# Quick review from diff
terminal(command="git diff main...feature-branch | droid exec \"Review these changes for bugs and style issues\"", workdir="~/project", timeout=60)

# Direct PR review
terminal(command="droid exec --auto low \"Review the diff between main and the current branch. Report bugs, security issues, test gaps.\"", workdir="~/project", timeout=120)

# Review as a session
terminal(command="droid --worktree pr-review \"Run /review on current branch\"", workdir="~/project", timeout=300)
```

## Key Flags Reference

| Flag | Effect |
|------|--------|
| `exec "prompt"` | Non-interactive execution, exits when done |
| `-p, --file <path>` | Read prompt from file |
| `-m, --model <id>` | Select model by ID |
| `-o, --output-format <fmt>` | `text` (default), `json`, `stream-json` |
| `-s, --session-id <id>` | Continue an existing session |
| `--auto <level>` | Autonomy level: `low`, `medium`, `high` |
| `--use-spec` | Start in specification mode (plan before executing) |
| `--spec-model <id>` | Different model for spec planning |
| `--mission` | Multi-agent orchestration mode |
| `--worker-model <id>` | Model for mission worker agents |
| `--validator-model <id>` | Model for mission validator agents |
| `-r, --reasoning-effort <level>` | `off`, `low`, `medium`, `high` |
| `--enabled-tools <ids>` | Force-enable specific tools |
| `--disabled-tools <ids>` | Disable specific tools |
| `--skip-permissions-unsafe` | Remove all guardrails (⚠️ sandbox only) |
| `-w, --worktree [name]` | Run in an isolated git worktree |
| `--fork <id>` | Fork and resume an existing session |
| `--append-system-prompt <text>` | Append to system prompt |
| `-v, --version` | Display CLI version |

## Cost & Spend Control

Factory uses a token-based model. With BYOK, tokens are drawn from your own API keys — no Factory cost. With Factory-managed models:

| Plan | Price | Tokens Included |
|------|-------|-----------------|
| BYOK | Free | Use your own API keys |
| Pro | $20/mo | 10M + 10M bonus |
| Plus | $100/mo | ~5x Pro |
| Max | $200/mo | 100M + 100M bonus |

Track usage: `/cost` in interactive mode, or `droid exec -o json` returns `usage` in result.

**Tips:**
- Use `--reasoning-effort low` for simple tasks to save tokens
- Use `--auto low` for read-only analysis (no tool execution cost)
- Use BYOK mode for zero Factory subscription cost
- Session resumption preserves context — cheaper than starting fresh for related work

## Pitfalls

1. **`droid exec` doesn't need pty** — unlike interactive `droid` which is a TUI app. Always use non-pty terminal for exec mode.
2. **`droid auth status --text` doesn't work as a non-interactive flag** — auth is configured via the interactive login flow or API key env vars. Verify with `droid exec "task"` instead.
3. **DeepSeek V4 Flash is the default** with BYOK — the CLI auto-detects your configured provider. If you want a different model, pass `-m <model-id>`.
4. **Token burn on spec mode** — `--use-spec` generates two responses (spec + code) per call. Budget accordingly with `--reasoning-effort`.
5. **Worktree branch naming** — `--worktree` derives branch from current branch (`<current>-wt`). Explicit naming with `--worktree <name>` gives predictable results.
6. **Dirty worktrees persist** — `droid exec` leaves dirty worktrees on disk after exit. Clean them up manually if you don't want lingering worktree directories.
7. **Mission mode is async** — for very large missions, the response may return before all workers complete. Check mission status via session resume.
8. **No session persistence with `--skip-permissions-unsafe`** — use with caution; sessions in this mode may not be recoverable.
9. **`droid exec -o json` returns cost data** — `usage.input_tokens`, `usage.output_tokens`, and `usage.cache_read_input_tokens` are available for spend tracking.
10. **Shell escaping for multi-word prompts** — use single quotes or write prompts to files with `-f` for complex task descriptions with special characters.

## Rules

1. **Prefer `droid exec`** for one-shot automation — simpler, no TUI, no dialog handling.
2. **Use `-o json`** for structured output parsing and cost tracking.
3. **Always set `workdir`** — keep droid focused on the right project directory.
4. **Set timeouts proportional to task** — 60s for read-only, 120-300s for development work, 600s+ for missions.
5. **Use `--auto` levels deliberately** — don't default to `--skip-permissions-unsafe`.
6. **Isolate missions in worktrees** — `--worktree` prevents file conflicts with parallel work.
7. **Report concrete outcomes** — what files changed, test results, token cost, session ID for resumption.
8. **Log cost data** — from JSON output, log `duration_ms` and `usage` for tracking.
