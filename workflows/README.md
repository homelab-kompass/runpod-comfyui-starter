# Starter workflows

Official ComfyUI templates from [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) (MIT). See `THIRD_PARTY_NOTICES.md`.

After the pod is ready, the same files are also copied to:

`/workspace/runpod-slim/ComfyUI/user/default/workflows/homelab-kompass/`

Open them in ComfyUI via **Workflow → Open**, or from that folder in the sidebar.

| File | Model alias (`MODELS=`) | Weights (not in the image) |
| --- | --- | --- |
| `01-sdxl-turbo.json` | `sdxl-turbo` | `models/checkpoints/sd_xl_turbo_1.0_fp16.safetensors` (~6.46 GB) |
| `02-sdxl.json` | `sdxl` | `models/checkpoints/sd_xl_base_1.0.safetensors` (~6.46 GB) |
| `03-flux-schnell.json` | `flux-schnell` | `models/checkpoints/flux1-schnell-fp8.safetensors` (~16.05 GB) |
| `04-wan22-5b-ti2v.json` | `wan22-5b` | Wan 2.2 TI2V 5B pack (~16.9 GB, see the downloader) |

Load weights first:

```bash
/workspace/homelab-kompass/download_models.sh sdxl-turbo
```

Or set `MODELS=sdxl-turbo` (or `HK_DOWNLOAD_MODELS`) before you start the pod. Leave it empty if you want ComfyUI to come up quickly.
