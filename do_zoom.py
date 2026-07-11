"""Zoom the active map view to the buffer layer, using the correct ArcGIS Pro API."""
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


code = r"""
mv = proj.activeView
if mv is None or not hasattr(mv, 'getLayerExtent'):
    result = {"zoomed": False, "reason": "no map view active - click the Map tab in ArcGIS Pro"}
else:
    lyr = get_map().listLayers("puntos_densidad_buffer_50m")[0]
    ext = mv.getLayerExtent(lyr, False, True)
    mv.camera.setExtent(ext)
    result = {"zoomed": True, "layer": lyr.name}
"""

print(json.dumps(call("execute_python", {"code": code}), indent=2, ensure_ascii=False))
