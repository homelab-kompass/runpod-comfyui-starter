# syntax=docker/dockerfile:1
# Homelab-Kompass ComfyUI Starter DE/EN
# Wrapper around the official Runpod ComfyUI image. No model weights are baked in.
#
# Pin is the latest CUDA 12.8 versioned tag as of 2026-11-17, not the stale
# :cuda12.8 alias (last updated 2026-08-27).
FROM runpod/comfyui:2.4.1-comfyuiv0.44.0-cuda12.8@sha256:1375617a2352d50a5409638fdba7761d33fae7fd6b0ab757ef80beb2e7092769

LABEL org.opencontainers.image.title="Homelab-Kompass ComfyUI Starter DE/EN" \
      org.opencontainers.image.description="Official Runpod ComfyUI (CUDA 12.8) with a bilingual starter, model downloader, and secure password defaults." \
      org.opencontainers.image.source="https://github.com/homelab-kompass/runpod-comfyui-starter" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.authors="Michael Weidinger / Homelab-Kompass" \
      org.opencontainers.image.version="0.1.1"

USER root

COPY scripts/ /opt/homelab-kompass/scripts/
COPY workflows/ /opt/homelab-kompass/workflows/
COPY welcome/ /opt/homelab-kompass/welcome/
COPY README.md README.de.md README.en.md LICENSE THIRD_PARTY_NOTICES.md VERSION /opt/homelab-kompass/

RUN chmod +x /opt/homelab-kompass/scripts/*.sh \
    && ln -sf /opt/homelab-kompass/scripts/download_models.sh /opt/homelab-kompass/download_models.sh \
    && ln -sf /opt/homelab-kompass/scripts/start.sh /opt/homelab-kompass/start.sh

# Official image ENTRYPOINT is /start.sh. Override so our wrapper can set
# passwords and copy docs, then exec the official script.
ENTRYPOINT ["/opt/homelab-kompass/scripts/start.sh"]

EXPOSE 8188 8080 8888 22
