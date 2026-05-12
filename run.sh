#!/usr/bin/env bash
# Fox2-clone launcher for Linux. Make executable: chmod +x run.sh
# Double-click in file manager (or run from terminal: ./run.sh).
# First launch creates .venv and installs dependencies (takes a few minutes).
# Subsequent launches start the GUI in ~1 second.

set -e
cd "$(dirname "$0")"

# ---- Check Python ----
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 not found. Install with: sudo apt install python3 python3-venv python3-tk"
    read -p "Press Enter to exit..."
    exit 1
fi

# ---- Check ffmpeg ----
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[WARNING] ffmpeg not found. Video assembly will not work."
    echo "Install: sudo apt install ffmpeg"
    sleep 2
fi

# ---- Create venv if missing ----
if [ ! -x ".venv/bin/python" ]; then
    echo "[setup] Creating virtual environment .venv ..."
    python3 -m venv .venv
    echo "[setup] Installing dependencies (may take a few minutes) ..."
    ".venv/bin/python" -m pip install --upgrade pip
    ".venv/bin/python" -m pip install -e .
fi

# ---- Launch GUI ----
exec ".venv/bin/python" -m fox2
