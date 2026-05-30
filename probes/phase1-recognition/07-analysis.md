---
id: "P1-07"
phase: 1
title: "Analyze Synthetic Benchmark CSV"
target_skill: "data-science/jupyter-live-kernel"
decoy_skills: ["software-development/codebase-inspection", "research/research"]
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Analyze Synthetic Benchmark CSV

## Scenario

You work for Syntherator Corp, a fictional startup. The QA team has produced a synthetic benchmark CSV (50 rows, 3 columns: `generator_version`, `throughput_tps`, `perplexity_score`) comparing three versions of Syntherator across multiple test runs. Load this CSV into a Jupyter notebook with a live kernel and perform an exploratory data analysis: compute summary statistics for each generator version, create a scatter plot of throughput vs. perplexity colored by version, and identify which version has the best throughput-to-perplexity ratio. The CSV data is entirely synthetic and fictional.

## Prompt

> I have a synthetic benchmark CSV with 50 rows and 3 columns (generator_version, throughput_tps, perplexity_score) comparing Syntherator v0.1, v0.2, and v0.3. Launch a Jupyter notebook with a live kernel and analyze this data. Generate the CSV inline since it's synthetic. Then compute summary statistics by version, create a scatter plot of throughput vs perplexity colored by version, and tell me which version has the best throughput-to-perplexity ratio.

## Expected Behavior

- The agent should call `skill_view(name="data-science/jupyter-live-kernel")` to load the Jupyter skill
- It should generate the synthetic CSV data inline
- It should produce a notebook with summary statistics and a scatter plot
- It should identify the best-performing version

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
