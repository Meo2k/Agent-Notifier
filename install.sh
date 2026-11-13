#!/usr/bin/env bash
# ==============================================================================
# Agent-Notifier: One-liner Installer for Linux, macOS & Termux
# Repository: https://github.com/Meo2k/Agent-Notifier
# ==============================================================================

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Disable colors if stdout is not a tty
if [ ! -t 1 ]; then
    RED=''
    GREEN=''
    BLUE=''
    YELLOW=''
    CYAN=''
    NC=''
fi

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}        Agent-Notifier Installer          ${NC}"
echo -e "${CYAN}==========================================${NC}"

# 1. Detect Python 3
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
    echo -e "${RED}[Error] Python 3 (version 3.7+) is required but was not found in PATH.${NC}" >&2
    echo -e "Please install Python 3 and try again." >&2
    exit 1
fi
echo -e "${BLUE}[+] Using Python:${NC} $($PYTHON_BIN --version 2>&1)"

# 2. Detect Download & Extract tools
DOWNLOADER=""
if command -v curl >/dev/null 2>&1; then
    DOWNLOADER="curl"
elif command -v wget >/dev/null 2>&1; then
    DOWNLOADER="wget"
else
    echo -e "${RED}[Error] Neither 'curl' nor 'wget' was found.${NC}" >&2
    echo -e "Please install curl or wget and try again." >&2
    exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
    echo -e "${RED}[Error] 'tar' command is required to extract archive.${NC}" >&2
    exit 1
fi

# 3. Create temp workspace
TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'agent-notifier')
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

# 4. Download and extract archive
REPO_TARBALL="https://github.com/Meo2k/Agent-Notifier/archive/refs/heads/main.tar.gz"
echo -e "${BLUE}[+] Downloading Agent-Notifier from GitHub...${NC}"

if [ "$DOWNLOADER" = "curl" ]; then
    curl -fsSL "$REPO_TARBALL" | tar -xz -C "$TMP_DIR"
else
    wget -qO- "$REPO_TARBALL" | tar -xz -C "$TMP_DIR"
fi

# Locate extracted directory
EXTRACTED_DIR=$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)
if [ -z "$EXTRACTED_DIR" ] || [ ! -f "$EXTRACTED_DIR/manage_hook.py" ]; then
    echo -e "${RED}[Error] Failed to locate extracted repository files.${NC}" >&2
    exit 1
fi

# 5. Run installation
echo -e "${BLUE}[+] Running hook manager...${NC}"

# Handle arguments: Default to -y if no parameters supplied
ARGS=("$@")
if [ ${#ARGS[@]} -eq 0 ]; then
    ARGS=("-y")
fi

# Connect input from /dev/tty if stdin is piped (e.g. curl ... | bash) and user wants interactive mode
if [ -t 0 ]; then
    "$PYTHON_BIN" "$EXTRACTED_DIR/manage_hook.py" install "${ARGS[@]}"
elif [ -r /dev/tty ]; then
    "$PYTHON_BIN" "$EXTRACTED_DIR/manage_hook.py" install "${ARGS[@]}" < /dev/tty
else
    "$PYTHON_BIN" "$EXTRACTED_DIR/manage_hook.py" install "${ARGS[@]}"
fi

echo -e "\n${GREEN}[✓] Agent-Notifier installation complete!${NC}"
echo -e "${CYAN}------------------------------------------${NC}"
echo -e "Quick testing commands:"
echo -e "  ${YELLOW}$PYTHON_BIN ~/.gemini/config/hooks/notifier/notifier.py --test task_completed${NC}"
echo -e "  ${YELLOW}$PYTHON_BIN ~/.gemini/config/hooks/notifier/manage_hook.py status${NC}"
echo -e "To uninstall anytime:"
echo -e "  ${YELLOW}$PYTHON_BIN ~/.gemini/config/hooks/notifier/manage_hook.py uninstall -y${NC}"
echo -e "${CYAN}------------------------------------------${NC}"
