





FROM node:22.20.0-bookworm-slim AS workbench_frontend
WORKDIR /frontend
COPY LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package.json \
     LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package-lock.json ./
RUN npm ci
COPY LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND ./
RUN npm run build

FROM python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS runtime_build
ARG RUNTIME_UID=1000
ARG RUNTIME_GID=1000
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && git config --system --add safe.directory /project \
    && rm -rf /var/lib/apt/lists/* \
    && (getent group ${RUNTIME_GID} || groupadd -g ${RUNTIME_GID} anechoic) \
    && useradd -u ${RUNTIME_UID} -g ${RUNTIME_GID} -m -d /home/anechoic anechoic
RUN python -m pip install --no-cache-dir uv==0.12.18
WORKDIR /workspace
COPY LAYER_3_ENGINE_STUDIO_C14/pyproject.toml LAYER_3_ENGINE_STUDIO_C14/uv.lock ./LAYER_3_ENGINE_STUDIO_C14/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_CACHE_DIR=/tmp/uv-cache
RUN --mount=type=cache,id=anechoic-uv,target=/tmp/uv-cache uv sync --project LAYER_3_ENGINE_STUDIO_C14 --locked --no-default-groups --group runtime
RUN /opt/venv/bin/python -c "import duckdb; c=duckdb.connect(':memory:',config={'extension_directory':'/home/anechoic/.duckdb/extensions'}); c.execute('INSTALL duckpgq FROM community'); c.close()" \
    && chown -R ${RUNTIME_UID}:${RUNTIME_GID} /home/anechoic/.duckdb
RUN rm -rf /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/pip* \
    /usr/local/lib/python3.14/site-packages/uv /usr/local/lib/python3.14/site-packages/uv-*.dist-info \
    /usr/local/lib/python3.14/site-packages/pip /usr/local/lib/python3.14/site-packages/pip-*.dist-info \
    /usr/local/lib/python3.14/ensurepip /usr/local/include/python3.14

FROM scratch
COPY --from=runtime_build / /
ARG RUNTIME_UID=1000
ARG RUNTIME_GID=1000
WORKDIR /workspace
COPY version.toml ./
COPY LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC ./LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC
COPY LAYER_3_ENGINE_STUDIO_C14/KERNEL_MIXER_C59 ./LAYER_3_ENGINE_STUDIO_C14/KERNEL_MIXER_C59
COPY LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21 ./LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21
COPY LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43 ./LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43
COPY LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane \
     ./LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane
COPY --from=workbench_frontend /frontend/dist \
     ./LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/dist
RUN mkdir -p /workspace/.anechoic_install \
    /workspace/.anechoic_tmp /workspace/tmp /workspace/.anechoic_anechoic \
    && chmod -R a+rX /workspace/LAYER_3_ENGINE_STUDIO_C14 \
    && chown -R ${RUNTIME_UID}:${RUNTIME_GID} /home/anechoic
ENV PATH=/opt/venv/bin:/usr/local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1
USER anechoic
HEALTHCHECK --interval=2s --timeout=5s --start-period=420s --retries=25 \
    CMD ["python", "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/healthcheck.py"]
ENTRYPOINT ["/opt/venv/bin/python", "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py"]
