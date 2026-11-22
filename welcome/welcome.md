# Homelab-Kompass ComfyUI Starter — checklist

**DE**

1. Logs öffnen und die FileBrowser- sowie Jupyter-Zugangsdaten notieren (wenn du keine eigenen gesetzt hast).
2. **Connect → Port 8188**. Diesen Link nicht öffentlich teilen — ComfyUI hat kein Login.
3. Starter-Workflows liegen unter `/workspace/homelab-kompass/workflows/` und in ComfyUI unter `user/default/workflows/homelab-kompass/`.
4. Modelle nur bewusst laden, z. B. `/workspace/homelab-kompass/download_models.sh sdxl-turbo`.
5. Ergebnisse sichern, danach den Pod **stoppen**. Ohne Netzwerk-Volume für eine längere Pause **beenden** — gestoppter Volume-Speicher kostet weiter, und zwar mehr als im laufenden Zustand.

Begleitartikel: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/

**EN**

1. Open the logs and copy the FileBrowser and Jupyter secrets (unless you set your own).
2. **Connect → port 8188**. Do not share that link — ComfyUI has no login.
3. Starter workflows are in `/workspace/homelab-kompass/workflows/` and in ComfyUI under `user/default/workflows/homelab-kompass/`.
4. Download weights on purpose, e.g. `/workspace/homelab-kompass/download_models.sh sdxl-turbo`.
5. Save your outputs, then **stop** the pod. For a longer pause without a network volume, **terminate** it — a stopped volume disk still incurs storage charges, at a higher rate than while running.

Guide: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/

Author: Michael Weidinger / Homelab-Kompass
