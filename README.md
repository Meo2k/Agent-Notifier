# Agent CLI Notifier

Audio alerts, TTS voice announcements, and desktop/mobile popups for Agent CLI lifecycle events across **Linux**, **Windows**, **macOS**, and **Termux (Android)**. <br/>
**<u>Note</u>**: the notifier can be used for different models and agents.

## Architecture

```text
Agent-Notifier/
├── configs/
│   ├── linux.json            # Linux-specific audio/TTS settings
│   ├── windows.json          # Windows-specific audio/TTS settings (SAPI / winsound)
│   ├── macos.json            # macOS-specific audio/TTS settings (say / afplay)
│   └── termux.json           # Termux (Android) audio/TTS settings (termux-api)
├── platforms/
│   ├── base.py               # Abstract Base Class (BasePlatformNotifier)
│   ├── linux.py              # Linux concrete notifier (notify-send, paplay, spd-say)
│   ├── windows.py            # Windows concrete notifier (PowerShell SAPI, winsound)
│   ├── macos.py              # macOS concrete notifier (osascript, afplay, say)
│   └── termux.py             # Termux notifier (termux-notification, termux-tts-speak)
├── detector_manager.py       # OS detector & factory manager (handles hook command generation)
├── notifier.py               # Core hook event consumer
├── manage_hook.py            # Cross-platform interactive hook installer & manager
├── .env.example              # Example environment reference
└── test scripts...
```

## Supported Platforms

| Platform | Notifications / Popup | Text-to-Speech (TTS) | Sound / Haptics |
| :--- | :--- | :--- | :--- |
| **Windows** | NotifyIcon / Balloon Tip | PowerShell System.Speech (SAPI) | `winsound` / SoundPlayer |
| **Linux** | `notify-send` | `spd-say` | `paplay` / `aplay` |
| **macOS** | `osascript` notification | `say` | `afplay` |
| **Termux (Android)** | `termux-notification` / `termux-toast` | `termux-tts-speak` (Android TTS) | `termux-media-player` / `termux-vibrate` |

## Usage

### 1. Installation
Install hooks interactively from the console (press Enter to use defaults):
```bash
python manage_hook.py install
```
*(Optional: Use `-y` or `--yes` to accept all default parameters automatically without prompting)*
```bash
python manage_hook.py install -y
```

### 2. Inspect Status
```bash
python manage_hook.py status
```

### 3. Uninstall
```bash
python manage_hook.py uninstall
```

## Testing

```bash
# Test alert directly via notifier
python notifier.py --test task_completed
python notifier.py --test question
python notifier.py --test task_error

# Shell simulation scripts (Linux / macOS / Termux)
./test_sound.sh
./test_popup.sh
./simulate_hooks.sh
```
