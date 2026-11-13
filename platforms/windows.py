import os
import shutil
import subprocess
from .base import BasePlatformNotifier

class WindowsNotifier(BasePlatformNotifier):
    """
    Windows notifier implementation using PowerShell System.Speech, winsound, and Windows notifications.
    """

    def show_popup(self, title: str, message: str, urgency: str = "normal", key: str = "") -> None:
        if shutil.which("notify-send"):
            subprocess.Popen(
                ["notify-send", title, message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return

        # Fallback to Windows notification via PowerShell NotifyIcon
        escaped_title = title.replace("'", "''")
        escaped_msg = message.replace("'", "''")
        ps_script = (
            "[void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms');"
            "$notify = New-Object System.Windows.Forms.NotifyIcon;"
            "$notify.Icon = [System.Drawing.SystemIcons]::Information;"
            "$notify.Visible = $True;"
            f"$notify.ShowBalloonTip(4000, '{escaped_title}', '{escaped_msg}', [System.Windows.Forms.ToolTipIcon]::Info)"
        )
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

    def play_sound(self, sound_file: str) -> None:
        if not (sound_file and os.path.exists(sound_file)):
            return

        engine = self.config.get("sound_engine", "winsound")
        if engine == "winsound" or sound_file.lower().endswith(".wav"):
            try:
                import winsound
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except Exception:
                pass

        # Fallback to PowerShell SoundPlayer
        escaped_path = sound_file.replace("'", "''")
        ps_cmd = f"(New-Object Media.SoundPlayer '{escaped_path}').PlaySync()"
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

    def speak_text(self, text: str) -> None:
        if not text:
            return

        escaped_voice = text.replace("'", "''")
        ps_cmd = (
            f"Add-Type -AssemblyName System.Speech; "
            f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{escaped_voice}')"
        )
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
