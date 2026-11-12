#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Stop - Task completed
cat << 'EOF' | python3 "$DIR/notifier.py" stop
{
  "executionNum": 1,
  "terminationReason": "NO_TOOL_CALL",
  "error": "",
  "fullyIdle": true,
  "hookEventName": "Stop"
}
EOF

sleep 2

# 2. PreToolUse - Ask question
cat << 'EOF' | python3 "$DIR/notifier.py" pre-tool
{
  "toolCall": {
    "name": "ask_question",
    "args": {
      "questions": [{ "question": "Would you like to proceed?" }]
    }
  },
  "hookEventName": "PreToolUse"
}
EOF

sleep 2

# 3. Stop - Error
cat << 'EOF' | python3 "$DIR/notifier.py" stop
{
  "executionNum": 1,
  "terminationReason": "ERROR",
  "error": "Execution timed out",
  "fullyIdle": true,
  "hookEventName": "Stop"
}
EOF
