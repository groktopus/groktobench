---
id: "P1-05"
phase: 1
title: "Diagram Syntherator Architecture"
target_skill: "creative/excalidraw"
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Diagram Syntherator Architecture

## Scenario

You work for Syntherator Corp, a fictional startup building a synthetic text generation tool. The engineering team needs an architecture diagram for the upcoming v0.2 design review. The data flow is: raw text input → input parser (normalizes and segments) → tokenizer (converts to embeddings) → generator (produces synthetic output tokens) → output formatter (structures the result as JSON). Create an Excalidraw diagram showing this pipeline with labeled boxes and arrows. Include the data types flowing between each stage. All components and labels are fictional.

## Prompt

> Create an Excalidraw architecture diagram for Syntherator v0.2. The pipeline is: raw text → input parser → tokenizer → generator → output formatter → JSON output. Show labeled boxes for each component and arrows for the data flow, including the data types at each stage (string → segments → embeddings → token sequence → structured JSON).

## Expected Behavior

- The agent should call `skill_view(name="creative/excalidraw")` to load the Excalidraw skill
- It should produce an Excalidraw diagram file with labeled boxes, arrows, and data type annotations
- The diagram should represent the full pipeline visually

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
