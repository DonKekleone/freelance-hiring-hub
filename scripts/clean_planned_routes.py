from pathlib import Path

planned_file = Path("planned_routes.txt")

routes = [
    line.strip()
    for line in planned_file.read_text().splitlines()
    if line.strip() and not line.strip().startswith("#")
]

remaining = []
completed = []

for route in routes:
    target = Path(route.strip("/")) / "index.html"

    if target.exists():
        completed.append(route)
    else:
        remaining.append(route)

planned_file.write_text(
    "\n".join(sorted(remaining)) + ("\n" if remaining else "")
)

print(f"Completed routes removed: {len(completed)}")
print(f"Remaining planned routes: {len(remaining)}")
