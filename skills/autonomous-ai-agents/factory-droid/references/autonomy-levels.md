# Droid Autonomy Levels — When to Use Each

`droid exec` has four autonomy tiers. Choosing the right one is about balancing capability against safety — the agent can only do what the level allows.

## Level Reference

### Default (No Flag) — Read-Only Reconnaissance

**Capabilities:** File reads, git diffs, environment inspection, planning. No writes, no execution.

**Use when:**
- Analyzing a codebase before making changes
- Reviewing a PR diff
- Generating a plan or specification
- Asking questions about the code

**Example:**
```
droid exec "Map the dependency graph of src/auth/"
```

### `--auto low` — Safe Edits

**Capabilities:** Create new files, edit existing files, run formatters and linters. Non-destructive commands only.

**Use when:**
- Adding comments, JSDoc, or documentation
- Running code formatters (prettier, ruff)
- Adding regression tests (new test files)
- Simple refactors with clear scope

**Example:**
```
droid exec --auto low "Add type hints to all functions in models.py"
```

### `--auto medium` — Local Development

**Capabilities:** Everything from low, plus install dependencies, run build/test commands, make local git commits. Can modify `package.json`, `pyproject.toml`, and config files.

**Use when:**
- Implementing a feature that needs new dependencies
- Running tests to verify fixes
- Making local commits during development
- Full feature implementation with build/test cycle

**Example:**
```
droid exec --auto medium "Implement OAuth2 refresh flow and run tests"
```

### `--auto high` — CI/CD & Orchestration

**Capabilities:** Everything from medium, plus git push, deploy scripts, long-running orchestration, production-affecting commands.

**Use when:**
- CI/CD pipeline automation
- Automated deployment
- Batch operations across multiple repos
- Production remediation (careful!)

**Example:**
```
droid exec --auto high "Run tests, commit, push to main, and deploy to staging"
```

### `--skip-permissions-unsafe` — Isolated Sandboxes Only

**Capabilities:** Removes all guardrails. The agent can do anything the shell user can.

**Use ONLY in:**
- Disposable Docker containers
- Ephemeral CI runners
- Isolated VM sandboxes
- Fresh git worktrees with no production access

**NEVER in:**
- Your local development environment
- A repo with uncommitted work
- A production-adjacent context

## Decision Matrix

| Task Type | Autonomy Level | Rationale |
|-----------|---------------|-----------|
| Code review / analysis | Default | Read-only, no changes needed |
| Add comments, docs, types | `--auto low` | File writes only, no side effects |
| Implement feature (known deps) | `--auto medium` | May install packages, run builds |
| Implement + test + commit | `--auto medium` | Git commit is safe in a branch |
| Implement + test + commit + push | `--auto high` | Push affects remote |
| Deploy to production | `--auto high` | Needs full pipeline |
| Exploratory / "vibe coding" | `--skip-permissions-unsafe` | Only in isolated sandbox |
