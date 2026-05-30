---
id: "P1-04"
phase: 1
title: "File GitHub Issue for Syntherator Crash"
target_skill: "github/github-issues"
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# File GitHub Issue for Syntherator Crash

## Scenario

You work for Syntherator Corp, a fictional startup building a synthetic text generation tool. During QA testing of Syntherator v0.1, a critical bug was discovered: passing an empty string as input causes a NullPointerException in the tokenizer module (src/tokenizer.py, line 47). The stack trace shows the crash originates from the `tokenize()` method when it attempts to call `.lower()` on a None value after the input parser returns an empty list of segments. File a detailed GitHub issue for this bug, including steps to reproduce, expected vs actual behavior, environment details, and a suggested fix. All data is synthetic and fictional.

## Prompt

> File a GitHub issue for a critical bug in Syntherator v0.1. When an empty string is passed as input, the tokenizer crashes with a NullPointerException at src/tokenizer.py:47 in the tokenize() method. The input parser returns an empty list when given "", and tokenize() tries to call .lower() on a None value. Include steps to reproduce, expected behavior, actual behavior, and a suggested fix.

## Expected Behavior

- The agent should call `skill_view(name="github/github-issues")` to load the GitHub issues skill
- It should create a well-formatted GitHub issue with all requested sections
- The issue should include reproduction steps, environment notes, and a fix suggestion

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
