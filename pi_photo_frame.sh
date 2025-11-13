#!/bin/bash
# Raspberry Pi Photo Frame with optional touchscreen gestures and hourly refresh
# Usage:
#   ./pi-photo-frame.sh -install
#   ./pi-photo-frame.sh -run -dir <photo_dir> [-delay <seconds>]
#   ./pi-photo-frame.sh -stop

set -euo pipefail

DEFAULT_DELAY=15
REFRESH_SECS=3600      # 1 hour = 3600 seconds

log() { echo "[*] $*"; }
warn() { echo "[!] $*" >&2; }
die() { echo "[x] $*" >&2; exit 1; }
is_cmd() { command -v "$1" >/dev/null 2>&1; }

session_type() {
  if [[ "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then echo "wayland"; return; fi
  if [[ "${XDG_SESSION_TYPE:-}" == "x11" ]]; then echo "x11"; return; fi
  echo "unknown"
}

detect_touch_event() {
  if compgen -G "/dev/input/by-id/*-event*" >/dev/null; then
    while IFS= read -r path; do
      if [[ "$(basename "$path" | tr '[:upper:]' '[:lower:]')" =~ touch|ts|touchscreen ]]; then
        realpath "$path" 2>/dev/null || echo "$path"
        return 0
      fi
    done < <(ls -1 /dev/input/by-id/*-event* 2>/dev/null)
  fi
  return 1
}

kill_existing() {
  local uid; uid="$(id -u)"
  # Kill feh processes first (they're spawned by the bash loop)
  pkill -u "$uid" -x feh 2>/dev/null || true
  # Kill lisgd gesture daemon
  pkill -u "$uid" -x lisgd 2>/dev/null || true
  # Also kill the background bash loop process if it exists
  pkill -u "$uid" -f "start_feh_loop" 2>/dev/null || true
}

start_lisgd_if_touch() {
  local touch_dev
  if ! touch_dev="$(detect_touch_event)"; then
    log "No touchscreen detected — not starting lisgd."
    return 0
  fi
  local sess 
  sess="$(session_type)"
  if [[ "$sess" == "wayland" ]]; then
    log "Starting lisgd on $touch_dev…"
    lisgd -d $touch_dev -g 1,LR,*,*,R,"wtype -k left"   -g 1,RL,*,*,R,"wtype -k right"    -g 1,DU,*,*,R,"wtype -k escape" &
  else
    log "Only wayland supported in this script, can't enable touchscreen"
    return 0
  fi
}

start_feh_loop() {
  local dir="$1" delay="$2"
  while true; do
    log "Launching feh slideshow…"
    feh -F -Z -Y -D "$delay" --randomize "$dir" &
    log "Running for $((REFRESH_SECS/60)) minutes before refresh."
    sleep "$REFRESH_SECS"
    log "Restarting feh to pick up new photos…"
    pkill -u "$(id -u)" -x feh || true
    sleep 1
  done
}

do_install() {
  log "Installing dependencies…"
  sudo apt update -y
  sudo apt install -y feh libinput-tools
  local sess; sess="$(session_type)"
  if [[ "$sess" == "wayland" ]]; then
    sudo apt install -y wtype xdotool
  fi
  if detect_touch_event >/dev/null; then
    log "Touchscreen detected — installing lisgd."
    sudo apt install -y lisgd
  else
    warn "No touchscreen detected — skipping lisgd."
  fi
  log "Installation complete."
}

do_run() {
  local dir="" delay="$DEFAULT_DELAY"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -dir) shift; dir="${1:-}";;
      -delay) shift; delay="${1:-}";;
    esac
    shift || true
  done
  [[ -n "$dir" && -d "$dir" ]] || die "Missing or invalid -dir <photo_directory>."
  kill_existing
  start_lisgd_if_touch
  log "Starting hourly feh restart loop…"
  start_feh_loop "$dir" "$delay"
  log "Background tasks started. Exiting shell."
}

do_stop() {
  log "Stopping photo frame processes…"
  kill_existing
  sleep 1
  local uid; uid="$(id -u)"
  if pgrep -u "$uid" -x feh >/dev/null 2>&1 || \
     pgrep -u "$uid" -x lisgd >/dev/null 2>&1 || \
     pgrep -u "$uid" -f "start_feh_loop" >/dev/null 2>&1; then
    warn "Some processes may still be running. Try again or kill manually."
  else
    log "All photo frame processes stopped."
  fi
}

# ---- main ----
case "${1:-}" in
  -install) do_install ;;
  -run) shift; do_run "$@" ;;
  -stop) do_stop ;;
  -h|--help|"") echo "Usage: $0 -install | -run -dir <path> [-delay N] | -stop" ;;
  *) echo "Unknown option $1" >&2; exit 1 ;;
esac

