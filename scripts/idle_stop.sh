#!/usr/bin/env bash
# Optional pod auto-stop. Does nothing unless the user set
# HK_AUTO_STOP_MINUTES and/or HK_IDLE_STOP_MINUTES, plus credentials
# to actually stop the pod (RUNPOD_POD_ID is usually injected by Runpod;
# RUNPOD_API_KEY must be provided by the user as a secret).
set -euo pipefail

log() { echo "[homelab-kompass-autostop] $*"; }

stop_pod() {
    local reason="$1"
    local pod_id="${RUNPOD_POD_ID:-}"
    if [[ -z "${pod_id}" ]]; then
        log "Cannot stop: RUNPOD_POD_ID is not set."
        return 1
    fi
    if [[ -z "${RUNPOD_API_KEY:-}" ]]; then
        log "Cannot stop: set RUNPOD_API_KEY as a Runpod secret so the pod can stop itself. Reason would have been: ${reason}"
        return 1
    fi
    log "Stopping pod ${pod_id}: ${reason}"
    # Prefer the REST v2 action endpoint; fall back to GraphQL.
    local code
    code="$(curl -sS -o /tmp/hk-pod-stop.out -w "%{http_code}" \
        --request POST \
        --url "https://api.runpod.io/v2/pods/${pod_id}/action" \
        --header "Authorization: Bearer ${RUNPOD_API_KEY}" \
        --header "Content-Type: application/json" \
        --data '{"action":"stop"}' || true)"
    if [[ "${code}" =~ ^2 ]]; then
        log "Stop request accepted (HTTP ${code})."
        return 0
    fi
    log "REST stop returned HTTP ${code}; trying GraphQL podStop."
    curl -sS -o /tmp/hk-pod-stop.out \
        --request POST \
        --url "https://api.runpod.io/graphql" \
        --header "Authorization: Bearer ${RUNPOD_API_KEY}" \
        --header "Content-Type: application/json" \
        --data "{\"query\":\"mutation { podStop(input: {podId: \\\"${pod_id}\\\"}) { id desiredStatus } }\"}" \
        || true
    log "GraphQL stop response written to /tmp/hk-pod-stop.out"
}

gpu_util() {
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        echo "unknown"
        return 1
    fi
    nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null \
        | awk '{s+=$1; n++} END {if(n>0) printf("%d", s/n); else print "unknown"}'
}

# Hard deadline: stop after N minutes from start, regardless of load.
if [[ -n "${HK_AUTO_STOP_MINUTES:-}" ]]; then
    if ! [[ "${HK_AUTO_STOP_MINUTES}" =~ ^[0-9]+$ ]] || [[ "${HK_AUTO_STOP_MINUTES}" -le 0 ]]; then
        log "Ignoring invalid HK_AUTO_STOP_MINUTES=${HK_AUTO_STOP_MINUTES}"
    else
        (
            log "Hard stop scheduled in ${HK_AUTO_STOP_MINUTES} minute(s)."
            sleep $((HK_AUTO_STOP_MINUTES * 60))
            stop_pod "HK_AUTO_STOP_MINUTES=${HK_AUTO_STOP_MINUTES} reached"
        ) &
    fi
fi

# Idle stop: GPU utilization stays at 0 for N minutes, after a grace period
# so first-boot copies and optional downloads can finish.
if [[ -n "${HK_IDLE_STOP_MINUTES:-}" ]]; then
    if ! [[ "${HK_IDLE_STOP_MINUTES}" =~ ^[0-9]+$ ]] || [[ "${HK_IDLE_STOP_MINUTES}" -le 0 ]]; then
        log "Ignoring invalid HK_IDLE_STOP_MINUTES=${HK_IDLE_STOP_MINUTES}"
        exit 0
    fi
    local_grace="${HK_IDLE_GRACE_MINUTES:-15}"
    if ! [[ "${local_grace}" =~ ^[0-9]+$ ]]; then
        local_grace=15
    fi
    log "Idle stop after ${HK_IDLE_STOP_MINUTES} minute(s) at 0% GPU util, grace ${local_grace} minute(s)."
    sleep $((local_grace * 60))
    idle_ticks=0
    needed="${HK_IDLE_STOP_MINUTES}"
    while true; do
        util="$(gpu_util || true)"
        if [[ "${util}" == "unknown" || -z "${util}" ]]; then
            log "nvidia-smi unavailable; idle auto-stop cannot measure GPU load. Giving up."
            exit 0
        fi
        if [[ "${util}" -eq 0 ]]; then
            idle_ticks=$((idle_ticks + 1))
            if [[ "${idle_ticks}" -ge "${needed}" ]]; then
                stop_pod "GPU idle for ${needed} minute(s)"
                exit 0
            fi
        else
            idle_ticks=0
        fi
        sleep 60
    done
fi

wait || true
