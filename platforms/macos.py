import os
import shutil
import subprocess
from .base import BasePlatformNotifier

class MacOSNotifier(BasePlatformNotifier):
    """
    macOS notifier implementation using osascript notifications, afplay, and say.
    """

    def show_popup(self, title: str, message: str, urgency: str = "normal", key: str = "") -> None:
        if not shutil.which("osascript"):
            return

        escaped_title = title.replace('"', '\\"')
        escaped_msg = message.replace('"', '\\"')
        script = f'display notification "{escaped_msg}" with title "{escaped_title}"'
        subprocess.Popen(
            ["osascript", "-e", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def play_sound(self, sound_file: str) -> None:
        if not (sound_file and os.path.exists(sound_file)):
            return

        engine = self.config.get("sound_engine", "afplay")
        if shutil.which(engine):
            subprocess.Popen(
                [engine, sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    def speak_text(self, text: str) -> None:
        if not text:
            return

        engine = self.config.get("tts_engine", "say")
        if shutil.which(engine):
            subprocess.Popen(
                [engine, text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
