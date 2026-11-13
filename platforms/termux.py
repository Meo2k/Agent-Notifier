import os
import shutil
import subprocess
from .base import BasePlatformNotifier

class TermuxNotifier(BasePlatformNotifier):
    """
    Termux (Android) notifier implementation using termux-api:
    - termux-notification / termux-toast for popups
    - termux-media-player / termux-vibrate for sound and haptics
    - termux-tts-speak for Text-to-Speech
    """

    def show_popup(self, title: str, message: str, urgency: str = "normal", key: str = "") -> None:
        if shutil.which("termux-notification"):
            priority = "high" if urgency == "critical" else "default"
            cmd = [
                "termux-notification",
                "--title", title,
                "--content", message,
                "--priority", priority,
            ]
            if urgency == "critical":
                cmd.extend(["--vibrate", "200,100,200"])
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        elif shutil.which("termux-toast"):
            subprocess.Popen(
                ["termux-toast", f"{title}: {message}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    def play_sound(self, sound_file: str) -> None:
        if sound_file and os.path.exists(sound_file) and shutil.which("termux-media-player"):
            subprocess.Popen(
                ["termux-media-player", "play", sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        elif shutil.which("termux-vibrate"):
            # Haptic vibration fallback
            subprocess.Popen(
                ["termux-vibrate", "-d", "150"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    def speak_text(self, text: str) -> None:
        if not text:
            return

        if shutil.which("termux-tts-speak"):
            subprocess.Popen(
                ["termux-tts-speak", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
