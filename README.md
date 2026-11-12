# Agent CLI Notifier

Audio alerts and desktop popups for Agent CLI lifecycle events. <br/>
**<u>Note</u>**: the notifier can use for different models. 

## Components

- `.env`: Path, hooks destination directory, hook name, and agent title.
- `config.json`: Master notification template with `{{AGENT_NAME}}`.
- `notifier.py`: Core hook event consumer template.
- `manage_hook.py`: Hook deployment, templating, and registration utility.
- `test_sound.sh` / `test_popup.sh` / `simulate_hooks.sh`: Testing scripts.

## Environment (`.env`)

```env
HOOKS_CONFIG_PATH=~/.gemini/config/hooks.json
HOOKS_DIR=~/.gemini/config/hooks/notifier
HOOK_NAME=antigravity-notifier
AGENT_NAME=Antigravity CLI
```

## Usage

```bash
# install hook
python3 manage_hook.py install

# inspect status
python3 manage_hook.py status

# remove the hook
python3 manage_hook.py uninstall
```

## Testing

```bash
./test_sound.sh
./test_popup.sh
./simulate_hooks.sh
```
