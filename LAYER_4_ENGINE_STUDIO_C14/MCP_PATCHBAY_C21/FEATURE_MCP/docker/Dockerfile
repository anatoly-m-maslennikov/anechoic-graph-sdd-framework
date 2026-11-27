





FROM node:22.20.0-bookworm-slim AS workbench_frontend
WORKDIR /frontend
COPY LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/package.json \
     LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/package-lock.json ./
RUN npm ci
COPY LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND ./
RUN npm run build

FROM python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS runtime_build
ARG RUNTIME_UID=1000
ARG RUNTIME_GID=1000
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates binutils \
    && rm -rf /var/lib/apt/lists/* \
    && (getent group ${RUNTIME_GID} || groupadd -g ${RUNTIME_GID} anechoic) \
    && useradd -u ${RUNTIME_UID} -g ${RUNTIME_GID} -m -d /home/anechoic anechoic
RUN python -B -m pip install --no-cache-dir --no-compile uv==0.12.18
WORKDIR /workspace
COPY LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock ./LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_CACHE_DIR=/tmp/uv-cache
RUN --mount=type=cache,id=anechoic-uv,target=/tmp/uv-cache uv sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked --no-compile-bytecode --no-default-groups --group runtime
RUN strip --strip-unneeded -o /tmp/cryptography-rust.so /opt/venv/lib/python3.14/site-packages/cryptography/hazmat/bindings/_rust.abi3.so \
    && mv /tmp/cryptography-rust.so /opt/venv/lib/python3.14/site-packages/cryptography/hazmat/bindings/_rust.abi3.so \
    && apt-get purge -y --auto-remove binutils
RUN /opt/venv/bin/python -B -c "import duckdb; c=duckdb.connect(':memory:',config={'extension_directory':'/home/anechoic/.duckdb/extensions'}); c.execute('INSTALL duckpgq FROM community'); c.close()" \
    && chown -R ${RUNTIME_UID}:${RUNTIME_GID} /home/anechoic/.duckdb
RUN rm -rf /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/pip* \
    /usr/local/lib/python3.14/site-packages/uv /usr/local/lib/python3.14/site-packages/uv-*.dist-info \
    /usr/local/lib/python3.14/site-packages/pip /usr/local/lib/python3.14/site-packages/pip-*.dist-info \
    /usr/local/lib/python3.14/ensurepip /usr/local/include/python3.14 \
    /usr/bin/perl /usr/bin/perl5.* /usr/lib/*/perl-base \
    && find /opt/venv/lib -type d \( -name test -o -name tests \) -prune -exec rm -rf {} + \
    && ! command -v git && ! command -v perl && ! command -v strip

FROM scratch AS runtime_base
ARG ANECHOIC_RUNTIME_PROFILE=dev-preprod
ENV ANECHOIC_RUNTIME_PROFILE=${ANECHOIC_RUNTIME_PROFILE}
COPY --from=runtime_build / /
ARG RUNTIME_UID=1000
ARG RUNTIME_GID=1000
WORKDIR /workspace
COPY version.toml LICENSE LICENSE.TLDR.md ./
COPY LAYER_1_META_ONTOLOGY_C9 ./LAYER_1_META_ONTOLOGY_C9
COPY LAYER_2_META_METHODOLOGY_C58 ./LAYER_2_META_METHODOLOGY_C58

COPY LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/DuckPGQ.LICENSE /usr/local/share/licenses/duckpgq/LICENSE
COPY LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC ./LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC
COPY LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73 ./LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73
COPY LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21 ./LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21
COPY LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43 ./LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43
COPY LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane \
     ./LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane
COPY --from=workbench_frontend /frontend/dist \
     ./LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/dist
RUN mkdir -p /var/lib/anechoic /workspace/.anechoic_install \
    /workspace/.anechoic_tmp /workspace/tmp /workspace/.anechoic_anechoic \
    && chmod -R a+rX /workspace/LAYER_1_META_ONTOLOGY_C9 /workspace/LAYER_2_META_METHODOLOGY_C58 \
    /workspace/LAYER_4_ENGINE_STUDIO_C14 \
    && chown -R ${RUNTIME_UID}:${RUNTIME_GID} /home/anechoic /var/lib/anechoic
ENV PATH=/opt/venv/bin:/usr/local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPYCACHEPREFIX=/workspace/.anechoic_tmp/python/bytecode
RUN PYTHONPYCACHEPREFIX=/workspace/.anechoic_tmp/python/bytecode /opt/venv/bin/python -B -m compileall -q --invalidation-mode timestamp \
    /usr/local/lib/python3.14 /opt/venv/lib/python3.14/site-packages /workspace/LAYER_4_ENGINE_STUDIO_C14 \
    && chmod -R a+rX "$PYTHONPYCACHEPREFIX"
HEALTHCHECK --interval=2s --timeout=5s --start-period=420s --retries=25 \
    CMD ["/opt/venv/bin/python", "-B", "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/healthcheck.py"]
ENTRYPOINT ["/opt/venv/bin/python", "-B", "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py"]

FROM runtime_base AS beta_base
COPY --from=workbench_frontend /usr/local/bin/node /usr/local/bin/node
COPY --from=workbench_frontend /frontend/node_modules/typescript ./LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript
COPY --from=workbench_frontend /frontend/node_modules/svelte ./LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/svelte
COPY LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67 ./LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67
COPY LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68 ./LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68
COPY LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69 ./LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69
RUN PYTHONPYCACHEPREFIX=/workspace/.anechoic_tmp/python/bytecode /opt/venv/bin/python -B -m compileall -q --invalidation-mode timestamp \
    /workspace/LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67 \
    /workspace/LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68 \
    /workspace/LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69 \
    && chmod -R a+rX "$PYTHONPYCACHEPREFIX" /workspace/LAYER_4_ENGINE_STUDIO_C14

FROM beta_base AS beta_next
COPY LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91 ./LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91
ENV ANECHOIC_RUNTIME_STACK=beta_next
LABEL org.anechoic.runtime.stack=beta_next
RUN PYTHONPYCACHEPREFIX=/workspace/.anechoic_tmp/python/bytecode /opt/venv/bin/python -B -m compileall -q --invalidation-mode timestamp \
    /workspace/LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91 \
    && chmod -R a+rX "$PYTHONPYCACHEPREFIX" /workspace/LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91
USER anechoic

FROM runtime_base AS current
ENV ANECHOIC_RUNTIME_STACK=current
COPY LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59 ./LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59
RUN PYTHONPYCACHEPREFIX=/workspace/.anechoic_tmp/python/bytecode /opt/venv/bin/python -B -m compileall -q --invalidation-mode timestamp \
    /workspace/LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59 \
    && chmod -R a+rX "$PYTHONPYCACHEPREFIX" /workspace/LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59
USER anechoic
