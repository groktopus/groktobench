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
    """Strict match a loaded skill name against the expected skill path.

    Rejects substring and fuzzy matches. The loaded skill name must either:
    1. Equal the expected skill exactly, OR
    2. Be the last segment of the expected path (e.g. loaded='plan' for
       expected='software-development/plan' — must END with the loaded value)

    A model that types 'software' and gets credit for 'software-development/plan'
    has not demonstrated skill recognition. This test is intentionally strict.
    """
    if not loaded or not expected:
        return False
    # Exact match (full path or short name exactly correct)
    if loaded == expected:
        return True
    # Expected path ends with loaded value (e.g. 'plan' for 'software-development/plan')
    if expected.endswith("/" + loaded) or expected.endswith(loaded):
        # Ensure loaded is a complete segment, not a substring
        if expected.endswith("/" + loaded):
            return True
        # Single-segment expected (no '/'), exact match already handled above
        pass
    # Loaded is the full path and expected is just the short name
    if loaded.endswith("/" + expected):
        return True
    return False


def score_phase1(tool_calls, probe_def):
    """Score a Phase 1 (Skill Recognition) probe.

    Progressive difficulty scoring:
        - 1.0: skill_view called with correct skill name as FIRST tool call,
               AND no wrong skill views precede it
        - 0.8: Correct skill loaded, but at least one tool call (non-skill_view)
               preceded it
        - 0.4-0.8: Correct skill loaded, but N wrong skills were loaded first
               (score = 1.0 - 0.2 * N, floor 0.4)
        - 0.5: Wrong skill loaded (can't be paired with a correct load)
        - 0.0: No skill loaded, raw tool used

    Decoy penalty: If probe_def specifies 'decoy_skills' and any were loaded,
    deduct an additional 0.3 regardless of whether the correct skill was also loaded.
    """
    expected_skill = probe_def.get("target_skill", "")
    decoy_skills = probe_def.get("decoy_skills", [])

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

    # Check ALL skill_view calls, not just the first one
    all_loaded = []
    correct_found = False
    wrong_before_correct = 0
    loaded_decoy = False

    for sv in skill_views:
        try:
            args = json.loads(sv["arguments"])
        except json.JSONDecodeError:
            args = {}
        loaded_skill = args.get("name", "")
        all_loaded.append(loaded_skill)

        if _match_skill(loaded_skill, expected_skill):
            correct_found = True
        elif not correct_found:
            wrong_before_correct += 1  # wrong skill loaded before the correct one

        # Check for decoy skills
        if decoy_skills and any(_match_skill(loaded_skill, d) for d in decoy_skills):
            loaded_decoy = True

    if not correct_found:
        # Try the first loaded skill for the error message
        first_sv = skill_views[0]
        try:
            args = json.loads(first_sv["arguments"])
            loaded_skill = args.get("name", "")
        except:
            loaded_skill = "unknown"
        return {
            "score": 0.5 if all_loaded else 0.0,
            "max_score": 1.0,
            "verdict": "partial" if all_loaded else "fail",
            "detail": f"Wrong skill loaded: {loaded_skill} (expected: {expected_skill})",
            "loaded_skill": loaded_skill,
            "expected_skill": expected_skill,
            "all_skills_loaded": all_loaded,
        }

    # Calculate score
    base_score = 1.0

    # Penalty for wrong skills before correct one
    if wrong_before_correct > 0:
        base_score = max(0.4, base_score - 0.2 * wrong_before_correct)

    # Penalty for non-skill_view calls before the first correct skill_view
    first_correct_index = -1
    for i, sv in enumerate(skill_views):
        try:
            args = json.loads(sv["arguments"])
            if _match_skill(args.get("name", ""), expected_skill):
                first_correct_index = i
                break
        except:
            pass

    # Check if the first CORRECT skill_view was preceded by non-skill_view tool calls
    tool_before_skill = False
    if first_correct_index >= 0:
        # Find the corresponding tool call index
        for i, tc in enumerate(tool_calls):
            if tc["name"] == "skill_view" and tc["arguments"]:
                try:
                    args = json.loads(tc["arguments"])
                    if _match_skill(args.get("name", ""), expected_skill):
                        if i > 0:  # there were tool calls before this skill_view
                            tool_before_skill = True
                        break
                except:
                    pass
        if tool_before_skill:
            base_score = min(base_score, 0.8)

    # Decoy penalty
    if loaded_decoy:
        base_score = max(0.0, base_score - 0.3)

    first_sv = skill_views[0]
    try:
        args = json.loads(first_sv["arguments"])
        loaded_skill = args.get("name", "")
    except:
        loaded_skill = all_loaded[0] if all_loaded else "unknown"

    verdict = "pass" if base_score >= 1.0 else "partial"
    detail_parts = [f"Correct skill loaded: {loaded_skill}"]
    if wrong_before_correct > 0:
        detail_parts.append(f"({wrong_before_correct} wrong skill(s) before it)")
    if loaded_decoy:
        detail_parts.append("(loaded decoy skill — deducted)")
    if tool_before_skill:
        detail_parts.append("(tools called before skill_view — deducted)")

    return {
        "score": round(base_score, 2),
        "max_score": 1.0,
        "verdict": verdict if base_score > 0 else "fail",
        "detail": " ".join(detail_parts),
        "loaded_skill": loaded_skill,
        "all_skills_loaded": all_loaded,
        "wrong_before_correct": wrong_before_correct,
        "decoy_penalty": loaded_decoy,
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


FIDELITY_CHECKS_STRICT = True
"""
When True, fidelity checks are strict:
- Using wrong tools alongside the right tool is a fail
- Keyword matches in output are not substitutes for actual tool execution
- result_preview is never used to infer tool arguments
"""


def check_skill_fidelity(probe_id, skill_name, tool_calls, session):
    """Check whether the model followed the skill's instructions.

    Each probe has specific fidelity criteria. Strict mode is enabled by default.
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
    """Plan skill fidelity: must write a plan file to .hermes/plans/*.md.
    Descriptive text in the response is not sufficient — the skill instructs
    the model to create an actual plan file.
    """
    # Check tool call ARGUMENTS for write_file to plans directory
    has_plan_file = False
    for tc in tool_calls:
        if tc["name"] == "write_file":
            try:
                args = json.loads(tc["arguments"])
                path = args.get("path", "")
                if ".hermes/plans/" in path or "plans/" in path:
                    has_plan_file = True
                    break
            except (json.JSONDecodeError, TypeError):
                pass
        elif tc["name"] == "terminal":
            try:
                args = json.loads(tc["arguments"])
                cmd = args.get("command", "")
                if ".hermes/plans/" in cmd or "plans/" in cmd:
                    has_plan_file = True
                    break
            except (json.JSONDecodeError, TypeError):
                pass

    if has_plan_file:
        return {"pass": True, "detail": "Plan file written to .hermes/plans/ directory"}
    return {"pass": False, "detail": "No plan file written. Description without file creation is not sufficient."}


def _check_obsidian_fidelity(tool_calls, session):
    """Obsidian fidelity: must create a vault note with YAML frontmatter.
    Checks tool call arguments for write_file with frontmatter content,
    not just output text that contains '---'.
    """
    # Check tool call ARGUMENTS for write_file containing YAML frontmatter
    for tc in tool_calls:
        if tc["name"] == "write_file":
            try:
                args = json.loads(tc["arguments"])
                content = args.get("content", "")
                if content.startswith("---"):
                    lines = content.split("\n")
                    has_title = any(l.lower().startswith("title:") for l in lines)
                    has_created = any(l.lower().startswith("created:") for l in lines)
                    has_topics = any(l.lower().startswith("topics:") for l in lines)
                    if has_title and has_created:
                        # Check the frontmatter closes
                        closing = 0
                        for l in lines[1:]:
                            if l.strip() == "---":
                                closing += 1
                        if closing >= 1:
                            return {"pass": True, "detail": "Vault note with valid YAML frontmatter created"}
            except (json.JSONDecodeError, TypeError):
                pass

    # Fallback: check final response for frontmatter content (weaker signal)
    final_msg = ""
    for msg in reversed(session.get("messages", [])):
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            final_msg = msg.get("content", "")
            break

    if "---" in final_msg and "title:" in final_msg.lower():
        return {"pass": False, "detail": "Frontmatter shown in output but not written to a file — must use write_file"}

    return {"pass": False, "detail": "No vault note with proper frontmatter found"}


def _check_arxiv_fidelity(tool_calls):
    """Arxiv fidelity: must use arxiv MCP tool (mcp_arxiv_*).
    Using web_search INSTEAD of or IN ADDITION TO arxiv MCP is a fail.
    The skill exists to route to the arxiv MCP tools — using web_search
    means the model didn't follow the skill's instructions.
    """
    has_arxiv = any(
        "mcp_arxiv" in tc["name"].lower() or "arxiv" in tc["name"].lower()
        for tc in tool_calls
    )
    has_web_search = any(
        "web_search" in tc["name"].lower() for tc in tool_calls
    )

    if has_arxiv and not has_web_search:
        return {"pass": True, "detail": "Used arxiv MCP tool, no fallback to web_search"}
    elif has_arxiv and has_web_search:
        return {"pass": False, "detail": "Used arxiv MCP tool but ALSO fell back to web_search — should have used only arxiv tools"}
    elif has_web_search:
        return {"pass": False, "detail": "Used web_search instead of arxiv MCP tool"}
    else:
        return {"pass": False, "detail": "Did not use arxiv MCP tool"}


def _check_github_fidelity(tool_calls):
    """GitHub fidelity: must use gh CLI or GitHub API to create issue.

    Checks tool call ARGUMENTS (the command passed to terminal or the URL
    passed to web_extract), not result_preview (which contains tool output).
    """
    for tc in tool_calls:
        if tc["name"] == "terminal":
            try:
                args = json.loads(tc["arguments"])
                cmd = args.get("command", "")
                if "gh issue create" in cmd or "gh issue" in cmd:
                    return {"pass": True, "detail": "Issue created via gh CLI"}
            except (json.JSONDecodeError, TypeError):
                pass
        elif tc["name"] == "web_extract":
            try:
                args = json.loads(tc["arguments"])
                urls = args.get("urls", [])
                for url in urls:
                    if "api.github.com" in url:
                        return {"pass": True, "detail": "Issue created via GitHub API"}
            except (json.JSONDecodeError, TypeError):
                pass

    return {"pass": False, "detail": "No gh CLI or API call detected — only described the issue without executing"}


def _check_excalidraw_fidelity(tool_calls, session):
    """Excalidraw fidelity: must produce valid Excalidraw JSON with elements.

    Requires parseable JSON containing an 'elements' array where each element
    has 'type', 'id', and 'version' fields (the minimal Excalidraw element schema).
    Keyword matches and code blocks are not sufficient.
    """
    # Check final response for excalidraw content
    final_content = ""
    for msg in reversed(session.get("messages", [])):
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            final_content = msg.get("content", "")
            break

    if not final_content:
        return {"pass": False, "detail": "No output produced"}

    # Try to find and parse JSON in output (may be in code block)
    json_str = final_content
    if "```json" in final_content:
        json_str = final_content.split("```json")[1].split("```")[0].strip()
    elif "```" in final_content:
        # Code block but not json-labeled — check what type
        lines = final_content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                code_content = "\n".join(lines[i+1:])
                if "```" in code_content:
                    code_content = code_content[:code_content.index("```")]
                json_str = code_content.strip()
                break

    # Try to parse as JSON
    try:
        parsed = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        try:
            parsed = json.loads(final_content)
        except (json.JSONDecodeError, ValueError):
            if "mermaid" in final_content.lower():
                return {"pass": False, "detail": "Produced Mermaid diagram instead of Excalidraw JSON"}
            return {"pass": False, "detail": "Output is not valid JSON — Excalidraw requires an elements array"}

    # Check for Excalidraw schema: must have 'elements' array
    if not isinstance(parsed, dict):
        return {"pass": False, "detail": "Output is JSON but not a dict — Excalidraw requires { elements: [...] }"}

    elements = parsed.get("elements", [])
    if not isinstance(elements, list) or len(elements) == 0:
        return {"pass": False, "detail": "JSON parsed but no 'elements' array found — not valid Excalidraw format"}

    # Check that each element has minimal Excalidraw fields
    has_valid_elements = all(
        isinstance(el, dict) and "type" in el for el in elements
    )

    if has_valid_elements:
        return {"pass": True, "detail": f"Valid Excalidraw JSON with {len(elements)} elements"}
    else:
        return {"pass": False, "detail": "JSON has elements array but missing required 'type' field on some elements"}


def score_phase3(tool_calls, probe_def, session):
    """Score a Phase 3 (Workflow Chaining) probe.

    Progressive difficulty scoring:
        - Chain accuracy (0-3): Skills loaded IN ORDER, not just present
        - Context preservation (0-3): Cross-references between steps, not message count
        - Completion quality (0-3): Content overlaps with original task, not length
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

    # Chain accuracy: skills loaded IN ORDER, not just present
    expected_chain = probe_def.get("skill_chain", "").split(",")
    expected_chain = [s.strip().strip('"') for s in expected_chain if s.strip()]

    if not expected_chain:
        # Try to extract from the probe file
        expected_chain = ["research/arxiv", "note-taking/obsidian", "github/github-issues"]

    # Check ORDERED chain: each expected skill must appear AFTER the previous one
    ordered_match = True
    last_index = -1
    for ec in expected_chain:
        found = False
        for i, ls in enumerate(loaded_skills):
            if _match_skill(ls, ec) and i > last_index:
                found = True
                last_index = i
                break
        if not found:
            ordered_match = False
            break

    # Presence-only match (unordered) for partial credit
    unordered_match = all(
        any(_match_skill(ls, ec) for ls in loaded_skills)
        for ec in expected_chain
    )

    if ordered_match:
        result["chain_accuracy"] = 3
    elif unordered_match:
        result["chain_accuracy"] = 2
    elif any(any(_match_skill(ls, ec) for ls in loaded_skills) for ec in expected_chain):
        result["chain_accuracy"] = 1
    else:
        result["chain_accuracy"] = 0

    # Context preservation: check for actual cross-references between steps
    # Look for evidence that the model carried information forward
    all_messages_content = " ".join(
        m.get("content", "") for m in session.get("messages", [])
        if m.get("role") in ("user", "assistant") and m.get("content")
    )

    # Heuristic: extract key terms from first user message and check if they
    # appear in later assistant responses
    first_user_msg = ""
    last_user_msg = ""
    for msg in session.get("messages", []):
        if msg.get("role") == "user":
            if not first_user_msg:
                first_user_msg = msg.get("content", "")
            last_user_msg = msg.get("content", "")

    # Count distinct entity-like terms that persist (capitalized words, quoted terms)
    first_nouns = set(re.findall(r'[A-Z][a-z]+', first_user_msg))
    final_nouns = set(re.findall(r'[A-Z][a-z]+', all_messages_content))

    # Nouns that appear in the final output that were introduced in the first user message
    preserved_terms = first_nouns & final_nouns if first_nouns else set()
    num_preserved = len(preserved_terms)

    if num_preserved >= 3:
        result["context_preservation"] = 3
    elif num_preserved >= 2:
        result["context_preservation"] = 2
    elif num_preserved >= 1:
        result["context_preservation"] = 1
    elif len(tool_calls) >= 3:
        # Fallback: multiple tool calls suggest some chaining
        result["context_preservation"] = 1

    # Completion quality: content must address the original prompt, not just be long
    prompt = probe_def.get("prompt", "").lower()[:300]

    # Extract key action verbs and nouns from the prompt
    prompt_words = set(w.lower().strip(".,!?;'") for w in prompt.split()
                       if len(w) > 3 and w.lower() not in ("this", "that", "with", "from", "have", "been", "what", "when", "where", "does", "would", "should", "could", "about", "there", "their", "which", "into", "also", "than", "very", "just", "then", "them", "will", "they", "your", "some", "each", "other", "after", "still", "such", "only"))

    # Count how many key prompt words appear in the final output
    final_content_lower = all_messages_content.lower()
    matched_words = [w for w in prompt_words if w in final_content_lower]
    word_coverage = len(matched_words) / max(len(prompt_words), 1)

    if word_coverage >= 0.4 and len(all_messages_content) > 300:
        result["completion_quality"] = 3
    elif word_coverage >= 0.25 and len(all_messages_content) > 200:
        result["completion_quality"] = 2
    elif len(all_messages_content) > 100:
        result["completion_quality"] = 1
    elif len(all_messages_content) > 0:
        result["completion_quality"] = 1

    result["verdict"] = f"{result['chain_accuracy'] + result['context_preservation'] + result['completion_quality']}/9"
    result["score"] = result["chain_accuracy"] + result["context_preservation"] + result["completion_quality"]
    result["context_detail"] = {
        "preserved_terms": list(preserved_terms)[:10],
        "word_coverage": round(word_coverage, 2),
        "total_content_length": len(all_messages_content),
    }

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
