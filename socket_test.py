"""Validate the live socket transport against the running bridge in ArcGIS Pro."""
import os, sys, time
sys.path.insert(0, r"D:\mcp para arguis pro\hardening")
import bridge_transport as bt

ipc = os.path.join(os.path.expanduser("~"), ".arcgis_mcp")
host, port = bt.read_port_file(ipc)
print("port.json ->", host, port)

t0 = time.time()
resp = bt.send_request(port, "ping", {}, host=host, timeout=10)
ms = round((time.time() - t0) * 1000, 1)
data = resp.get("data") if isinstance(resp.get("data"), dict) else {}
print("ping ok=%s status=%s version=%s latency=%sms protocol=%s" % (
    resp.get("ok"), data.get("status"), data.get("version"), ms, resp.get("protocol")))

r2 = bt.send_request(port, "recipe",
                     {"name": "qa_layer", "params": {"layer_name": "puntos_densidad_arguis_pro_XYTableToPoint"}},
                     host=host, timeout=20)
d2 = r2.get("data") or {}
print("recipe/qa_layer via socket ok=%s features=%s crs=%s protocol=%s" % (
    r2.get("ok"), d2.get("feature_count"), (d2.get("crs") or {}).get("name"), r2.get("protocol")))
