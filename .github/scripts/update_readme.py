###############################################
# Author : Jon Brown
# Date   : 2025-10-27
# Version: 0.5
###############################################
START_MARKER = "<!-- VERSION_HISTORY_START -->"
END_MARKER = "<!-- VERSION_HISTORY_END -->"

with open("RELEASE_NOTES.md") as f:
    notes = f.read()

with open("README.md") as f:
    lines = f.readlines()

start = lines.index(START_MARKER + "\n")
end = lines.index(END_MARKER + "\n")

new_lines = lines[:start+1] + [notes + "\n"] + lines[end:]
with open("README.md", "w") as f:
    f.writelines(new_lines)

