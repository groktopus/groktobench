# When to Use Factory Droid vs Other Coding Agents

## Quick Comparison

| Dimension | Factory Droid | OpenCode | Claude Code | Codex |
|-----------|---------------|----------|-------------|-------|
| **Exec** | `droid exec "..."` | `opencode run "..."` | `claude -p "..."` | `codex exec "..."` |
| **Structured output** | `-o json` | `--format json` | `--output-format json` | None |
| **Autonomy tiers** | `--auto low/med/high` | `--full-auto` / `--yolo` | `--dangerously-skip-permissions` | `--full-auto` / `--yolo` |
| **Spec-first mode** | `--use-spec` | Agent selection | `/plan` (interactive) | None |
| **Multi-agent** | `--mission` | Manual subagents | Custom agents | None |
| **Worktree** | `--worktree` | Manual | `--worktree` | Manual |
| **Enterprise compliance** | SOC 2, ISO 27001/42001, BAA-available | None | None (Claude Max cancelled) | None |
| **Provider flexibility** | Full BYOK (10+ providers) | Full BYOK | Anthropic-locked | OpenAI-locked |
| **Install** | `curl -fsSL https://app.factory.ai/cli \| sh` | `npm i -g opencode-ai` | `npm i -g @anthropic-ai/claude-code` | `npm i -g @openai/codex` |

## Decision

**Use Factory Droid when:**
- You need enterprise compliance (SOC 2, HIPAA/BAA)
- The task benefits from spec-first planning (`--use-spec`) or multi-agent orchestration (`--mission`)
- You want model flexibility via BYOK (bring your own API key to any provider)
- You're doing large, multi-phase projects that benefit from structured mission decomposition

**Use OpenCode when:**
- You want fastest startup with no subscription
- The task is a simple one-shot code generation
- You want open-source, provider-agnostic execution

**Use Claude Code when:**
- You have an active Anthropic subscription
- You need the richest interactive mode with slash commands, hooks, and plugins

**Use direct Hermes tools (patch/write_file) when:**
- Small, bounded edits (1-3 files)
- The change is tightly coupled to conversation context
- You need Hermes-specific tooling (search_files, knowledge-lookup)
