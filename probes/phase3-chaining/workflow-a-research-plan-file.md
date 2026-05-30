---
id: "P3-A"
phase: 3
title: "Research → Plan → File: Small LLM Tool-Calling"
skill_chain: ["research/arxiv", "note-taking/obsidian", "github/github-issues"]
scoring:
  max_points: 9
  criteria:
    chain_accuracy: "skills loaded and used in the correct sequence (0-3)"
    context_preservation: "information from step N correctly informs step N+1 (0-3)"
    completion_quality: "final output addresses the original goal (0-3)"
---

# Research → Plan → File: Small LLM Tool-Calling

## Workflow

The model researches whether small language models (under 3B parameters) can perform reliable tool calling by searching arXiv for relevant papers, synthesizes the findings into a structured Obsidian vault note, and then files a GitHub issue on the fictional "Syntherator" project recommending whether to adopt a small model for its internal text classification pipeline — carrying key research conclusions across all three steps.

## Skill Chain

1. **research/arxiv** — Search arXiv for recent papers on small LLM tool-calling (under 3B params). Retrieve at least 3-5 relevant papers with their titles, authors, and key findings.
2. **note-taking/obsidian** — Create a new Obsidian vault note titled "Small-LLM-Tool-Calling-Research" that distills the arXiv findings into structured sections (key papers, methodology patterns, reported accuracy, limitations). The research results from step 1 must be carried forward and cited.
3. **github/github-issues** — File a GitHub issue in the Syntherator/Syntherator repository titled "Evaluate small LLM (<3B params) for internal text classification" that references the research findings and makes a concrete recommendation about feasibility, trade-offs, and next steps.

## Prompt

> You are evaluating whether Syntherator — a synthetic text-generation tool — should replace its current text classification backbone with a small language model under 3 billion parameters. First, use the arxiv research skill to find recent papers on small LLM tool-calling capabilities. Search for papers that specifically evaluate models under 3B params on function-calling, tool use, or structured output tasks. Retrieve at least 3 relevant papers and note their methods and key accuracy numbers. Second, use the Obsidian note-taking skill to create a permanent research note titled "Small-LLM-Tool-Calling-Research" that organizes these findings into digestible sections: paper summaries, methodology patterns, reported tool-calling accuracy, and identified limitations. Make sure the note cites each paper by title and first author. Third, use the GitHub issues skill to file an issue on the Syntherator/Syntherator repository titled "Evaluate small LLM (<3B params) for internal text classification". The issue body should summarize the research, cite the key papers, assess the feasibility of using a sub-3B model for Syntherator's classification pipeline, and propose concrete next steps (e.g., benchmark candidates, fallback strategy if accuracy is insufficient). Each step must build on the previous one — the Obsidian note must reference the arXiv papers found, and the GitHub issue must reference the Obsidian note's conclusions.

## Expected Behavior

- Step 1 returns real or plausible arXiv paper metadata (titles, authors, publication years, abstracts) matching the query "small LLM tool-calling" or equivalent.
- Step 2 creates a well-structured markdown note whose "Key Papers" section cites the exact papers found in step 1 by title and author. The note includes sections for methodology patterns, reported accuracy, and limitations.
- Step 3 files a GitHub issue whose body references specific papers from step 1 and cites conclusions from the Obsidian note created in step 2. The issue makes a clear feasibility assessment and proposes 2-3 concrete next steps.
- Context flows without repeated queries: the model does not re-search step 1 when writing step 3; it remembers what it found.

## Scoring

- **Chain accuracy (0-3)**: Were the skills loaded and used in the correct sequence (arxiv → obsidian → github-issues)?
- **Context preservation (0-3)**: Did information discovered in step 1 correctly inform steps 2 and 3? Are paper citations consistent across all steps?
- **Completion quality (0-3)**: Is the final GitHub issue coherent, evidence-backed, and does it propose actionable next steps for Syntherator?
