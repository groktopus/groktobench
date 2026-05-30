# Groktobench — Scoring Rubric

This document defines the detailed scoring criteria for each phase of the Hermes Agent Readiness Protocol (HARP).

## Phase 1: Skill Recognition (0-8 points)

Each probe is scored 0, 0.5, or 1 point.

### Scoring Rules

| Points | Criterion | How to determine |
|--------|-----------|-----------------|
| 1.0 | `skill_view()` called with correct skill as first action | Parse session export: first tool call is `skill_view` with `name` matching the expected skill |
| 0.5 | A skill was loaded but it was the wrong one | `skill_view` called but with a skill name that doesn't match the expected target |
| 0.0 | No skill loaded | First tool call is anything else (web_search, terminal, write_file, etc.) |

### Edge Cases

- **Model loads multiple skills**: Score 1.0 if the correct skill is in the first 3 `skill_view` calls
- **Model loads skill but never uses it**: Still scores 1.0 — recognition is about loading, not execution
- **Model describes the skill verbally instead of loading it**: Score 0.0 — `skill_view` must be called as a tool

### Probe-Specific Notes

| Probe ID | Expected Skill | Accepted Variants |
|----------|---------------|-------------------|
| P1-01 | `research/arxiv` | `arxiv` (partial match) |
| P1-02 | `note-taking/obsidian` | `obsidian` |
| P1-03 | `software-development/plan` | `plan` |
| P1-04 | `github/github-issues` | `github-issues`, `github/issues` |
| P1-05 | `creative/excalidraw` | `excalidraw` |
| P1-06 | `autonomous-ai-agents/hermes-agent` | `hermes-agent` |
| P1-07 | `data-science/jupyter-live-kernel` | `jupyter-live-kernel`, `jupyter` |
| P1-08 | `software-development/spike` | `spike` |

## Phase 2: Skill Fidelity (0-15 points)

Each probe is scored 0, 1, 2, or 3 points.

### General Scoring Rules

| Points | Criterion | Description |
|--------|-----------|-------------|
| 3 | Full fidelity | Correct skill loaded AND output follows skill's instructions exactly |
| 2 | Partial fidelity | Correct skill loaded but output format or tool usage deviates |
| 1 | Wrong skill | A different skill was loaded |
| 0 | No skill | No `skill_view` call — raw tools or hallucination |

### Probe-Specific Fidelity Checks

#### P2-01: Plan Fidelity

Full fidelity (3 pts):
- Creates a markdown file in `.hermes/plans/` directory
- Contains goal, approach, and step-by-step sections
- Does NOT execute any code (no `terminal` calls with build/run commands)

Partial fidelity (2 pts):
- Loaded plan skill but output is prose in the chat response (not saved to file)
- OR created a plan but also started implementing

#### P2-02: Obsidian Fidelity

Full fidelity (3 pts):
- Creates a note file with `.md` extension
- YAML frontmatter includes at minimum `title:` and `created:` fields
- Body contains the architecture description

Partial fidelity (2 pts):
- Created a markdown file but without proper frontmatter
- OR created file in wrong location (not vault-style directory)

#### P2-03: Arxiv Fidelity

Full fidelity (3 pts):
- Uses `mcp_arxiv_search_papers` tool
- Query is properly structured (quoted phrases, field specifiers, or Boolean operators)
- Does NOT fall back to `web_search`

Partial fidelity (2 pts):
- Uses `web_search` instead of arxiv MCP tool
- OR uses arxiv tool but with a poorly structured query (single word, no Boolean)

#### P2-04: GitHub Fidelity

Full fidelity (3 pts):
- Calls `gh issue create` via terminal, OR posts to GitHub API
- Title and body are included with proper structure
- Issue is actually created (not just described)

Partial fidelity (2 pts):
- Describes what the issue would say without creating it
- OR creates the issue but with missing fields (no body, no title)

#### P2-05: Excalidraw Fidelity

Full fidelity (3 pts):
- Produces valid Excalidraw JSON with `elements` array
- Each element has `type`, `x`, `y`, `width`, `height` fields
- Architecture diagram is recognizable from the elements

Partial fidelity (2 pts):
- Produces a Mermaid diagram or ASCII art instead of Excalidraw JSON
- OR produces JSON that doesn't match Excalidraw schema
- OR describes the diagram in prose only

## Phase 3: Workflow Chaining (0-18 points)

Each workflow is scored 0-9 points across three axes.

### Chain Accuracy (0-3 points)

| Points | Criterion |
|--------|-----------|
| 3 | All skills loaded and used in the correct sequential order |
| 2 | Skills loaded but in wrong order, or one skill skipped |
| 1 | Only 1 of 3 skills loaded |
| 0 | No skills loaded, raw tools used throughout |

How to determine: Parse all `skill_view` calls from the session export. Compare the sequence against the expected chain. Check that each skill's tools are actually used between load events.

### Context Preservation (0-3 points)

| Points | Criterion |
|--------|-----------|
| 3 | Information from step 1 (papers, findings) explicitly referenced in step 2 and step 3 outputs |
| 2 | Some context carries through but references are vague or incomplete |
| 1 | Minimal context transfer — steps appear independent |
| 0 | No context transfer — session restarts between steps |

How to determine: Read the session messages. Look for cross-references in later steps to data discovered in earlier steps. Token continuity (no reset between steps) is a baseline indicator.

### Completion Quality (0-3 points)

| Points | Criterion |
|--------|-----------|
| 3 | All deliverables produced, each in correct format, coherent output |
| 2 | All steps attempted but one or more deliverables incomplete |
| 1 | Only partial completion — some steps not attempted |
| 0 | Task abandoned or produced unrelated output |

How to determine: Check final output against each step's expected deliverable. For Workflow A: papers found? note created? issue filed? For Workflow B: root cause found? fix written? prevention plan documented?

## HARP Score Calculation

```
HARP = ((P1_score × 2.5) + (P2_score × 2.0) + (P3_score × 2.0)) / 100

Where:
  P1_score: 0-8   (weight 2.5 = max 20 points)
  P2_score: 0-15  (weight 2.0 = max 30 points)
  P3_score: 0-18  (weight 2.0 = max 36 points)

  Max raw: 20 + 30 + 36 = 86
  Normalized to 0-100: (raw_score / 86) × 100
```

Phase 1 has the highest per-point weight because skill-selection behavior is the primary evaluation axis. A model that loads the right skill will almost always score well in Phases 2 and 3 as a consequence.

## Thresholds

| HARP Score | Verdict | Action |
|-----------|---------|--------|
| 85-100 | Daily driver | Use as main agent |
| 65-84 | Viable with caveats | Use but monitor specific gaps |
| 45-64 | Experimental | Aux roles only |
| <45 | Not suitable | Do not use as Hermes agent |

### Diagnostic Patterns

- **High P1, Low P2**: Model knows which skill to load but ignores the skill's instructions. Will load the right tooling but produce wrong output.
- **Low P1, High P2**: Model doesn't naturally load skills but executes well when guided. Good candidate for structured workflows with explicit step-by-step instructions.
- **High P1+P2, Low P3**: Model handles individual tasks well but can't chain them. Fine for single-turn operations but not complex workflows.
- **All low**: Model is not suited for agentic work regardless of reasoning benchmarks.
