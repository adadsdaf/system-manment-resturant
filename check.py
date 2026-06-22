with open("ui/admin_settings.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines[:60], start=1):
    print(f"{i}: {line}", end="")
