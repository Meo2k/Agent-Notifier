import os
import sys
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from platforms.base import BasePlatformNotifier
from platforms.linux import LinuxNotifier
from platforms.windows import WindowsNotifier
from platforms.macos import MacOSNotifier

class DetectorManager:
    """
    Detects the host operating system / environment, loads the appropriate configuration,
    returns the concrete notifier, and generates platform-compatible hook commands.
    """

    PLATFORM_MAP = {
        "linux": LinuxNotifier,
        "windows": WindowsNotifier,
        "macos": MacOSNotifier,
    }

    def __init__(self, base_dir: Optional[Path] = None, force_os: Optional[str] = None):
        self.base_dir = Path(base_dir).resolve() if base_dir else Path(__file__).resolve().parent
        self.os_name = force_os or self.detect_os()

    @staticmethod
    def detect_os() -> str:
        """
        Detects operating system:
        'windows', 'macos', or 'linux'.
        """
        system = platform.system().lower()
        if system == "windows" or sys.platform.startswith("win"):
            return "windows"
        elif system == "darwin" or sys.platform == "darwin":
            return "macos"
        else:
            return "linux"

    def get_config_path(self) -> Path:
        """
        Resolves the configuration file for the detected environment:
        1. configs/{os_name}.json
        2. config.{os_name}.json
        3. config.json (root fallback)
        """
        os_config = self.base_dir / "configs" / f"{self.os_name}.json"
        if os_config.exists():
            return os_config

        flat_config = self.base_dir / f"config.{self.os_name}.json"
        if flat_config.exists():
            return flat_config

        return self.base_dir / "config.json"

    def load_config(self) -> Dict[str, Any]:
        """
        Reads and parses the JSON configuration file.
        """
        config_path = self.get_config_path()
        if not config_path.exists():
            print(f"[DetectorManager Warning] Config file not found at: {config_path}", file=sys.stderr)
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DetectorManager Error] Failed parsing JSON from {config_path}: {e}", file=sys.stderr)
            return {}

    def get_notifier(self, custom_config: Optional[Dict[str, Any]] = None) -> BasePlatformNotifier:
        """
        Factory method returning a BasePlatformNotifier instance for the detected OS.
        """
        config = custom_config if custom_config is not None else self.load_config()
        notifier_class = self.PLATFORM_MAP.get(self.os_name, LinuxNotifier)
        return notifier_class(config=config)

    def get_python_cmd(self) -> str:
        """
        Determines the appropriate python command name for the OS.
        """
        if self.os_name == "windows":
            return "python"
        return "python3"

    def get_hook_commands(self, target_notifier: Path) -> Tuple[str, str]:
        """
        Generates platform-compatible hook shell commands for PreToolUse and Stop.
        """
        py_cmd = self.get_python_cmd()

        if self.os_name == "windows":
            target_str = str(target_notifier)
            pre_tool_cmd = (
                f'if exist "{target_str}" '
                f'({py_cmd} "{target_str}" pre-tool) '
                f'else (echo {{"decision": "allow"}})'
            )
            stop_cmd = (
                f'if exist "{target_str}" '
                f'({py_cmd} "{target_str}" stop) '
                f'else (echo {{"decision": ""}})'
            )
        else:
            target_str = target_notifier.as_posix()
            pre_tool_cmd = (
                f"[ -f '{target_str}' ] && {py_cmd} '{target_str}' pre-tool "
                f'|| echo \'{{"decision": "allow"}}\''
            )
            stop_cmd = (
                f"[ -f '{target_str}' ] && {py_cmd} '{target_str}' stop "
                f'|| echo \'{{"decision": ""}}\''
            )

        return pre_tool_cmd, stop_cmd

    def get_hook_payload(self, target_notifier: Path) -> Dict[str, Any]:
        """
        Generates full hook payload dictionary for hooks.json registration.
        """
        pre_tool_cmd, stop_cmd = self.get_hook_commands(target_notifier)
        return {
            "PreToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": pre_tool_cmd,
                            "timeout": 5
                        }
                    ]
                }
            ],
            "Stop": [
                {
                    "type": "command",
                    "command": stop_cmd,
                    "timeout": 5
                }
            ]
        }
