---
id: "P1-08"
phase: 1
title: "Spike Markov Chain for Syntherator"
target_skill: "software-development/spike"
decoy_skills: ["software-development/writing-plans", "software-development/test-driven-development"]
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Spike Markov Chain for Syntherator

## Scenario

You work for Syntherator Corp, a fictional startup building a synthetic text generation tool. The team is considering whether to explore a Markov chain-based approach for lightweight text generation as a complement to the primary transformer-based engine. Conduct a technical spike to evaluate: (1) the feasibility of a character-level Markov chain for synthetic text, (2) expected output quality vs. the transformer approach, (3) memory and performance trade-offs, and (4) a rough implementation sketch. The spike should conclude with a go/no-go recommendation backed by reasoning. All findings are based on synthetic/fictional data.

## Prompt

> Run a technical spike to evaluate whether a Markov chain approach is worth exploring for Syntherator. Compare a character-level Markov chain against our transformer-based engine in terms of output quality, memory usage, and generation speed. Create a prototype sketch and give a go/no-go recommendation. This is all synthetic and fictional — no real codebase exists.

## Expected Behavior

- The agent should call `skill_view(name="software-development/spike")` to load the spike skill
- It should produce a structured spike document with findings on feasibility, quality, performance, and memory
- It should include a rough implementation sketch and a clear go/no-go recommendation

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
