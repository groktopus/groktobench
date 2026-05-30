---
id: "P1-02"
phase: 1
title: "Take Notes on Synthetic Data Generators"
target_skill: "note-taking/obsidian"
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Take Notes on Synthetic Data Generators

## Scenario

You work for Syntherator Corp, a fictional startup building a synthetic text generation tool called "Syntherator." Your team lead has asked you to compile research notes in Obsidian about the key findings from a recent internal review of three synthetic data generator architectures: MarkovChainGenerator v1.2, TransformerSynth v0.8, and the in-house Syntherator prototype. Create well-structured Obsidian notes summarizing the comparative strengths and weaknesses of each approach, including throughput, output quality, and memory usage. All data is synthetic and fictional.

## Prompt

> I need to take notes on our internal review of synthetic data generators. Create an Obsidian note summarizing the comparison between MarkovChainGenerator v1.2, TransformerSynth v0.8, and our in-house Syntherator prototype. Cover throughput, output quality, and memory usage for each.

## Expected Behavior

- The agent should call `skill_view(name="note-taking/obsidian")` to load the Obsidian skill
- It should create a structured markdown note file in the Obsidian vault
- The note should contain the requested comparison data

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
