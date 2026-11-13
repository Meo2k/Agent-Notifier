#!/usr/bin/env bash
# ==============================================================================
# Agent-Notifier: One-liner Uninstaller for Linux, macOS & Termux
# Repository: https://github.com/Meo2k/Agent-Notifier
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ ! -t 1 ]; then
    RED=''
    GREEN=''
    BLUE=''
    YELLOW=''
    CYAN=''
    NC=''
fi

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}       Agent-Notifier Uninstaller         ${NC}"
echo -e "${CYAN}==========================================${NC}"

# Detect Python 3
PYTHON_BIN=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" >/dev/null 2>&1; then
            PYTHON_BIN="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}[Error] Python 3 was not found in PATH.${NC}" >&2
    exit 1
fi

ARGS=("$@")
if [ ${#ARGS[@]} -eq 0 ]; then
    ARGS=("-y")
fi

LOCAL_MANAGER="$HOME/.gemini/config/hooks/notifier/manage_hook.py"

if [ -f "$LOCAL_MANAGER" ]; then
    echo -e "${BLUE}[+] Using local hook manager at: $LOCAL_MANAGER${NC}"
    if [ -t 0 ]; then
        "$PYTHON_BIN" "$LOCAL_MANAGER" uninstall "${ARGS[@]}"
    elif [ -r /dev/tty ]; then
        "$PYTHON_BIN" "$LOCAL_MANAGER" uninstall "${ARGS[@]}" < /dev/tty
    else
        "$PYTHON_BIN" "$LOCAL_MANAGER" uninstall "${ARGS[@]}"
    fi
else
    # Fallback: Download archive to run uninstaller
    TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'agent-notifier')
    cleanup() {
        rm -rf "$TMP_DIR"
    }
    trap cleanup EXIT INT TERM

    echo -e "${BLUE}[+] Downloading uninstaller from GitHub...${NC}"
    REPO_TARBALL="https://github.com/Meo2k/Agent-Notifier/archive/refs/heads/main.tar.gz"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$REPO_TARBALL" | tar -xz -C "$TMP_DIR"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "$REPO_TARBALL" | tar -xz -C "$TMP_DIR"
    else
        echo -e "${RED}[Error] Neither curl nor wget found.${NC}" >&2
        exit 1
    fi

    EXTRACTED_DIR=$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)
    if [ -t 0 ]; then
        "$PYTHON_BIN" "$EXTRACTED_DIR/manage_hook.py" uninstall "${ARGS[@]}"
    elif [ -r /dev/tty ]; then
        "$PYTHON_BIN" "$EXTRACTED_DIR/manage_hook.py" uninstall "${ARGS[@]}" < /dev/tty
    else
        "$PYTHON_BIN" "$EXTRACTED_DIR/manage_hook.py" uninstall "${ARGS[@]}"
    fi
fi

echo -e "\n${GREEN}[✓] Agent-Notifier uninstalled successfully!${NC}"
