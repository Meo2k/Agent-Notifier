from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlatformNotifier(ABC):
    """
    Abstract Base Class for OS-specific notifiers.
    All platform implementations (Linux, Windows, macOS) must implement these methods.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def show_popup(self, title: str, message: str, urgency: str = "normal", key: str = "") -> None:
        """Display a desktop popup / toast notification."""
        pass

    @abstractmethod
    def play_sound(self, sound_file: str) -> None:
        """Play an alert sound file."""
        pass

    @abstractmethod
    def speak_text(self, text: str) -> None:
        """Perform Text-to-Speech (TTS) announcement."""
        pass

    def trigger_alert(self, key: str, custom_message: Optional[str] = None) -> None:
        """
        Coordinates alert delivery (popup, sound, voice) according to config.
        """
        msg_info = self.config.get("messages", {}).get(key, {})
        title = msg_info.get("title", "{{AGENT_NAME}}")
        message = custom_message or msg_info.get("message", "")
        voice = msg_info.get("voice", "")
        sound_file = msg_info.get("sound", "")
        urgency = msg_info.get("urgency", "normal")

        if self.config.get("popup_enabled", True) and (title or message):
            self.show_popup(title=title, message=message, urgency=urgency, key=key)

        if self.config.get("sound_enabled", True) and sound_file:
            self.play_sound(sound_file)

        if self.config.get("voice_enabled", True) and voice:
            self.speak_text(voice)
