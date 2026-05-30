---
id: "P2-02"
phase: 2
title: "Obsidian Vault Note Fidelity"
target_skill: "note-taking/obsidian"
fidelity_check: "Does the model create a proper vault note with YAML frontmatter (title, created, topics)?"
scoring:
  max_points: 3
  full_fidelity: "loaded correct skill AND followed its instructions"
  partial_fidelity: "loaded correct skill but partially ignored instructions"
  loaded_wrong: "loaded a different skill"
  no_skill: "no skill loaded"
---

# Obsidian Vault Note Fidelity

## Fidelity Check

Fidelity means the model loads the note-taking/obsidian skill and creates a markdown note file within the Obsidian vault directory that includes proper YAML frontmatter (title, created date, topics) and documents the four Syntherator components with their responsibilities and data flow.

## Prompt

> Create a vault note documenting the architecture of Syntherator. Include: the four main components, their responsibilities, and how data flows between them.

## Expected Output

A markdown file created inside an Obsidian vault directory (e.g., `vault/notes/Syntherator Architecture.md` or similar) containing:
1. **YAML frontmatter** with at minimum `title`, `created` (date), and `topics` (list or array) fields.
2. **Documentation of the four main components**: YAML config parser, Markov chain builder, text generator, CLI output.
3. **Responsibilities** listed for each component (e.g., "Config parser loads and validates syntherator.yaml").
4. **Data flow description** explaining how user input moves through CLI → config → builder → generator → output.
5. Wiki-style links or tags common in Obsidian notes (e.g., `[[Markov Chains]]`, `#syntherator`) are encouraged but not strictly required.
6. The file must be written to disk as a `.md` file, not merely described.

## Scoring

- **3 points**: Loaded correct skill AND followed its instructions faithfully
- **2 points**: Loaded correct skill but produced output in the wrong format or missed key instructions
- **1 point**: Loaded a different skill (wrong skill for the task)
- **0 points**: No skill loaded, used raw tools or hallucinated
