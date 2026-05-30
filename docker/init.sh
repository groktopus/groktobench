#!/bin/sh
# Groktobench — init script
# Runs at container start. Configures Hermes with the model under test
# from environment variables, then idles for probe execution.

set -e

echo "[groktobench] Configuring Hermes for model: ${GROKTOBENCH_MODEL}"

# Write the provider config using env vars
hermes config set providers.openrouter.api_key "${GROKTOBENCH_API_KEY}"
hermes config set model.provider openrouter
hermes config set model.model "${GROKTOBENCH_MODEL}"

if [ -n "${GROKTOBENCH_BASE_URL}" ]; then
    hermes config set providers.openrouter.base_url "${GROKTOBENCH_BASE_URL}"
fi

echo "[groktobench] Hermes configured. Ready for probes."

# Stay alive — the container is probed via docker exec
tail -f /dev/null
