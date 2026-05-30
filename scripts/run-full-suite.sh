#!/bin/sh
# Groktobench — Run the full evaluation suite
#
# Usage: run-full-suite.sh <container-name>
#
# Runs all 15 probes, scores each, and generates a diagnostic report.
# The container must be running (docker compose up -d).
#
# Docker host abstraction:
#   Set GROKTOBENCH_DOCKER to a command prefix for remote Docker access.
#   Examples:
#     export GROKTOBENCH_DOCKER="docker"                          # local (default)
#     export GROKTOBENCH_DOCKER="ssh user@buildbox docker"         # remote via SSH
#     export GROKTOBENCH_DOCKER="DOCKER_HOST=tcp://host:2376 docker"  # remote TCP
# See run-probe.sh for full details.

set -u

CONTAINER="${1:?Usage: run-full-suite.sh <container-name>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="/tmp/groktobench-$(date +%Y%m%d_%H%M%S)"
SUMMARY_FILE="$OUTPUT_DIR/summary.json"

mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "  Groktobench — Full Evaluation Suite"
echo "=========================================="
echo "Container: $CONTAINER"
echo "Output:    $OUTPUT_DIR"
echo "Probes:    $REPO_ROOT/probes"
echo ""

# --- Phase 1: Skill Recognition (8 probes) ---
echo "--- Phase 1: Skill Recognition ---"
P1_SCORE=0
P1_MAX=8
for probe in "$REPO_ROOT/probes/phase1-recognition/"*.md; do
    name=$(basename "$probe" .md)
    echo "  Running $name..."
    sh "$REPO_ROOT/scripts/run-probe.sh" "$CONTAINER" "$probe" "$OUTPUT_DIR" > /dev/null 2>&1

    # Score the probe
    session_file="$OUTPUT_DIR/${name}_session.jsonl"
    if [ -f "$session_file" ]; then
        score_result=$(python3 "$REPO_ROOT/scripts/score-probe.py" "$session_file" "$probe" 2>/dev/null)
        probe_score=$(echo "$score_result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['score'])" 2>/dev/null)
        if [ -n "$probe_score" ]; then
            P1_SCORE=$(echo "$P1_SCORE + $probe_score" | bc 2>/dev/null || echo "$P1_SCORE")
            echo "    Score: $probe_score/1"
        else
            echo "    Score: ERROR"
        fi
        # Save score result
        echo "$score_result" > "$OUTPUT_DIR/${name}_score.json"
    else
        echo "    Score: NO_SESSION"
    fi
done

# --- Phase 2: Skill Fidelity (5 probes) ---
echo "--- Phase 2: Skill Fidelity ---"
P2_SCORE=0
P2_MAX=15
for probe in "$REPO_ROOT/probes/phase2-fidelity/"*.md; do
    name=$(basename "$probe" .md)
    echo "  Running $name..."
    sh "$REPO_ROOT/scripts/run-probe.sh" "$CONTAINER" "$probe" "$OUTPUT_DIR" > /dev/null 2>&1

    session_file="$OUTPUT_DIR/${name}_session.jsonl"
    if [ -f "$session_file" ]; then
        score_result=$(python3 "$REPO_ROOT/scripts/score-probe.py" "$session_file" "$probe" 2>/dev/null)
        probe_score=$(echo "$score_result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['raw_score'])" 2>/dev/null)
        if [ -n "$probe_score" ]; then
            P2_SCORE=$(echo "$P2_SCORE + $probe_score" | bc 2>/dev/null || echo "$P2_SCORE")
            echo "    Score: $probe_score/3"
        else
            echo "    Score: ERROR"
        fi
        echo "$score_result" > "$OUTPUT_DIR/${name}_score.json"
    else
        echo "    Score: NO_SESSION"
    fi
done

# --- Phase 3: Workflow Chaining (2 probes) ---
echo "--- Phase 3: Workflow Chaining ---"
P3_SCORE=0
P3_MAX=18
for probe in "$REPO_ROOT/probes/phase3-chaining/"*.md; do
    name=$(basename "$probe" .md)
    echo "  Running $name..."
    sh "$REPO_ROOT/scripts/run-probe.sh" "$CONTAINER" "$probe" "$OUTPUT_DIR" > /dev/null 2>&1

    session_file="$OUTPUT_DIR/${name}_session.jsonl"
    if [ -f "$session_file" ]; then
        score_result=$(python3 "$REPO_ROOT/scripts/score-probe.py" "$session_file" "$probe" 2>/dev/null)
        probe_score=$(echo "$score_result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['score'])" 2>/dev/null)
        if [ -n "$probe_score" ]; then
            P3_SCORE=$(echo "$P3_SCORE + $probe_score" | bc 2>/dev/null || echo "$P3_SCORE")
            echo "    Score: $probe_score/9"
        else
            echo "    Score: ERROR"
        fi
        echo "$score_result" > "$OUTPUT_DIR/${name}_score.json"
    else
        echo "    Score: NO_SESSION"
    fi
done

# --- Generate Report ---
echo ""
echo "--- Generating Report ---"

P1_PCT=$(echo "scale=1; $P1_SCORE * 100 / $P1_MAX" | bc 2>/dev/null || echo "0")
P2_PCT=$(echo "scale=1; $P2_SCORE * 100 / $P2_MAX" | bc 2>/dev/null || echo "0")
P3_PCT=$(echo "scale=1; $P3_SCORE * 100 / $P3_MAX" | bc 2>/dev/null || echo "0")

# HARP score: (P1 × 2.5) + (P2 × 2.0) + (P3 × 2.0), normalized to max 100
MAX_HARP=$(echo "8 * 2.5 + 15 * 2.0 + 18 * 2.0" | bc)
HARP_RAW=$(echo "$P1_SCORE * 2.5 + $P2_SCORE * 2.0 + $P3_SCORE * 2.0" | bc)
HARP=$(echo "scale=1; $HARP_RAW * 100 / $MAX_HARP" | bc 2>/dev/null || echo "0")

# Verdict
VERDICT=""
if [ "$(echo "$HARP >= 85" | bc)" -eq 1 ]; then
    VERDICT="Daily driver — use confidently as main agent"
elif [ "$(echo "$HARP >= 65" | bc)" -eq 1 ]; then
    VERDICT="Viable with caveats — good for structured work"
elif [ "$(echo "$HARP >= 45" | bc)" -eq 1 ]; then
    VERDICT="Experimental — expect course-correction for aux roles"
else
    VERDICT="Not suitable as main agent"
fi

# Build summary JSON
cat > "$SUMMARY_FILE" << EOF
{
    "harp_score": $HARP,
    "max_score": 100,
    "verdict": "$VERDICT",
    "phases": {
        "phase1_skill_recognition": {
            "score": $P1_SCORE,
            "max": $P1_MAX,
            "percentage": $P1_PCT,
            "probes_completed": $(ls "$OUTPUT_DIR"/P1-*_score.json 2>/dev/null | wc -l | tr -d ' ')
        },
        "phase2_skill_fidelity": {
            "score": $P2_SCORE,
            "max": $P2_MAX,
            "percentage": $P2_PCT,
            "probes_completed": $(ls "$OUTPUT_DIR"/P2-*_score.json 2>/dev/null | wc -l | tr -d ' ')
        },
        "phase3_workflow_chaining": {
            "score": $P3_SCORE,
            "max": $P3_MAX,
            "percentage": $P3_PCT,
            "probes_completed": $(ls "$OUTPUT_DIR"/P3-*_score.json 2>/dev/null | wc -l | tr -d ' ')
        }
    },
    "run_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# Print report
echo ""
echo "=========================================="
echo "  HARP Score: $HARP/100"
echo "  Verdict: $VERDICT"
echo "=========================================="
echo ""
echo "  Phase 1 — Skill Recognition:  $P1_SCORE/$P1_MAX ($P1_PCT%)"
echo "  Phase 2 — Skill Fidelity:     $P2_SCORE/$P2_MAX ($P2_PCT%)"
echo "  Phase 3 — Workflow Chaining:  $P3_SCORE/$P3_MAX ($P3_PCT%)"
echo ""
echo "Diagnostic profile:"
echo "  $(python3 -c "
import json
with open('$SUMMARY_FILE') as f:
    d = json.load(f)
p1 = d['phases']['phase1_skill_recognition']
p2 = d['phases']['phase2_skill_fidelity']
p3 = d['phases']['phase3_workflow_chaining']
bars = lambda p: '█' * int(p/10) + '░' * (10 - int(p/10))
print(f'  Skill Recognition:  {bars(p1[\"percentage\"])}  {p1[\"percentage\"]}%')
print(f'  Skill Fidelity:     {bars(p2[\"percentage\"])}  {p2[\"percentage\"]}%')
print(f'  Workflow Chaining:  {bars(p3[\"percentage\"])}  {p3[\"percentage\"]}%')
" 2>/dev/null)"
echo ""
echo "Full results: $SUMMARY_FILE"
echo "Raw data:     $OUTPUT_DIR"
