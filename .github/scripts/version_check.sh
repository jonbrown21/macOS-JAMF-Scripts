#!/bin/bash
# version_check.sh — recursive version header updater for sh/zsh/py

set -euo pipefail

AUTHOR="Jon Brown"
TODAY="$(date +%Y-%m-%d)"

# Portable in-place sed (macOS/BSD + GNU)
sedi() {
  if sed --version >/dev/null 2>&1; then
    sed -i "$@"
  else
    # BSD sed needs a backup suffix (empty string)
    sed -i '' "$@"
  fi
}

bump_semver_like() {
  # Accepts MAJOR.MINOR (defaults to 0.1)
  local v="${1:-0.1}"
  local major="${v%%.*}"
  local minor="${v#*.}"
  # fallback if parse fails
  [[ "$major" =~ ^[0-9]+$ ]] || major=0
  [[ "$minor" =~ ^[0-9]+$ ]] || minor=1

  if (( minor >= 10 )); then
    major=$((major + 1))
    minor=0
  else
    minor=$((minor + 1))
  fi
  echo "${major}.${minor}"
}

ensure_header_shell() {
  # $1=file  (shebang preserved if present)
  local f="$1"
  local hdr_version
  hdr_version="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"
  local new_version

  if [[ -z "$hdr_version" ]]; then
    new_version="$(bump_semver_like "")"
    if head -n1 "$f" | grep -q '^#!'; then
      # insert after shebang
      {
        head -n1 "$f"
        printf '%s\n' \
"###############################################
# Author : ${AUTHOR}
# Date   : ${TODAY}
# Version: ${new_version}
###############################################"
        tail -n +2 "$f"
      } >"${f}.tmp" && mv "${f}.tmp" "$f"
    else
      # insert at top
      {
        printf '%s\n' \
"###############################################
# Author : ${AUTHOR}
# Date   : ${TODAY}
# Version: ${new_version}
###############################################"
        cat "$f"
      } >"${f}.tmp" && mv "${f}.tmp" "$f"
    fi
  else
    new_version="$(bump_semver_like "$hdr_version")"
    sedi "s/^# Version: .*/# Version: ${new_version}/" "$f"
    sedi "s/^# Date   : .*/# Date   : ${TODAY}/" "$f"
  fi
}

ensure_header_python() {
  # $1=file  (header + __version__)
  local f="$1"
  local hdr_version
  hdr_version="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"
  local new_version

  # 1) __version__ line
  if grep -qE '^__version__\s*=' "$f"; then
    :
  else
    if head -n1 "$f" | grep -q '^#!'; then
      { head -n1 "$f"; echo '__version__ = "0.1"'; tail -n +2 "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
    else
      { echo '__version__ = "0.1"'; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
    fi
  fi

  # 2) Header comment block
  if [[ -z "$hdr_version" ]]; then
    new_version="0.1"
    if head -n1 "$f" | grep -q '^#!'; then
      { head -n1 "$f"
        printf '%s\n' \
"###############################################
# Author : ${AUTHOR}
# Date   : ${TODAY}
# Version: ${new_version}
###############################################"
        tail -n +2 "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
    else
      { printf '%s\n' \
"###############################################
# Author : ${AUTHOR}
# Date   : ${TODAY}
# Version: ${new_version}
###############################################"
        cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
    fi
  else
    new_version="$(bump_semver_like "$hdr_version")"
    sedi "s/^# Version: .*/# Version: ${new_version}/" "$f"
    sedi "s/^# Date   : .*/# Date   : ${TODAY}/" "$f"
  fi

  # 3) Keep __version__ in sync with header
  local hv
  hv="$(awk -F': ' '/^# Version:/{print $2; exit}' "$f")"
  if [[ -n "$hv" ]]; then
    sedi "s/^(__version__\s*=\s*).*/\1\"${hv}\"/" "$f"
  fi
}

export LC_ALL=C
# Recursively enumerate tracked files that match our patterns
mapfile -d '' FILES < <(git ls-files -z '**/*.sh' '**/*.zsh' '**/*.py')

for f in "${FILES[@]}"; do
  case "$f" in
    *.sh|*.zsh) ensure_header_shell  "$f" ;;
    *.py)      ensure_header_python "$f" ;;
  esac
done