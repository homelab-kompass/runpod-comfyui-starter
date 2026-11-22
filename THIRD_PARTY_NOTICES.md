# Third-party notices

This repository's own scripts, documentation, and configuration are licensed under the MIT License (see `LICENSE`), Copyright (c) 2026 Michael Weidinger / Homelab-Kompass.

## Official Runpod ComfyUI image

The container image is based on `runpod/comfyui` (see the pinned tag and digest in the `Dockerfile`). ComfyUI, ComfyUI-Manager, JupyterLab, FileBrowser, and other software shipped in that base image remain under their own licenses. We do not relicense them.

## Starter workflows

The JSON files in `workflows/` are official ComfyUI workflow templates from [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates), licensed under the MIT License, Copyright (c) 2023-present Comfy Org. A copy of that license:

```
MIT License

Copyright (c) 2023-present Comfy Org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Sources:

- `01-sdxl-turbo.json` ← `templates/sdxlturbo_example.json`
- `02-sdxl.json` ← `templates/image_sdxl_simple.json`
- `03-flux-schnell.json` ← `templates/flux_schnell.json`
- `04-wan22-5b-ti2v.json` ← `templates/video_wan2_2_5B_ti2v.json`

## Optional model weights (not included in the image)

The downloader can fetch third-party weights at runtime. Those files are not part of this image. You must follow the license of each model you download, including:

- Stability AI SDXL 1.0: CreativeML Open RAIL++-M
- Stability AI SDXL-Turbo: see the model card on Hugging Face
- Black Forest Labs FLUX.1 [schnell]: Apache License 2.0
- Black Forest Labs FLUX.1 [dev]: Non-Commercial License (https://bfl.ai/legal/non-commercial-license-terms) — not downloaded unless you set `HF_TOKEN` and `ACCEPT_LICENSE=yes`
- Wan 2.2 (Wan-AI / Comfy-Org repack): Apache License 2.0
