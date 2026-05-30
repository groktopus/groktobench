---
id: "P2-03"
phase: 2
title: "ArXiv Research Search Fidelity"
target_skill: "research/arxiv"
fidelity_check: "Does the model use the mcp_arxiv_search_papers tool with a proper query, rather than reaching for web_search?"
scoring:
  max_points: 3
  full_fidelity: "loaded correct skill AND followed its instructions"
  partial_fidelity: "loaded correct skill but partially ignored instructions"
  loaded_wrong: "loaded a different skill"
  no_skill: "no skill loaded"
---

# ArXiv Research Search Fidelity

## Fidelity Check

Fidelity means the model loads the research/arxiv skill and calls the `mcp_arxiv_search_papers` tool with a well-formed query containing both "Markov chain text generation" and "language model distillation" concepts — rather than using a generic web search tool, an inferior search method, or describing search results without actually running the tool.

## Prompt

> Search for recent papers on Markov chain text generation and language model distillation for small footprint models.

## Expected Output

A response that includes:
1. Confirmation that `mcp_arxiv_search_papers` was invoked (tool call evidence, not just prose).
2. A query that properly combines both topics — e.g., using quoted phrases like `"Markov chain" text generation` AND `"language model distillation"` or similar.
3. Actual search results returned from the tool: paper titles, authors, arXiv IDs, and abstracts or summaries.
4. The response should NOT use `web_search`, `google`, `bing`, or any non-arXiv search tool.
5. The model should not fabricate paper metadata — results must come from the actual tool call.

## Scoring

- **3 points**: Loaded correct skill AND followed its instructions faithfully
- **2 points**: Loaded correct skill but produced output in the wrong format or missed key instructions
- **1 point**: Loaded a different skill (wrong skill for the task)
- **0 points**: No skill loaded, used raw tools or hallucinated
