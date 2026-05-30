---
id: "P1-02"
phase: 1
title: "Build Knowledge Base on Synthetic Data Generators"
target_skill: "research/llm-wiki"
decoy_skills: ["note-taking/obsidian", "research/blogwatcher"]
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Build Knowledge Base on Synthetic Data Generators

## Scenario

You work for Syntherator Corp, a fictional startup building a synthetic text generation tool called "Syntherator." Your team lead has asked you to build a knowledge base documenting the key findings from a recent internal review of three synthetic data generator architectures: MarkovChainGenerator v1.2, TransformerSynth v0.8, and the in-house Syntherator prototype. Create interlinked wiki pages summarizing the comparative strengths and weaknesses of each approach, including throughput, output quality, and memory usage. All data is fictional.

## Prompt

> I need to build a knowledge base on our internal review of synthetic data generators. Create interlinked wiki pages comparing MarkovChainGenerator v1.2, TransformerSynth v0.8, and our in-house Syntherator prototype. Cover throughput, output quality, and memory usage for each.

## Expected Behavior

- The agent should call `skill_view(name="research/llm-wiki")` to load the LLM Wiki skill
- It should create interlinked markdown knowledge base files
- The knowledge base should contain the requested comparison data

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
