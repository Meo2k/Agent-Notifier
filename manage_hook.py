#!/usr/bin/env python3
import os
import sys
import json
import shutil
from pathlib import Path
from detector_manager import DetectorManager

CURRENT_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG_PATH = "~/.gemini/config/hooks.json"
DEFAULT_HOOKS_DIR = "~/.gemini/config/hooks/notifier"
DEFAULT_HOOK_NAME = "antigravity-notifier"
DEFAULT_AGENT_NAME = "Antigravity CLI"

def prompt_input(label: str, default_val: str) -> str:
    """Prompt user for input in console with a default value fallback."""
    try:
        user_val = input(f"{label} [{default_val}]: ").strip()
        return user_val if user_val else default_val
    except (EOFError, KeyboardInterrupt):
        print("\n[Canceled] Operation aborted by user.")
        sys.exit(1)

def load_hooks(config_path: Path):
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return {}

def save_hooks(config_path: Path, data: dict):
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def deploy_template(source_path: Path, target_path: Path, agent_name: str):
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()
    rendered = content.replace("{{AGENT_NAME}}", agent_name)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(rendered)

def deploy_dir_templates(source_dir: Path, target_dir: Path, agent_name: str):
    target_dir.mkdir(parents=True, exist_ok=True)
    for root, _, files in os.walk(source_dir):
        rel_root = Path(root).relative_to(source_dir)
        dest_root = target_dir / rel_root
        dest_root.mkdir(parents=True, exist_ok=True)
        for file in files:
            src_file = Path(root) / file
            dst_file = dest_root / file
            if file.endswith((".json", ".py", ".md")):
                deploy_template(src_file, dst_file, agent_name)
            else:
                shutil.copy2(src_file, dst_file)

def install(auto_confirm: bool = False):
    print("=== Antigravity Hook Installation ===")
    if auto_confirm:
        agent_name = DEFAULT_AGENT_NAME
        hook_name = DEFAULT_HOOK_NAME
        hooks_config_path_raw = DEFAULT_CONFIG_PATH
        hooks_dir_raw = DEFAULT_HOOKS_DIR
    else:
        agent_name = prompt_input("Enter Agent Name", DEFAULT_AGENT_NAME)
        hook_name = prompt_input("Enter Hook Name", DEFAULT_HOOK_NAME)
        hooks_config_path_raw = prompt_input("Enter Hooks Config Path", DEFAULT_CONFIG_PATH)
        hooks_dir_raw = prompt_input("Enter Hooks Destination Directory", DEFAULT_HOOKS_DIR)

    hooks_config_path = Path(hooks_config_path_raw).expanduser().resolve()
    hooks_dir = Path(hooks_dir_raw).expanduser().resolve()

    target_notifier = hooks_dir / "notifier.py"
    target_detector = hooks_dir / "detector_manager.py"
    target_platforms = hooks_dir / "platforms"
    target_configs = hooks_dir / "configs"
    target_config = hooks_dir / "config.json"

    source_notifier = CURRENT_DIR / "notifier.py"
    source_detector = CURRENT_DIR / "detector_manager.py"
    source_platforms = CURRENT_DIR / "platforms"
    source_configs = CURRENT_DIR / "configs"
    source_config = CURRENT_DIR / "config.json"

    hooks_dir.mkdir(parents=True, exist_ok=True)

    deploy_template(source_notifier, target_notifier, agent_name)
    try:
        target_notifier.chmod(0o755)
    except Exception:
        pass
    print(f"[Deployed] {target_notifier} (AGENT_NAME='{agent_name}')")

    if source_detector.exists() and hooks_dir != CURRENT_DIR:
        deploy_template(source_detector, target_detector, agent_name)
        print(f"[Deployed] {target_detector}")

    if source_platforms.exists() and hooks_dir != CURRENT_DIR:
        deploy_dir_templates(source_platforms, target_platforms, agent_name)
        print(f"[Deployed] {target_platforms}")

    if source_configs.exists() and hooks_dir != CURRENT_DIR:
        deploy_dir_templates(source_configs, target_configs, agent_name)
        print(f"[Deployed] {target_configs}")

    if source_config.exists() and hooks_dir != CURRENT_DIR:
        deploy_template(source_config, target_config, agent_name)
        print(f"[Deployed] {target_config}")

    # Generate OS-compatible payload via DetectorManager
    detector = DetectorManager(base_dir=CURRENT_DIR)
    hook_payload = detector.get_hook_payload(target_notifier)

    hooks = load_hooks(hooks_config_path)
    hooks[hook_name] = hook_payload
    save_hooks(hooks_config_path, hooks)
    print(f"[OK] Registered hook '{hook_name}' in: {hooks_config_path}")
    print(f"     Target script: {target_notifier}")
    print(f"     Detected Environment: {detector.os_name.upper()}")

def uninstall(auto_confirm: bool = False):
    print("=== Hook Uninstallation ===")
    if auto_confirm:
        hook_name = DEFAULT_HOOK_NAME
        hooks_config_path_raw = DEFAULT_CONFIG_PATH
        hooks_dir_raw = DEFAULT_HOOKS_DIR
    else:
        hook_name = prompt_input("Enter Hook Name to remove", DEFAULT_HOOK_NAME)
        hooks_config_path_raw = prompt_input("Enter Hooks Config Path", DEFAULT_CONFIG_PATH)
        hooks_dir_raw = prompt_input("Enter Hooks Directory to clean (or press Enter to skip files)", DEFAULT_HOOKS_DIR)

    hooks_config_path = Path(hooks_config_path_raw).expanduser().resolve()
    hooks_dir = Path(hooks_dir_raw).expanduser().resolve() if hooks_dir_raw else None

    hooks = load_hooks(hooks_config_path)
    if hook_name in hooks:
        del hooks[hook_name]
        save_hooks(hooks_config_path, hooks)
        print(f"[OK] Removed hook '{hook_name}' from: {hooks_config_path}")
    else:
        print(f"[Info] Hook '{hook_name}' not found in: {hooks_config_path}")

    if hooks_dir and hooks_dir.exists() and hooks_dir != CURRENT_DIR:
        for file_name in ["notifier.py", "detector_manager.py", "config.json"]:
            file_path = hooks_dir / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"[Cleaned] Removed {file_path}")
        for dir_name in ["platforms", "configs"]:
            dir_path = hooks_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"[Cleaned] Removed {dir_path}")

def status(auto_confirm: bool = True):
    hooks_config_path = Path(DEFAULT_CONFIG_PATH).expanduser().resolve()
    hooks = load_hooks(hooks_config_path)
    detector = DetectorManager(base_dir=CURRENT_DIR)

    print(f"[Config Path] {hooks_config_path}")
    print(f"[Detected Environment] {detector.os_name.upper()}")
    print(f"[Default Hook Name] {DEFAULT_HOOK_NAME}")
    if DEFAULT_HOOK_NAME in hooks:
        print(f"[Status] ACTIVE:")
        print(json.dumps(hooks[DEFAULT_HOOK_NAME], indent=2))
    else:
        print(f"[Status] INACTIVE")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    auto_flag = "-y" in sys.argv or "--yes" in sys.argv

    if action == "install":
        install(auto_confirm=auto_flag)
    elif action == "uninstall":
        uninstall(auto_confirm=auto_flag)
    elif action == "status":
        status(auto_confirm=auto_flag)
    else:
        print("Usage: python manage_hook.py [install|uninstall|status] [-y|--yes]")
