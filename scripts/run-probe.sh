#!/bin/sh
# Groktobench — Run a single probe against Docker Hermes
#
# Usage: ./run-probe.sh <container-name> <probe-file> [output-dir]
#
# Runs the probe prompt through hermes -z inside the Docker container,
# then exports the session for scoring.
#
# Requires: docker, hermes (for session export)
# The container must have been started with docker-compose.

set -u

CONTAINER="${1:?Usage: run-probe.sh <container> <probe-file> [output-dir]}"
PROBE_FILE="${2:?Usage: run-probe.sh <container> <probe-file> [output-dir]}"
OUTPUT_DIR="${3:-/tmp/groktobench}"

mkdir -p "$OUTPUT_DIR"

# Extract the probe ID and prompt from the markdown file
PROBE_ID=$(grep -E '^id: ' "$PROBE_FILE" | sed 's/^id: "//;s/"$//' || echo "unknown")
PROMPT=$(grep -A100 '^## Prompt' "$PROBE_FILE" | tail -n +3 | sed -n '1,/^## /p' | head -n -1 | sed 's/^> //')

if [ -z "$PROMPT" ]; then
    echo "ERROR: Could not extract prompt from $PROBE_FILE"
    exit 1
fi

echo "[groktobench] Running probe $PROBE_ID..."

# Run the probe via docker exec hermes -z
docker exec "$CONTAINER" hermes -z "$PROMPT" > "$OUTPUT_DIR/${PROBE_ID}_stdout.txt" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[groktobench] WARNING: hermes -z exited with code $EXIT_CODE"
fi

# Find the most recent session and export it
# The session list shows most recent first
SESSION_ID=$(docker exec "$CONTAINER" hermes sessions list 2>/dev/null | \
    grep -v "^Title\|^──\|^$" | head -1 | awk '{print $NF}')

if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "—" ]; then
    docker exec "$CONTAINER" hermes sessions export --session-id "$SESSION_ID" \
        "$OUTPUT_DIR/${PROBE_ID}_session.jsonl" 2>/dev/null
    echo "[groktobench] Session $SESSION_ID exported"
else
    echo "[groktobench] WARNING: No session found to export"
fi

echo "[groktobench] Probe $PRINTF_COMPLETED"
echo "Output: $OUTPUT_DIR/${PROBE_ID}_session.jsonl"
