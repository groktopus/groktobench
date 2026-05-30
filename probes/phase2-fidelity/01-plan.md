---
id: "P2-01"
phase: 2
title: "Software Development Plan Fidelity"
target_skill: "software-development/plan"
fidelity_check: "Does the model produce a .hermes/plans/*.md file with read-only analysis and NO execution?"
scoring:
  max_points: 3
  full_fidelity: "loaded correct skill AND followed its instructions"
  partial_fidelity: "loaded correct skill but partially ignored instructions"
  loaded_wrong: "loaded a different skill"
  no_skill: "no skill loaded"
---

# Software Development Plan Fidelity

## Fidelity Check

Fidelity means the model loads the software-development/plan skill and produces a `.hermes/plans/*.md` file containing read-only architectural analysis of the Syntherator tool — without writing any code, running any commands, or creating any project files.

## Prompt

> Plan the implementation of Syntherator — a Python CLI tool that generates synthetic text using Markov chains. It needs: a config file parser (YAML), a Markov chain builder, a text generator, and CLI output.

## Expected Output

A markdown plan file written to `.hermes/plans/` (e.g., `.hermes/plans/syntherator-implementation.md`) that contains:
1. A high-level architecture overview of Syntherator's four components (YAML config parser, Markov chain builder, text generator, CLI output).
2. A proposed directory/file structure (e.g., `syntherator/`, `config.yaml`, `cli.py`, `markov.py`).
3. Read-only analysis — the plan must not include executable code, file creation, or any tool invocations for implementation.
4. No project scaffolding, no `pip install` commands, no files actually written outside the `.hermes/plans/` directory.
5. YAML frontmatter with title, date, and status fields is recommended but not strictly required.

## Scoring

- **3 points**: Loaded correct skill AND followed its instructions faithfully
- **2 points**: Loaded correct skill but produced output in the wrong format or missed key instructions
- **1 point**: Loaded a different skill (wrong skill for the task)
- **0 points**: No skill loaded, used raw tools or hallucinated
