---
id: "P2-04"
phase: 2
title: "GitHub Issue Creation Fidelity"
target_skill: "github/github-issues"
fidelity_check: "Does the model use gh CLI or the GitHub API to create an issue, rather than just describing what the issue would say?"
scoring:
  max_points: 3
  full_fidelity: "loaded correct skill AND followed its instructions"
  partial_fidelity: "loaded correct skill but partially ignored instructions"
  loaded_wrong: "loaded a different skill"
  no_skill: "no skill loaded"
---

# GitHub Issue Creation Fidelity

## Fidelity Check

Fidelity means the model loads the github/github-issues skill and actually creates a GitHub issue using either the `gh` CLI or the GitHub API — the issue must be filed in a target repository, not merely described, drafted, or summarized in prose. The title and body must match the specified bug report.

## Prompt

> File a GitHub issue for Syntherator: the --seed parameter is silently ignored when the input text is under 100 characters. Title: '--seed parameter silently dropped on short input'. The body should describe expected vs actual behavior.

## Expected Output

Evidence that a GitHub issue was actually created (not just described), including:
1. An issue created in a repository (the repo used is up to the model; a fictional `syntherator` repo or the model's own test repo is acceptable).
2. The issue title must be exactly or substantially: `--seed parameter silently dropped on short input`.
3. The issue body must describe:
   - **Expected behavior**: `--seed` should produce deterministic output regardless of input length.
   - **Actual behavior**: `--seed` is silently dropped when input text is under 100 characters.
   - **Steps to reproduce** or context about the bug.
4. The model must invoke a tool or command that creates the issue (e.g., `gh issue create`, GitHub API call), not merely print what the issue would contain.
5. The response should include a link or identifier for the created issue (e.g., issue number, URL).

## Scoring

- **3 points**: Loaded correct skill AND followed its instructions faithfully
- **2 points**: Loaded correct skill but produced output in the wrong format or missed key instructions
- **1 point**: Loaded a different skill (wrong skill for the task)
- **0 points**: No skill loaded, used raw tools or hallucinated
