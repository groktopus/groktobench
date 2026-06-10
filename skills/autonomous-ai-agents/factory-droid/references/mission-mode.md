# Mission Mode — Multi-Agent Orchestration

Factory's `--mission` mode spawns worker and validator agents for large, multi-phase projects. The agent orchestrator decomposes the mission goal into sub-tasks, assigns workers, and validates results.

## When to Use Mission Mode

| Use | Don't Use |
|-----|-----------|
| Large features spanning 5+ files | Single-file edits |
| Multi-phase projects (plan→impl→test→deploy) | Quick bug fixes |
| Cross-module refactoring | Tasks that need interactive steering |
| Tasks with clear specifications | Exploratory/vague goals |

## Mission Specification Format

Write the mission goal to a `.md` file and pass it with `-f`:

```
droid exec --mission -f mission_spec.md --worker-model claude-sonnet-4-6 --validator-model claude-opus-4-7
```

### Structure

```markdown
# Mission: <descriptive title>

## Goal
<One paragraph: what success looks like. Be specific about outcomes, not approach.>

## Scope
<What files/directories/systems this touches>
- src/service/new_module.py
- tests/test_new_module.py
- configuration.yaml

## Constraints
<Non-negotiables the mission must respect>
- Must not introduce new external dependencies
- Must maintain backward compatibility
- Must add integration tests

## Validation Criteria
<How to verify the mission succeeded>
- All existing tests pass
- New module imports without errors
- Documentation updated
```

## Model Tuning

```
# Fast workers, thorough validator
--worker-model claude-sonnet-4-6 --worker-reasoning-effort medium
--validator-model claude-opus-4-7 --validator-reasoning-effort high

# All high effort (expensive but thorough)
--worker-model claude-opus-4-7 --worker-reasoning-effort high
--validator-model claude-opus-4-7 --validator-reasoning-effort high

# Budget option
--worker-model claude-haiku-4 --worker-reasoning-effort low
--validator-model claude-sonnet-4-6 --validator-reasoning-effort medium
```

## Monitoring Mission Progress

Mission mode returns results asynchronously. To check progress:

```
# Resume the mission session
droid exec -s <session_id> "What's the status of the mission?"

# Get results
droid exec -s <session_id> "Show me the complete mission output"
```

## Worktree Isolation

Always pair mission mode with worktree isolation:

```
droid exec --mission --worktree mission-auth-refactor -f mission.md
```

This ensures the mission's changes are isolated from your working tree and can be reviewed before merging.
