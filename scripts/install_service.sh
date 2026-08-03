#!/usr/bin/env bash
# Install a systemd *user* timer that runs the report hourly.
# Usage: bash scripts/install_service.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$(command -v python3)"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$UNIT_DIR"

# remove legacy unit name if previously installed as solana-pulse
systemctl --user disable --now solana-pulse.timer 2>/dev/null || true
rm -f "$UNIT_DIR/solana-pulse.service" "$UNIT_DIR/solana-pulse.timer"

cat > "$UNIT_DIR/solana-eye.service" <<EOF
[Unit]
Description=solana-eye: auto-updating Solana ecosystem report
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=${PYTHON} ${REPO_DIR}/run.py
WorkingDirectory=${REPO_DIR}
EOF

cat > "$UNIT_DIR/solana-eye.timer" <<EOF
[Unit]
Description=Run solana-eye hourly

[Timer]
OnCalendar=*:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now solana-eye.timer
systemctl --user start solana-eye.service
echo "Installed. Status:"
systemctl --user list-timers solana-eye.timer
