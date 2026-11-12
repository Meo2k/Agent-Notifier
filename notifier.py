#!/usr/bin/env python3
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        print(f"[Notifier Error] Missing: {CONFIG_FILE}", file=sys.stderr)
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Notifier Error] JSON parse failure in {CONFIG_FILE}: {e}", file=sys.stderr)
        return {}

def trigger_alert(key, custom_message=None):
    cfg = load_config()
    msg_info = cfg.get("messages", {}).get(key, {})

    title = msg_info.get("title", "Antigravity CLI")
    message = custom_message or msg_info.get("message", "")
    voice = msg_info.get("voice", "")
    sound_file = msg_info.get("sound", "")
    urgency = msg_info.get("urgency", "normal")

    if cfg.get("popup_enabled", True) and shutil.which("notify-send"):
        icon_map = {
            "task_completed": "dialog-information",
            "task_error": "dialog-error",
            "question": "dialog-question",
            "permission_needed": "dialog-warning",
        }
        subprocess.Popen(
            [
                "notify-send",
                "-u", urgency,
                "-i", icon_map.get(key, "dialog-information"),
                "-a", "Antigravity CLI",
                title,
                message,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    if cfg.get("sound_enabled", True) and sound_file and os.path.exists(sound_file):
        engine = cfg.get("sound_engine", "paplay")
        if shutil.which(engine):
            subprocess.Popen(
                [engine, sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    if cfg.get("voice_enabled", True) and voice:
        engine = cfg.get("tts_engine", "spd-say")
        if shutil.which(engine):
            subprocess.Popen(
                [engine, "-r", "10", voice],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

def handle_stop(payload):
    reason = payload.get("terminationReason", "")
    err = payload.get("error", "")

    if err or reason == "ERROR":
        trigger_alert("task_error", custom_message=f"Error: {err}" if err else None)
    elif reason not in ("USER_CANCELED",):
        trigger_alert("task_completed")

    return {"decision": ""}

def handle_pre_tool(payload):
    tool_call = payload.get("toolCall", {})
    if tool_call.get("name") == "ask_question":
        questions = tool_call.get("args", {}).get("questions", [])
        q_text = questions[0].get("question", "") if questions and isinstance(questions[0], dict) else ""
        trigger_alert("question", custom_message=f"Question: {q_text}" if q_text else None)

    return {"decision": "allow"}

def main():
    if len(sys.argv) > 1 and sys.argv[1].startswith("--test"):
        test_type = sys.argv[2] if len(sys.argv) > 2 else "task_completed"
        trigger_alert(test_type)
        return

    action = sys.argv[1] if len(sys.argv) > 1 else ""
    payload = {}
    if not sys.stdin.isatty():
        try:
            content = sys.stdin.read().strip()
            if content:
                payload = json.loads(content)
        except Exception:
            pass

    if action == "stop":
        response = handle_stop(payload)
    elif action == "pre-tool":
        response = handle_pre_tool(payload)
    else:
        response = {"decision": "allow"}

    print(json.dumps(response))

if __name__ == "__main__":
    main()
