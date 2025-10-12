#!/usr/bin/env bash
# version_check.sh — recursive version header updater for sh/zsh/py
# - Finds tracked *.sh, *.zsh, *.py (respects .gitignore)
# - Ensures a header block with Author / Date / Version
# - Bumps Version (MAJOR.MINOR) if header exists
# - For Python: keeps __version__ in sync with the header
set -euo pipefail

AUTHOR="Jon Brown"
TODAY="$(date +%Y-%m-%d)"

# sed -i helper using extended regex (-E) on GNU and BSD sed
sedi() {
  if sed --version >/dev/null 2>&1; then
    sed -E -i "$@"
  else
    sed -E -i '' "$@"
  fi
}

bump_semver_like() {
  local v="${1:-0.1}"
  local major="${v%%.*}"
  local minor="${v#*.}"
  [[ "$major" =~ ^[0-9]+$ ]] || major=0
  [[ "$minor" =~ ^[0-9]+$ ]] || minor=1
  if (( minor >= 10 )); then major=$((major + 1)); minor=0; else minor=$((minor + 1)); fi
  echo "${major}.${minor}"
}

insert_header_block() {
  local f="$1" v="$2"
  local block="###############################################
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
  local f="$1"
  local cur; cur="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"
  if [[ -z "$cur" ]]; then
    insert_header_block "$f" "0.1"
  else
    local new; new="$(bump_semver_like "$cur")"
    sedi "s/^# Version: .*/# Version: ${new}/" "$f"
    sedi "s/^# Date   : .*/# Date   : ${TODAY}/" "$f"
  fi
}

ensure_python_version_line() {
  local f="$1" v="$2"
  # remove any stray __version__ lines that might be above the header
  awk '!/^__version__/ {print}' "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"

  if grep -qE '^# Version:' "$f"; then
    # insert __version__ immediately after the header block
    awk -v ver="$v" '
      BEGIN { seen=0; lines=0 }
      {
        print
        if (!seen && $0 ~ /^###############################################$/) {
          lines++
          if (lines==5) { print "__version__ = \"" ver "\""; seen=1 }
        }
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
  local f="$1"
  local cur; cur="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"
  if [[ -z "$cur" ]]; then
    local init="0.1"
    insert_header_block "$f" "$init"
    ensure_python_version_line "$f" "$init"
  else
    local new; new="$(bump_semver_like "$cur")"
    sedi "s/^# Version: .*/# Version: ${new}/" "$f"
    sedi "s/^# Date   : .*/# Date   : ${TODAY}/" "$f"
    ensure_python_version_line "$f" "$new"
  fi
}

# Collect tracked files (respects .gitignore)
FILES=()
while IFS= read -r -d '' f; do FILES+=("$f"); done < <(git ls-files -z '**/*.sh' '**/*.zsh' '**/*.py')

if [[ "${#FILES[@]}" -eq 0 ]]; then
  echo "version_check.sh: No *.sh/*.zsh/*.py files found."
  exit 0
fi

for f in "${FILES[@]}"; do
  case "$f" in
    *.sh|*.zsh) echo "Updating header (shell): $f"; ensure_header_shell "$f" ;;
    *.py)       echo "Updating header + __version__ (python): $f"; ensure_header_python "$f" ;;
  esac
done

echo "✅ version_check.sh: All done."