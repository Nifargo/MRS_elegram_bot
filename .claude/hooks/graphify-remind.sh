#!/bin/bash
# Reminds Claude to run /graphify --update after a commit touches docs/papers/images.
# The post-commit git hook (graphify hook install) sets graphify-out/needs_update
# when a commit contains non-code files it can't re-extract without an LLM.
# Used as a PostToolUse hook for Bash.

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

case "$CMD" in
  *git\ commit*) ;;
  *) exit 0 ;;
esac

if ! command -v graphify >/dev/null 2>&1; then
  exit 0
fi

ROOT="$CLAUDE_PROJECT_DIR"
if [ -f "$ROOT/graphify-out/.graphify_root" ]; then
  ROOT=$(cat "$ROOT/graphify-out/.graphify_root")
fi

OUTPUT=$(graphify check-update "$ROOT" 2>/dev/null)

if [ -n "$OUTPUT" ]; then
  cat <<EOF
<system-reminder>
$OUTPUT
Запусти /graphify --update, щоб додати ці зміни в граф (семантичне переоновлення документів/не-кодових файлів).
</system-reminder>
EOF
fi

exit 0