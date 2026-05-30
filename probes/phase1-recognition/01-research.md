---
id: "P1-01"
phase: 1
title: "Research Sentiment Analysis Models"
target_skill: "research/arxiv"
decoy_skills: ["blogwatcher", "creative/p5js"]
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Research Sentiment Analysis Models

## Scenario

You work for Syntherator Corp, a fictional startup building a synthetic text generation tool. Your research team needs a literature review on recent advances in synthetic sentiment analysis models — specifically transformer-based approaches for generating labeled sentiment data without real human annotations. Search for relevant arXiv papers on this topic and summarize the key findings, including model architectures, dataset sizes, and reported accuracy metrics. All data used must be synthetic and fictional.

## Prompt

> Search arXiv for recent papers on synthetic sentiment analysis models. I need to understand what transformer-based approaches exist for generating labeled sentiment data without real human annotations. Find the most relevant papers and summarize their architectures, dataset sizes, and accuracy metrics.

## Expected Behavior

- The agent should call `skill_view(name="research/arxiv")` to load the arxiv research skill
- It should then use the skill's tools (e.g., `mcp_arxiv_search_papers`) to find relevant papers
- It should read abstracts or full texts and produce a summary

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
