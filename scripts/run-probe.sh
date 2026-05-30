#!/bin/sh
# Groktobench — Run a single probe against Docker Hermes
#
# Usage: ./run-probe.sh <container-name> <probe-file> [output-dir]
#
# Runs the probe prompt through hermes -z inside a Docker container,
# then exports the session for scoring.
#
# Docker host abstraction:
#   By default, uses the local `docker` CLI.
#   Set GROKTOBENCH_DOCKER to a command prefix for remote Docker access.
#   Examples:
#     export GROKTOBENCH_DOCKER="docker"                          # local (default)
#     export GROKTOBENCH_DOCKER="ssh user@buildbox docker"         # remote via SSH
#     export GROKTOBENCH_DOCKER="DOCKER_HOST=tcp://host:2376 docker"  # remote TCP
#     export GROKTOBENCH_DOCKER="podman"                           # alternative runtime
#
# Requires: docker (or configured equivalent), hermes (for session export)

set -u

CONTAINER="${1:?Usage: run-probe.sh <container> <probe-file> [output-dir]}"
PROBE_FILE="${2:?Usage: run-probe.sh <container> <probe-file> [output-dir]}"
OUTPUT_DIR="${3:-/tmp/groktobench}"

# Docker command — configurable for remote hosts
DOCKER_CMD="${GROKTOBENCH_DOCKER:-docker}"

mkdir -p "$OUTPUT_DIR"

# Extract probe ID from filename (for output file naming) and prompt from the markdown
PROBE_NAME=$(basename "$PROBE_FILE" .md)
PROMPT=$(grep -A100 '^## Prompt' "$PROBE_FILE" | tail -n +3 | sed -n '1,/^## /p' | head -n -1 | sed 's/^> //')

if [ -z "$PROMPT" ]; then
    echo "ERROR: Could not extract prompt from $PROBE_FILE"
    exit 1
fi

echo "[groktobench] Running probe $PROBE_NAME..."

# Run the probe via hermes -z inside the container
$DOCKER_CMD exec "$CONTAINER" hermes -z "$PROMPT" --yolo > "$OUTPUT_DIR/${PROBE_NAME}_stdout.txt" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[groktobench] WARNING: hermes -z exited with code $EXIT_CODE"
fi

# Find the most recent session and export it
# The session list shows most recent first
SESSION_ID=$($DOCKER_CMD exec "$CONTAINER" hermes sessions list 2>/dev/null | \
    tail -n +3 | head -1 | awk '{print $NF}')

if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "—" ]; then
    # Export to a temp file inside the container, then copy it out
    $DOCKER_CMD exec "$CONTAINER" hermes sessions export --session-id "$SESSION_ID" \
        "/tmp/${PROBE_NAME}_session.jsonl" 2>/dev/null
    $DOCKER_CMD cp "${CONTAINER}:/tmp/${PROBE_NAME}_session.jsonl" \
        "$OUTPUT_DIR/${PROBE_NAME}_session.jsonl" 2>/dev/null
    $DOCKER_CMD exec "$CONTAINER" rm -f "/tmp/${PROBE_NAME}_session.jsonl" 2>/dev/null
    echo "[groktobench] Session $SESSION_ID exported"
else
    echo "[groktobench] WARNING: No session found to export"
fi

echo "[groktobench] Probe $PROBE_NAME completed"
echo "Output: $OUTPUT_DIR/${PROBE_NAME}_session.jsonl"
