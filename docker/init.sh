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

# Trim skills to only what probes need — s6-overlay syncs 90+ bundled
# skills at boot, which overwhelms hermes -z mode. Keep only the skills
# that Phase 1-3 probes test.
KEEP="arxiv obsidian plan github-issues creative-ideation writing-plans spike"
for skill_dir in /opt/data/skills/*/; do
    name=$(basename "$skill_dir")
    keep=0
    for keep_skill in $KEEP; do
        case "$name" in
            *"$keep_skill"*) keep=1;;
        esac
    done
    if [ "$keep" -eq 0 ]; then
        rm -rf "$skill_dir" 2>/dev/null || true
    fi
done

echo "[groktobench] Ready for probes. Skills: $(ls /opt/data/skills/ 2>/dev/null | wc -l)"
tail -f /dev/null
