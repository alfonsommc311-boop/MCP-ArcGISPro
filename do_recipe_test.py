"""Exercise the new 'recipe' bridge op via IPC (what the run_recipe MCP tool sends)."""
import os, json, time

IPC = os.path.join(os.path.expanduser("~"), ".arcgis_mcp")
CMD, RES, LOCK = (os.path.join(IPC, x) for x in ("command.json", "result.json", "lock"))


def call(op, args):
    for f in (RES, LOCK):
        try: os.remove(f)
        except FileNotFoundError: pass
    with open(CMD, "w", encoding="utf-8") as f:
        json.dump({"op": op, "args": args}, f)
    deadline = time.time() + 60
    while time.time() < deadline:
        if os.path.exists(RES) and not os.path.exists(LOCK):
            with open(RES, "r", encoding="utf-8") as f:
                return json.load(f)
        time.sleep(0.1)
    return {"ok": False, "error": "timeout"}


LYR = "puntos_densidad_arguis_pro_XYTableToPoint"
import tempfile
csv_out = os.path.join(tempfile.gettempdir(), "recipe_attrs.csv")

print(">> recipe qa_layer")
print(json.dumps(call("recipe", {"name": "qa_layer", "params": {"layer_name": LYR}}), indent=2, ensure_ascii=False)[:900])

print("\n>> recipe export_attributes_csv (limit 2)")
print(json.dumps(call("recipe", {"name": "export_attributes_csv",
      "params": {"layer_name": LYR, "out_path": csv_out, "limit": 2}}), indent=2, ensure_ascii=False))

print("\n>> recipe unknown (error path)")
print(json.dumps(call("recipe", {"name": "does_not_exist", "params": {}}), indent=2, ensure_ascii=False))
