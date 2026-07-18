#!/usr/bin/env bash
# Print a shareable LAN URL (and QR code, if possible) for the running game.
set -euo pipefail

PORT="${PORT:-8000}"

detect_ip() {
  if command -v ipconfig >/dev/null 2>&1; then
    for iface in en0 en1 en2; do
      ip="$(ipconfig getifaddr "$iface" 2>/dev/null || true)"
      if [ -n "$ip" ]; then
        echo "$ip"
        return
      fi
    done
  fi
  # Linux / fallback: ask the OS which local IP it would use to reach the internet.
  # (No packet is actually sent for a UDP connect.)
  python3 - <<'PY' 2>/dev/null
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
finally:
    s.close()
PY
}

IP="$(detect_ip || true)"
URL="http://${IP}:${PORT}"
BONJOUR_URL="http://$(hostname -s 2>/dev/null || hostname).local:${PORT}"

echo
echo "=================================================="
echo "  TEXT DUNGEON is live on your local network"
echo "=================================================="
if [ -n "$IP" ]; then
  echo "  ${URL}"
fi
echo "  ${BONJOUR_URL}   (Apple devices, some Linux/Android)"
echo "=================================================="
echo

if [ -z "$IP" ]; then
  echo "(couldn't auto-detect a LAN IP; share the Bonjour URL above instead)"
  echo
  return 0 2>/dev/null || exit 0
fi

if command -v qrencode >/dev/null 2>&1; then
  qrencode -t ANSIUTF8 "$URL"
elif python3 -c "import qrcode" >/dev/null 2>&1; then
  python3 - "$URL" <<'PY'
import sys
import qrcode

qr = qrcode.QRCode(border=1)
qr.add_data(sys.argv[1])
qr.make()
qr.print_ascii(invert=True)
PY
else
  echo "(install 'qrencode' for a scannable QR code here, e.g.: brew install qrencode)"
fi
echo
