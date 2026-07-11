"""Helper: send one command to the ArcGIS Pro bridge via IPC and print the result.
Usage: python arcgis_call.py <op> '<json_args>'
"""
import os, json, time, sys

IPC = os.path.join(os.path.expanduser("~"), ".arcgis_mcp")
CMD = os.path.join(IPC, "command.json")
RES = os.path.join(IPC, "result.json")
LOCK = os.path.join(IPC, "lock")

op = sys.argv[1]
args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

for f in (RES, LOCK):
    try: os.remove(f)
    except FileNotFoundError: pass

with open(CMD, "w", encoding="utf-8") as f:
    json.dump({"op": op, "args": args}, f)

deadline = time.time() + 30
while time.time() < deadline:
    if os.path.exists(RES) and not os.path.exists(LOCK):
        with open(RES, "r", encoding="utf-8") as f:
            print(f.read())
        sys.exit(0)
    time.sleep(0.1)
print('{"ok": false, "error": "timeout"}')
sys.exit(1)
