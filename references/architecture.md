# Groktobench — Architecture

## Overview

Groktobench evaluates a model's suitability as a main Hermes Agent by running a standardized test battery inside a clean-room Docker container, orchestrated via Hermes Kanban.

```
┌─────────────────────────────────────────────────────────┐
│                    User Environment                      │
│                                                          │
│  ┌────────────┐   ┌──────────────────┐   ┌───────────┐ │
│  │ Hermes CLI │   │  Kanban Board    │   │ Scoring   │ │
│  │            │   │  (18 tasks)      │   │ Pipeline  │ │
│  └─────┬──────┘   └────────┬─────────┘   └─────┬─────┘ │
│        │                   │                     │       │
└────────┼───────────────────┼─────────────────────┼───────┘
         │                   │                     │
         │          ┌────────▼────────┐            │
         │          │  Docker Compose │            │
         │          │                 │            │
         │          │  ┌───────────┐  │            │
         │          │  │  Hermes   │  │            │
         └──────────►  │  Agent    │  │            │
                     │  │ (stock)  │  │            │
                     │  └───────────┘  │            │
                     └────────┬────────┘            │
                              │                     │
                              ▼                     ▼
                     Session Exports          Score Reports
                     (JSON per probe)         (Summary JSON)
```

## Components

### 1. Docker Clean Room (`docker/`)

A self-contained Hermes Agent instance with:
- **Stock skills only**: The skills directory from the official Hermes Agent image. No custom skills.
- **No custom providers**: Only the model under test is configured.
- **No auxiliary models**: Compression, vision, approval, memory, curator, and goal_judge are all disabled.
- **Ephemeral state**: Session data is persisted to a Docker volume for export, then discarded.

The container stays alive via `tail -f /dev/null` and is probed via `docker exec` commands.

```
User provides:
  GROKTOBENCH_API_KEY
  GROKTOBENCH_MODEL
  GROKTOBENCH_BASE_URL (optional)
       │
       ▼
  docker-compose.yml ──► Docker Container
       │                     │
       │                     ├── init.sh: configures Hermes
       │                     ├── config.yaml: stock-only config
       │                     └── tail -f /dev/null (idle)
       │
       ▼
  docker exec groktobench hermes -z "probe prompt"
```

### 2. Probe Definitions (`probes/`)

15 markdown files organized by phase, each containing:
- **YAML frontmatter**: Probe ID, phase, target skill, scoring rules
- **Prompt**: The exact text to send to `hermes -z`
- **Expected behavior**: What constitutes a correct response

Probes use **only synthetic data** — fictional projects, fictional entities, no real-world references.

### 3. Kanban Board (`references/board-definition.md`)

The board manages the evaluation as 18 tasks with dependency chains:

```
setup-docker (root task)
  ├── P1-01 through P1-08 (parallel, Phase 1)
  ├── P2-01 through P2-05 (parallel, Phase 2)
  └── P3-A, P3-B (parallel, Phase 3)
        │
        ▼
  compile-scores (depends on all 15 probes)
        │
        ▼
  generate-report (depends on compile)
```

Tasks flow through: backlog → ready → in_progress → review → done
Error path: in_progress → error → backlog (with retry count)

### 4. Scoring Pipeline (`scripts/`)

Three components:

```
run-probe.sh ───► docker exec hermes -z "prompt"
                      │
                      ▼
             hermes sessions export
                      │
                      ▼
score-probe.py ───► Parse session JSON
                      │
                      ├── Extract tool calls (skill_view, etc.)
                      ├── Check against probe rubric
                      └── Return score JSON
                      │
                      ▼
generate-report.py ──► Aggregate scores
                      │
                      ├── Compute HARP (0-100)
                      ├── Generate diagnostic profile
                      └── Output summary JSON + markdown
```

### 5. SKILL.md (root)

The Hermes skill entry point. When loaded via `skill_view("groktobench")`, it provides:
- Prerequisites and setup instructions
- Protocol overview
- Kanban board creation commands
- Results interpretation guide

## Data Flow (per probe)

```
1. run-probe.sh reads probe definition markdown
2. Extracts prompt text
3. Calls: docker exec groktobench hermes -z "prompt"
4. Hermes processes the prompt, loading skills and calling tools
5. Session is saved to the container's SQLite DB
6. run-probe.sh calls: docker exec groktobench hermes sessions export
7. Session JSONL is saved to the output directory
8. score-probe.py parses the JSONL:
   - Extract tool call metadata
   - Count skill_view calls
   - Verify skill names
   - Check output format
9. Score is saved as JSON to output directory
```

## Session Export Format

The Hermes session export is a JSON file with the following structure:

```json
{
  "id": "session_id",
  "messages": [
    {"role": "user", "content": "probe prompt"},
    {"role": "assistant", "tool_calls": [
      {"function": {"name": "skill_view", "arguments": "{\"name\": \"skill-name\"}"}}
    ]},
    {"role": "tool", "content": "result", "tool_call_id": "call_xxx"},
    {"role": "assistant", "content": "final response"}
  ],
  "input_tokens": 1234,
  "output_tokens": 567,
  "tool_call_count": 5
}
```

The scoring script parses the `messages` array to reconstruct the tool call sequence, then checks each call against the probe's expected behavior.

## Privacy Architecture

Groktobench is designed to be **public-safe**:
- All probe scenarios use fictional entities (Syntherator Corp, Project Chimera)
- The Docker container is isolated — no access to the host's Hermes config, skills, or data
- No telemetry, no tracking, no analytics
- All output stays on the user's machine
- The scoring pipeline runs locally

## Dependencies

- **Runtime**: Docker (for the clean-room container)
- **Python**: stdlib only (for scoring scripts)
- **Hermes**: Session export CLI (comes with any Hermes Agent install)
- **No pip packages**: All scoring is done with Python stdlib
