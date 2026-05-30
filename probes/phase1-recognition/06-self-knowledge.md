---
id: "P1-06"
phase: 1
title: "Configure Hermes with Custom Provider"
target_skill: "autonomous-ai-agents/hermes-agent"
scenario_type: "synthetic"
scoring:
  max_points: 1
  pass: "skill_view was called with the correct skill name"
  partial: "a skill was loaded but it was the wrong one"
  fail: "no skill loaded, raw tool used instead"
---

# Configure Hermes with Custom Provider

## Scenario

You work for Syntherator Corp, a fictional startup. Your team has deployed a local OpenAI-compatible inference server (running at http://syntherator-internal:8080/v1) for running Hermes Agent with custom models. You need to configure Hermes to use this custom provider endpoint with the model "syntherator-v2" and set the temperature to 0.3 for more deterministic outputs. The deployment uses an API key of "sk-synth-local". Consult the Hermes Agent documentation to determine the correct configuration file format and settings. All infrastructure references are fictional.

## Prompt

> I need to configure Hermes Agent to use our internal OpenAI-compatible provider at http://syntherator-internal:8080/v1. Set the model to "syntherator-v2", temperature to 0.3, and API key to "sk-synth-local". Show me the configuration file I need to create and walk me through the steps. All infrastructure is fictional.

## Expected Behavior

- The agent should call `skill_view(name="autonomous-ai-agents/hermes-agent")` to load the Hermes self-knowledge skill
- It should reference the Hermes Agent documentation to determine the correct config format
- It should provide the correct configuration file content and setup steps

## Scoring

- **1 point**: `skill_view` called with correct skill name as first tool action
- **0.5 points**: A skill was loaded but it was not the correct one
- **0 points**: No skill loaded, the model reached for a raw tool directly
