import sys
import os

source = r"c:\Users\belam\OneDrive\Bureau\1Program\temacina-project\SAFEX_DATA_LAYER_ROADMAP.txt"
dest_dir = r"c:\Users\belam\OneDrive\Bureau\1Program\temacina-project\dashboard-backend\apps\safex\services"
dest = os.path.join(dest_dir, "company.py")
init_file = os.path.join(dest_dir, "__init__.py")

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
if not os.path.exists(init_file):
    with open(init_file, "w") as f:
        pass

with open(source, "r", encoding="utf-8") as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if line.startswith("from django.core.cache import cache") and i > 600:
        start = i
    elif start != -1 and line.startswith("────────────────────────────────────────────────────────────") and i > start:
        end = i - 1
        break

if start != -1 and end != -1:
    with open(dest, "w", encoding="utf-8") as f:
        f.writelines(lines[start:end])
    print(f"Successfully extracted {end - start} lines to {dest}")
else:
    print(f"Failed to find start/end: start={start}, end={end}")
