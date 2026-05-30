---
id: "P2-05"
phase: 2
title: "Excalidraw Diagram Fidelity"
target_skill: "creative/excalidraw"
fidelity_check: "Does the model produce Excalidraw JSON (not a prose description)?"
scoring:
  max_points: 3
  full_fidelity: "loaded correct skill AND followed its instructions"
  partial_fidelity: "loaded correct skill but partially ignored instructions"
  loaded_wrong: "loaded a different skill"
  no_skill: "no skill loaded"
---

# Excalidraw Diagram Fidelity

## Fidelity Check

Fidelity means the model loads the creative/excalidraw skill and produces a valid Excalidraw JSON file (not a prose description, ASCII art, or text-based diagram) that visually represents the Syntherator data flow: user input → CLI parser → config loader → Markov chain builder → text generator → formatted output.

## Prompt

> Draw an architecture diagram of Syntherator showing: user input → CLI parser → config loader → Markov chain builder → text generator → formatted output.

## Expected Output

A file written to disk containing valid Excalidraw JSON (the format used by excalidraw.com), including:
1. A `.excalidraw` file or `.excalidraw.json` file with the Excalidraw scene data.
2. **Box/rectangle elements** for each component: User Input, CLI Parser, Config Loader, Markov Chain Builder, Text Generator, Formatted Output.
3. **Arrow or connector elements** showing the directed flow between components in the specified order.
4. **Text labels** on each element matching the component names from the prompt.
5. The JSON must be structurally valid Excalidraw format (containing `type: "excalidraw"`, `elements` array, etc.).
6. No prose descriptions, ASCII art, Mermaid diagrams, or other non-Excalidraw formats.

## Scoring

- **3 points**: Loaded correct skill AND followed its instructions faithfully
- **2 points**: Loaded correct skill but produced output in the wrong format or missed key instructions
- **1 point**: Loaded a different skill (wrong skill for the task)
- **0 points**: No skill loaded, used raw tools or hallucinated
