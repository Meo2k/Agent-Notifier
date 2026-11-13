#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from detector_manager import DetectorManager

SCRIPT_DIR = Path(__file__).resolve().parent

# Initialize platform-specific notifier through DetectorManager
manager = DetectorManager(base_dir=SCRIPT_DIR)
notifier = manager.get_notifier()

def trigger_alert(key, custom_message=None):
    notifier.trigger_alert(key, custom_message=custom_message)

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
    name = tool_call.get("name", "")
    args = tool_call.get("args", {})
    workspace_paths = payload.get("workspacePaths", [])

    if name == "ask_question":
        questions = args.get("questions", [])
        q_text = questions[0].get("question", "") if questions and isinstance(questions[0], dict) else ""
        trigger_alert("question", custom_message=f"Question: {q_text}" if q_text else None)
        return {"decision": "allow"}

    path_arg = args.get("Path")
    if path_arg and workspace_paths:
        try:
            target = Path(path_arg).resolve()
            is_outside = True
            for wp in workspace_paths:
                try:
                    target.relative_to(Path(wp).resolve())
                    is_outside = False
                    break
                except ValueError:
                    pass
            if is_outside:
                trigger_alert("permission_needed", custom_message=f"Outside workspace: {path_arg}")
                return {"decision": "ask", "reason": f"Access outside workspace: {path_arg}"}
        except Exception:
            pass

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
