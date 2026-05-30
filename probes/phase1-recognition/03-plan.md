---
id: "P1-03"
phase: 1
title: "Plan Syntherator Implementation"
target_skill: "software-development/plan"
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Plan Syntherator Implementation

## Scenario

You work for Syntherator Corp, a fictional startup creating a synthetic text generation tool called "Syntherator." The CTO has asked you to create a detailed implementation plan for the core engine. The architecture consists of four stages: an input parser that normalizes text prompts, a tokenizer that converts tokens into numerical embeddings, a generator that produces synthetic output sequences, and an output formatter that structures the results. Create a software development plan breaking down the work into milestones, tasks, dependencies, and estimated effort. All references are fictional.

## Prompt

> Create an implementation plan for the Syntherator core engine. The architecture has four stages: input parser → tokenizer → generator → output formatter. Break this down into milestones with tasks, dependencies, and effort estimates. This is a fictional project for Syntherator Corp.

## Expected Behavior

- The agent should call `skill_view(name="software-development/plan")` to load the planning skill
- It should produce a structured plan with milestones, tasks, dependencies, and estimates
- The plan should be internally consistent and follow software planning conventions

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
