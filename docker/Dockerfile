#
# Groktobench — Clean-room Hermes Agent container
#
# Based on the official Hermes Agent Docker image. Strips custom skills,
# forces stock-only skills, and exposes oneshot mode for evaluation.
#
# Build:   docker build -t groktobench-hermes -f docker/Dockerfile .
# Run:     docker compose -f docker/docker-compose.yml up -d
# Test:    docker exec groktobench hermes -z "List your available toolsets"
#

FROM ghcr.io/nousresearch/hermes-agent:latest

# Remove any user-installed custom skills that might have been baked in
RUN rm -rf /opt/data/skills/* 2>/dev/null || true

# Copy our minimal config template and init script
COPY docker/config.yaml /opt/data/config.yaml
COPY docker/init.sh /opt/data/init.sh
RUN chmod +x /opt/data/init.sh

# Install dependencies needed for stock Hermes skills
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    chromium \
    jupyter-notebook \
    git \
    2>/dev/null \
    && rm -rf /var/lib/apt/lists/*

ENV HERMES_HOME=/opt/data
ENV HOME=/opt/data
