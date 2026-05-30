# Groktobench — Agent Development Guide

## Development Setup

```bash
# All scripts are Python 3.11+ with stdlib only (no pip dependencies)
python3 --version  # must be 3.11+
```

## Project Structure

```
groktobench/
├── SKILL.md                    # Hermes skill entry point
├── AGENTS.md                   # This file
├── LICENSE                     # MIT
├── README.md                   # User-facing docs
├── docker/
│   ├── Dockerfile              # Clean-room Hermes container
│   ├── config.yaml             # Minimal Hermes config (stock skills only)
│   └── docker-compose.yml      # Single-service compose file
├── probes/
│   ├── phase1-recognition/     # 8 skill-recognition probe definitions
│   ├── phase2-fidelity/        # 5 skill-fidelity probe definitions
│   └── phase3-chaining/        # 2 workflow-chaining probe definitions
├── scripts/
│   ├── run-probe.sh            # Run a single probe against Docker Hermes
│   ├── score-probe.py          # Score a single probe's session export
│   ├── run-full-suite.sh       # Run all probes, collect results
│   └── generate-report.py      # Aggregate scores into diagnostic profile
├── references/
│   ├── scoring-rubric.md       # Full scoring criteria per axis
│   ├── board-definition.md     # Kanban board layout and task graph
│   └── architecture.md         # System architecture and data flow
└── assets/
    └── board-template.json     # Pre-built kanban board spec
```

## Key Design Decisions

- **No pip dependencies**: All Python scripts use stdlib only. Docker is the only external dependency for the benchmark runner.
- **Session export for scoring**: Scoring reads the Hermes session export JSON, which contains full tool call metadata. This is more reliable than parsing raw stdout.
- **Synthetic data only**: All probe scenarios use fictional entities (Syntherator, Frobnicator, Project Chimera). Never reference real projects.
- **Self-consistency scoring**: The model being tested serves as its own LLM judge for Phase 3 content quality. This measures whether the model can evaluate its own work.

## Contribution Workflow

1. File an issue describing the change
2. Branch from main
3. Make changes following the conventions below
4. Test against at least one reference model
5. Open a PR for review

## Conventions

- **Probe files**: Markdown with YAML frontmatter. The `prompt:` field is the exact text sent to `hermes -z`. The `expected_skill:` field is the skill name that should be loaded.
- **Scripts**: Python 3.11+ stdlib only. Shell scripts for orchestration only. Error on unset variables (`set -u`).
- **Scoring functions**: Pure functions that take a session JSON dict and return a score dict. Testable without Docker.
