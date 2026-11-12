#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
ENV_FILE = CURRENT_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

HOOKS_CONFIG_PATH = Path(os.getenv("HOOKS_CONFIG_PATH", "~/.gemini/config/hooks.json")).expanduser().resolve()
HOOK_NAME = os.getenv("HOOK_NAME", "antigravity-notifier")
HOOKS_DIR = Path(os.getenv("HOOKS_DIR", CURRENT_DIR)).expanduser().resolve()
AGENT_NAME = os.getenv("AGENT_NAME", "Antigravity CLI").strip()

TARGET_NOTIFIER = HOOKS_DIR / "notifier.py"
TARGET_CONFIG = HOOKS_DIR / "config.json"

SOURCE_NOTIFIER = CURRENT_DIR / "notifier.py"
SOURCE_CONFIG = CURRENT_DIR / "config.json"

HOOK_PAYLOAD = {
    "PreToolUse": [
        {
            "matcher": "*",
            "hooks": [
                {
                    "type": "command",
                    "command": f"[ -f '{TARGET_NOTIFIER}' ] && python3 '{TARGET_NOTIFIER}' pre-tool || echo '{{\"decision\": \"allow\"}}'",
                    "timeout": 5
                }
            ]
        }
    ],
    "Stop": [
        {
            "type": "command",
            "command": f"[ -f '{TARGET_NOTIFIER}' ] && python3 '{TARGET_NOTIFIER}' stop || echo '{{\"decision\": \"\"}}'",
            "timeout": 5
        }
    ]
}

def load_hooks():
    if not HOOKS_CONFIG_PATH.exists():
        return {}
    try:
        with open(HOOKS_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {HOOKS_CONFIG_PATH}: {e}")
        return {}

def save_hooks(data):
    HOOKS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HOOKS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def deploy_template(source_path: Path, target_path: Path, agent_name: str):
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()
    rendered = content.replace("{{AGENT_NAME}}", agent_name)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(rendered)

def install():
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)

    deploy_template(SOURCE_NOTIFIER, TARGET_NOTIFIER, AGENT_NAME)
    TARGET_NOTIFIER.chmod(0o755)
    print(f"[Rendered & Deployed] {TARGET_NOTIFIER} (AGENT_NAME='{AGENT_NAME}')")

    deploy_template(SOURCE_CONFIG, TARGET_CONFIG, AGENT_NAME)
    print(f"[Rendered & Deployed] {TARGET_CONFIG} (AGENT_NAME='{AGENT_NAME}')")

    hooks = load_hooks()
    hooks[HOOK_NAME] = HOOK_PAYLOAD
    save_hooks(hooks)
    print(f"[OK] Registered hook '{HOOK_NAME}' in: {HOOKS_CONFIG_PATH}")
    print(f"     Target script: {TARGET_NOTIFIER}")

def uninstall():
    hooks = load_hooks()
    if HOOK_NAME in hooks:
        del hooks[HOOK_NAME]
        save_hooks(hooks)
        print(f"[OK] Removed hook '{HOOK_NAME}' from: {HOOKS_CONFIG_PATH}")
    else:
        print(f"[Info] Hook '{HOOK_NAME}' not found in: {HOOKS_CONFIG_PATH}")

    if TARGET_NOTIFIER.exists():
        TARGET_NOTIFIER.unlink()
        print(f"[Cleaned] Removed {TARGET_NOTIFIER}")

    if TARGET_CONFIG.exists():
        TARGET_CONFIG.unlink()
        print(f"[Cleaned] Removed {TARGET_CONFIG}")

def status():
    hooks = load_hooks()
    print(f"[Config Path] {HOOKS_CONFIG_PATH}")
    print(f"[Hooks Directory] {HOOKS_DIR}")
    print(f"[Agent Name] {AGENT_NAME}")
    print(f"[Deployed Script] {TARGET_NOTIFIER} ({'Found' if TARGET_NOTIFIER.exists() else 'Missing'})")
    print(f"[Deployed Config] {TARGET_CONFIG} ({'Found' if TARGET_CONFIG.exists() else 'Missing'})")
    print(f"[Hook Name] {HOOK_NAME}")
    if HOOK_NAME in hooks:
        print(f"[Status] ACTIVE:")
        print(json.dumps(hooks[HOOK_NAME], indent=2))
    else:
        print(f"[Status] INACTIVE")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "install":
        install()
    elif action == "uninstall":
        uninstall()
    elif action == "status":
        status()
    else:
        print("Usage: python3 manage_hook.py [install|uninstall|status]")
