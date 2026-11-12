# Agent CLI Notifier

Audio alerts and desktop popups for Agent CLI lifecycle events.

## Components

- `.env`: Path and hook name configuration.
- `config.json`: Master notification settings. You can modify it to suit for your system 
- `notifier.py`: Core hook event consumer.
- `manage_hook.py`: Hook registration utility.
- `test_sound.sh` / `test_popup.sh` / `simulate_hooks.sh`: Testing scripts.

## Usage

```bash
# Register hook
python3 manage_hook.py install

# Check status
python3 manage_hook.py status

# Remove hook
python3 manage_hook.py uninstall
```

## Testing

```bash
./test_sound.sh
./test_popup.sh
./simulate_hooks.sh
```
