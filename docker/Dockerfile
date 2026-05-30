#
# Groktobench — Clean-room Hermes Agent container
#
# Builds on top of a locally-built Hermes Agent image (from the
# NousResearch/hermes-agent repo). The base image must be built first
# from the hermes-agent repository's Dockerfile.
#
# Build:   docker build -t groktobench-hermes -f docker/Dockerfile .
# Run:     docker compose -f docker/docker-compose.yml up -d
# Test:    docker exec groktobench hermes -z "List your available toolsets"
#
# For the deploy-and-run.sh workflow, the base image is built
# automatically on the Docker host as the first step.
#

ARG BASE_IMAGE=hermes-agent:latest
FROM $BASE_IMAGE

# Remove any user-installed custom skills that might have been baked in
RUN rm -rf /opt/data/skills/* 2>/dev/null || true

# Copy our minimal config template and init script
COPY docker/config.yaml /opt/data/config.yaml
COPY docker/init.sh /opt/hermes/groktobench-init.sh
RUN chmod +x /opt/hermes/groktobench-init.sh

# Install dependencies needed for stock Hermes skills
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    chromium \
    jupyter-notebook \
    git \
    2>/dev/null \
    && rm -rf /var/lib/apt/lists/*

ENV HERMES_HOME=/opt/data
ENV HOME=/opt/data
