#!/bin/sh
# Groktobench — init script
# Runs at container start. Configures Hermes with the model under test
# from environment variables, then idles for probe execution.

set -e

echo "[groktobench] Configuring Hermes for model: ${GROKTOBENCH_MODEL}"

# 1. Write .env — Hermes detects provider from base_url and needs DEEPSEEK_API_KEY
echo "DEEPSEEK_API_KEY=${GROK...Y}" > /opt/data/.env
echo "OPENROUTER_API_KEY=${GROK...Y}" >> /opt/data/.env

# 2. Write config.yaml directly
BASE_URL="${GROKTOBENCH_BASE_URL:-https://api.deepseek.com/v1}"
cat > /opt/data/config.yaml << YAMLEOF
model:
  provider: deepseek
  default: "${GROKTOBENCH_MODEL}"
  model: "${GROKTOBENCH_MODEL}"
providers:
  deepseek:
    base_url: "${BASE_URL}"
auxiliary:
  compression: null
  vision: null
  approval: null
  memory: null
  title_generation: null
  curator: null
  goal_judge: null
memory:
  provider: null
kanban:
  enabled: false
YAMLEOF

echo "[groktobench] Hermes configured. Ready for probes."

# Stay alive — the container is probed via docker exec
tail -f /dev/null
