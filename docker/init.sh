#!/bin/sh
# Groktobench — init script
# Runs at container start. The .env file (with API keys) is mounted
# from the host by docker-compose — init.sh just writes the model config
# and trims the skill set to only what the probes need.
set -e

echo "[groktobench] Configuring Hermes for model: ${GROKTOBENCH_MODEL:-deepseek-v4-flash}"

MODEL="${GROKTOBENCH_MODEL:-deepseek-v4-flash}"
BASE_URL="${GROKTOBENCH_BASE_URL:-https://api.deepseek.com/v1}"

# Write config.yaml
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

echo "[groktobench] Skills available: $(ls /opt/data/skills/ 2>/dev/null | wc -l)"
tail -f /dev/null
