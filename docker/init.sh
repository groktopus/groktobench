#!/bin/sh
# Groktobench — init script
# Runs at container start. The .env file (with API keys) is mounted
# from the host by docker-compose — init.sh just writes the model config.
set -e

echo "[groktobench] Configuring Hermes for model: ${GROKTOBENCH_MODEL:-deepseek-v4-flash}"

MODEL="${GROKTOBENCH_MODEL:-deepseek-v4-flash}"
BASE_URL="${GROKTOBENCH_BASE_URL:-https://api.deepseek.com/v1}"

cat > /opt/data/config.yaml << YAMLEOF
model:
  provider: deepseek
  default: "${MODEL}"
  model: "${MODEL}"
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

echo "[groktobench] Ready for probes."
tail -f /dev/null
