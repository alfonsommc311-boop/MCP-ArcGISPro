"""One-off: run Buffer on the density points via the ArcGIS Pro bridge, add result to map, zoom."""
import os, json, time

IPC = os.path.join(os.path.expanduser("~"), ".arcgis_mcp")
CMD = os.path.join(IPC, "command.json")
RES = os.path.join(IPC, "result.json")
LOCK = os.path.join(IPC, "lock")


def call(op, args=None):
    args = args or {}
    for f in (RES, LOCK):
        try:
            os.remove(f)
        except FileNotFoundError:
            pass
    with open(CMD, "w", encoding="utf-8") as f:
        json.dump({"op": op, "args": args}, f)
    deadline = time.time() + 60
    while time.time() < deadline:
        if os.path.exists(RES) and not os.path.exists(LOCK):
            with open(RES, "r", encoding="utf-8") as f:
                return json.load(f)
        time.sleep(0.1)
    return {"ok": False, "error": "timeout"}


GDB = r"C:\Users\USUARIO\Documents\ArcGIS\Projects\pistas y veresa virgen de fatima\pistas y veresa virgen de fatima.gdb"
IN = os.path.join(GDB, "puntos_densidad_arguis_pro_XYTableToPoint")
OUT = os.path.join(GDB, "puntos_densidad_buffer_50m")
OUT_NAME = "puntos_densidad_buffer_50m"

print(">> Buffer 50 m ...")
r = call("run_geoprocessing", {"tool": "analysis.Buffer", "params": [IN, OUT, "50 Meters"]})
print(json.dumps(r, indent=2, ensure_ascii=False))
if not r.get("ok"):
    raise SystemExit("Buffer failed")

print(">> Add buffer layer to map ...")
print(json.dumps(call("add_vector_layer", {"path": OUT}), indent=2, ensure_ascii=False))

print(">> Count features in buffer ...")
print(json.dumps(call("count_features", {"layer": OUT_NAME}), indent=2, ensure_ascii=False))

print(">> Zoom to buffer ...")
print(json.dumps(call("zoom_to_layer", {"name": OUT_NAME}), indent=2, ensure_ascii=False))
