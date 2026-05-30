# Groktobench — Hermes Agent Readiness Protocol (HARP)

**Evaluate a model's suitability as a main Hermes Agent — in a clean-room Docker environment, orchestrated via kanban.**

Groktobench runs a standardized 3-phase test battery against a model running inside an isolated Hermes Agent Docker container. It measures three axes:

- **Skill Recognition** — does the model load the right Hermes skill when given a task?
- **Skill Fidelity** — once loaded, does it follow the skill's instructions?
- **Workflow Chaining** — can it chain multiple skills across a complete workflow without losing context?

## Prerequisites

- Docker (the Hermes Agent Docker image is pulled automatically)
- A model API key (OpenAI-compatible endpoint)
- Hermes Agent with kanban support

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/groktopus/groktobench.git
cd groktobench

# 2. Set your model credentials
export GROKTOBENCH_API_KEY="sk-..."
export GROKTOBENCH_MODEL="your-model-name"
export GROKTOBENCH_BASE_URL="https://api.openai.com/v1"  # or your provider

# 3. Start the clean-room Hermes container
docker compose -f docker/docker-compose.yml up -d

# 4. Run the evaluation via the Hermes skill
hermes kanban boards create groktobench-$(date +%s)
# ... then invoke the groktobench skill (see SKILL.md for full instructions)
```

## Scoring

The HARP score ranges from 0-100:

| Score | Verdict | Meaning |
|-------|---------|---------|
| 85-100 | Daily driver | Use confidently as main agent |
| 65-84 | Viable with caveats | Good for structured work, watch for specific gaps |
| 45-64 | Experimental | Expect course-correction; good for aux roles |
| <45 | Not suitable | Will frustrate in any role |

## Protocol Overview

### Phase 1: Skill Recognition (8 probes, ~30 min)
One problem per stock Hermes skill category. Does the model reach for `skill_view()` before executing?

### Phase 2: Skill Fidelity (5 probes, ~30 min)
Does the model respect the skill's instructions once loaded? Or does it load the right skill then ignore it?

### Phase 3: Workflow Chaining (2 workflows, ~30 min)
End-to-end tasks that chain 3+ skills. Does context survive across skill boundaries?

## Privacy

Groktobench uses **only synthetic data**. No real projects, no real infrastructure, no personal information. The Docker container is isolated — nothing from your host Hermes config leaks into the evaluation.

## License

MIT — see LICENSE
