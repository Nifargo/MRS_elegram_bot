#!/bin/bash
# ══════════════════════════════════════════════════════════════════════
# Claude Code PreToolUse Hook — Combined Bash Command Protection
# ══════════════════════════════════════════════════════════════════════
# Blocks dangerous shell commands before execution.
# Merges two hooks:
#   • Hook 1: git workflow, databases, package publishing, system commands
#   • Hook 2: aggressive rm protection, critical paths, fork bomb
#
# Exit 2 = block the action
# Exit 0 = allow
# ══════════════════════════════════════════════════════════════════════

# Requires jq for JSON parsing — fail closed if missing
if ! command -v jq >/dev/null 2>&1; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"jq is required for command protection hooks but is not installed."}}' >&2
  exit 2
fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

deny() {
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$1\"}}"
  exit 2
}

# ──────────────────────────────────────────────
# 1. GIT PROTECTIONS
# ──────────────────────────────────────────────

# Detect git push (handles chaining with &&, ;, |, subshells)
if echo "$COMMAND" | grep -qE '(^|[;&|()]+[[:space:]]*)git[[:space:]]+push'; then

  # Block push to main or master
  if echo "$COMMAND" | grep -qE 'git[[:space:]]+push.*(origin[[:space:]]+|:)(main|master)\b'; then
    deny "Blocked: cannot push directly to main/master. Use a feature branch and create a PR."
  fi

  # Block bare 'git push' when on main/master
  if echo "$COMMAND" | grep -qE 'git[[:space:]]+push[[:space:]]*($|[;&|])'; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
      deny "Blocked: you are on $CURRENT_BRANCH. Use a feature branch and create a PR."
    fi
  fi

  # Block force push (allow --force-with-lease)
if echo "$COMMAND" | grep -qE 'git[[:space:]]+push.*[[:space:]](-[a-zA-Z]*f|--force)([[:space:]]|$)' && \
     ! echo "$COMMAND" | grep -q '\-\-force-with-lease'; then
    deny "Blocked: force push is not allowed. Use --force-with-lease if you need to overwrite remote."
  fi
fi

# Block git reset --hard (loses uncommitted work permanently)
if echo "$COMMAND" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard'; then
  deny "Blocked: git reset --hard discards uncommitted changes permanently. Use git stash or git reset --soft instead."
fi

# Block git clean -f (permanently deletes untracked files)
if echo "$COMMAND" | grep -qE 'git[[:space:]]+clean[[:space:]]+-[a-zA-Z]*f'; then
  deny "Blocked: git clean -f permanently deletes untracked files. Review with git clean -n first, then run manually."
fi

# ──────────────────────────────────────────────
# 2. DESTRUCTIVE FILESYSTEM OPERATIONS
# ──────────────────────────────────────────────

# Block ANY rm with both recursive + force flags (rm -rf, rm -fr, rm -Rf, --recursive --force, etc.)
if echo "$COMMAND" | grep -qE '(^|[;&|]\s*)rm\s+' && \
   echo "$COMMAND" | grep -qE '[[:space:]](-[a-zA-Z]*r[a-zA-Z]*|--recursive)([[:space:]]|$)' && \
   echo "$COMMAND" | grep -qE '[[:space:]](-[a-zA-Z]*f[a-zA-Z]*|--force)([[:space:]]|$)'; then
  deny "Blocked: rm with both recursive and force flags is not allowed. Use 'rm -r <path>' without -f so you get prompted."
fi

# Block rm on critical system/project paths (even without -rf)
CRITICAL_PATHS=(
  "/"
  "/home"
  "/etc"
  "/var"
  "/usr"
  "/tmp"
  "/root"
  ".git"
  "node_modules"
  ".env"
  "\$HOME"
  "~"
  "../.."
)

for cpath in "${CRITICAL_PATHS[@]}"; do
  escaped=$(printf '%s' "$cpath" | sed 's/[.[\*^$()+?{|]/\\&/g')
  if echo "$COMMAND" | grep -qE "rm\s+.*(^|\s|/)${escaped}(\s|/|$)"; then
    deny "Blocked: rm targeting critical path '${cpath}' is not allowed. Specify a safe target directory."
  fi
done

# ──────────────────────────────────────────────
# 3. DANGEROUS DATABASE OPERATIONS
# ──────────────────────────────────────────────

# Block DROP TABLE/DATABASE/SCHEMA
if echo "$COMMAND" | grep -qiE 'DROP[[:space:]]+(TABLE|DATABASE|SCHEMA)[[:space:]]'; then
  deny "Blocked: DROP TABLE/DATABASE/SCHEMA detected. This is destructive and irreversible. Run manually if intended."
fi

# Block DELETE FROM without WHERE
if echo "$COMMAND" | grep -qiE 'DELETE[[:space:]]+FROM[[:space:]]+[a-zA-Z_]+[[:space:]]*($|;)' && \
   ! echo "$COMMAND" | grep -qiE 'WHERE'; then
  deny "Blocked: DELETE FROM without WHERE clause would delete all rows. Add a WHERE clause."
fi

# Block TRUNCATE TABLE
if echo "$COMMAND" | grep -qiE 'TRUNCATE[[:space:]]+TABLE'; then
  deny "Blocked: TRUNCATE TABLE detected. This is destructive and irreversible. Run manually if intended."
fi

# ──────────────────────────────────────────────
# 4. DANGEROUS SYSTEM COMMANDS
# ──────────────────────────────────────────────

# Block chmod 777
if echo "$COMMAND" | grep -qE 'chmod[[:space:]]+777'; then
  deny "Blocked: chmod 777 gives everyone read/write/execute. Use more restrictive permissions (e.g., 755 or 644)."
fi

# Block recursive chmod/chown on root
if echo "$COMMAND" | grep -qE '(^|[;&|]\s*)(chmod|chown)\s+.*-R\s+.*\s+/\s*$'; then
  deny "Blocked: recursive chmod/chown on '/' is not allowed."
fi

# Block piping curl/wget to shell execution
if echo "$COMMAND" | grep -qE '(curl|wget)[[:space:]].*\|[[:space:]]*(bash|sh|zsh|sudo)'; then
  deny "Blocked: piping downloaded content directly to a shell is dangerous. Download first, inspect, then execute."
fi

# Block mkfs (format filesystem)
if echo "$COMMAND" | grep -qE '(^|[;&|]\s*)mkfs'; then
  deny "Blocked: mkfs (format filesystem) is not allowed."
fi

# Block dd writing to block devices
if echo "$COMMAND" | grep -qE '(^|[;&|]\s*)dd\s+.*of=/dev/'; then
  deny "Blocked: dd writing to block devices is not allowed."
fi

# Block dd with if= (reading raw devices — also dangerous)
if echo "$COMMAND" | grep -qE 'dd[[:space:]]+if='; then
  deny "Blocked: destructive disk operation detected (dd if=). This can cause irreversible data loss."
fi

# Block writing directly to block devices via redirect
if echo "$COMMAND" | grep -qE '>\s*/dev/(sd[a-z]|nvme|vd[a-z]|xvd[a-z])'; then
  deny "Blocked: writing directly to block device is not allowed."
fi

# Block fork bomb pattern :(){:|:&};:
if echo "$COMMAND" | grep -qE ':\(\)\s*\{'; then
  deny "Blocked: fork bomb pattern detected."
fi

# ──────────────────────────────────────────────
# 5. ACCIDENTAL PACKAGE PUBLISHING
# ──────────────────────────────────────────────

if echo "$COMMAND" | grep -qE '(npm|yarn|pnpm|bun)[[:space:]]+publish'; then
  deny "Blocked: publishing npm packages should be done manually or via CI, not through Claude Code."
fi

if echo "$COMMAND" | grep -qE 'cargo[[:space:]]+publish'; then
  deny "Blocked: publishing crates should be done manually or via CI, not through Claude Code."
fi

if echo "$COMMAND" | grep -qE 'gem[[:space:]]+push'; then
  deny "Blocked: publishing gems should be done manually or via CI, not through Claude Code."
fi

if echo "$COMMAND" | grep -qE 'twine[[:space:]]+upload'; then
  deny "Blocked: publishing Python packages should be done manually or via CI, not through Claude Code."
fi

if echo "$COMMAND" | grep -qE 'pip[[:space:]]+upload'; then
  deny "Blocked: publishing Python packages should be done manually or via CI, not through Claude Code."
fi

exit 0