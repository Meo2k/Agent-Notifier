# Antigravity CLI Notifier

Audio alerts and desktop popups for Antigravity CLI lifecycle events.

## Components

- `.env`: Path, hooks destination directory, hook name, and agent title.
- `config.json`: Master notification template with `{{AGENT_NAME}}`.
- `notifier.py`: Core hook event consumer template.
- `manage_hook.py`: Hook deployment, templating, and registration utility.
- `test_sound.sh` / `test_popup.sh` / `simulate_hooks.sh`: Testing scripts.

## Environment (`.env`)

```env
HOOKS_CONFIG_PATH=/home/meo2k/.gemini/config/hooks.json
HOOKS_DIR=/home/meo2k/.gemini/config/hooks/notifier
HOOK_NAME=antigravity-notifier
AGENT_NAME=Antigravity CLI
```

## Usage

```bash
# Renders {{AGENT_NAME}} into notifier.py and config.json, deploys to HOOKS_DIR, and registers fail-safe hooks
python3 manage_hook.py install

# Inspect status and verify deployed files
python3 manage_hook.py status

# Unregisters from hooks.json and cleans deployed files
python3 manage_hook.py uninstall
```

## Testing

```bash
./test_sound.sh
./test_popup.sh
./simulate_hooks.sh
```
