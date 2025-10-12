#!/usr/bin/env bash
# version_check.sh — recursive version header updater for sh/zsh/py
# - Recursively finds tracked *.sh, *.zsh, *.py (respects .gitignore)
# - Ensures a header block with Author / Date / Version
# - Bumps Version (simple MAJOR.MINOR scheme) if header already present
# - For Python: ensures __version__ exists and is kept in sync with header
# Compatible with macOS (BSD sed) and Linux (GNU sed)

set -euo pipefail

AUTHOR="Jon Brown"
TODAY="$(date +%Y-%m-%d)"

# sed -i helper using *extended regex* (-E) on both GNU and BSD sed
sedi() {
  if sed --version >/dev/null 2>&1; then
    sed -E -i "$@"
  else
    sed -E -i '' "$@"
  fi
}

# Simple bump for MAJOR.MINOR (defaults to 0.1 on first insert; rolls minor then major)
bump_semver_like() {
  local v="${1:-0.1}"
  local major="${v%%.*}"
  local minor="${v#*.}"
  [[ "$major" =~ ^[0-9]+$ ]] || major=0
  [[ "$minor" =~ ^[0-9]+$ ]] || minor=1
  if (( minor >= 10 )); then
    major=$((major + 1)); minor=0
  else
    minor=$((minor + 1))
  fi
  echo "${major}.${minor}"
}

insert_header_block() {
  # $1=file  $2=initial_version
  local f="$1" v="$2"
  local block
  block="###############################################
# Author : ${AUTHOR}
# Date   : ${TODAY}
# Version: ${v}
###############################################"
  if head -n1 "$f" | grep -q '^#!'; then
    { head -n1 "$f"; printf '%s\n' "$block"; tail -n +2 "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
  else
    { printf '%s\n' "$block"; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
  fi
}

ensure_header_shell() {
  # $1=file (shebang preserved if present)
  local f="$1"
  local cur
  cur="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"
  if [[ -z "$cur" ]]; then
    insert_header_block "$f" "0.1"
  else
    local new; new="$(bump_semver_like "$cur")"
    sedi "s/^# Version: .*/# Version: ${new}/" "$f"
    sedi "s/^# Date   : .*/# Date   : ${TODAY}/" "$f"
  fi
}

ensure_python_version_line() {
  # $1=file  $2=version_to_set (creates or updates __version__)
  local f="$1" v="$2"
  # If __version__ exists, replace its value; else insert near the top (after shebang if present)
  if grep -qE '^__version__\s*=' "$f"; then
    awk -v ver="$v" '
      BEGIN{done=0}
      {
        if(!done && $0 ~ /^__version__[[:space:]]*=/){
          print "__version__ = \"" ver "\""; done=1; next
        }
        print
      }' "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
  else
    if head -n1 "$f" | grep -q '^#!'; then
      { head -n1 "$f"; echo "__version__ = \"${v}\""; tail -n +2 "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
    else
      { echo "__version__ = \"${v}\""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
    fi
  fi
}

ensure_header_python() {
  # $1=file
  local f="$1"
  local cur
  cur="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"

  if [[ -z "$cur" ]]; then
    local init="0.1"
    # Insert header first so we can read it back reliably
    insert_header_block "$f" "$init"
    ensure_python_version_line "$f" "$init"
  else
    local new; new="$(bump_semver_like "$cur")"
    # Update header fields
    sedi "s/^# Version: .*/# Version: ${new}/" "$f"
    sedi "s/^# Date   : .*/# Date   : ${TODAY}/" "$f"
    # Sync __version__ to header (new)
    ensure_python_version_line "$f" "$new"
  fi
}

# ---- Collect tracked candidate files recursively (respects .gitignore) ----
FILES=()
while IFS= read -r -d '' f; do FILES+=("$f"); done < <(git ls-files -z '**/*.sh' '**/*.zsh' '**/*.py')

# Nothing to do?
if [[ "${#FILES[@]}" -eq 0 ]]; then
  echo "version_check.sh: No *.sh/*.zsh/*.py files found via git ls-files."
  exit 0
fi

# ---- Process files ----
for f in "${FILES[@]}"; do
  case "$f" in
    *.sh|*.zsh)
      echo "Updating header (shell): $f"
      ensure_header_shell "$f"
      ;;
    *.py)
      echo "Updating header + __version__ (python): $f"
      ensure_header_python "$f"
      ;;
  esac
done

echo "version_check.sh: done."