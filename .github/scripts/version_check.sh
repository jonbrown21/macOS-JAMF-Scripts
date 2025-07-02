#!/bin/bash

# version_check.sh
# Adds or updates version headers in shell scripts

AUTHOR="Jon Brown"
TODAY=$(date +%Y-%m-%d)

for file in Scripts/*; do
  [[ "$file" != *.sh && "$file" != *.zsh ]] && continue

  HEADER=$(grep -m1 '^# Version:' "$file")
  if [[ -z "$HEADER" ]]; then
    sed -i '1i\
###############################################\
\n# Author : '"$AUTHOR"'\
\n# Date   : '"$TODAY"'\
\n# Version: 0.1\
\n###############################################\
\n' "$file"
  else
    VERSION=$(echo "$HEADER" | awk '{print $3}')
    MAJOR=$(echo $VERSION | cut -d. -f1)
    MINOR=$(echo $VERSION | cut -d. -f2)
    if [[ "$MINOR" -ge 10 ]]; then
      MAJOR=$((MAJOR + 1))
      MINOR=0
    else
      MINOR=$((MINOR + 1))
    fi
    NEW_VERSION="$MAJOR.$MINOR"
    sed -i "s/^# Version: .*/# Version: $NEW_VERSION/" "$file"
    sed -i "s/^# Date   : .*/# Date   : $TODAY/" "$file"
  fi
done