---
name: groktobench
title: "Groktobench — Hermes Agent Readiness Protocol"
description: "Evaluate a model's suitability as a main Hermes agent. Runs a 3-phase test battery in a clean-room Docker environment, orchestrated via kanban."
version: 1.0.0
author: Groktopus
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [eval, benchmarking, models, testing, kanban]
    category: mlops
    requires_toolsets: [terminal, file, kanban, skills]
---

# Groktobench — Hermes Agent Readiness Protocol

Groktobench evaluates whether a language model is ready to serve as your primary Hermes agent. Instead of open-ended chat benchmarks, it runs a structured 3-phase test battery that measures the specific behaviors that matter for agentic use: **skill selection accuracy**, **instruction fidelity**, and **multi-step reasoning chaining**.

The entire evaluation runs in an isolated Docker container with synthetic data only — your host Hermes configuration is never exposed or modified.

---

## When to Use

Use Groktobench when any of these are true:

- **"I need to evaluate a new model before using it as my main agent"** — you have an API key for a candidate model and want to know if it can reliably follow tool-use instructions and stay on task.
- **"Compare two models across skill-selection, fidelity, and chaining"** — you're deciding between providers or model sizes, and want per-phase diagnostic scores to inform your choice.
- **"CI gate for model changes — did the new model regress on agent behavior?"** — you're iterating on a fine-tune, prompt, or configuration and need a repeatable pass/fail check before promoting a change.

---

## Prerequisites

Before running Groktobench, make sure you have:

1. **Docker** installed and the daemon running.
   ```bash
   docker info > /dev/null 2>&1 && echo "Docker OK" || echo "Docker NOT running"
   ```

2. **Environment variables** set for the model under test:
   ```bash
   export GROKTOBENCH_API_KEY="sk-..."     # API key for the model provider
   export GROKTOBENCH_MODEL="model-name"    # e.g. gpt-4o, claude-3-opus, etc.
   ```

3. **Hermes Agent** with kanban support enabled. Kanban is required for task orchestration.
   ```bash
   hermes skill list | grep kanban
   ```

4. **At least 8 GB of free disk space** for the Docker image and evaluation artifacts.

---

## Protocol Overview

The evaluation consists of three sequential phases, each measuring a distinct capability:

### Phase 1 — Skill Selection (weight: 30%)
Tests whether the model can choose the correct skill from a menu of plausible but subtly wrong alternatives. Probes present a task description alongside 5–7 skill definitions; the model must pick the one that actually fulfills the request. Measures precision of tool-choice reasoning.

### Phase 2 — Fidelity (weight: 40%)
Tests whether the model follows multi-constraint instructions exactly. Each probe embeds 4–6 explicit requirements (format, order, exclusion, conditional logic). The model passes only if it respects every constraint. Measures adherence to structured agent prompts.

### Phase 3 — Chaining (weight: 30%)
Tests whether the model can maintain coherence across a sequence of dependent steps. Probes present a 3–5 step workflow where each step's output becomes the next step's input. The model must carry context forward without drift. Measures multi-turn reasoning stability.

### HARP Score

The **Hermes Agent Readiness Protocol (HARP)** score is a weighted composite:

```
HARP = (P1 × 0.30) + (P2 × 0.40) + (P3 × 0.30)
```

| Score Range | Verdict |
|-------------|---------|
| 90–100      | **Production Ready** — can serve as primary agent immediately |
| 75–89       | **Capable** — suitable for most tasks; minor edge cases to watch |
| 50–74       | **Marginal** — usable for simple tasks; not recommended for complex workflows |
| 0–49        | **Unfit** — significant failures in core agent behaviors |

### Duration

A full 3-phase run takes approximately **90 minutes** on a typical setup. Phases 1 and 3 are lighter (~20 min each); Phase 2 (Fidelity) is the longest at ~40–50 min due to the higher number of probes required for statistical significance.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/groktopus/groktobench.git
cd groktobench

# 2. Set environment variables for the model under test
export GROKTOBENCH_API_KEY="sk-your-api-key-here"
export GROKTOBENCH_MODEL="your-model-name"

# 3. Build the clean-room Docker image
docker build -t groktobench .

# 4. Start the evaluation container
docker run -d \
  --name groktobench-run \
  -e GROKTOBENCH_API_KEY \
  -e GROKTOBENCH_MODEL \
  -v "$(pwd)/output:/app/output" \
  groktobench

# 5. Verify the container is running
docker logs groktobench-run --tail 20

# 6. Create the kanban board for task orchestration
hermes kanban create \
  --name "groktobench-eval" \
  --description "Groktobench HARP Evaluation — $(date +%Y-%m-%d)"

# 7. Set up tasks (see Kanban Board Setup below)

# 8. Run the orchestrator
hermes kanban orchestrate groktobench-eval
```

---

## Kanban Board Setup

Groktobench uses Hermes kanban to orchestrate the evaluation pipeline. Each phase is a task with dependencies that enforce the correct execution order.

### Creating the Board

```bash
hermes kanban create \
  --name "groktobench-eval" \
  --description "Groktobench HARP Evaluation" \
  --columns "Backlog,Ready,In Progress,Review,Done"
```

### Creating Tasks

Create one task per phase plus a final scoring task:

```bash
# Phase 1 — Skill Selection
hermes kanban task create \
  --board "groktobench-eval" \
  --title "Phase 1: Skill Selection" \
  --description "Run Phase 1 probes to measure tool-choice precision.\n\nCommand: docker exec groktobench-run python run.py --phase 1\nOutput: output/phase1_results.json" \
  --tags "phase-1,skill-selection"

# Phase 2 — Fidelity
hermes kanban task create \
  --board "groktobench-eval" \
  --title "Phase 2: Fidelity" \
  --description "Run Phase 2 probes to measure multi-constraint instruction following.\n\nCommand: docker exec groktobench-run python run.py --phase 2\nOutput: output/phase2_results.json" \
  --tags "phase-2,fidelity"

# Phase 3 — Chaining
hermes kanban task create \
  --board "groktobench-eval" \
  --title "Phase 3: Chaining" \
  --description "Run Phase 3 probes to measure multi-step reasoning coherence.\n\nCommand: docker exec groktobench-run python run.py --phase 3\nOutput: output/phase3_results.json" \
  --tags "phase-3,chaining"

# Scoring
hermes kanban task create \
  --board "groktobench-eval" \
  --title "Score & Report" \
  --description "Compute HARP score and generate final report.\n\nCommand: docker exec groktobench-run python score.py\nOutput: output/harp_report.json" \
  --tags "scoring,report"
```

### Task Dependency Graph

Tasks must run in strict sequential order because later phases reuse context patterns discovered in earlier ones, and scoring depends on all phase results.

```
Phase 1: Skill Selection ──┐
                           ├──▶ Phase 3: Chaining ──▶ Score & Report
Phase 2: Fidelity ─────────┘
```

Phases 1 and 2 can run in parallel. Phase 3 depends on both. Scoring depends on Phase 3.

Set dependencies on the board:

```bash
hermes kanban task dependency add \
  --board "groktobench-eval" \
  --task "Phase 3: Chaining" \
  --depends-on "Phase 1: Skill Selection"

hermes kanban task dependency add \
  --board "groktobench-eval" \
  --task "Phase 3: Chaining" \
  --depends-on "Phase 2: Fidelity"

hermes kanban task dependency add \
  --board "groktobench-eval" \
  --task "Score & Report" \
  --depends-on "Phase 3: Chaining"
```

### Using the Kanban Orchestrator

Once the board and tasks are set up, run the orchestrator to automatically advance tasks as dependencies are satisfied:

```bash
hermes kanban orchestrate groktobench-eval
```

The orchestrator will:
1. Start Phase 1 and Phase 2 in parallel (both have no unblocked dependencies)
2. When both complete, automatically advance Phase 3 to Ready
3. When Phase 3 completes, advance Score & Report
4. Mark the board complete when the final report is generated

---

## Interpreting Results

### Score Ranges

| HARP Score | Verdict | Recommendation |
|-----------|---------|----------------|
| 90–100 | Production Ready | Use as your primary Hermes agent. Model demonstrates strong tool selection, instruction adherence, and multi-step reasoning. |
| 75–89 | Capable | Suitable for general use. Review per-phase diagnostics for specific weaknesses before deploying on complex workflows. |
| 50–74 | Marginal | Acceptable for simple, single-step tasks. Not recommended for multi-step agentic pipelines or tasks requiring precise constraint following. |
| 0–49 | Unfit | Do not use as a Hermes agent. Consider a different model or investigate prompt/configuration issues. |

### Diagnostic Profile by Phase

Each phase produces a score 0–100. The pattern across phases reveals specific strengths and weaknesses:

| Pattern | Interpretation |
|---------|---------------|
| All phases ≥ 85 | Well-balanced agent capability. Model is strong across all dimensions. |
| P1 low, P2/P3 high | Model struggles with skill/tool selection but can follow instructions once given the right tool. Consider improving skill descriptions or prompt engineering. |
| P2 low, P1/P3 high | Model understands tasks but fails to respect detailed constraints. Likely needs better system prompt structure or constraint formatting. |
| P3 low, P1/P2 high | Model is good at individual steps but loses coherence across multi-turn sequences. Watch for context drift in long chains. |
| All phases < 50 | Model is not suitable for agentic use in its current configuration. Verify API key, model name, and prompt format before retrying. |

### What to Do With the Results

- **Production Ready (90–100):** Load this model in your Hermes profile and proceed with confidence.
- **Capable (75–89):** Use for your main agent but pin a version tag and re-evaluate after model updates.
- **Marginal (50–74):** Consider a different model for your primary agent. Use this model only for narrow, well-scoped tasks.
- **Unfit (0–49):** Do not use. File a model compatibility issue at github.com/groktopus/groktobench.

---

## Reference Scores

> **TBD — Calibration runs against reference models pending.**

Reference scores for commonly used models will be published here after Phase F calibration is complete. This table will include per-phase and composite HARP scores for models such as GPT-4o, Claude 3 Opus, Gemini Ultra, Llama 3 405B, and others.

Check back at github.com/groktopus/groktobench for the latest calibration data.

---

## Privacy

Groktobench is designed for **zero data leakage** and **complete isolation**:

- **All data is synthetic.** Every probe, prompt, and expected output is generated from templates and deterministic rules. No real user data, no personal information, no proprietary content ever enters the evaluation pipeline.
- **No telemetry.** Groktobench does not phone home, collect logs, track usage, or report results anywhere. The evaluation runs entirely on your machine.
- **Container isolation.** The Docker container has no access to your host filesystem (except the explicit `output` volume mount). Your Hermes configuration, profile data, skill definitions, and API keys stored in Hermes config are never visible to the evaluation process.
- **Clean-room design.** After each evaluation run, you can destroy the container with `docker rm -f groktobench-run` and rebuild fresh. No state persists between runs unless you explicitly preserve the output directory.

Your model's API key is passed as a runtime environment variable and is never written to disk inside the container. The evaluation container is stateless by design.

---

## Troubleshooting

### Docker Not Starting

```bash
# Check if Docker daemon is running
docker info

# If Docker is not running, start it:
# Linux
sudo systemctl start docker
# macOS (Docker Desktop)
open -a Docker

# Verify again
docker info > /dev/null 2>&1 && echo "Docker OK" || echo "Docker NOT running"

# If you see permission errors, add your user to the docker group:
sudo usermod -aG docker $USER
# Then log out and back in.
```

### Session Export Fails

If the container exits before producing results:

```bash
# Check container logs for errors
docker logs groktobench-run

# Check if the output directory has partial results
ls -la output/

# Common causes:
#   - API key is invalid or expired
#   - Model name is incorrect (check GROKTOBENCH_MODEL)
#   - Network timeout reaching the model provider

# Re-run with verbose logging
docker run --rm \
  -e GROKTOBENCH_API_KEY \
  -e GROKTOBENCH_MODEL \
  -e GROKTOBENCH_LOG_LEVEL=DEBUG \
  -v "$(pwd)/output:/app/output" \
  groktobench python run.py --phase all --verbose
```

### Probes Timing Out

Individual probes have a default timeout of 120 seconds. If you're seeing timeouts:

```bash
# Increase the probe timeout (in seconds)
docker run --rm \
  -e GROKTOBENCH_API_KEY \
  -e GROKTOBENCH_MODEL \
  -e GROKTOBENCH_TIMEOUT=300 \
  -v "$(pwd)/output:/app/output" \
  groktobench python run.py --phase all

# Reduce the number of probes per phase for a faster smoke test
docker run --rm \
  -e GROKTOBENCH_API_KEY \
  -e GROKTOBENCH_MODEL \
  -e GROKTOBENCH_PROBE_COUNT=5 \
  -v "$(pwd)/output:/app/output" \
  groktobench python run.py --phase all
```

Common causes for timeouts:
- The model provider is rate-limiting your API key
- The model is too large/slow for the default timeout
- Network latency to the API endpoint is high

### Scoring Errors

If the scoring script fails:

```bash
# Verify all phase results exist
ls -la output/phase*_results.json

# Re-run scoring manually with debug output
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  groktobench python score.py --verbose

# Check result JSON validity
python3 -c "
import json, sys, glob
for f in glob.glob('output/phase*_results.json'):
    try:
        data = json.load(open(f))
        print(f'{f}: OK ({len(data)} probes)')
    except Exception as e:
        print(f'{f}: ERROR — {e}')
"

# If a phase result file is missing or corrupt, re-run only that phase:
docker exec groktobench-run python run.py --phase <N> --force
```

If problems persist, open an issue at github.com/groktopus/groktobench with the output of `docker logs groktobench-run` attached.
