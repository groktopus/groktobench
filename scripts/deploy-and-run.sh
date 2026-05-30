#!/bin/sh
# Groktobench — Deploy and run evaluation on a remote Docker host
#
# Usage: ./deploy-and-run.sh <docker-host> <container-name>
#
# The main agent SCPs the entire Groktobench repo to a remote Docker host,
# runs the evaluation there (where Docker CLI is available), and retrieves
# the results. The main agent only needs SSH+SCP — no Docker CLI required.
#
# Prerequisites on the main agent:
#   - SSH access to the Docker host (key-based auth)
#   - SCP or rsync available
#
# Prerequisites on the Docker host:
#   - Docker CLI installed and working
#   - The same GROKTOBENCH_* env vars set (or configurable)
#   - Python 3 (for the scoring script)
#
# Examples:
#   ./deploy-and-run.sh gpuslut01 groktobench-run
#   ./deploy-and-run.sh user@buildbox.local groktobench
#   ./deploy-and-run.sh 10.0.1.50 hermes-eval
#
# Environment variables (set these before running):
#   GROKTOBENCH_API_KEY    — API key for the model under test (required)
#   GROKTOBENCH_MODEL      — Model name (required)
#   GROKTOBENCH_BASE_URL   — API base URL (optional)
#   GROKTOBENCH_REMOTE_DIR — Remote working directory (default: /tmp/groktobench)

set -u

DOCKER_HOST="${1:?Usage: deploy-and-run.sh <docker-host> <container-name>}"
CONTAINER_NAME="${2:?Usage: deploy-and-run.sh <docker-host> <container-name>}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE_DIR="${GROKTOBENCH_REMOTE_DIR:-/tmp/groktobench}"
REMOTE_RESULTS_DIR="${REMOTE_DIR}/results"
LOCAL_RESULTS_DIR="/tmp/groktobench-$(date +%Y%m%d_%H%M%S)"

# Validate required env vars
if [ -z "${GROKTOBENCH_API_KEY:-}" ]; then
    echo "ERROR: GROKTOBENCH_API_KEY must be set"
    exit 1
fi
if [ -z "${GROKTOBENCH_MODEL:-}" ]; then
    echo "ERROR: GROKTOBENCH_MODEL must be set"
    exit 1
fi

echo "=========================================="
echo "  Groktobench — Remote Deploy & Run"
echo "=========================================="
echo "Docker host:    $DOCKER_HOST"
echo "Container:      $CONTAINER_NAME"
echo "Remote dir:     $REMOTE_DIR"
echo "Model:          $GROKTOBENCH_MODEL"
echo ""

# --- Step 1: Prepare deployment tarball ---
echo "[1/5] Packaging Groktobench..."
DEPLOY_ARCHIVE="/tmp/groktobench-deploy-$(date +%s).tar.gz"
tar czf "$DEPLOY_ARCHIVE" \
    -C "$REPO_ROOT" \
    --exclude=".git" \
    --exclude="*.swp" \
    --exclude=".DS_Store" \
    .

echo "      Archive: $DEPLOY_ARCHIVE ($(du -h "$DEPLOY_ARCHIVE" | cut -f1))"

# --- Step 2: Copy to remote host ---
echo "[2/5] Copying to $DOCKER_HOST..."
ssh "$DOCKER_HOST" "mkdir -p $REMOTE_DIR $REMOTE_RESULTS_DIR"
scp "$DEPLOY_ARCHIVE" "${DOCKER_HOST}:${REMOTE_DIR}/"
ssh "$DOCKER_HOST" "tar xzf ${REMOTE_DIR}/$(basename $DEPLOY_ARCHIVE) -C $REMOTE_DIR && rm ${REMOTE_DIR}/$(basename $DEPLOY_ARCHIVE)"
echo "      Deployed to $REMOTE_DIR"

# --- Step 3: Build Hermes Agent base image on remote host ---
echo "[3/5] Building Hermes Agent base image on $DOCKER_HOST..."
echo "      Cloning NousResearch/hermes-agent (if needed)..."
ssh "$DOCKER_HOST" \
    "if [ ! -d ${REMOTE_DIR}/hermes-agent ] || [ ! -f ${REMOTE_DIR}/hermes-agent/Dockerfile ]; then \
         git clone --depth 1 https://github.com/NousResearch/hermes-agent.git ${REMOTE_DIR}/hermes-agent 2>&1 | tail -1; \
     else \
         echo 'Already cloned'; \
     fi"
echo "      Building hermes-agent image (this takes a few minutes)..."
BUILD_OUTPUT=$(ssh "$DOCKER_HOST" \
    "cd ${REMOTE_DIR}/hermes-agent && docker build -t hermes-agent:latest . 2>&1")
echo "$BUILD_OUTPUT" | tail -3
echo "      Hermes Agent base image built"

# --- Step 4: Build Groktobench image on top ---
echo "[4/5] Building Groktobench image..."
ssh "$DOCKER_HOST" \
    "cd $REMOTE_DIR && \
     docker build -t groktobench-hermes -f docker/Dockerfile \
       --build-arg BASE_IMAGE=hermes-agent:latest ." 2>&1 | tail -3
echo "      Groktobench image built"

# --- Step 5: Write env file and run the evaluation ---
echo "[5/5] Running evaluation on $DOCKER_HOST..."
echo "      Container: $CONTAINER_NAME"
echo "      (this will take ~90 minutes)"
echo ""

# Write env file on the remote host (local heredoc expands vars, piped through SSH)
ssh "$DOCKER_HOST" "cat > ${REMOTE_DIR}/.env" <<EOF
GROKTOBENCH_API_KEY=${GROKTOBENCH_API_KEY}
GROKTOBENCH_MODEL=${GROKTOBENCH_MODEL}
EOF
# Append optional base URL
if [ -n "${GROKTOBENCH_BASE_URL:-}" ]; then
    ssh "$DOCKER_HOST" "echo GROKTOBENCH_BASE_URL=${GROKTOBENCH_BASE_URL} >> ${REMOTE_DIR}/.env"
fi

# Start the container
ssh "$DOCKER_HOST" \
    "cd $REMOTE_DIR && \
     docker compose -f docker/docker-compose.yml --env-file .env up -d 2>&1" | tail -3

# Wait for container to be ready
echo "      Waiting for container..."
sleep 5
ssh "$DOCKER_HOST" \
    "docker exec $CONTAINER_NAME hermes -z 'ping' > /dev/null 2>&1 && \
     echo '      Container ready' || \
     echo '      WARNING: Container may not be ready yet'"

# Run the full probe suite
echo "      Running probes..."
ssh "$DOCKER_HOST" \
    "cd $REMOTE_DIR && \
     GROKTOBENCH_DOCKER='docker' \
     sh scripts/run-full-suite.sh $CONTAINER_NAME 2>&1"

# --- Step 6: Retrieve results ---
echo "[6/5] Retrieving results..."
# Find the results directory on the remote host
ssh "$DOCKER_HOST" \
    "latest=\$(ls -dt /tmp/groktobench-* 2>/dev/null | head -1) && \
     if [ -n \"\$latest\" ]; then \
         cp -r \"\$latest\"/* $REMOTE_RESULTS_DIR/ 2>/dev/null; \
         echo 'Results staged'; \
     else \
         echo 'No results found'; \
     fi"

# SCP results back
scp -r "${DOCKER_HOST}:${REMOTE_RESULTS_DIR}/" "$LOCAL_RESULTS_DIR/" 2>/dev/null || {
    echo "WARNING: Could not retrieve results from remote"
    echo "Check $REMOTE_RESULTS_DIR on $DOCKER_HOST manually"
}

# Cleanup remote
ssh "$DOCKER_HOST" "rm -rf $REMOTE_DIR 2>/dev/null; echo 'Remote cleanup done'" 2>/dev/null

echo ""
echo "=========================================="
echo "  Evaluation Complete"
echo "=========================================="
echo "Results: $LOCAL_RESULTS_DIR"
echo ""

# Print summary if available
if [ -f "$LOCAL_RESULTS_DIR/summary.json" ]; then
    echo "HARP Score Summary:"
    python3 -c "
import json
with open('$LOCAL_RESULTS_DIR/summary.json') as f:
    d = json.load(f)
print(f'  HARP Score: {d[\"harp_score\"]}/100')
print(f'  Verdict:    {d[\"verdict\"]}')
for phase, data in d.get('phases', {}).items():
    print(f'  {phase}: {data[\"score\"]}/{data[\"max\"]} ({data[\"percentage\"]}%)')
"
fi

echo ""
echo "Raw session data: $LOCAL_RESULTS_DIR"
