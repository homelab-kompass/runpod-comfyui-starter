# ComfyUI Starter DE/EN (Homelab-Kompass)

Homelab-Kompass ComfyUI Starter. Builds on the official Runpod ComfyUI template (CUDA 12.8, pinned version tag) and adds a short English/German guide, starter workflows, and a downloader for selected openly licensed models.

**Author:** Michael Weidinger, Homelab-Kompass
**Guide:** [ComfyUI on Runpod in 10 minutes](https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/)

This image ships **without model weights**.

## Quick start

1. This template is the **CUDA 12.8** variant, for cards such as the RTX 4090. A CUDA 13 variant for RTX 5090 / Blackwell is not published yet.
2. Deploy a GPU pod from this template. Recommended: 150 GB container disk, 80 GB volume at `/workspace`. For repeated use, attach a Secure Cloud network volume.
3. Set `COMFYUI_PASSWORD`, `JUPYTER_PASSWORD` and `FILEBROWSER_PASSWORD` before you deploy if you want chosen values. If you leave them empty, the entrypoint generates random secrets (at least 12 characters, typically 20) and prints them **only in the pod logs**. The official start script will not start ComfyUI without `COMFYUI_PASSWORD`.
4. Watch the logs until ComfyUI is ready (first boot can take several minutes). Then **Connect → port 8188** and enter the ComfyUI password.
5. Port **8188 requires the ComfyUI password** in the browser. Still do not share the link.
6. Open a starter workflow, for example SDXL-Turbo. Download weights when you need them:
   ```bash
   /workspace/homelab-kompass/download_models.sh sdxl-turbo
   ```
   or set `MODELS=sdxl-turbo` before start. The default is empty, so the UI comes up quickly.
7. When you are done: save your outputs and **stop** the pod. For a longer pause without a network volume, **terminate** it; a stopped volume disk still incurs storage charges, at a higher rate than while running.

## Ports

| Port | Protocol | Service | Notes |
| --- | --- | --- | --- |
| 8188 | HTTP | ComfyUI | Browser login; password from env or logs |
| 8080 | HTTP | FileBrowser | User `admin`, password from env or logs |
| 8888 | HTTP | JupyterLab | Token from env or logs |
| 22 | TCP | SSH | Optional; set `PUBLIC_KEY` |

FileBrowser stores its database at `/workspace/runpod-slim/filebrowser.db`. If you reuse a volume that still has the official default password, that password stays in force — change it immediately.

ComfyUI lives at `/workspace/runpod-slim/ComfyUI` in the official image (not `/workspace/ComfyUI`).

## Environment variables

| Variable | Required | Meaning |
| --- | --- | --- |
| `COMFYUI_PASSWORD` | recommended | Password for the ComfyUI UI (at least 12 characters); otherwise `start.sh` generates a 20-character value and prints it to the logs. ComfyUI will not start without this password. |
| `JUPYTER_PASSWORD` | recommended | Jupyter token; otherwise generated and printed to the logs |
| `FILEBROWSER_PASSWORD` | recommended | FileBrowser password; generated if unset (only applied when no FileBrowser database exists on the volume yet) |
| `MODELS` or `HK_DOWNLOAD_MODELS` | no | Comma-separated aliases, e.g. `sdxl-turbo` or `flux-schnell,sdxl`. Empty = no automatic download |
| `HF_TOKEN` | no | Runpod secret only, for gated Hugging Face downloads |
| `ACCEPT_LICENSE` | no | Together with `HF_TOKEN`, only if you choose to fetch FLUX.1 [dev] yourself |
| `PUBLIC_KEY` | no | SSH public key |
| `HK_AUTO_STOP_MINUTES` | no | Optional: stop the pod after N minutes |
| `HK_IDLE_STOP_MINUTES` | no | Optional: stop the pod after N minutes of 0% GPU utilization |
| `HK_IDLE_GRACE_MINUTES` | no | Grace period before idle measurement, default 15 |
| `RUNPOD_API_KEY` | auto-stop only | Set as a secret, or the pod cannot stop itself. `RUNPOD_POD_ID` is usually injected by Runpod. |

Auto-stop is off unless you set those variables.

## Model downloader

Script: `/workspace/homelab-kompass/download_models.sh`

| Alias | What is fetched | Approx. size | License |
| --- | --- | --- | --- |
| `sdxl-turbo` | `sd_xl_turbo_1.0_fp16.safetensors` | 6.46 GB | see the Stability AI model card |
| `sdxl` | `sd_xl_base_1.0.safetensors` | 6.46 GB | CreativeML Open RAIL++-M |
| `flux-schnell` | packed FP8 checkpoint `flux1-schnell-fp8.safetensors` | 16.05 GB | Apache 2.0 (FLUX.1 [schnell]) |
| `wan22-5b` | Wan 2.2 TI2V 5B (model, VAE, UMT5) | 16.9 GB | Apache 2.0 |

FLUX.1 [dev] is **not** included and is not downloaded automatically (Black Forest Labs Non-Commercial License: https://bfl.ai/legal/non-commercial-license-terms). The script fetches it only if you have read and accepted that license, set `HF_TOKEN` and `ACCEPT_LICENSE=yes`, and request `flux-dev` explicitly. That remains your responsibility.

The downloader verifies SHA-256 when Hugging Face publishes the checksum, and aborts if `/workspace` does not have enough free space.

## Costs and stopping

A running GPU keeps billing after you close the browser. Stop the pod when you are done. A **stopped** volume (not a network volume) still incurs storage charges, at a higher rate than while the pod is running. For a longer pause without a network volume, terminate the pod after saving your work.

Optional safeguard: `HK_IDLE_STOP_MINUTES` plus your `RUNPOD_API_KEY` as a secret.

## Licenses

- Our scripts, documentation, and configuration: MIT, author Michael Weidinger / Homelab-Kompass (see `LICENSE`).
- Base image `runpod/comfyui`, ComfyUI, ComfyUI-Manager, and the other programs in the image: their own licenses.
- Starter workflows: official templates from [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates), MIT, see `THIRD_PARTY_NOTICES.md`.
- Model weights: not in the image; follow each provider's license.

## Image and version

- Image: `ghcr.io/homelab-kompass/runpod-comfyui-starter`
- Current version: see the `VERSION` file
- Base: `runpod/comfyui:2.4.1-comfyuiv0.44.0-cuda12.8` (digest pinned in the `Dockerfile`)
