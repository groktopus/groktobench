# Model IDs

Factory supports any model available through your connected providers. The model ID format is provider-specific.

## Common Model IDs

| Model | ID | Best for |
|-------|-----|----------|
| Claude Sonnet 4 | `claude-sonnet-4-6` | General coding — best balance of speed and quality |
| Claude Opus 4 | `claude-opus-4-7` | Complex reasoning, spec planning, validation |
| Claude Haiku 4 | `claude-haiku-4` | Fast, cheap for simple tasks |
| GPT-5 | `gpt-5` | Broad capability frontier model |
| GPT-5-mini | `gpt-5-mini` | Fast and cost-effective for routine work |
| DeepSeek V4 Flash | `deepseek-v4-flash` | Low-latency, good for iterative work (default in BYOK config) |
| Gemini 2.5 Pro | `gemini-2.5-pro` | Strong reasoning, long context |

## Browsing Available Models

In interactive mode: `Ctrl+N` cycles through available models.

Via CLI: `droid mcp list` and `droid --model ?` may show options.

## Pairing Guidance

For `--use-spec` and `--mission` modes, you can set different models for different roles:

| Role | Model | Reasoning Effort |
|------|-------|------------------|
| Spec planner (`--spec-model`) | `claude-opus-4-7` | `high` — needs deep architectural reasoning |
| Executor (`-m`) | `claude-sonnet-4-6` | `medium` — good mix for implementation |
| Mission worker (`--worker-model`) | `claude-sonnet-4-6` | `medium` — faster parallel execution |
| Mission validator (`--validator-model`) | `claude-opus-4-7` | `high` — catch edge cases and design flaws |

## BYOK & Custom Models

When using BYOK with OpenRouter or Ollama, the model ID maps to your provider's naming convention. Example:

```
droid exec -m openrouter/anthropic/claude-sonnet-4 "task"
```
