# ComfyUI Starter DE/EN (Homelab-Kompass)

Homelab-Kompass ComfyUI Starter. Basiert auf der offiziellen Runpod-ComfyUI-Vorlage (CUDA 12.8, gepinnter Versionstag), ergänzt um eine deutsche und englische Kurzanleitung, Starter-Workflows und ein Skript zum Laden ausgewählter, offen lizenzierter Modelle.

**Autor:** Michael Weidinger, Homelab-Kompass
**Begleitartikel:** [ComfyUI auf Runpod in 10 Minuten](https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/)

Dieses Image enthält **keine Modellgewichte**.

## Schnellstart

1. Dieses Template ist die **CUDA-12.8-Variante**, passend für typische Karten wie die RTX 4090. Für RTX 5090 / Blackwell brauchst du später die CUDA-13-Variante (noch nicht veröffentlicht).
2. Lege in Runpod eine GPU-Cloud-Instanz mit diesem Template an. Empfohlen: Container-Disk 150 GB, Volume 80 GB unter `/workspace`. Für wiederholte Nutzung ein Netzwerk-Volume in der Secure Cloud anhängen.
3. Setze vor dem Start, wenn du die Werte selbst festlegen willst, `JUPYTER_PASSWORD` und `FILEBROWSER_PASSWORD`. Wenn du sie leer lässt, erzeugt der Start ein Zufallspasswort und schreibt es **nur in die Pod-Logs**.
4. Nach dem Start die Logs prüfen, bis ComfyUI bereit ist (das kann beim ersten Start einige Minuten dauern). Dann **Connect → Port 8188**.
5. Port **8188 ist über die Proxy-URL ohne Anmeldung erreichbar** — den Link nicht öffentlich teilen.
6. Einen Starter-Workflow öffnen, zum Beispiel „SDXL-Turbo“. Modelle bei Bedarf laden:
   ```bash
   /workspace/homelab-kompass/download_models.sh sdxl-turbo
   ```
   oder vor dem Start `MODELS=sdxl-turbo` setzen (dann startet 8188 erst vollständig, wenn der Download durch ist oder parallel weiterläuft). Standard ist: nichts automatisch laden, damit die Oberfläche schnell kommt.
7. Wenn du fertig bist: Ergebnisse sichern, Pod **stoppen**. Für längere Pausen ohne Netzwerk-Volume den Pod **beenden**, sonst läuft die Speichermiete weiter. Gestoppte Volume-Disks sind teurer als laufende.

## Ports

| Port | Protokoll | Dienst | Hinweis |
| --- | --- | --- | --- |
| 8188 | HTTP | ComfyUI | Keine Anmeldung an der Proxy-URL |
| 8080 | HTTP | FileBrowser | Benutzer `admin`, Passwort aus Env oder Logs |
| 8888 | HTTP | JupyterLab | Token aus Env oder Logs |
| 22 | TCP | SSH | Optional, `PUBLIC_KEY` setzen |

FileBrowser legt seine Datenbank unter `/workspace/runpod-slim/filebrowser.db` an. Wenn du ein Volume wiederverwendest, das noch das offizielle Standardpasswort enthält, gilt dieses weiterhin — dann sofort ändern.

ComfyUI selbst liegt im offiziellen Image unter `/workspace/runpod-slim/ComfyUI` (nicht unter `/workspace/ComfyUI`).

## Umgebungsvariablen

| Variable | Pflicht | Bedeutung |
| --- | --- | --- |
| `JUPYTER_PASSWORD` | empfohlen | Jupyter-Token; sonst generiert `start.sh` einen Wert und schreibt ihn in die Logs |
| `FILEBROWSER_PASSWORD` | empfohlen | FileBrowser-Passwort; sonst generiert (greift nur, wenn noch keine FileBrowser-Datenbank auf dem Volume liegt) |
| `MODELS` oder `HK_DOWNLOAD_MODELS` | nein | Kommagetrennte Aliase, z. B. `sdxl-turbo` oder `flux-schnell,sdxl`. Leer = kein Automatik-Download |
| `HF_TOKEN` | nein | Nur als Runpod-Secret, für gated Hugging-Face-Downloads |
| `ACCEPT_LICENSE` | nein | Nur zusammen mit `HF_TOKEN`, wenn du FLUX.1 [dev] selbst laden willst |
| `PUBLIC_KEY` | nein | SSH-Public-Key |
| `HK_AUTO_STOP_MINUTES` | nein | Optional: Pod nach N Minuten stoppen |
| `HK_IDLE_STOP_MINUTES` | nein | Optional: Pod stoppen, wenn die GPU N Minuten bei 0 % Auslastung bleibt |
| `HK_IDLE_GRACE_MINUTES` | nein | Wartezeit vor der Idle-Messung, Standard 15 |
| `RUNPOD_API_KEY` | nur für Auto-Stop | Als Secret setzen, sonst kann der Pod sich nicht selbst stoppen. `RUNPOD_POD_ID` setzt Runpod in der Regel selbst. |

Auto-Stop ist absichtlich aus. Ohne diese Variablen läuft der Pod, bis du ihn stoppst.

## Modell-Downloader

Skript: `/workspace/homelab-kompass/download_models.sh`

| Alias | Was geladen wird | Ungefähre Größe | Lizenz |
| --- | --- | --- | --- |
| `sdxl-turbo` | `sd_xl_turbo_1.0_fp16.safetensors` | 6,46 GB | siehe Model Card von Stability AI |
| `sdxl` | `sd_xl_base_1.0.safetensors` | 6,46 GB | CreativeML Open RAIL++-M |
| `flux-schnell` | gepackter FP8-Checkpoint `flux1-schnell-fp8.safetensors` | 16,05 GB | Apache 2.0 (FLUX.1 [schnell]) |
| `wan22-5b` | Wan 2.2 TI2V 5B (Modell, VAE, UMT5) | 16,9 GB | Apache 2.0 |

FLUX.1 [dev] wird **nicht** mitgeliefert und nicht automatisch geladen (nicht-kommerzielle Lizenz von Black Forest Labs: https://bfl.ai/legal/non-commercial-license-terms). Nur wenn du die Lizenz gelesen und akzeptiert hast, `HF_TOKEN` und `ACCEPT_LICENSE=yes` setzt und `flux-dev` ausdrücklich aufrufst, lädt das Skript die Gewichte. Das bleibt deine Verantwortung.

Der Downloader prüft SHA-256, soweit Hugging Face die Prüfsumme öffentlich angibt, und bricht ab, wenn auf `/workspace` zu wenig Platz ist.

## Kosten und Stoppen

Eine laufende GPU wird weiter berechnet, auch wenn du das Browserfenster schließt. Stoppe den Pod, sobald du fertig bist. Ein **gestopptes** Volume (kein Netzwerk-Volume) kostet weiter Speicher — laut Runpod-Doku teurer als im laufenden Zustand. Für längere Pausen ohne Netzwerk-Volume den Pod **beenden**, vorher Ergebnisse sichern.

Optionaler Schutz vor vergessenen Pods: `HK_IDLE_STOP_MINUTES` plus dein `RUNPOD_API_KEY` als Secret.

## Lizenzen

- Unsere Skripte, Dokumentation und Konfiguration: MIT, Autor Michael Weidinger / Homelab-Kompass (siehe `LICENSE`).
- Basisimage `runpod/comfyui`, ComfyUI, ComfyUI-Manager und die übrigen Programme im Image: jeweils deren eigene Lizenzen.
- Starter-Workflows: offizielle Vorlagen von [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates), MIT, siehe `THIRD_PARTY_NOTICES.md`.
- Modellgewichte: nicht im Image, es gelten die Lizenzen der jeweiligen Anbieter.

## Image und Version

- Image: `ghcr.io/homelab-kompass/runpod-comfyui-starter`
- Aktuelle Version: siehe Datei `VERSION`
- Basis: `runpod/comfyui:2.4.1-comfyuiv0.44.0-cuda12.8` (Digest ist im `Dockerfile` gepinnt)
