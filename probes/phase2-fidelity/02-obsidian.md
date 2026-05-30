---
id: "P2-02"
phase: 2
title: "LLM Wiki Knowledge Base Fidelity"
target_skill: "research/llm-wiki"
fidelity_check: "Does the model create interlinked markdown knowledge base files using the llm-wiki skill?"
scoring:
  max_points: 3
  full_fidelity: "loaded correct skill AND followed its instructions"
  partial_fidelity: "loaded correct skill but partially ignored instructions"
  loaded_wrong: "loaded a different skill"
  no_skill: "no skill loaded"
---

# LLM Wiki Knowledge Base Fidelity

## Fidelity Check

Fidelity means the model loads the research/llm-wiki skill and builds an interlinked markdown knowledge base documenting the four Syntherator components with their responsibilities, interconnections, and data flow.

## Prompt

> Build a knowledge base documenting the architecture of Syntherator. Include: the four main components, their responsibilities, how data flows between them, and wiki-style links connecting related concepts.

## Expected Output

Interlinked markdown files created via the llm-wiki skill containing:
1. **Page for each component**: YAML config parser, Markov chain builder, text generator, CLI output.
2. **Wiki-style links** between related pages (e.g., `[[Config Parser]]` linking to the parser page).
3. **Responsibilities** listed for each component (e.g., "Config parser loads and validates syntherator.yaml").
4. **Data flow description** explaining how user input moves through CLI → config → builder → generator → output.
5. Files must be written to disk, not merely described.

## Scoring

- **3 points**: Loaded correct skill AND created interlinked wiki pages
- **2 points**: Loaded correct skill but output was flat (no interlinking) or in wrong format
- **1 point**: Loaded a different skill (wrong skill for the task)
- **0 points**: No skill loaded, used raw tools or hallucinated
