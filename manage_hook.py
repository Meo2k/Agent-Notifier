#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
ENV_FILE = CURRENT_DIR / ".env"
NOTIFIER_SCRIPT = CURRENT_DIR / "notifier.py"

load_dotenv(dotenv_path=ENV_FILE)

HOOKS_CONFIG_PATH = Path(os.getenv("HOOKS_CONFIG_PATH", "~/.gemini/config/hooks.json")).expanduser().resolve()
HOOK_NAME = os.getenv("HOOK_NAME", "antigravity-notifier")

HOOK_PAYLOAD = {
    "PreToolUse": [
        {
            "matcher": "ask_question",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 '{NOTIFIER_SCRIPT}' pre-tool",
                    "timeout": 5
                }
            ]
        }
    ],
    "Stop": [
        {
            "type": "command",
            "command": f"python3 '{NOTIFIER_SCRIPT}' stop",
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

def install():
    hooks = load_hooks()
    hooks[HOOK_NAME] = HOOK_PAYLOAD
    save_hooks(hooks)
    print(f"[OK] Registered hook '{HOOK_NAME}' in: {HOOKS_CONFIG_PATH}")

def uninstall():
    hooks = load_hooks()
    if HOOK_NAME in hooks:
        del hooks[HOOK_NAME]
        save_hooks(hooks)
        print(f"[OK] Removed hook '{HOOK_NAME}' from: {HOOKS_CONFIG_PATH}")
    else:
        print(f"[Info] Hook '{HOOK_NAME}' not found in: {HOOKS_CONFIG_PATH}")

def status():
    hooks = load_hooks()
    print(f"[Config Source] {HOOKS_CONFIG_PATH}")
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
