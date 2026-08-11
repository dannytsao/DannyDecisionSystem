FROM python:3.13-slim

RUN apt-get update \
    && apt-get install --no-install-recommends --yes bash ripgrep ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY tests /app/tests
COPY examples /app/examples
COPY automation /app/automation

ENV DDS_ARTIFACT_DIR=/tmp/dds-runner
ENTRYPOINT ["bash", "/app/automation/run-job.sh"]
