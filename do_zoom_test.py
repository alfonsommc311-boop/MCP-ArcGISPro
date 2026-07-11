"""Verify a ROBUST zoom: use Describe(layer).extent (reliable) vs getLayerExtent (view-dependent)."""
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
m = get_map()
lyr = m.listLayers("puntos_densidad_buffer_50m")[0]
sr_utm = arcpy.Describe(lyr).spatialReference

def meters(e):
    if e is None: return None
    em = e.projectAs(sr_utm)
    return {"width_m": round(em.XMax-em.XMin,1), "height_m": round(em.YMax-em.YMin,1)}

# getLayerExtent (view-dependent)
gle = meters(mv.getLayerExtent(lyr, False, True))

# Describe extent (reliable, from data source)
desc_ext = arcpy.Describe(lyr).extent
desc_m = meters(desc_ext)

# Robust zoom: set camera to the Describe extent (carries UTM SR -> reprojected by ArcGIS)
mv.camera.setExtent(desc_ext)
cam_after = meters(mv.camera.getExtent())

result = {
    "getLayerExtent_m": gle,
    "describe_extent_m": desc_m,
    "camera_after_setExtent_m": cam_after,
    "robust_zoom_ok": bool(cam_after and cam_after["width_m"] > 100),
}
"""

print(json.dumps(call("execute_python", {"code": code}), indent=2, ensure_ascii=False))
