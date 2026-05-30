#!/bin/sh
# Groktobench — init script
# Runs at container start. Configures Hermes with the model under test
# from environment variables, then idles for probe execution.

set -e

echo "[groktobench] Configuring Hermes for model: ${GROKTOBENCH_MODEL}"

# Write API key to .env where Hermes expects it (OPENROUTER_API_KEY)
# and set model config
echo "OPENROUTER_API_KEY=${GROKTOBENCH_API_KEY}" >> /opt/data/.env
hermes config set model.provider openrouter
hermes config set model.model "${GROKTOBENCH_MODEL}"

if [ -n "${GROKTOBENCH_BASE_URL}" ]; then
    hermes config set providers.openrouter.base_url "${GROKTOBENCH_BASE_URL}"
fi

echo "[groktobench] Hermes configured. Ready for probes."

# Stay alive — the container is probed via docker exec
tail -f /dev/null
