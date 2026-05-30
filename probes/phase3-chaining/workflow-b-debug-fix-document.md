---
id: "P3-B"
phase: 3
title: "Debug → Fix → Document: Markov Chain Empty Output Bug"
skill_chain: ["software-development/systematic-debugging", "software-development/test-driven-development", "software-development/plan"]
scoring:
  max_points: 9
  criteria:
    chain_accuracy: "skills loaded and used in the correct sequence (0-3)"
    context_preservation: "information from step N correctly informs step N+1 (0-3)"
    completion_quality: "final output addresses the original goal (0-3)"
---

# Debug → Fix → Document: Markov Chain Empty Output Bug

## Workflow

The model diagnoses a bug in Syntherator's Markov chain text generator (produces empty output when input has <5 unique words), applies test-driven development to write and verify a fix, then produces a prevention plan — carrying the root-cause analysis forward to inform the test cases and the prevention strategy at each step.

## Skill Chain

1. **software-development/systematic-debugging** — Root-cause the bug: Syntherator's `MarkovChainGenerator.generate()` returns an empty string when the input corpus contains fewer than 5 unique tokens. Hypothesize why (e.g., chain-building threshold too high, vocabulary size gate, insufficient state transitions) and verify with a reproducible test case.
2. **software-development/test-driven-development** — Using the root cause identified in step 1, write a failing test first that reproduces the empty-output bug on a small corpus (<5 unique words), then implement the fix (e.g., lowering the threshold, falling back to unigram sampling, or padding the state table), and confirm the test passes.
3. **software-development/plan** — Write a prevention plan that addresses this class of bug going forward. The plan must reference the root cause from step 1 and the fix from step 2, and propose preventive measures such as input validation, automated edge-case regression tests, and a minimum-vocabulary check in the public API.

## Prompt

> Syntherator's Markov chain generator has a bug: `MarkovChainGenerator.generate(corpus)` returns an empty string whenever the input text contains fewer than 5 unique words. This is a production issue because user-submitted prompts are sometimes very short. Your task has three parts. First, use the systematic debugging skill to investigate the root cause. Examine the likely algorithm: the generator probably builds a prefix→suffix mapping table and walks it to produce output. If there's a hardcoded minimum vocabulary size for building chains, that's a candidate. Another possibility: the chain-building logic requires N unique words to seed N-gram states, and below 5 the state table is empty. Form a hypothesis, describe how you would verify it (code review, adding debug logging, or writing a minimal reproduction), and state the root cause clearly. Second, use the test-driven development skill to write a fix. Begin by writing a failing unit test that constructs a MarkovChainGenerator, calls generate("hello world how are you") with exactly 5 unique words, asserts non-empty output — this should reproduce the bug with <5 unique words (e.g., "hello world hello world"). Then implement the fix — options include lowering the minimum vocabulary threshold to 2, using unigram fallback for small corpora, or padding the state table. Run the test to confirm it passes. Third, use the planning skill to write a concise but thorough prevention plan titled "Preventing Edge-Case Failures in MarkovChainGenerator". The plan should: (a) reference the root cause from step 1 and the fix from step 2 by name, (b) propose 3 preventive measures (input validation at the public API boundary, an edge-case regression test suite maintained alongside the generator, and a minimum-vocabulary check with a clear error message), and (c) suggest a code review checklist item for similar threshold-based algorithms across the Syntherator codebase. Each step must flow from the previous: the TDD fix must address the exact root cause found in step 1, and the prevention plan must reference both.

## Expected Behavior

- Step 1 produces a clear root-cause statement (e.g., "the chain builder discards any corpus with <5 unique tokens due to a guard in `_build_chain()` that returns early when `len(unique_tokens) < MIN_VOCAB_SIZE` where `MIN_VOCAB_SIZE = 5`") and includes a minimal reproduction.
- Step 2 writes a failing test for a corpus with ≤4 unique words, then implements a fix that makes it pass. The test and fix are coherent with the root cause from step 1 (e.g., if step 1 identified a threshold, step 2 lowers or removes it).
- Step 3 produces a prevention plan titled "Preventing Edge-Case Failures in MarkovChainGenerator" that explicitly references the root cause from step 1 and the fix from step 2, and proposes at least 3 concrete preventive measures with actionable details.
- Context is preserved: the model does not re-debug or re-discover the root cause when writing steps 2 and 3.

## Scoring

- **Chain accuracy (0-3)**: Were the skills loaded and used in the correct sequence (systematic-debugging → test-driven-development → plan)?
- **Context preservation (0-3)**: Did the root-cause diagnosis from step 1 directly inform the TDD fix in step 2? Did steps 1 and 2 inform the prevention plan in step 3?
- **Completion quality (0-3)**: Is the final prevention plan coherent, actionable, and clearly connected to the specific bug and fix documented in the previous steps?
