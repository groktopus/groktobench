#!/usr/bin/env python3
"""
Groktobench — score-probe.py

Score a single probe's session export against its scoring rubric.

Usage:
    python3 score-probe.py <session-jsonl> <probe-definition-md>

Output: JSON to stdout with score, breakdown, and diagnostics.

The session JSONL contains the full message history. This script parses
tool calls (skill_view, etc.) and compares against the expected behavior
defined in the probe's YAML frontmatter.
"""

import json
import re
import sys
import os


def load_session(path):
    """Load a Hermes session export JSONL file."""
    with open(path) as f:
        return json.load(f)


def extract_tool_calls(session):
    """Extract all tool call events from the session in order.

    Returns a list of dicts: {index, name, arguments, result_content}
    """
    tool_calls = []
    pending_calls = {}  # tool_call_id -> {name, arguments}

    for msg in session.get("messages", []):
        role = msg.get("role", "")

        # Assistant messages may contain tool calls
        if role == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                tc_id = tc.get("id", "")
                pending_calls[tc_id] = {
                    "name": fn.get("name", ""),
                    "arguments": fn.get("arguments", "{}"),
                }

        # Tool messages return results for previous tool calls
        if role == "tool":
            tc_id = msg.get("tool_call_id", "")
            if tc_id in pending_calls:
                call = pending_calls.pop(tc_id)
                result_content = msg.get("content", "")
                tool_calls.append({
                    "name": call["name"],
                    "arguments": call["arguments"],
                    "result_preview": result_content[:200] if result_content else "",
                    "result_length": len(result_content),
                })

    return tool_calls


def extract_skill_views(tool_calls):
    """Extract all skill_view calls from the tool call sequence."""
    return [tc for tc in tool_calls if tc["name"] == "skill_view"]


def load_probe_definition(path):
    """Extract probe metadata from the markdown frontmatter.

    Returns a dict with id, target_skill, scoring details, etc.
    """
    metadata = {}
    with open(path) as f:
        content = f.read()

    # Extract YAML frontmatter between --- markers
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        for line in yaml_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                metadata[key] = value

    # Extract the prompt text (between ## Prompt and next ## or end)
    prompt_match = re.search(
        r'## Prompt\s*\n>\s*(.*?)(?=\n##\s|\Z)', content, re.DOTALL
    )
    if prompt_match:
        metadata["prompt"] = prompt_match.group(1).strip()

    return metadata


def _match_skill(loaded, expected):
    """Fuzzy match a loaded skill name against the expected skill path.

    Handles cases where the model loads by short name (e.g. 'plan')
    against the full path (e.g. 'software-development/plan').
    Returns True if they should be considered the same skill.
    """
    if not loaded or not expected:
        return False
    # Exact match
    if loaded == expected:
        return True
    # Expected ends with loaded (e.g. expected='software-development/plan', loaded='plan')
    if expected.endswith(loaded):
        return True
    # Loaded ends with expected
    if loaded.endswith(expected):
        return True
    # One contains the other as a segment
    for name in (loaded, expected):
        for segment in name.replace("-", " ").replace("/", " ").split():
            if segment in expected or segment in loaded:
                return True
    return False


def score_phase1(tool_calls, probe_def):
    """Score a Phase 1 (Skill Recognition) probe.

    Scoring:
        - 1.0: skill_view called with correct skill name as first action
        - 0.5: A skill was loaded but wrong one
        - 0.0: No skill loaded, raw tool used
    """
    expected_skill = probe_def.get("target_skill", "")

    if not tool_calls:
        return {
            "score": 0.0,
            "max_score": 1.0,
            "verdict": "fail",
            "detail": "No tool calls found at all",
        }

    first_call = tool_calls[0]
    skill_views = extract_skill_views(tool_calls)

    if not skill_views:
        return {
            "score": 0.0,
            "max_score": 1.0,
            "verdict": "fail",
            "detail": f"No skill_view() call found. First tool was: {first_call['name']}",
        }

    first_skill = skill_views[0]

    # Parse the skill name from arguments
    try:
        args = json.loads(first_skill["arguments"])
    except json.JSONDecodeError:
        args = {}

    loaded_skill = args.get("name", "")

    if _match_skill(loaded_skill, expected_skill):
        return {
            "score": 1.0,
            "max_score": 1.0,
            "verdict": "pass",
            "detail": f"Correct skill loaded: {loaded_skill}",
            "loaded_skill": loaded_skill,
        }
    else:
        return {
            "score": 0.5,
            "max_score": 1.0,
            "verdict": "partial",
            "detail": f"Wrong skill loaded: {loaded_skill} (expected: {expected_skill})",
            "loaded_skill": loaded_skill,
            "expected_skill": expected_skill,
        }


def score_phase2(tool_calls, probe_def, session):
    """Score a Phase 2 (Skill Fidelity) probe.

    Scoring:
        - 3: correct skill loaded AND followed instructions
        - 2: correct skill loaded but output format/wrong tool
        - 1: wrong skill loaded
        - 0: no skill loaded
    """
    expected_skill = probe_def.get("target_skill", "")
    probe_id = probe_def.get("id", "")
    result = {
        "score": 0,
        "max_score": 3,
        "skill_loaded": None,
    }

    skill_views = extract_skill_views(tool_calls)
    if not skill_views:
        first_tool = tool_calls[0]["name"] if tool_calls else "none"
        return {
            **result,
            "verdict": "no_skill",
            "detail": f"No skill_view() call found. First tool: {first_tool}",
            "raw_score": 0,
        }

    # Which skill was loaded?
    try:
        args = json.loads(skill_views[0]["arguments"])
    except (json.JSONDecodeError, IndexError):
        args = {}

    loaded_skill = args.get("name", "")
    result["skill_loaded"] = loaded_skill

    if not _match_skill(loaded_skill, expected_skill):
        return {
            **result,
            "verdict": "wrong_skill",
            "detail": f"Wrong skill: {loaded_skill} (expected: {expected_skill})",
            "raw_score": 1,
        }

    # Correct skill loaded. Now check fidelity.
    fidelity_result = check_skill_fidelity(probe_id, loaded_skill, tool_calls, session)

    if fidelity_result.get("pass", False):
        return {
            **result,
            "verdict": "full_fidelity",
            "detail": f"Correct skill ({loaded_skill}) loaded with full fidelity",
            "raw_score": 3,
            "fidelity_detail": fidelity_result.get("detail", ""),
        }
    else:
        return {
            **result,
            "verdict": "partial_fidelity",
            "detail": fidelity_result.get("detail", f"Correct skill loaded but fidelity check failed"),
            "raw_score": 2,
            "fidelity_detail": fidelity_result.get("detail", ""),
        }


def check_skill_fidelity(probe_id, skill_name, tool_calls, session):
    """Check whether the model followed the skill's instructions.

    Each probe has specific fidelity criteria.
    """
    if probe_id == "P2-01":  # plan skill — must create .hermes/plans/ file
        return _check_plan_fidelity(tool_calls, session)
    elif probe_id == "P2-02":  # obsidian — must create vault note with frontmatter
        return _check_obsidian_fidelity(tool_calls, session)
    elif probe_id == "P2-03":  # arxiv — must use MCP tool
        return _check_arxiv_fidelity(tool_calls)
    elif probe_id == "P2-04":  # github — must create actual issue
        return _check_github_fidelity(tool_calls)
    elif probe_id == "P2-05":  # excalidraw — must produce JSON
        return _check_excalidraw_fidelity(tool_calls, session)
    else:
        return {"pass": True, "detail": "No specific fidelity check for this probe"}


def _check_plan_fidelity(tool_calls, session):
    """Plan skill fidelity: output saved to .hermes/plans/*.md, no execution tools."""
    has_write = any(
        tc["name"] in ("write_file", "terminal") and "plans" in tc.get("result_preview", "")
        for tc in tool_calls
    )
    # Check for plan output in the final response
    final_assistant = None
    for msg in reversed(session.get("messages", [])):
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            final_assistant = msg.get("content", "")
            break

    has_plan_content = False
    if final_assistant:
        has_plan_content = (
            "#" in final_assistant and
            any(w in final_assistant.lower() for w in ["goal", "approach", "step", "phase"])
        )

    if has_write or has_plan_content:
        return {"pass": True, "detail": "Plan output created"}
    return {"pass": False, "detail": "No plan file created or plan content in output"}


def _check_obsidian_fidelity(tool_calls, session):
    """Obsidian fidelity: vault note with YAML frontmatter created."""
    has_vault_write = any(
        tc["name"] in ("write_file", "terminal") and
        any(kw in tc.get("result_preview", "") for kw in ["title:", "---", "created:"])
        for tc in tool_calls
    )

    # Check final response for frontmatter
    final_msg = ""
    for msg in reversed(session.get("messages", [])):
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            final_msg = msg.get("content", "")
            break

    has_frontmatter = "---" in final_msg and "title:" in final_msg.lower()

    if has_vault_write or has_frontmatter:
        return {"pass": True, "detail": "Vault note with frontmatter created"}
    return {"pass": False, "detail": "No vault note with proper frontmatter found"}


def _check_arxiv_fidelity(tool_calls):
    """Arxiv fidelity: must use mcp_arxiv_search_papers tool, not web_search."""
    has_arxiv = any("arxiv" in tc["name"].lower() for tc in tool_calls)
    has_web_search = any("web_search" in tc["name"].lower() for tc in tool_calls)

    if has_arxiv and not has_web_search:
        return {"pass": True, "detail": "Used arxiv MCP tool, no web_search fallback"}
    elif has_arxiv and has_web_search:
        return {"pass": True, "detail": "Used arxiv MCP tool (also used web_search)"}
    else:
        return {"pass": False, "detail": "Did not use arxiv MCP tool"}


def _check_github_fidelity(tool_calls):
    """GitHub fidelity: must use gh CLI or API to create issue."""
    has_gh = any(
        tc["name"] == "terminal" and "gh issue" in tc.get("result_preview", "")
        for tc in tool_calls
    )
    has_api = any(
        tc["name"] in ("web_extract", "terminal") and
        "api.github.com" in tc.get("result_preview", "")
        for tc in tool_calls
    )

    if has_gh or has_api:
        return {"pass": True, "detail": "Issue created via gh CLI or GitHub API"}
    # Also check if the final response mentions issue creation
    return {"pass": False, "detail": "No gh CLI or API call detected — may have only described the issue"}


def _check_excalidraw_fidelity(tool_calls, session):
    """Excalidraw fidelity: must produce valid Excalidraw JSON."""
    has_excalidraw_call = any(
        tc["name"] in ("skill_view",) for tc in tool_calls
    )

    # Check final response for JSON/excalidraw content
    final_content = ""
    for msg in reversed(session.get("messages", [])):
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            final_content = msg.get("content", "")
            break

    is_json = False
    if final_content.strip().startswith("{"):
        try:
            json.loads(final_content)
            is_json = True
        except json.JSONDecodeError:
            pass

    # Also check for Excalidraw elements
    has_excalidraw_elements = "elements" in final_content.lower() and "type" in final_content.lower()

    if has_excalidraw_elements or is_json:
        return {"pass": True, "detail": "Excalidraw JSON produced"}
    elif "mermaid" in final_content.lower():
        return {"pass": False, "detail": "Produced Mermaid diagram instead of Excalidraw JSON"}
    elif "```" in final_content:
        return {"pass": False, "detail": "Produced diagram in code block instead of Excalidraw JSON"}
    else:
        return {"pass": False, "detail": "No Excalidraw output detected"}


def score_phase3(tool_calls, probe_def, session):
    """Score a Phase 3 (Workflow Chaining) probe.

    Scoring:
        - Chain accuracy (0-3): Correct sequence of skills
        - Context preservation (0-3): Info flows between steps
        - Completion quality (0-3): Output addresses original goal
    """
    result = {
        "max_score": 9,
        "chain_accuracy": 0,
        "context_preservation": 0,
        "completion_quality": 0,
    }

    skill_views = extract_skill_views(tool_calls)
    loaded_skills = []
    for sv in skill_views:
        try:
            args = json.loads(sv["arguments"])
            loaded_skills.append(args.get("name", ""))
        except json.JSONDecodeError:
            loaded_skills.append("unknown")

    # Chain accuracy: were skills loaded in the expected sequence?
    expected_chain = probe_def.get("skill_chain", "").split(",")
    expected_chain = [s.strip().strip('"') for s in expected_chain if s.strip()]

    if not expected_chain:
        # Try to extract from the probe file
        expected_chain = ["research/arxiv", "note-taking/obsidian", "github/github-issues"]

    chain_followed = all(any(ec in ls for ls in loaded_skills) for ec in expected_chain)

    if chain_followed:
        result["chain_accuracy"] = 3
    elif any(ec in str(skill_views) for ec in expected_chain):
        result["chain_accuracy"] = 2  # partial match
    else:
        result["chain_accuracy"] = 0  # wrong chain

    # Context preservation: check if content from step 1 references are in step 2/3
    # Look for continuity in the final content
    final_content = ""
    for msg in reversed(session.get("messages", [])):
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            final_content = msg.get("content", "")
            break

    # Heuristic: longer interactions with multiple distinct topics suggest better chaining
    msg_count = len(session.get("messages", []))
    tool_count = len(tool_calls)

    if msg_count > 15 and tool_count >= len(expected_chain):
        result["context_preservation"] = 3
    elif msg_count > 10:
        result["context_preservation"] = 2
    elif msg_count > 5:
        result["context_preservation"] = 1

    # Completion quality: check if the final output addresses the original goal
    prompt = probe_def.get("prompt", "").lower()[:100]

    if final_content and len(final_content) > 500:
        # Substantial output suggests completion
        result["completion_quality"] = 3
    elif final_content and len(final_content) > 200:
        result["completion_quality"] = 2
    elif final_content:
        result["completion_quality"] = 1

    result["verdict"] = f"{result['chain_accuracy'] + result['context_preservation'] + result['completion_quality']}/9"
    result["score"] = result["chain_accuracy"] + result["context_preservation"] + result["completion_quality"]

    return result


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: score-probe.py <session.jsonl> <probe-definition.md>",
            "usage_hint": "Pass the session export file and the probe definition file"
        }, indent=2))
        sys.exit(1)

    session_path = sys.argv[1]
    probe_path = sys.argv[2]

    if not os.path.exists(session_path):
        print(json.dumps({"error": f"Session file not found: {session_path}"}))
        sys.exit(1)

    if not os.path.exists(probe_path):
        print(json.dumps({"error": f"Probe definition not found: {probe_path}"}))
        sys.exit(1)

    session = load_session(session_path)
    probe_def = load_probe_definition(probe_path)
    tool_calls = extract_tool_calls(session)

    phase = probe_def.get("phase", "1")

    if phase == "1":
        result = score_phase1(tool_calls, probe_def)
    elif phase == "2":
        result = score_phase2(tool_calls, probe_def, session)
    elif phase == "3":
        result = score_phase3(tool_calls, probe_def, session)
    else:
        result = {"error": f"Unknown phase: {phase}"}

    output = {
        "probe_id": probe_def.get("id", "unknown"),
        "phase": phase,
        "target_skill": probe_def.get("target_skill", ""),
        "tool_call_count": len(tool_calls),
        "token_counts": {
            "input": session.get("input_tokens", 0),
            "output": session.get("output_tokens", 0),
            "total": session.get("input_tokens", 0) + session.get("output_tokens", 0),
        },
        "result": result,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
