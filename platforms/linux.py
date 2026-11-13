import os
import shutil
import subprocess
from .base import BasePlatformNotifier

class LinuxNotifier(BasePlatformNotifier):
    """
    Linux notifier implementation using notify-send, paplay/aplay, and spd-say.
    """

    def show_popup(self, title: str, message: str, urgency: str = "normal", key: str = "") -> None:
        if not shutil.which("notify-send"):
            return

        icon_map = {
            "task_completed": "dialog-information",
            "task_error": "dialog-error",
            "question": "dialog-question",
            "permission_needed": "dialog-warning",
        }
        icon = icon_map.get(key, "dialog-information")

        subprocess.Popen(
            [
                "notify-send",
                "-u", urgency,
                "-i", icon,
                "-a", "{{AGENT_NAME}}",
                title,
                message,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def play_sound(self, sound_file: str) -> None:
        if not (sound_file and os.path.exists(sound_file)):
            return

        engine = self.config.get("sound_engine", "paplay")
        if shutil.which(engine):
            subprocess.Popen(
                [engine, sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        elif shutil.which("aplay"):
            subprocess.Popen(
                ["aplay", sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    def speak_text(self, text: str) -> None:
        if not text:
            return

        engine = self.config.get("tts_engine", "spd-say")
        if shutil.which(engine):
            cmd = [engine, "-r", "10", text] if engine == "spd-say" else [engine, text]
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
