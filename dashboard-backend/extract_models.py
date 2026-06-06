import sys

source = r"c:\Users\belam\OneDrive\Bureau\1Program\temacina-project\SAFEX_DATA_LAYER_ROADMAP.txt"
dest = r"c:\Users\belam\OneDrive\Bureau\1Program\temacina-project\dashboard-backend\apps\safex\models.py"

with open(source, "r", encoding="utf-8") as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if line.startswith("from django.db import models"):
        start = i
    elif start != -1 and line.startswith("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"):
        end = i - 1
        break

if start != -1 and end != -1:
    with open(dest, "w", encoding="utf-8") as f:
        f.writelines(lines[start:end])
    print(f"Successfully extracted {end - start} lines to {dest}")
else:
    print(f"Failed to find start/end: start={start}, end={end}")
