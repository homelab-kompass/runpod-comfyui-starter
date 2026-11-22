#!/usr/bin/env python3
"""Download selected, openly licensed model weights for the Homelab-Kompass
ComfyUI Starter. No weights are bundled in the image.

Aliases (comma-separated in MODELS or HK_DOWNLOAD_MODELS, or argv):
  sdxl-turbo, sdxl, flux-schnell, wan22-5b

Gated / non-commercial:
  flux-dev  — only with HF_TOKEN and ACCEPT_LICENSE=yes (or ACCEPT_FLUX_DEV_LICENSE=yes)
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path

COMFYUI_DIR = Path(os.environ.get("COMFYUI_DIR", "/workspace/runpod-slim/ComfyUI"))
MODELS_ROOT = COMFYUI_DIR / "models"
LICENSE_DIR = Path("/workspace/homelab-kompass/licenses")
RESERVE_BYTES = 2 * 1024 * 1024 * 1024  # keep 2 GiB free after planned downloads


def log(msg: str) -> None:
    print(f"[homelab-kompass-downloader] {msg}", flush=True)


def wait_for_models_dir(timeout_s: int = 900) -> Path:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if MODELS_ROOT.is_dir():
            return MODELS_ROOT
        time.sleep(5)
    raise SystemExit(
        f"Timed out waiting for {MODELS_ROOT}. Is the official ComfyUI first-boot copy still running?"
    )


def free_bytes(path: Path) -> int:
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize


def sha256_file(path: Path, expected: str | None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    digest = h.hexdigest()
    if expected and digest != expected:
        raise SystemExit(f"Checksum mismatch for {path.name}: got {digest}, expected {expected}")
    return digest


def truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on", "accept"}


def accepted_flux_dev_license() -> bool:
    return truthy(os.environ.get("ACCEPT_LICENSE")) or truthy(
        os.environ.get("ACCEPT_FLUX_DEV_LICENSE")
    ) or truthy(os.environ.get("HK_ACCEPT_FLUX_DEV_LICENSE"))


def write_license_note(name: str, text: str) -> None:
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    (LICENSE_DIR / name).write_text(text, encoding="utf-8")


def download_hf(repo: str, filename: str, dest: Path, expected_sha256: str | None, size: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size == size:
        if expected_sha256:
            log(f"Already present, verifying checksum: {dest}")
            sha256_file(dest, expected_sha256)
        else:
            log(f"Already present: {dest}")
        return
    if dest.exists() and dest.stat().st_size != size:
        log(f"Incomplete file {dest} ({dest.stat().st_size} bytes), re-downloading.")
        dest.unlink()

    available = free_bytes(dest.parent)
    if available < size + RESERVE_BYTES:
        need = (size + RESERVE_BYTES) / (1024**3)
        have = available / (1024**3)
        raise SystemExit(
            f"Not enough free space on /workspace for {filename}: "
            f"need about {need:.1f} GiB including reserve, have {have:.1f} GiB. "
            "Attach a larger volume or a network volume and retry."
        )

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        log("huggingface_hub is missing; installing it with pip...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "huggingface_hub"])
        from huggingface_hub import hf_hub_download  # type: ignore

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or None
    log(f"Downloading {repo}/{filename} -> {dest}")
    tmp_name = hf_hub_download(
        repo_id=repo,
        filename=filename,
        token=token,
        resume_download=True,
    )
    src = Path(tmp_name)
    if dest.exists():
        dest.unlink()
    try:
        os.link(src, dest)
    except OSError:
        import shutil

        shutil.copy2(src, dest)
    if expected_sha256:
        sha256_file(dest, expected_sha256)
        log(f"Checksum OK: {dest.name}")
    else:
        log(f"Downloaded (no published checksum to verify): {dest}")


# sizes and sha256 from Hugging Face LFS metadata, retrieved 2026-11-22
PACKS: dict[str, dict] = {
    "sdxl-turbo": {
        "title": "SDXL-Turbo (Stability AI)",
        "license": "See the Stability AI model card: https://huggingface.co/stabilityai/sdxl-turbo",
        "files": [
            {
                "repo": "stabilityai/sdxl-turbo",
                "filename": "sd_xl_turbo_1.0_fp16.safetensors",
                "dest": "checkpoints/sd_xl_turbo_1.0_fp16.safetensors",
                "sha256": "e869ac7d6942cb327d68d5ed83a40447aadf20e0c3358d98b2cc9e270db0da26",
                "size": 6938081905,
            }
        ],
    },
    "sdxl": {
        "title": "SDXL 1.0 Base (Stability AI, CreativeML Open RAIL++-M)",
        "license": "CreativeML Open RAIL++-M: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0",
        "files": [
            {
                "repo": "stabilityai/stable-diffusion-xl-base-1.0",
                "filename": "sd_xl_base_1.0.safetensors",
                "dest": "checkpoints/sd_xl_base_1.0.safetensors",
                "sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b",
                "size": 6938078334,
            }
        ],
    },
    "flux-schnell": {
        "title": "FLUX.1 [schnell] fp8 packed checkpoint (Apache 2.0)",
        "license": "Apache License 2.0 (Black Forest Labs FLUX.1 [schnell]). Packed checkpoint from https://huggingface.co/Comfy-Org/flux1-schnell",
        "files": [
            {
                "repo": "Comfy-Org/flux1-schnell",
                "filename": "flux1-schnell-fp8.safetensors",
                "dest": "checkpoints/flux1-schnell-fp8.safetensors",
                "sha256": "ead426278b49030e9da5df862994f25ce94ab2ee4df38b556ddddb3db093bf72",
                "size": 17236328572,
            }
        ],
    },
    "flux-schnell-full": {
        "title": "FLUX.1 [schnell] full transformer + text encoders (Apache 2.0)",
        "license": "Apache License 2.0 (Black Forest Labs FLUX.1 [schnell]). Transformer from Comfy-Org/flux1-schnell; text encoders from comfyanonymous/flux_text_encoders.",
        "files": [
            {
                "repo": "Comfy-Org/flux1-schnell",
                "filename": "flux1-schnell.safetensors",
                "dest": "diffusion_models/flux1-schnell.safetensors",
                "sha256": "9403429e0052277ac2a87ad800adece5481eecefd9ed334e1f348723621d2a0a",
                "size": 23782506688,
            },
            {
                "repo": "comfyanonymous/flux_text_encoders",
                "filename": "clip_l.safetensors",
                "dest": "text_encoders/clip_l.safetensors",
                "sha256": "660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd",
                "size": 246144152,
            },
            {
                "repo": "comfyanonymous/flux_text_encoders",
                "filename": "t5xxl_fp8_e4m3fn.safetensors",
                "dest": "text_encoders/t5xxl_fp8_e4m3fn.safetensors",
                "sha256": "7d330da4816157540d6bb7838bf63a0f02f573fc48ca4d8de34bb0cbfd514f09",
                "size": 4893934904,
            },
        ],
    },
    "wan22-5b": {
        "title": "Wan 2.2 TI2V 5B (Apache 2.0, Comfy-Org repack)",
        "license": "Apache License 2.0. Source: https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged",
        "files": [
            {
                "repo": "Comfy-Org/Wan_2.2_ComfyUI_Repackaged",
                "filename": "split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors",
                "dest": "diffusion_models/wan2.2_ti2v_5B_fp16.safetensors",
                "sha256": "456f901338bd9eadbded3828b819109a9b68e8a525ca5cf8d0049a69fcfeca1e",
                "size": 9999658848,
            },
            {
                "repo": "Comfy-Org/Wan_2.2_ComfyUI_Repackaged",
                "filename": "split_files/vae/wan2.2_vae.safetensors",
                "dest": "vae/wan2.2_vae.safetensors",
                "sha256": "e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156",
                "size": 1409400960,
            },
            {
                "repo": "Comfy-Org/Wan_2.2_ComfyUI_Repackaged",
                "filename": "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "dest": "text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "sha256": "c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68",
                "size": 6735906897,
            },
        ],
    },
}

ALIASES = {
    "sdxl-turbo": "sdxl-turbo",
    "sdxlturbo": "sdxl-turbo",
    "turbo": "sdxl-turbo",
    "sdxl": "sdxl",
    "sdxl-base": "sdxl",
    "flux-schnell": "flux-schnell",
    "flux_schnell": "flux-schnell",
    "schnell": "flux-schnell",
    "flux-schnell-fp8": "flux-schnell",
    "flux-schnell-full": "flux-schnell-full",
    "flux-schnell-fp16": "flux-schnell-full",
    "wan22-5b": "wan22-5b",
    "wan22": "wan22-5b",
    "wan2.2-5b": "wan22-5b",
    "wan2.2": "wan22-5b",
}

FLUX_DEV_HELP = """\
Refusing to download FLUX.1 [dev].

FLUX.1 [dev] is under Black Forest Labs' Non-Commercial License:
https://bfl.ai/legal/non-commercial-license-terms

It is not included in this image and is not downloaded automatically.

If you have read the license, accept its terms, and want to download the
weights yourself (for a permitted non-commercial use), set all of:

  HF_TOKEN=<your Hugging Face token with access to black-forest-labs/FLUX.1-dev>
  ACCEPT_LICENSE=yes

and run:  /workspace/homelab-kompass/download_models.sh flux-dev

This is your responsibility. Commercial use and several other uses are
not covered without a separate license from Black Forest Labs.
"""


def flux_dev_pack() -> dict:
    return {
        "title": "FLUX.1 [dev] (Non-Commercial License — user accepted)",
        "license": "Non-Commercial License: https://bfl.ai/legal/non-commercial-license-terms",
        "files": [
            {
                "repo": "black-forest-labs/FLUX.1-dev",
                "filename": "flux1-dev.safetensors",
                "dest": "diffusion_models/flux1-dev.safetensors",
                "sha256": None,  # gated; Hugging Face does not publish the LFS sha publicly
                "size": 23802985984,
            },
            {
                "repo": "black-forest-labs/FLUX.1-dev",
                "filename": "ae.safetensors",
                "dest": "vae/ae.safetensors",
                "sha256": None,
                "size": 335304388,
            },
            {
                "repo": "comfyanonymous/flux_text_encoders",
                "filename": "clip_l.safetensors",
                "dest": "text_encoders/clip_l.safetensors",
                "sha256": "660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd",
                "size": 246144152,
            },
            {
                "repo": "comfyanonymous/flux_text_encoders",
                "filename": "t5xxl_fp8_e4m3fn.safetensors",
                "dest": "text_encoders/t5xxl_fp8_e4m3fn.safetensors",
                "sha256": "7d330da4816157540d6bb7838bf63a0f02f573fc48ca4d8de34bb0cbfd514f09",
                "size": 4893934904,
            },
        ],
    }


def parse_selection(raw: str) -> list[str]:
    items: list[str] = []
    for part in raw.replace(";", ",").split(","):
        key = part.strip().lower()
        if not key:
            continue
        items.append(key)
    return items


def main() -> int:
    raw = ""
    if len(sys.argv) > 1:
        raw = ",".join(sys.argv[1:])
    if not raw:
        raw = os.environ.get("MODELS") or os.environ.get("HK_DOWNLOAD_MODELS") or ""
    selection = parse_selection(raw)
    if not selection:
        log(
            "Nothing to download. Pass aliases (e.g. sdxl-turbo) or set MODELS / HK_DOWNLOAD_MODELS. "
            "Available: sdxl-turbo, sdxl, flux-schnell, wan22-5b. flux-dev requires HF_TOKEN and ACCEPT_LICENSE=yes."
        )
        return 0

    wait_for_models_dir()
    unknown: list[str] = []
    errors = 0

    for item in selection:
        if item in {"flux-dev", "flux_dev", "fluxdev", "flux.dev"}:
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            if not token or not accepted_flux_dev_license():
                log(FLUX_DEV_HELP)
                errors += 1
                continue
            log(
                "FLUX.1 [dev] requested. You set ACCEPT_LICENSE. "
                "This is a non-commercial license. Downloading is your responsibility."
            )
            pack = flux_dev_pack()
        elif item in ALIASES:
            pack = PACKS[ALIASES[item]]
        else:
            unknown.append(item)
            continue

        write_license_note(
            f"{item.replace('/', '_')}.txt",
            pack["title"] + "\n\n" + pack["license"] + "\n",
        )
        log(f"=== {pack['title']} ===")
        log(pack["license"])
        # Pre-flight space for this pack (skip files already present with the right size)
        needed = 0
        for f in pack["files"]:
            dest = MODELS_ROOT / f["dest"]
            if dest.exists() and dest.stat().st_size == f["size"]:
                continue
            needed += f["size"]
        if needed and free_bytes(MODELS_ROOT) < needed + RESERVE_BYTES:
            have = free_bytes(MODELS_ROOT) / (1024**3)
            need = (needed + RESERVE_BYTES) / (1024**3)
            log(
                f"Not enough free space for {item}: need about {need:.1f} GiB including reserve, have {have:.1f} GiB."
            )
            errors += 1
            continue
        try:
            for f in pack["files"]:
                dest = MODELS_ROOT / f["dest"]
                download_hf(f["repo"], f["filename"], dest, f.get("sha256"), f["size"])
        except SystemExit as exc:
            log(str(exc))
            errors += 1
        except Exception as exc:  # noqa: BLE001 — surface download errors, keep other packs going
            log(f"Download failed for {item}: {exc}")
            errors += 1

    if unknown:
        log("Unknown alias(es): " + ", ".join(unknown))
        log("Known: sdxl-turbo, sdxl, flux-schnell, flux-schnell-full, wan22-5b, flux-dev (restricted).")
        errors += 1

    if errors:
        log(f"Finished with {errors} error(s).")
        return 1
    log("All requested downloads finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
